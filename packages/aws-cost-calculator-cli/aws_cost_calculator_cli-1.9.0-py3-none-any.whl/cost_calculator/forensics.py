"""
Cost forensics module - Resource inventory and CloudTrail analysis
"""
import boto3
from datetime import datetime, timedelta
from collections import defaultdict
import json


def inventory_resources(account_id, profile, region='us-west-2'):
    """
    Inventory AWS resources in an account
    
    Args:
        account_id: AWS account ID
        profile: AWS profile name (SSO)
        region: AWS region
        
    Returns:
        dict with resource inventory
    """
    session = boto3.Session(profile_name=profile)
    inventory = {
        'account_id': account_id,
        'profile': profile,
        'region': region,
        'timestamp': datetime.utcnow().isoformat(),
        'ec2_instances': [],
        'efs_file_systems': [],
        'load_balancers': [],
        'dynamodb_tables': []
    }
    
    try:
        # EC2 Instances
        ec2_client = session.client('ec2', region_name=region)
        instances_response = ec2_client.describe_instances()
        
        for reservation in instances_response['Reservations']:
            for instance in reservation['Instances']:
                if instance['State']['Name'] == 'running':
                    name = 'N/A'
                    for tag in instance.get('Tags', []):
                        if tag['Key'] == 'Name':
                            name = tag['Value']
                            break
                    
                    inventory['ec2_instances'].append({
                        'instance_id': instance['InstanceId'],
                        'instance_type': instance['InstanceType'],
                        'name': name,
                        'state': instance['State']['Name'],
                        'launch_time': instance['LaunchTime'].isoformat(),
                        'availability_zone': instance['Placement']['AvailabilityZone']
                    })
        
        # EFS File Systems
        efs_client = session.client('efs', region_name=region)
        efs_response = efs_client.describe_file_systems()
        
        total_efs_size = 0
        for fs in efs_response['FileSystems']:
            size_bytes = fs['SizeInBytes']['Value']
            size_gb = size_bytes / (1024**3)
            total_efs_size += size_gb
            
            inventory['efs_file_systems'].append({
                'file_system_id': fs['FileSystemId'],
                'name': fs.get('Name', 'N/A'),
                'size_gb': round(size_gb, 2),
                'creation_time': fs['CreationTime'].isoformat(),
                'number_of_mount_targets': fs['NumberOfMountTargets']
            })
        
        inventory['total_efs_size_gb'] = round(total_efs_size, 2)
        
        # Load Balancers
        elbv2_client = session.client('elbv2', region_name=region)
        elb_response = elbv2_client.describe_load_balancers()
        
        for lb in elb_response['LoadBalancers']:
            inventory['load_balancers'].append({
                'name': lb['LoadBalancerName'],
                'type': lb['Type'],
                'dns_name': lb['DNSName'],
                'scheme': lb['Scheme'],
                'created_time': lb['CreatedTime'].isoformat(),
                'availability_zones': [az['ZoneName'] for az in lb['AvailabilityZones']]
            })
        
        # DynamoDB Tables (only if region supports it)
        try:
            ddb_client = session.client('dynamodb', region_name=region)
            tables_response = ddb_client.list_tables()
            
            for table_name in tables_response['TableNames'][:20]:  # Limit to 20 tables
                table_desc = ddb_client.describe_table(TableName=table_name)
                table_info = table_desc['Table']
                
                # Get backup settings
                try:
                    backup_desc = ddb_client.describe_continuous_backups(TableName=table_name)
                    pitr_status = backup_desc['ContinuousBackupsDescription']['PointInTimeRecoveryDescription']['PointInTimeRecoveryStatus']
                except:
                    pitr_status = 'UNKNOWN'
                
                size_gb = table_info.get('TableSizeBytes', 0) / (1024**3)
                
                inventory['dynamodb_tables'].append({
                    'table_name': table_name,
                    'size_gb': round(size_gb, 2),
                    'item_count': table_info.get('ItemCount', 0),
                    'pitr_status': pitr_status,
                    'created_time': table_info['CreationDateTime'].isoformat()
                })
        except Exception as e:
            # DynamoDB might not be available in all regions
            pass
            
    except Exception as e:
        inventory['error'] = str(e)
    
    return inventory


def analyze_cloudtrail(account_id, profile, start_date, end_date, region='us-west-2'):
    """
    Analyze CloudTrail events for an account
    
    Args:
        account_id: AWS account ID
        profile: AWS profile name (SSO)
        start_date: Start datetime
        end_date: End datetime
        region: AWS region
        
    Returns:
        dict with CloudTrail event summary
    """
    session = boto3.Session(profile_name=profile)
    ct_client = session.client('cloudtrail', region_name=region)
    
    analysis = {
        'account_id': account_id,
        'profile': profile,
        'region': region,
        'start_date': start_date.isoformat(),
        'end_date': end_date.isoformat(),
        'event_summary': {},
        'write_events': [],
        'error': None
    }
    
    # Events that indicate resource creation/modification
    write_event_names = [
        'RunInstances', 'CreateVolume', 'AttachVolume',
        'CreateFileSystem', 'ModifyFileSystem',
        'CreateLoadBalancer', 'ModifyLoadBalancerAttributes',
        'CreateTable', 'UpdateTable', 'UpdateContinuousBackups',
        'CreateBackupVault', 'StartBackupJob'
    ]
    
    try:
        event_counts = defaultdict(int)
        
        # Query CloudTrail
        paginator = ct_client.get_paginator('lookup_events')
        
        for page in paginator.paginate(
            StartTime=start_date,
            EndTime=end_date,
            MaxResults=50,
            PaginationConfig={'MaxItems': 200}
        ):
            for event in page.get('Events', []):
                event_name = event.get('EventName', '')
                event_counts[event_name] += 1
                
                # Capture write events
                if event_name in write_event_names:
                    event_detail = json.loads(event['CloudTrailEvent'])
                    
                    analysis['write_events'].append({
                        'time': event.get('EventTime').isoformat(),
                        'event_name': event_name,
                        'username': event.get('Username', 'N/A'),
                        'resources': [
                            {
                                'type': r.get('ResourceType', 'N/A'),
                                'name': r.get('ResourceName', 'N/A')
                            }
                            for r in event.get('Resources', [])[:3]
                        ]
                    })
        
        # Convert to regular dict and sort
        analysis['event_summary'] = dict(sorted(
            event_counts.items(),
            key=lambda x: x[1],
            reverse=True
        ))
        
    except Exception as e:
        analysis['error'] = str(e)
    
    return analysis


def format_investigation_report(cost_data, inventories, cloudtrail_data=None):
    """
    Format investigation data into markdown report
    
    Args:
        cost_data: Cost analysis results from trends/drill
        inventories: List of resource inventories
        cloudtrail_data: List of CloudTrail analyses (optional)
        
    Returns:
        str: Markdown formatted report
    """
    report = []
    report.append("# Cost Investigation Report")
    report.append(f"**Generated:** {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}")
    report.append("")
    
    # Cost Analysis Section
    if cost_data:
        report.append("## Cost Analysis")
        report.append("")
        # Add cost data formatting here
        # This will be populated from trends/drill results
    
    # Resource Inventory Section
    if inventories:
        report.append("## Resource Inventory")
        report.append("")
        
        for inv in inventories:
            profile_name = inv.get('profile', inv['account_id'])
            report.append(f"### Account {inv['account_id']} ({profile_name})")
            report.append(f"**Region:** {inv['region']}")
            report.append("")
            
            # EC2 Instances
            if inv['ec2_instances']:
                report.append(f"**EC2 Instances:** {len(inv['ec2_instances'])} running")
                for instance in inv['ec2_instances'][:10]:  # Show first 10
                    report.append(f"- `{instance['instance_id']}`: {instance['instance_type']} ({instance['name']})")
                    report.append(f"  - Launched: {instance['launch_time'][:10]}, AZ: {instance['availability_zone']}")
                if len(inv['ec2_instances']) > 10:
                    report.append(f"  ... and {len(inv['ec2_instances']) - 10} more")
                report.append("")
            
            # EFS File Systems
            if inv['efs_file_systems']:
                total_size = inv.get('total_efs_size_gb', 0)
                report.append(f"**EFS File Systems:** {len(inv['efs_file_systems'])} total, {total_size:,.0f} GB")
                for fs in inv['efs_file_systems']:
                    report.append(f"- `{fs['file_system_id']}` ({fs['name']}): {fs['size_gb']:,.2f} GB")
                    report.append(f"  - Created: {fs['creation_time'][:10]}")
                report.append("")
            
            # Load Balancers
            if inv['load_balancers']:
                report.append(f"**Load Balancers:** {len(inv['load_balancers'])}")
                for lb in inv['load_balancers'][:10]:  # Show first 10
                    report.append(f"- `{lb['name']}`: {lb['type']}")
                    report.append(f"  - Created: {lb['created_time'][:10]}, Scheme: {lb['scheme']}")
                if len(inv['load_balancers']) > 10:
                    report.append(f"  ... and {len(inv['load_balancers']) - 10} more")
                report.append("")
            
            # DynamoDB Tables
            if inv['dynamodb_tables']:
                report.append(f"**DynamoDB Tables:** {len(inv['dynamodb_tables'])}")
                for table in inv['dynamodb_tables'][:10]:
                    report.append(f"- `{table['table_name']}`: {table['size_gb']:.2f} GB, {table['item_count']:,} items")
                    report.append(f"  - PITR: {table['pitr_status']}, Created: {table['created_time'][:10]}")
                if len(inv['dynamodb_tables']) > 10:
                    report.append(f"  ... and {len(inv['dynamodb_tables']) - 10} more")
                report.append("")
            
            report.append("---")
            report.append("")
    
    # CloudTrail Section
    if cloudtrail_data:
        report.append("## CloudTrail Events")
        report.append("")
        
        for ct in cloudtrail_data:
            profile_name = ct.get('profile', ct['account_id'])
            report.append(f"### Account {ct['account_id']} ({profile_name})")
            report.append(f"**Period:** {ct['start_date'][:10]} to {ct['end_date'][:10]}")
            report.append("")
            
            if ct.get('error'):
                report.append(f"⚠️ Error: {ct['error']}")
                report.append("")
                continue
            
            # Write events (resource changes)
            if ct['write_events']:
                report.append(f"**Resource Changes:** {len(ct['write_events'])} events")
                for evt in ct['write_events'][:10]:
                    report.append(f"- `{evt['time'][:19]}` - **{evt['event_name']}**")
                    report.append(f"  - User: {evt['username']}")
                    if evt['resources']:
                        for res in evt['resources']:
                            report.append(f"  - Resource: {res['type']} - {res['name']}")
                report.append("")
            
            # Event summary
            if ct['event_summary']:
                report.append("**Top Events:**")
                for event_name, count in list(ct['event_summary'].items())[:15]:
                    report.append(f"- {event_name}: {count}")
                report.append("")
            
            report.append("---")
            report.append("")
    
    return "\n".join(report)

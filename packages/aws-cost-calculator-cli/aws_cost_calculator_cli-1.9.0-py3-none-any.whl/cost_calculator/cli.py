#!/usr/bin/env python3
"""
AWS Cost Calculator CLI

Usage:
    cc --profile myprofile
    cc --profile myprofile --start-date 2025-11-04
    cc --profile myprofile --offset 2 --window 30
"""

import click
import boto3
import json
import os
import platform
from datetime import datetime, timedelta
from pathlib import Path
from cost_calculator.trends import format_trends_markdown
from cost_calculator.monthly import format_monthly_markdown
from cost_calculator.drill import format_drill_down_markdown
from cost_calculator.executor import execute_trends, execute_monthly, execute_drill


def apply_auth_options(config, sso=None, access_key_id=None, secret_access_key=None, session_token=None):
    """Apply authentication options to profile config
    
    Args:
        config: Profile configuration dict
        sso: AWS SSO profile name
        access_key_id: AWS Access Key ID
        secret_access_key: AWS Secret Access Key
        session_token: AWS Session Token
    
    Returns:
        Updated config dict
    """
    import subprocess
    
    if sso:
        # SSO authentication - trigger login if needed
        try:
            # Test if SSO session is valid
            result = subprocess.run(
                ['aws', 'sts', 'get-caller-identity', '--profile', sso],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                if 'expired' in result.stderr.lower() or 'token' in result.stderr.lower():
                    click.echo(f"SSO session expired or not initialized. Logging in...")
                    subprocess.run(['aws', 'sso', 'login', '--profile', sso], check=True)
        except Exception as e:
            click.echo(f"Warning: Could not verify SSO session: {e}")
        
        config['aws_profile'] = sso
    elif access_key_id and secret_access_key:
        # Static credentials provided via CLI
        config['credentials'] = {
            'aws_access_key_id': access_key_id,
            'aws_secret_access_key': secret_access_key,
            'region': 'us-east-1'
        }
        if session_token:
            config['credentials']['aws_session_token'] = session_token
    
    return config


def load_profile(profile_name):
    """Load profile configuration from local file or DynamoDB API"""
    import os
    import requests
    
    config_dir = Path.home() / '.config' / 'cost-calculator'
    config_file = config_dir / 'profiles.json'
    creds_file = config_dir / 'credentials.json'
    
    # Try local file first
    if config_file.exists():
        with open(config_file) as f:
            profiles = json.load(f)
        
        if profile_name in profiles:
            profile = profiles[profile_name]
            
            # Load credentials if using static credentials (not SSO)
            if 'aws_profile' not in profile:
                if not creds_file.exists():
                    # Try environment variables
                    if os.environ.get('AWS_ACCESS_KEY_ID'):
                        profile['credentials'] = {
                            'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
                            'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
                            'aws_session_token': os.environ.get('AWS_SESSION_TOKEN')
                        }
                        return profile
                    
                    raise click.ClickException(
                        f"No credentials found for profile '{profile_name}'.\n"
                        f"Run: cc configure --profile {profile_name}"
                    )
                
                with open(creds_file) as f:
                    creds = json.load(f)
                
                if profile_name not in creds:
                    raise click.ClickException(
                        f"No credentials found for profile '{profile_name}'.\n"
                        f"Run: cc configure --profile {profile_name}"
                    )
                
                profile['credentials'] = creds[profile_name]
            
            return profile
    
    # Profile not found locally - try DynamoDB API
    api_secret = os.environ.get('COST_API_SECRET')
    if not api_secret:
        raise click.ClickException(
            f"Profile '{profile_name}' not found locally and COST_API_SECRET not set.\n"
            f"Run: cc init --profile {profile_name}"
        )
    
    try:
        response = requests.post(
            'https://64g7jq7sjygec2zmll5lsghrpi0txrzo.lambda-url.us-east-1.on.aws/',
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get', 'profile_name': profile_name},
            timeout=10
        )
        
        if response.status_code == 200:
            response_data = response.json()
            # API returns {"profile": {...}} wrapper
            profile_data = response_data.get('profile', response_data)
            profile = {'accounts': profile_data['accounts']}
            
            # Check for AWS_PROFILE environment variable (SSO support)
            if os.environ.get('AWS_PROFILE'):
                profile['aws_profile'] = os.environ['AWS_PROFILE']
            # Use environment credentials
            elif os.environ.get('AWS_ACCESS_KEY_ID'):
                profile['credentials'] = {
                    'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
                    'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
                    'aws_session_token': os.environ.get('AWS_SESSION_TOKEN')
                }
            
            return profile
        else:
            raise click.ClickException(
                f"Profile '{profile_name}' not found in DynamoDB.\n"
                f"Run: cc profile create --name {profile_name} --accounts \"...\""
            )
    except requests.exceptions.RequestException as e:
        raise click.ClickException(
            f"Failed to fetch profile from API: {e}\n"
            f"Run: cc init --profile {profile_name}"
        )


def calculate_costs(profile_config, accounts, start_date, offset, window):
    """
    Calculate AWS costs for the specified period.
    
    Args:
        profile_config: Profile configuration (with aws_profile or credentials)
        accounts: List of AWS account IDs
        start_date: Start date (defaults to today)
        offset: Days to go back from start_date (default: 2)
        window: Number of days to analyze (default: 30)
    
    Returns:
        dict with cost breakdown
    """
    # Calculate date range
    if start_date:
        end_date = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        end_date = datetime.now()
    
    # Go back by offset days
    end_date = end_date - timedelta(days=offset)
    
    # Start date is window days before end_date
    start_date_calc = end_date - timedelta(days=window)
    
    # Format for API (end date is exclusive, so add 1 day)
    api_start = start_date_calc.strftime('%Y-%m-%d')
    api_end = (end_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    click.echo(f"Analyzing: {api_start} to {end_date.strftime('%Y-%m-%d')} ({window} days)")
    
    # Initialize boto3 client
    try:
        if 'aws_profile' in profile_config:
            # SSO-based authentication
            aws_profile = profile_config['aws_profile']
            click.echo(f"AWS Profile: {aws_profile} (SSO)")
            click.echo(f"Accounts: {len(accounts)}")
            click.echo("")
            session = boto3.Session(profile_name=aws_profile)
            ce_client = session.client('ce', region_name='us-east-1')
        else:
            # Static credentials
            creds = profile_config['credentials']
            click.echo(f"AWS Credentials: Static")
            click.echo(f"Accounts: {len(accounts)}")
            click.echo("")
            
            session_kwargs = {
                'aws_access_key_id': creds['aws_access_key_id'],
                'aws_secret_access_key': creds['aws_secret_access_key'],
                'region_name': creds.get('region', 'us-east-1')
            }
            
            if 'aws_session_token' in creds:
                session_kwargs['aws_session_token'] = creds['aws_session_token']
            
            session = boto3.Session(**session_kwargs)
            ce_client = session.client('ce')
            
    except Exception as e:
        if 'Token has expired' in str(e) or 'sso' in str(e).lower():
            if 'aws_profile' in profile_config:
                raise click.ClickException(
                    f"AWS SSO session expired or not initialized.\n"
                    f"Run: aws sso login --profile {profile_config['aws_profile']}"
                )
            else:
                raise click.ClickException(
                    f"AWS credentials expired.\n"
                    f"Run: cc configure --profile <profile_name>"
                )
        raise
    
    # Build filter
    cost_filter = {
        "And": [
            {
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": accounts
                }
            },
            {
                "Dimensions": {
                    "Key": "BILLING_ENTITY",
                    "Values": ["AWS"]
                }
            },
            {
                "Not": {
                    "Dimensions": {
                        "Key": "RECORD_TYPE",
                        "Values": ["Tax", "Support"]
                    }
                }
            }
        ]
    }
    
    # Get daily costs
    click.echo("Fetching cost data...")
    try:
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': api_start,
                'End': api_end
            },
            Granularity='DAILY',
            Metrics=['NetAmortizedCost'],
            Filter=cost_filter
        )
    except Exception as e:
        if 'Token has expired' in str(e) or 'expired' in str(e).lower():
            raise click.ClickException(
                f"AWS SSO session expired.\n"
                f"Run: aws sso login --profile {aws_profile}"
            )
        raise
    
    # Calculate total
    total_cost = sum(
        float(day['Total']['NetAmortizedCost']['Amount'])
        for day in response['ResultsByTime']
    )
    
    # Get support cost from the 1st of the month containing the end date
    # Support is charged on the 1st of each month for the previous month's usage
    # For Oct 3-Nov 2 analysis, we get support from Nov 1 (which is October's support)
    support_month_date = end_date.replace(day=1)
    support_date_str = support_month_date.strftime('%Y-%m-%d')
    support_date_end = (support_month_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    click.echo("Fetching support costs...")
    support_response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': support_date_str,
            'End': support_date_end
        },
        Granularity='DAILY',
        Metrics=['NetAmortizedCost'],
        Filter={
            "And": [
                {
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": accounts
                    }
                },
                {
                    "Dimensions": {
                        "Key": "RECORD_TYPE",
                        "Values": ["Support"]
                    }
                }
            ]
        }
    )
    
    support_cost = float(support_response['ResultsByTime'][0]['Total']['NetAmortizedCost']['Amount'])
    
    # Calculate days in the month that the support covers
    # Support on Nov 1 covers October (31 days)
    support_month = support_month_date - timedelta(days=1)  # Go back to previous month
    import calendar
    days_in_support_month = calendar.monthrange(support_month.year, support_month.month)[1]
    
    # Support allocation: divide by 2 (50% allocation), then by days in month
    support_per_day = (support_cost / 2) / days_in_support_month
    
    # Calculate daily rate
    # NOTE: We divide operational by window, but support by days_in_support_month
    # This matches the console's calculation method
    daily_operational = total_cost / days_in_support_month  # Use 31 for October, not 30
    daily_total = daily_operational + support_per_day
    
    # Annual projection
    annual = daily_total * 365
    
    return {
        'period': {
            'start': api_start,
            'end': end_date.strftime('%Y-%m-%d'),
            'days': window
        },
        'costs': {
            'total_operational': total_cost,
            'daily_operational': daily_operational,
            'support_month': support_cost,
            'support_per_day': support_per_day,
            'daily_total': daily_total,
            'annual_projection': annual
        }
    }


@click.group()
def cli():
    """
    AWS Cost Calculator - Calculate daily and annual AWS costs
    
    \b
    Two authentication methods:
    1. AWS SSO (recommended for interactive use)
    2. Static credentials (for automation/CI)
    
    \b
    Quick Start:
      # SSO Method
      aws sso login --profile my_aws_profile
      cc init --profile myprofile --aws-profile my_aws_profile --accounts "123,456,789"
      cc calculate --profile myprofile
    
      # Static Credentials Method
      cc init --profile myprofile --aws-profile dummy --accounts "123,456,789"
      cc configure --profile myprofile
      cc calculate --profile myprofile
    
    \b
    For detailed documentation, see:
      - COST_CALCULATION_METHODOLOGY.md
      - README.md
    """
    pass


@cli.command('setup-cur')
@click.option('--database', required=True, prompt='CUR Athena Database', help='Athena database name for CUR')
@click.option('--table', required=True, prompt='CUR Table Name', help='CUR table name')
@click.option('--s3-output', required=True, prompt='S3 Output Location', help='S3 bucket for Athena query results')
def setup_cur(database, table, s3_output):
    """
    Configure CUR (Cost and Usage Report) settings for resource-level queries
    
    Saves CUR configuration to ~/.config/cost-calculator/cur_config.json
    
    Example:
      cc setup-cur --database my_cur_db --table cur_table --s3-output s3://my-bucket/
    """
    import json
    
    config_dir = Path.home() / '.config' / 'cost-calculator'
    config_dir.mkdir(parents=True, exist_ok=True)
    
    config_file = config_dir / 'cur_config.json'
    
    config = {
        'database': database,
        'table': table,
        's3_output': s3_output
    }
    
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    click.echo(f"✓ CUR configuration saved to {config_file}")
    click.echo(f"  Database: {database}")
    click.echo(f"  Table: {table}")
    click.echo(f"  S3 Output: {s3_output}")
    click.echo("")
    click.echo("You can now use: cc drill --service 'EC2 - Other' --resources")


@cli.command('setup-api')
@click.option('--api-secret', required=True, prompt=True, hide_input=True, help='COST_API_SECRET value')
def setup_api(api_secret):
    """
    Configure COST_API_SECRET for backend API access
    
    Saves the API secret to the appropriate location based on your OS:
    - Mac/Linux: ~/.zshrc or ~/.bashrc
    - Windows: User environment variables
    
    Example:
      cc setup-api --api-secret your-secret-here
      
    Or let it prompt you (input will be hidden):
      cc setup-api
    """
    system = platform.system()
    
    if system == "Windows":
        # Windows: Set user environment variable
        try:
            import winreg
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, 'Environment', 0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, 'COST_API_SECRET', 0, winreg.REG_SZ, api_secret)
            winreg.CloseKey(key)
            click.echo("✓ COST_API_SECRET saved to Windows user environment variables")
            click.echo("  Please restart your terminal for changes to take effect")
        except Exception as e:
            click.echo(f"✗ Error setting Windows environment variable: {e}", err=True)
            click.echo("\nManual setup:")
            click.echo("1. Open System Properties > Environment Variables")
            click.echo("2. Add new User variable:")
            click.echo("   Name: COST_API_SECRET")
            click.echo(f"   Value: {api_secret}")
            return
    else:
        # Mac/Linux: Add to shell profile
        shell = os.environ.get('SHELL', '/bin/bash')
        
        if 'zsh' in shell:
            profile_file = Path.home() / '.zshrc'
        else:
            profile_file = Path.home() / '.bashrc'
        
        # Check if already exists
        export_line = f'export COST_API_SECRET="{api_secret}"'
        
        try:
            if profile_file.exists():
                content = profile_file.read_text()
                if 'COST_API_SECRET' in content:
                    # Replace existing
                    lines = content.split('\n')
                    new_lines = []
                    for line in lines:
                        if 'COST_API_SECRET' in line and line.strip().startswith('export'):
                            new_lines.append(export_line)
                        else:
                            new_lines.append(line)
                    profile_file.write_text('\n'.join(new_lines))
                    click.echo(f"✓ Updated COST_API_SECRET in {profile_file}")
                else:
                    # Append
                    with profile_file.open('a') as f:
                        f.write(f'\n# AWS Cost Calculator API Secret\n{export_line}\n')
                    click.echo(f"✓ Added COST_API_SECRET to {profile_file}")
            else:
                # Create new file
                profile_file.write_text(f'# AWS Cost Calculator API Secret\n{export_line}\n')
                click.echo(f"✓ Created {profile_file} with COST_API_SECRET")
            
            # Also set for current session
            os.environ['COST_API_SECRET'] = api_secret
            click.echo(f"✓ Set COST_API_SECRET for current session")
            click.echo(f"\nTo use in new terminals, run: source {profile_file}")
            
        except Exception as e:
            click.echo(f"✗ Error writing to {profile_file}: {e}", err=True)
            click.echo(f"\nManual setup: Add this line to {profile_file}:")
            click.echo(f"  {export_line}")
            return


@cli.command()
@click.option('--profile', required=True, help='Profile name (e.g., myprofile)')
@click.option('--start-date', help='Start date (YYYY-MM-DD, default: today)')
@click.option('--offset', default=2, help='Days to go back from start date (default: 2)')
@click.option('--window', default=30, help='Number of days to analyze (default: 30)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
@click.option('--sso', help='AWS SSO profile name (e.g., my_sso_profile)')
@click.option('--access-key-id', help='AWS Access Key ID (for static credentials)')
@click.option('--secret-access-key', help='AWS Secret Access Key (for static credentials)')
@click.option('--session-token', help='AWS Session Token (for static credentials)')
def calculate(profile, start_date, offset, window, json_output, sso, access_key_id, secret_access_key, session_token):
    """
    Calculate AWS costs for the specified period
    
    \b
    Authentication Options:
      1. SSO: --sso <profile_name>
         Example: cc calculate --profile myprofile --sso my_sso_profile
      
      2. Static Credentials: --access-key-id, --secret-access-key, --session-token
         Example: cc calculate --profile myprofile --access-key-id ASIA... --secret-access-key ... --session-token ...
      
      3. Environment Variables: AWS_PROFILE or AWS_ACCESS_KEY_ID/AWS_SECRET_ACCESS_KEY
    """
    
    # Load profile configuration
    config = load_profile(profile)
    
    # Apply authentication options
    config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
    
    # Calculate costs
    result = calculate_costs(
        profile_config=config,
        accounts=config['accounts'],
        start_date=start_date,
        offset=offset,
        window=window
    )
    
    if json_output:
        click.echo(json.dumps(result, indent=2))
    else:
        # Pretty print results
        click.echo("=" * 60)
        click.echo(f"Period: {result['period']['start']} to {result['period']['end']}")
        click.echo(f"Days analyzed: {result['period']['days']}")
        click.echo("=" * 60)
        click.echo(f"Total operational cost: ${result['costs']['total_operational']:,.2f}")
        click.echo(f"Daily operational: ${result['costs']['daily_operational']:,.2f}")
        click.echo(f"Support (month): ${result['costs']['support_month']:,.2f}")
        click.echo(f"Support per day (÷2÷days): ${result['costs']['support_per_day']:,.2f}")
        click.echo("=" * 60)
        click.echo(f"DAILY RATE: ${result['costs']['daily_total']:,.2f}")
        click.echo(f"ANNUAL PROJECTION: ${result['costs']['annual_projection']:,.0f}")
        click.echo("=" * 60)


@cli.command()
@click.option('--profile', required=True, help='Profile name to create')
@click.option('--aws-profile', required=True, help='AWS CLI profile name')
@click.option('--accounts', required=True, help='Comma-separated list of account IDs')
def init(profile, aws_profile, accounts):
    """Initialize a new profile configuration"""
    
    config_dir = Path.home() / '.config' / 'cost-calculator'
    config_file = config_dir / 'profiles.json'
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Load existing profiles or create new
    if config_file.exists() and config_file.stat().st_size > 0:
        try:
            with open(config_file) as f:
                profiles = json.load(f)
        except json.JSONDecodeError:
            profiles = {}
    else:
        profiles = {}
    
    # Parse accounts
    account_list = [acc.strip() for acc in accounts.split(',')]
    
    # Add new profile
    profiles[profile] = {
        'aws_profile': aws_profile,
        'accounts': account_list
    }
    
    # Save
    with open(config_file, 'w') as f:
        json.dump(profiles, f, indent=2)
    
    click.echo(f"✓ Profile '{profile}' created with {len(account_list)} accounts")
    click.echo(f"✓ Configuration saved to {config_file}")
    click.echo(f"\nUsage: cc calculate --profile {profile}")


@cli.command()
def list_profiles():
    """List all configured profiles"""
    
    config_file = Path.home() / '.config' / 'cost-calculator' / 'profiles.json'
    
    if not config_file.exists():
        click.echo("No profiles configured. Run: cc init --profile <name>")
        return
    
    with open(config_file) as f:
        profiles = json.load(f)
    
    if not profiles:
        click.echo("No profiles configured.")
        return
    
    click.echo("Configured profiles:")
    click.echo("")
    for name, config in profiles.items():
        click.echo(f"  {name}")
        if 'aws_profile' in config:
            click.echo(f"    AWS Profile: {config['aws_profile']} (SSO)")
        else:
            click.echo(f"    AWS Credentials: Configured (Static)")
        click.echo(f"    Accounts: {len(config['accounts'])}")
        click.echo("")


@cli.command()
def setup():
    """Show setup instructions for manual profile configuration"""
    import platform
    
    system = platform.system()
    
    if system == "Windows":
        config_path = "%USERPROFILE%\\.config\\cost-calculator\\profiles.json"
        config_path_example = "C:\\Users\\YourName\\.config\\cost-calculator\\profiles.json"
        mkdir_cmd = "mkdir %USERPROFILE%\\.config\\cost-calculator"
        edit_cmd = "notepad %USERPROFILE%\\.config\\cost-calculator\\profiles.json"
    else:  # macOS/Linux
        config_path = "~/.config/cost-calculator/profiles.json"
        config_path_example = "/Users/yourname/.config/cost-calculator/profiles.json"
        mkdir_cmd = "mkdir -p ~/.config/cost-calculator"
        edit_cmd = "nano ~/.config/cost-calculator/profiles.json"
    
    click.echo("=" * 70)
    click.echo("AWS Cost Calculator - Manual Profile Setup")
    click.echo("=" * 70)
    click.echo("")
    click.echo(f"Platform: {system}")
    click.echo(f"Config location: {config_path}")
    click.echo("")
    click.echo("Step 1: Create the config directory")
    click.echo(f"  {mkdir_cmd}")
    click.echo("")
    click.echo("Step 2: Create the profiles.json file")
    click.echo(f"  {edit_cmd}")
    click.echo("")
    click.echo("Step 3: Add your profile configuration (JSON format):")
    click.echo("")
    click.echo('  {')
    click.echo('    "myprofile": {')
    click.echo('      "aws_profile": "my_aws_profile",')
    click.echo('      "accounts": [')
    click.echo('        "123456789012",')
    click.echo('        "234567890123",')
    click.echo('        "345678901234"')
    click.echo('      ]')
    click.echo('    }')
    click.echo('  }')
    click.echo("")
    click.echo("Step 4: Save the file")
    click.echo("")
    click.echo("Step 5: Verify it works")
    click.echo("  cc list-profiles")
    click.echo("")
    click.echo("Step 6: Configure AWS credentials")
    click.echo("  Option A (SSO):")
    click.echo("    aws sso login --profile my_aws_profile")
    click.echo("    cc calculate --profile myprofile")
    click.echo("")
    click.echo("  Option B (Static credentials):")
    click.echo("    cc configure --profile myprofile")
    click.echo("    cc calculate --profile myprofile")
    click.echo("")
    click.echo("=" * 70)
    click.echo("")
    click.echo("For multiple profiles, add more entries to the JSON:")
    click.echo("")
    click.echo('  {')
    click.echo('    "profile1": { ... },')
    click.echo('    "profile2": { ... }')
    click.echo('  }')
    click.echo("")
    click.echo(f"Full path example: {config_path_example}")
    click.echo("=" * 70)


@cli.command()
@click.option('--profile', required=True, help='Profile name to configure')
@click.option('--access-key-id', prompt=True, hide_input=False, help='AWS Access Key ID')
@click.option('--secret-access-key', prompt=True, hide_input=True, help='AWS Secret Access Key')
@click.option('--session-token', default='', help='AWS Session Token (optional, for temporary credentials)')
@click.option('--region', default='us-east-1', help='AWS Region (default: us-east-1)')
def configure(profile, access_key_id, secret_access_key, session_token, region):
    """Configure AWS credentials for a profile (alternative to SSO)"""
    
    config_dir = Path.home() / '.config' / 'cost-calculator'
    config_file = config_dir / 'profiles.json'
    creds_file = config_dir / 'credentials.json'
    
    # Create config directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Load existing profiles
    if config_file.exists() and config_file.stat().st_size > 0:
        try:
            with open(config_file) as f:
                profiles = json.load(f)
        except json.JSONDecodeError:
            profiles = {}
    else:
        profiles = {}
    
    # Check if profile exists
    if profile not in profiles:
        click.echo(f"Error: Profile '{profile}' not found. Create it first with: cc init --profile {profile}")
        return
    
    # Remove aws_profile if it exists (switching from SSO to static creds)
    if 'aws_profile' in profiles[profile]:
        del profiles[profile]['aws_profile']
    
    # Save updated profile
    with open(config_file, 'w') as f:
        json.dump(profiles, f, indent=2)
    
    # Load or create credentials file
    if creds_file.exists() and creds_file.stat().st_size > 0:
        try:
            with open(creds_file) as f:
                creds = json.load(f)
        except json.JSONDecodeError:
            creds = {}
    else:
        creds = {}
    
    # Store credentials (encrypted would be better, but for now just file permissions)
    creds[profile] = {
        'aws_access_key_id': access_key_id,
        'aws_secret_access_key': secret_access_key,
        'region': region
    }
    
    if session_token:
        creds[profile]['aws_session_token'] = session_token
    
    # Save credentials with restricted permissions
    with open(creds_file, 'w') as f:
        json.dump(creds, f, indent=2)
    
    # Set file permissions to 600 (owner read/write only)
    creds_file.chmod(0o600)
    
    click.echo(f"✓ AWS credentials configured for profile '{profile}'")
    click.echo(f"✓ Credentials saved to {creds_file} (permissions: 600)")
    click.echo(f"\nUsage: cc calculate --profile {profile}")
    click.echo("\nNote: Credentials are stored locally. For temporary credentials,")
    click.echo("      you'll need to reconfigure when they expire.")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--weeks', default=3, help='Number of weeks to analyze (default: 3)')
@click.option('--output', default='cost_trends.md', help='Output markdown file (default: cost_trends.md)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--access-key-id', help='AWS Access Key ID')
@click.option('--secret-access-key', help='AWS Secret Access Key')
@click.option('--session-token', help='AWS Session Token')
def trends(profile, weeks, output, json_output, sso, access_key_id, secret_access_key, session_token):
    """Analyze cost trends with Week-over-Week and Trailing 30-Day comparisons"""
    
    # Load profile configuration
    config = load_profile(profile)
    config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
    
    click.echo(f"Analyzing last {weeks} weeks...")
    click.echo("")
    
    # Execute via API or locally
    trends_data = execute_trends(config, weeks)
    
    if json_output:
        # Output as JSON
        import json
        click.echo(json.dumps(trends_data, indent=2, default=str))
    else:
        # Generate markdown report
        markdown = format_trends_markdown(trends_data)
        
        # Save to file
        with open(output, 'w') as f:
            f.write(markdown)
        
        click.echo(f"✓ Trends report saved to {output}")
        click.echo("")
        
        # Show summary
        click.echo("WEEK-OVER-WEEK:")
        for comparison in trends_data['wow_comparisons']:
            prev_week = comparison['prev_week']['label']
            curr_week = comparison['curr_week']['label']
            num_increases = len(comparison['increases'])
            num_decreases = len(comparison['decreases'])
            
            click.echo(f"  {prev_week} → {curr_week}")
            click.echo(f"    Increases: {num_increases}, Decreases: {num_decreases}")
            
            if comparison['increases']:
                top = comparison['increases'][0]
                click.echo(f"    Top: {top['service']} (+${top['change']:,.2f})")
            
            click.echo("")
        
        click.echo("TRAILING 30-DAY (T-30):")
        for comparison in trends_data['t30_comparisons']:
            baseline_week = comparison['baseline_week']['label']
            curr_week = comparison['curr_week']['label']
            num_increases = len(comparison['increases'])
            num_decreases = len(comparison['decreases'])
            
            click.echo(f"  {curr_week} vs {baseline_week}")
            click.echo(f"    Increases: {num_increases}, Decreases: {num_decreases}")
            
            if comparison['increases']:
                top = comparison['increases'][0]
                click.echo(f"    Top: {top['service']} (+${top['change']:,.2f})")
            
            click.echo("")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--months', default=6, help='Number of months to analyze (default: 6)')
@click.option('--output', default='monthly_trends.md', help='Output markdown file (default: monthly_trends.md)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--access-key-id', help='AWS Access Key ID')
@click.option('--secret-access-key', help='AWS Secret Access Key')
@click.option('--session-token', help='AWS Session Token')
def monthly(profile, months, output, json_output, sso, access_key_id, secret_access_key, session_token):
    """Analyze month-over-month cost trends at service level"""
    
    # Load profile
    config = load_profile(profile)
    config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
    
    click.echo(f"Analyzing last {months} months...")
    click.echo("")
    
    # Execute via API or locally
    monthly_data = execute_monthly(config, months)
    
    if json_output:
        # Output as JSON
        output_data = {
            'generated': datetime.now().isoformat(),
            'months': months,
            'comparisons': []
        }
        
        for comparison in monthly_data['comparisons']:
            output_data['comparisons'].append({
                'prev_month': comparison['prev_month']['label'],
                'curr_month': comparison['curr_month']['label'],
                'increases': comparison['increases'],
                'decreases': comparison['decreases'],
                'total_increase': comparison['total_increase'],
                'total_decrease': comparison['total_decrease']
            })
        
        click.echo(json.dumps(output_data, indent=2))
    else:
        # Generate markdown report
        markdown = format_monthly_markdown(monthly_data)
        
        # Save to file
        with open(output, 'w') as f:
            f.write(markdown)
        
        click.echo(f"✓ Monthly trends report saved to {output}")
        click.echo("")
        
        # Show summary
        for comparison in monthly_data['comparisons']:
            prev_month = comparison['prev_month']['label']
            curr_month = comparison['curr_month']['label']
            num_increases = len(comparison['increases'])
            num_decreases = len(comparison['decreases'])
            
            click.echo(f"{prev_month} → {curr_month}")
            click.echo(f"  Increases: {num_increases}, Decreases: {num_decreases}")
            
            if comparison['increases']:
                top = comparison['increases'][0]
                click.echo(f"  Top: {top['service']} (+${top['change']:,.2f})")
            
            click.echo("")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--weeks', default=4, help='Number of weeks to analyze (default: 4)')
@click.option('--service', help='Filter by service name (e.g., "EC2 - Other")')
@click.option('--account', help='Filter by account ID')
@click.option('--usage-type', help='Filter by usage type')
@click.option('--resources', is_flag=True, help='Show individual resource IDs (requires CUR, uses Athena)')
@click.option('--output', default='drill_down.md', help='Output markdown file (default: drill_down.md)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--access-key-id', help='AWS Access Key ID')
@click.option('--secret-access-key', help='AWS Secret Access Key')
@click.option('--session-token', help='AWS Session Token')
def drill(profile, weeks, service, account, usage_type, resources, output, json_output, sso, access_key_id, secret_access_key, session_token):
    """
    Drill down into cost changes by service, account, or usage type
    
    Add --resources flag to see individual resource IDs and costs (requires CUR data via Athena)
    """
    
    # Load profile
    config = load_profile(profile)
    config = apply_auth_options(config, sso, access_key_id, secret_access_key, session_token)
    
    # Show filters
    click.echo(f"Analyzing last {weeks} weeks...")
    if service:
        click.echo(f"  Service filter: {service}")
    if account:
        click.echo(f"  Account filter: {account}")
    if usage_type:
        click.echo(f"  Usage type filter: {usage_type}")
    if resources:
        click.echo(f"  Mode: Resource-level (CUR via Athena)")
    click.echo("")
    
    # Execute via API or locally
    drill_data = execute_drill(config, weeks, service, account, usage_type, resources)
    
    # Handle resource-level output differently
    if resources:
        from cost_calculator.cur import format_resource_output
        output_text = format_resource_output(drill_data)
        click.echo(output_text)
        return
    
    if json_output:
        # Output as JSON
        output_data = {
            'generated': datetime.now().isoformat(),
            'weeks': weeks,
            'filters': drill_data['filters'],
            'group_by': drill_data['group_by'],
            'comparisons': []
        }
        
        for comparison in drill_data['comparisons']:
            output_data['comparisons'].append({
                'prev_week': comparison['prev_week']['label'],
                'curr_week': comparison['curr_week']['label'],
                'increases': comparison['increases'],
                'decreases': comparison['decreases'],
                'total_increase': comparison['total_increase'],
                'total_decrease': comparison['total_decrease']
            })
        
        click.echo(json.dumps(output_data, indent=2))
    else:
        # Generate markdown report
        markdown = format_drill_down_markdown(drill_data)
        
        # Save to file
        with open(output, 'w') as f:
            f.write(markdown)
        
        click.echo(f"✓ Drill-down report saved to {output}")
        click.echo("")
        
        # Show summary
        group_by_label = {
            'SERVICE': 'services',
            'LINKED_ACCOUNT': 'accounts',
            'USAGE_TYPE': 'usage types',
            'REGION': 'regions'
        }.get(drill_data['group_by'], 'items')
        
        click.echo(f"Showing top {group_by_label}:")
        for comparison in drill_data['comparisons']:
            prev_week = comparison['prev_week']['label']
            curr_week = comparison['curr_week']['label']
            num_increases = len(comparison['increases'])
            num_decreases = len(comparison['decreases'])
            
            click.echo(f"{prev_week} → {curr_week}")
            click.echo(f"  Increases: {num_increases}, Decreases: {num_decreases}")
            
            if comparison['increases']:
                top = comparison['increases'][0]
                click.echo(f"  Top: {top['dimension'][:50]} (+${top['change']:,.2f})")
            
            click.echo("")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--type', 'analysis_type', default='summary',
              type=click.Choice(['summary', 'volatility', 'trends', 'search']),
              help='Analysis type')
@click.option('--weeks', default=12, help='Number of weeks (default: 12)')
@click.option('--pattern', help='Service search pattern (for search type)')
@click.option('--min-cost', type=float, help='Minimum cost filter (for search type)')
@click.option('--json-output', is_flag=True, help='Output as JSON')
def analyze(profile, analysis_type, weeks, pattern, min_cost, json_output):
    """Perform pandas-based analysis (aggregations, volatility, trends, search)"""
    
    config = load_profile(profile)
    
    if not json_output:
        click.echo(f"Running {analysis_type} analysis for {weeks} weeks...")
    
    from cost_calculator.executor import execute_analyze
    result = execute_analyze(config, weeks, analysis_type, pattern, min_cost)
    
    if json_output:
        import json
        click.echo(json.dumps(result, indent=2, default=str))
    else:
        # Format output based on type
        if analysis_type == 'summary':
            click.echo(f"\n📊 Summary ({result.get('total_services', 0)} services)")
            click.echo(f"Weeks analyzed: {result.get('weeks_analyzed', 0)}")
            click.echo(f"\nTop 10 Services (by total change):")
            for svc in result.get('services', [])[:10]:
                click.echo(f"  {svc['service']}")
                click.echo(f"    Total: ${svc['change_sum']:,.2f}")
                click.echo(f"    Average: ${svc['change_mean']:,.2f}")
                click.echo(f"    Volatility: {svc['volatility']:.3f}")
        
        elif analysis_type == 'volatility':
            click.echo(f"\n📈 High Volatility Services:")
            for svc in result.get('high_volatility_services', [])[:10]:
                click.echo(f"  {svc['service']}: CV={svc['coefficient_of_variation']:.3f}")
            
            outliers = result.get('outliers', [])
            if outliers:
                click.echo(f"\n⚠️  Outliers ({len(outliers)}):")
                for o in outliers[:5]:
                    click.echo(f"  {o['service']} ({o['week']}): ${o['change']:,.2f} (z={o['z_score']:.2f})")
        
        elif analysis_type == 'trends':
            inc = result.get('increasing_trends', [])
            dec = result.get('decreasing_trends', [])
            
            click.echo(f"\n📈 Increasing Trends ({len(inc)}):")
            for t in inc[:5]:
                click.echo(f"  {t['service']}: ${t['avg_change']:,.2f}/week")
            
            click.echo(f"\n📉 Decreasing Trends ({len(dec)}):")
            for t in dec[:5]:
                click.echo(f"  {t['service']}: ${t['avg_change']:,.2f}/week")
        
        elif analysis_type == 'search':
            matches = result.get('matches', [])
            click.echo(f"\n🔍 Search Results ({len(matches)} matches)")
            if pattern:
                click.echo(f"Pattern: {pattern}")
            if min_cost:
                click.echo(f"Min cost: ${min_cost:,.2f}")
            
            for m in matches[:20]:
                click.echo(f"  {m['service']}: ${m['curr_cost']:,.2f}")


@cli.command()
@click.argument('operation', type=click.Choice(['list', 'get', 'create', 'update', 'delete']))
@click.option('--name', help='Profile name')
@click.option('--accounts', help='Comma-separated account IDs')
@click.option('--description', help='Profile description')
def profile(operation, name, accounts, description):
    """Manage profiles (CRUD operations)"""
    
    from cost_calculator.executor import execute_profile_operation
    
    # Parse accounts if provided
    account_list = None
    if accounts:
        account_list = [a.strip() for a in accounts.split(',')]
    
    result = execute_profile_operation(
        operation=operation,
        profile_name=name,
        accounts=account_list,
        description=description
    )
    
    if operation == 'list':
        profiles = result.get('profiles', [])
        click.echo(f"\n📋 Profiles ({len(profiles)}):")
        for p in profiles:
            click.echo(f"  {p['profile_name']}: {len(p.get('accounts', []))} accounts")
            if p.get('description'):
                click.echo(f"    {p['description']}")
    
    elif operation == 'get':
        profile_data = result.get('profile', {})
        click.echo(f"\n📋 Profile: {profile_data.get('profile_name')}")
        click.echo(f"Accounts: {len(profile_data.get('accounts', []))}")
        if profile_data.get('description'):
            click.echo(f"Description: {profile_data['description']}")
        click.echo(f"\nAccounts:")
        for acc in profile_data.get('accounts', []):
            click.echo(f"  {acc}")
    
    else:
        click.echo(result.get('message', 'Operation completed'))


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--sso', help='AWS SSO profile to use')
@click.option('--weeks', default=8, help='Number of weeks to analyze')
@click.option('--account', help='Focus on specific account ID')
@click.option('--service', help='Focus on specific service')
@click.option('--no-cloudtrail', is_flag=True, help='Skip CloudTrail analysis (faster)')
@click.option('--output', default='investigation_report.md', help='Output file path')
def investigate(profile, sso, weeks, account, service, no_cloudtrail, output):
    """
    Multi-stage cost investigation:
    1. Analyze cost trends and drill-downs
    2. Inventory actual resources in problem accounts
    3. Analyze CloudTrail events (optional)
    4. Generate comprehensive report
    """
    from cost_calculator.executor import execute_trends, execute_drill, get_credentials_dict
    from cost_calculator.api_client import call_lambda_api, is_api_configured
    from cost_calculator.forensics import format_investigation_report
    from datetime import datetime, timedelta
    
    click.echo("=" * 80)
    click.echo("COST INVESTIGATION")
    click.echo("=" * 80)
    click.echo(f"Profile: {profile}")
    click.echo(f"Weeks: {weeks}")
    if account:
        click.echo(f"Account: {account}")
    if service:
        click.echo(f"Service: {service}")
    click.echo("")
    
    # Load profile
    config = load_profile(profile)
    
    # Override with SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Step 1: Cost Analysis
    click.echo("Step 1/3: Analyzing cost trends...")
    try:
        trends_data = execute_trends(config, weeks)
        click.echo(f"✓ Found cost data for {weeks} weeks")
    except Exception as e:
        click.echo(f"✗ Error analyzing trends: {str(e)}")
        trends_data = None
    
    # Step 2: Drill-down
    click.echo("\nStep 2/3: Drilling down into costs...")
    drill_data = None
    if service or account:
        try:
            drill_data = execute_drill(config, weeks, service, account, None, False)
            click.echo(f"✓ Drill-down complete")
        except Exception as e:
            click.echo(f"✗ Error in drill-down: {str(e)}")
    
    # Step 3: Resource Inventory
    click.echo("\nStep 3/3: Inventorying resources...")
    inventories = []
    cloudtrail_analyses = []
    
    # Determine which accounts to investigate
    accounts_to_investigate = []
    if account:
        accounts_to_investigate = [account]
    else:
        # Extract top cost accounts from trends/drill data
        # For now, we'll need the user to specify
        click.echo("⚠️  No account specified. Use --account to inventory resources.")
    
    # For each account, do inventory and CloudTrail via backend API
    for acc_id in accounts_to_investigate:
        click.echo(f"\n  Investigating account {acc_id}...")
        
        # Get credentials (SSO or static)
        account_creds = get_credentials_dict(config)
        if not account_creds:
            click.echo(f"    ⚠️  No credentials available for account")
            continue
        
        # Inventory resources via backend API only
        if not is_api_configured():
            click.echo(f"    ✗ API not configured. Set COST_API_SECRET environment variable.")
            continue
        
        try:
            regions = ['us-west-2', 'us-east-1', 'eu-west-1']
            for region in regions:
                try:
                    inv = call_lambda_api(
                        'forensics',
                        account_creds,
                        [],  # accounts not needed for forensics
                        operation='inventory',
                        account_id=acc_id,
                        region=region
                    )
                    
                    if not inv.get('error'):
                        inventories.append(inv)
                        click.echo(f"    ✓ Inventory complete for {region}")
                        click.echo(f"      - EC2: {len(inv['ec2_instances'])} instances")
                        click.echo(f"      - EFS: {len(inv['efs_file_systems'])} file systems ({inv.get('total_efs_size_gb', 0):,.0f} GB)")
                        click.echo(f"      - ELB: {len(inv['load_balancers'])} load balancers")
                        break
                except Exception as e:
                    continue
        except Exception as e:
            click.echo(f"    ✗ Inventory error: {str(e)}")
        
        # CloudTrail analysis via backend API only
        if not no_cloudtrail:
            if not is_api_configured():
                click.echo(f"    ✗ CloudTrail skipped: API not configured")
            else:
                try:
                    start_date = (datetime.now() - timedelta(days=weeks * 7)).isoformat() + 'Z'
                    end_date = datetime.now().isoformat() + 'Z'
                    
                    ct_analysis = call_lambda_api(
                        'forensics',
                        account_creds,
                        [],
                        operation='cloudtrail',
                        account_id=acc_id,
                        start_date=start_date,
                        end_date=end_date,
                        region='us-west-2'
                    )
                    
                    cloudtrail_analyses.append(ct_analysis)
                    
                    if ct_analysis.get('error'):
                        click.echo(f"    ⚠️  CloudTrail: {ct_analysis['error']}")
                    else:
                        click.echo(f"    ✓ CloudTrail analysis complete")
                        click.echo(f"      - {len(ct_analysis['event_summary'])} event types")
                        click.echo(f"      - {len(ct_analysis['write_events'])} resource changes")
                except Exception as e:
                    click.echo(f"    ✗ CloudTrail error: {str(e)}")
    
    # Generate report
    click.echo(f"\nGenerating report...")
    report = format_investigation_report(trends_data, inventories, cloudtrail_analyses if not no_cloudtrail else None)
    
    # Write to file
    with open(output, 'w') as f:
        f.write(report)
    
    click.echo(f"\n✓ Investigation complete!")
    click.echo(f"✓ Report saved to: {output}")
    click.echo("")


def find_account_profile(account_id):
    """
    Find the SSO profile name for a given account ID
    Returns profile name or None
    """
    import subprocess
    
    try:
        # Get list of profiles
        result = subprocess.run(
            ['aws', 'configure', 'list-profiles'],
            capture_output=True,
            text=True
        )
        
        profiles = result.stdout.strip().split('\n')
        
        # Check each profile
        for profile in profiles:
            try:
                result = subprocess.run(
                    ['aws', 'sts', 'get-caller-identity', '--profile', profile],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if account_id in result.stdout:
                    return profile
            except:
                continue
        
        return None
    except:
        return None


if __name__ == '__main__':
    cli()

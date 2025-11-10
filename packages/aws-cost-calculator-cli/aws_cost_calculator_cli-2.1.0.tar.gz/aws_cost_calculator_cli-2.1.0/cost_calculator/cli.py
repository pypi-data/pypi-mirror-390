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

# API Configuration - can be overridden via environment variable
PROFILES_API_URL = os.environ.get(
    'COST_CALCULATOR_PROFILES_URL',
    'https://64g7jq7sjygec2zmll5lsghrpi0txrzo.lambda-url.us-east-1.on.aws/'
)
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


def get_api_secret():
    """Get API secret from config file or environment variable"""
    import os
    
    # Check environment variable first
    api_secret = os.environ.get('COST_API_SECRET')
    if api_secret:
        return api_secret
    
    # Check config file
    config_dir = Path.home() / '.config' / 'cost-calculator'
    config_file = config_dir / 'config.json'
    
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
            return config.get('api_secret')
    
    return None


def get_exclusions(profile_name=None):
    """Get exclusions configuration from DynamoDB API"""
    import requests
    
    api_secret = get_api_secret()
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET"
        )
    
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get_exclusions', 'profile_name': profile_name},
            timeout=10
        )
        
        if response.status_code == 200:
            return response.json().get('exclusions', {})
        else:
            # Return defaults if API fails
            return {
                'record_types': ['Tax', 'Support'],
                'services': [],
                'usage_types': [],
                'line_item_types': []
            }
    except:
        # Return defaults if request fails
        return {
            'record_types': ['Tax', 'Support'],
            'services': [],
            'usage_types': [],
            'line_item_types': []
        }


def build_exclusion_filter(exclusions):
    """Build AWS Cost Explorer filter from exclusions config"""
    filter_parts = []
    
    # Exclude record types (Tax, Support, etc.)
    if exclusions.get('record_types'):
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "RECORD_TYPE",
                    "Values": exclusions['record_types']
                }
            }
        })
    
    # Exclude specific services (OCBLateFee, etc.)
    if exclusions.get('services'):
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": exclusions['services']
                }
            }
        })
    
    # Exclude usage types
    if exclusions.get('usage_types'):
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "USAGE_TYPE",
                    "Values": exclusions['usage_types']
                }
            }
        })
    
    # Exclude line item types (Refund, Credit, etc.)
    if exclusions.get('line_item_types'):
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "LINE_ITEM_TYPE",
                    "Values": exclusions['line_item_types']
                }
            }
        })
    
    return filter_parts


def load_profile(profile_name):
    """Load profile configuration from DynamoDB API (API-only, no local files)"""
    import requests
    
    # Get API secret
    api_secret = get_api_secret()
    
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET\n"
            "Or set environment variable: export COST_API_SECRET=YOUR_SECRET"
        )
    
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get', 'profile_name': profile_name},
            timeout=10
        )
        
        if response.status_code == 200:
            response_data = response.json()
            # API returns {"profile": {...}} wrapper
            profile_data = response_data.get('profile', response_data)
            profile = {'accounts': profile_data['accounts']}
            
            # If profile has aws_profile field, use it
            if 'aws_profile' in profile_data:
                profile['aws_profile'] = profile_data['aws_profile']
            # Check for AWS_PROFILE environment variable (SSO support)
            elif os.environ.get('AWS_PROFILE'):
                profile['aws_profile'] = os.environ['AWS_PROFILE']
            # Use environment credentials
            elif os.environ.get('AWS_ACCESS_KEY_ID'):
                profile['credentials'] = {
                    'aws_access_key_id': os.environ['AWS_ACCESS_KEY_ID'],
                    'aws_secret_access_key': os.environ['AWS_SECRET_ACCESS_KEY'],
                    'aws_session_token': os.environ.get('AWS_SESSION_TOKEN')
                }
            else:
                # Try to find a matching AWS profile by name
                # This allows "khoros" profile to work with "khoros_umbrella" AWS profile
                import subprocess
                try:
                    result = subprocess.run(
                        ['aws', 'configure', 'list-profiles'],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        available_profiles = result.stdout.strip().split('\n')
                        # Try exact match first
                        if profile_name in available_profiles:
                            profile['aws_profile'] = profile_name
                        # Try with common suffixes
                        elif f"{profile_name}_umbrella" in available_profiles:
                            profile['aws_profile'] = f"{profile_name}_umbrella"
                        elif f"{profile_name}-umbrella" in available_profiles:
                            profile['aws_profile'] = f"{profile_name}-umbrella"
                        elif f"{profile_name}_prod" in available_profiles:
                            profile['aws_profile'] = f"{profile_name}_prod"
                        # If no match found, leave it unset - user must provide --sso
                except:
                    # If we can't list profiles, leave it unset - user must provide --sso
                    pass
            
            return profile
        else:
            raise click.ClickException(
                f"Profile '{profile_name}' not found in DynamoDB.\n"
                f"Run: cc profile create --name {profile_name} --accounts \"...\""
            )
    except requests.exceptions.RequestException as e:
        raise click.ClickException(
            f"Failed to fetch profile from API: {e}\n"
            "Check your API secret and network connection."
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
    
    # Build filter with dynamic exclusions
    exclusions = get_exclusions()  # Get from DynamoDB
    exclusion_filters = build_exclusion_filter(exclusions)
    
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
            }
        ]
    }
    
    # Add dynamic exclusion filters
    cost_filter["And"].extend(exclusion_filters)
    
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
@click.option('--api-secret', help='API secret for DynamoDB profile access')
@click.option('--show', is_flag=True, help='Show current configuration')
def configure(api_secret, show):
    """
    Configure Cost Calculator CLI settings.
    
    This tool requires an API secret to access profiles stored in DynamoDB.
    The secret can be configured here or set via COST_API_SECRET environment variable.
    
    Examples:
        # Configure API secret
        cc configure --api-secret YOUR_SECRET_KEY
        
        # Show current configuration
        cc configure --show
        
        # Use environment variable instead (no configuration needed)
        export COST_API_SECRET=YOUR_SECRET_KEY
    """
    import os
    
    config_dir = Path.home() / '.config' / 'cost-calculator'
    config_dir.mkdir(parents=True, exist_ok=True)
    config_file = config_dir / 'config.json'
    
    if show:
        # Show current configuration
        if config_file.exists():
            with open(config_file) as f:
                config = json.load(f)
                if 'api_secret' in config:
                    masked_secret = config['api_secret'][:8] + '...' + config['api_secret'][-4:]
                    click.echo(f"API Secret: {masked_secret} (configured)")
                else:
                    click.echo("API Secret: Not configured")
        else:
            click.echo("No configuration file found")
        
        # Check environment variable
        import os
        if os.environ.get('COST_API_SECRET'):
            click.echo("Environment: COST_API_SECRET is set")
        else:
            click.echo("Environment: COST_API_SECRET is not set")
        
        return
    
    if not api_secret:
        raise click.ClickException(
            "Please provide --api-secret or use --show to view current configuration\n"
            "Example: cc configure --api-secret YOUR_SECRET_KEY"
        )
    
    # Load existing config
    config = {}
    if config_file.exists():
        with open(config_file) as f:
            config = json.load(f)
    
    # Update API secret
    config['api_secret'] = api_secret
    
    # Save config
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=2)
    
    # Set restrictive permissions (Unix/Mac only - Windows uses different permission model)
    import platform
    if platform.system() != 'Windows':
        os.chmod(config_file, 0o600)
    
    masked_secret = api_secret[:8] + '...' + api_secret[-4:]
    click.echo(f"✓ API secret configured: {masked_secret}")
    click.echo(f"\nYou can now run: cc calculate --profile PROFILE_NAME")
    click.echo(f"\nNote: Profiles are stored in DynamoDB and accessed via the API.")

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
    
    # Validate that we have a way to get credentials
    if 'aws_profile' not in config and 'credentials' not in config:
        import subprocess
        try:
            result = subprocess.run(
                ['aws', 'configure', 'list-profiles'],
                capture_output=True,
                text=True,
                timeout=5
            )
            available = result.stdout.strip().split('\n') if result.returncode == 0 else []
            suggestion = f"\nAvailable AWS profiles: {', '.join(available[:5])}" if available else ""
        except:
            suggestion = ""
        
        raise click.ClickException(
            f"Profile '{profile}' has no AWS authentication configured.\n"
            f"Use --sso flag to specify your AWS SSO profile:\n"
            f"  cc investigate --profile {profile} --sso YOUR_AWS_PROFILE{suggestion}"
        )
    
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


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--days', type=int, default=10, help='Number of days to analyze (default: 10)')
@click.option('--service', help='Filter by service name')
@click.option('--account', help='Filter by account ID')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def daily(profile, start_date, end_date, days, service, account, sso, output_json):
    """
    Get daily cost breakdown with granular detail.
    
    Shows day-by-day costs for specific services and accounts, useful for:
    - Identifying cost spikes on specific dates
    - Validating daily cost patterns
    - Calculating precise daily averages
    
    Examples:
        # Last 10 days of CloudWatch costs for specific account
        cc daily --profile khoros --days 10 --service AmazonCloudWatch --account 820054669588
        
        # Custom date range with JSON output for automation
        cc daily --profile khoros --start-date 2025-10-28 --end-date 2025-11-06 --json
        
        # Find high-cost days using jq
        cc daily --profile khoros --days 30 --json | jq '.daily_costs | map(select(.cost > 1000))'
    """
    # Load profile
    config = load_profile(profile)
    
    # Apply SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Calculate date range
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end = datetime.now()
    
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start = end - timedelta(days=days)
    
    click.echo(f"Daily breakdown: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
    if service:
        click.echo(f"Service filter: {service}")
    if account:
        click.echo(f"Account filter: {account}")
    click.echo("")
    
    # Get credentials
    try:
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session = boto3.Session(
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                aws_session_token=creds.get('aws_session_token')
            )
        
        ce_client = session.client('ce', region_name='us-east-1')
        
        # Build filter
        filter_parts = []
        
        # Account filter
        if account:
            filter_parts.append({
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": [account]
                }
            })
        else:
            filter_parts.append({
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": config['accounts']
                }
            })
        
        # Service filter
        if service:
            filter_parts.append({
                "Dimensions": {
                    "Key": "SERVICE",
                    "Values": [service]
                }
            })
        
        # Exclude support and tax
        filter_parts.append({
            "Not": {
                "Dimensions": {
                    "Key": "RECORD_TYPE",
                    "Values": ["Tax", "Support"]
                }
            }
        })
        
        cost_filter = {"And": filter_parts} if len(filter_parts) > 1 else filter_parts[0]
        
        # Get daily costs
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start.strftime('%Y-%m-%d'),
                'End': (end + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter=cost_filter
        )
        
        # Collect results
        daily_costs = []
        total = 0
        for day in response['ResultsByTime']:
            date = day['TimePeriod']['Start']
            cost = float(day['Total']['UnblendedCost']['Amount'])
            total += cost
            daily_costs.append({'date': date, 'cost': cost})
        
        num_days = len(response['ResultsByTime'])
        daily_avg = total / num_days if num_days > 0 else 0
        annual = daily_avg * 365
        
        # Output results
        if output_json:
            import json
            result = {
                'period': {
                    'start': start.strftime('%Y-%m-%d'),
                    'end': end.strftime('%Y-%m-%d'),
                    'days': num_days
                },
                'filters': {
                    'service': service,
                    'account': account
                },
                'daily_costs': daily_costs,
                'summary': {
                    'total': total,
                    'daily_avg': daily_avg,
                    'annual_projection': annual
                }
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("Date       | Cost")
            click.echo("-----------|-----------")
            for item in daily_costs:
                click.echo(f"{item['date']} | ${item['cost']:,.2f}")
            click.echo("-----------|-----------")
            click.echo(f"Total      | ${total:,.2f}")
            click.echo(f"Daily Avg  | ${daily_avg:,.2f}")
            click.echo(f"Annual     | ${annual:,.0f}")
        
    except Exception as e:
        raise click.ClickException(f"Failed to get daily costs: {e}")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--account', help='Account ID to compare')
@click.option('--service', help='Service to compare')
@click.option('--before', required=True, help='Before period (YYYY-MM-DD:YYYY-MM-DD)')
@click.option('--after', required=True, help='After period (YYYY-MM-DD:YYYY-MM-DD)')
@click.option('--expected-reduction', type=float, help='Expected reduction percentage')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def compare(profile, account, service, before, after, expected_reduction, sso, output_json):
    """
    Compare costs between two periods for validation and analysis.
    
    Perfect for:
    - Validating cost optimization savings
    - Before/after migration analysis
    - Measuring impact of infrastructure changes
    - Automated savings validation in CI/CD
    
    Examples:
        # Validate Datadog migration savings (expect 50% reduction)
        cc compare --profile khoros --account 180770971501 --service AmazonCloudWatch \
          --before "2025-10-28:2025-11-06" --after "2025-11-17:2025-11-26" --expected-reduction 50
        
        # Compare total costs across all accounts
        cc compare --profile khoros --before "2025-10-01:2025-10-31" --after "2025-11-01:2025-11-30"
        
        # JSON output for automated validation
        cc compare --profile khoros --service EC2 --before "2025-10-01:2025-10-07" \
          --after "2025-11-08:2025-11-14" --json | jq '.comparison.met_expectation'
    """
    # Load profile
    config = load_profile(profile)
    
    # Apply SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Parse periods
    try:
        before_start, before_end = before.split(':')
        after_start, after_end = after.split(':')
    except ValueError:
        raise click.ClickException("Period format must be 'YYYY-MM-DD:YYYY-MM-DD'")
    
    if not output_json:
        click.echo(f"Comparing periods:")
        click.echo(f"  Before: {before_start} to {before_end}")
        click.echo(f"  After:  {after_start} to {after_end}")
        if service:
            click.echo(f"  Service: {service}")
        if account:
            click.echo(f"  Account: {account}")
        click.echo("")
    
    # Get credentials
    try:
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session = boto3.Session(
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                aws_session_token=creds.get('aws_session_token')
            )
        
        ce_client = session.client('ce', region_name='us-east-1')
        
        # Build filter
        def build_filter():
            filter_parts = []
            
            if account:
                filter_parts.append({
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": [account]
                    }
                })
            else:
                filter_parts.append({
                    "Dimensions": {
                        "Key": "LINKED_ACCOUNT",
                        "Values": config['accounts']
                    }
                })
            
            if service:
                filter_parts.append({
                    "Dimensions": {
                        "Key": "SERVICE",
                        "Values": [service]
                    }
                })
            
            filter_parts.append({
                "Not": {
                    "Dimensions": {
                        "Key": "RECORD_TYPE",
                        "Values": ["Tax", "Support"]
                    }
                }
            })
            
            return {"And": filter_parts} if len(filter_parts) > 1 else filter_parts[0]
        
        cost_filter = build_filter()
        
        # Get before period costs
        before_response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': before_start,
                'End': (datetime.strptime(before_end, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter=cost_filter
        )
        
        # Get after period costs
        after_response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': after_start,
                'End': (datetime.strptime(after_end, '%Y-%m-%d') + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            Granularity='DAILY',
            Metrics=['UnblendedCost'],
            Filter=cost_filter
        )
        
        # Calculate totals
        before_total = sum(float(day['Total']['UnblendedCost']['Amount']) for day in before_response['ResultsByTime'])
        after_total = sum(float(day['Total']['UnblendedCost']['Amount']) for day in after_response['ResultsByTime'])
        
        before_days = len(before_response['ResultsByTime'])
        after_days = len(after_response['ResultsByTime'])
        
        before_daily = before_total / before_days if before_days > 0 else 0
        after_daily = after_total / after_days if after_days > 0 else 0
        
        reduction = before_daily - after_daily
        reduction_pct = (reduction / before_daily * 100) if before_daily > 0 else 0
        annual_savings = reduction * 365
        
        # Output results
        if output_json:
            import json
            result = {
                'before': {
                    'period': {'start': before_start, 'end': before_end},
                    'total': before_total,
                    'daily_avg': before_daily,
                    'days': before_days
                },
                'after': {
                    'period': {'start': after_start, 'end': after_end},
                    'total': after_total,
                    'daily_avg': after_daily,
                    'days': after_days
                },
                'comparison': {
                    'daily_reduction': reduction,
                    'reduction_pct': reduction_pct,
                    'annual_savings': annual_savings
                }
            }
            
            if expected_reduction is not None:
                result['comparison']['expected_reduction_pct'] = expected_reduction
                result['comparison']['met_expectation'] = reduction_pct >= expected_reduction
            
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo("Before Period:")
            click.echo(f"  Total: ${before_total:,.2f}")
            click.echo(f"  Daily Avg: ${before_daily:,.2f}")
            click.echo(f"  Days: {before_days}")
            click.echo("")
            click.echo("After Period:")
            click.echo(f"  Total: ${after_total:,.2f}")
            click.echo(f"  Daily Avg: ${after_daily:,.2f}")
            click.echo(f"  Days: {after_days}")
            click.echo("")
            click.echo("Comparison:")
            click.echo(f"  Daily Reduction: ${reduction:,.2f}")
            click.echo(f"  Reduction %: {reduction_pct:.1f}%")
            click.echo(f"  Annual Savings: ${annual_savings:,.0f}")
            
            if expected_reduction is not None:
                click.echo("")
                if reduction_pct >= expected_reduction:
                    click.echo(f"✅ Savings achieved: {reduction_pct:.1f}% (expected {expected_reduction}%)")
                else:
                    click.echo(f"⚠️  Below target: {reduction_pct:.1f}% (expected {expected_reduction}%)")
        
    except Exception as e:
        raise click.ClickException(f"Comparison failed: {e}")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--tag-key', required=True, help='Tag key to filter by')
@click.option('--tag-value', help='Tag value to filter by (optional)')
@click.option('--start-date', help='Start date (YYYY-MM-DD)')
@click.option('--end-date', help='End date (YYYY-MM-DD)')
@click.option('--days', type=int, default=30, help='Number of days to analyze (default: 30)')
@click.option('--sso', help='AWS SSO profile name')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def tags(profile, tag_key, tag_value, start_date, end_date, days, sso, output_json):
    """
    Analyze costs grouped by resource tags for cost attribution.
    
    Useful for:
    - Cost allocation by team, project, or environment
    - Identifying untagged resources (cost attribution gaps)
    - Tracking costs by cost center or department
    - Validating tagging compliance
    
    Examples:
        # See all costs by Environment tag
        cc tags --profile khoros --tag-key "Environment" --days 30
        
        # Filter to specific tag value
        cc tags --profile khoros --tag-key "Team" --tag-value "Platform" --days 30
        
        # Find top cost centers with JSON output
        cc tags --profile khoros --tag-key "CostCenter" --days 30 --json | \
          jq '.tag_costs | sort_by(-.cost) | .[:5]'
        
        # Identify untagged resources (look for empty tag values)
        cc tags --profile khoros --tag-key "Owner" --days 7
    """
    # Load profile
    config = load_profile(profile)
    
    # Apply SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Calculate date range
    if end_date:
        end = datetime.strptime(end_date, '%Y-%m-%d')
    else:
        end = datetime.now()
    
    if start_date:
        start = datetime.strptime(start_date, '%Y-%m-%d')
    else:
        start = end - timedelta(days=days)
    
    if not output_json:
        click.echo(f"Tag-based cost analysis: {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        click.echo(f"Tag key: {tag_key}")
        if tag_value:
            click.echo(f"Tag value: {tag_value}")
        click.echo("")
    
    # Get credentials
    try:
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session = boto3.Session(
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                aws_session_token=creds.get('aws_session_token')
            )
        
        ce_client = session.client('ce', region_name='us-east-1')
        
        # Build filter
        filter_parts = [
            {
                "Dimensions": {
                    "Key": "LINKED_ACCOUNT",
                    "Values": config['accounts']
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
        
        # Add tag filter if value specified
        if tag_value:
            filter_parts.append({
                "Tags": {
                    "Key": tag_key,
                    "Values": [tag_value]
                }
            })
        
        cost_filter = {"And": filter_parts}
        
        # Get costs grouped by tag values
        response = ce_client.get_cost_and_usage(
            TimePeriod={
                'Start': start.strftime('%Y-%m-%d'),
                'End': (end + timedelta(days=1)).strftime('%Y-%m-%d')
            },
            Granularity='MONTHLY',
            Metrics=['UnblendedCost'],
            GroupBy=[{
                'Type': 'TAG',
                'Key': tag_key
            }],
            Filter=cost_filter
        )
        
        # Collect results
        tag_costs = {}
        for period in response['ResultsByTime']:
            for group in period['Groups']:
                tag_val = group['Keys'][0].split('$')[1] if '$' in group['Keys'][0] else group['Keys'][0]
                cost = float(group['Metrics']['UnblendedCost']['Amount'])
                tag_costs[tag_val] = tag_costs.get(tag_val, 0) + cost
        
        # Sort by cost
        sorted_tags = sorted(tag_costs.items(), key=lambda x: x[1], reverse=True)
        
        total = sum(tag_costs.values())
        num_days = (end - start).days
        daily_avg = total / num_days if num_days > 0 else 0
        
        # Output results
        if output_json:
            import json
            result = {
                'period': {
                    'start': start.strftime('%Y-%m-%d'),
                    'end': end.strftime('%Y-%m-%d'),
                    'days': num_days
                },
                'tag_key': tag_key,
                'tag_value_filter': tag_value,
                'tag_costs': [{'tag_value': k, 'cost': v, 'percentage': (v/total*100) if total > 0 else 0} for k, v in sorted_tags],
                'summary': {
                    'total': total,
                    'daily_avg': daily_avg,
                    'annual_projection': daily_avg * 365
                }
            }
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Tag Value{' '*(30-len('Tag Value'))} | Cost       | %")
            click.echo("-" * 60)
            for tag_val, cost in sorted_tags:
                pct = (cost / total * 100) if total > 0 else 0
                tag_display = tag_val[:30].ljust(30)
                click.echo(f"{tag_display} | ${cost:>9,.2f} | {pct:>5.1f}%")
            click.echo("-" * 60)
            click.echo(f"{'Total'.ljust(30)} | ${total:>9,.2f} | 100.0%")
            click.echo("")
            click.echo(f"Daily Avg: ${daily_avg:,.2f}")
            click.echo(f"Annual Projection: ${daily_avg * 365:,.0f}")
        
    except Exception as e:
        raise click.ClickException(f"Tag analysis failed: {e}")


@cli.command()
@click.option('--profile', required=True, help='Profile name')
@click.option('--query', required=True, help='SQL query to execute')
@click.option('--database', default='athenacurcfn_cloud_intelligence_dashboard', help='Athena database name')
@click.option('--output-bucket', help='S3 bucket for query results (default: from profile)')
@click.option('--sso', help='AWS SSO profile name')
def query(profile, query, database, output_bucket, sso):
    """
    Execute custom Athena SQL query on CUR data
    
    Example:
        cc query --profile khoros --query "SELECT line_item_usage_account_id, SUM(line_item_unblended_cost) as cost FROM cloud_intelligence_dashboard WHERE line_item_usage_start_date >= DATE '2025-11-01' GROUP BY 1 ORDER BY 2 DESC LIMIT 10"
    """
    # Load profile
    config = load_profile(profile)
    
    # Apply SSO if provided
    if sso:
        config['aws_profile'] = sso
    
    # Get credentials
    try:
        if 'aws_profile' in config:
            session = boto3.Session(profile_name=config['aws_profile'])
        else:
            creds = config['credentials']
            session = boto3.Session(
                aws_access_key_id=creds['aws_access_key_id'],
                aws_secret_access_key=creds['aws_secret_access_key'],
                aws_session_token=creds.get('aws_session_token')
            )
        
        athena_client = session.client('athena', region_name='us-east-1')
        
        # Default output location
        if not output_bucket:
            output_bucket = 's3://khoros-finops-athena/athena/'
        
        click.echo(f"Executing query on database: {database}")
        click.echo(f"Output location: {output_bucket}")
        click.echo("")
        
        # Execute query
        response = athena_client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={'Database': database},
            ResultConfiguration={'OutputLocation': output_bucket}
        )
        
        query_id = response['QueryExecutionId']
        click.echo(f"Query ID: {query_id}")
        click.echo("Waiting for query to complete...")
        
        # Wait for completion
        import time
        max_wait = 60
        waited = 0
        while waited < max_wait:
            status_response = athena_client.get_query_execution(QueryExecutionId=query_id)
            status = status_response['QueryExecution']['Status']['State']
            
            if status == 'SUCCEEDED':
                click.echo("✓ Query completed successfully")
                break
            elif status in ['FAILED', 'CANCELLED']:
                reason = status_response['QueryExecution']['Status'].get('StateChangeReason', 'Unknown')
                raise click.ClickException(f"Query {status}: {reason}")
            
            time.sleep(2)
            waited += 2
        
        if waited >= max_wait:
            raise click.ClickException(f"Query timeout after {max_wait}s. Check query ID: {query_id}")
        
        # Get results
        results = athena_client.get_query_results(QueryExecutionId=query_id)
        
        # Display results
        rows = results['ResultSet']['Rows']
        if not rows:
            click.echo("No results returned")
            return
        
        # Header
        headers = [col['VarCharValue'] for col in rows[0]['Data']]
        click.echo(" | ".join(headers))
        click.echo("-" * (len(" | ".join(headers))))
        
        # Data rows
        for row in rows[1:]:
            values = [col.get('VarCharValue', '') for col in row['Data']]
            click.echo(" | ".join(values))
        
        click.echo("")
        click.echo(f"Returned {len(rows)-1} rows")
        
    except Exception as e:
        raise click.ClickException(f"Query failed: {e}")


@cli.group()
def exclusions():
    """
    Manage cost exclusions (services/types to exclude from calculations).
    
    Exclusions are stored in DynamoDB and apply globally or per-profile.
    Common exclusions: Tax, Support, OCBLateFee, Refunds, Credits
    """
    pass


@exclusions.command('show')
@click.option('--profile', help='Show profile-specific exclusions (default: global)')
@click.option('--json', 'output_json', is_flag=True, help='Output as JSON')
def show_exclusions(profile, output_json):
    """Show current exclusions configuration"""
    import requests
    
    api_secret = get_api_secret()
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET"
        )
    
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get_exclusions', 'profile_name': profile},
            timeout=10
        )
        
        if response.status_code == 200:
            exclusions_data = response.json().get('exclusions', {})
            
            if output_json:
                click.echo(json.dumps(exclusions_data, indent=2))
            else:
                scope = profile if profile else "global"
                click.echo(f"Exclusions ({scope}):")
                click.echo("")
                
                if exclusions_data.get('record_types'):
                    click.echo("Record Types:")
                    for rt in exclusions_data['record_types']:
                        click.echo(f"  - {rt}")
                    click.echo("")
                
                if exclusions_data.get('services'):
                    click.echo("Services:")
                    for svc in exclusions_data['services']:
                        click.echo(f"  - {svc}")
                    click.echo("")
                
                if exclusions_data.get('line_item_types'):
                    click.echo("Line Item Types:")
                    for lit in exclusions_data['line_item_types']:
                        click.echo(f"  - {lit}")
                    click.echo("")
                
                if exclusions_data.get('usage_types'):
                    click.echo("Usage Types:")
                    for ut in exclusions_data['usage_types']:
                        click.echo(f"  - {ut}")
        else:
            raise click.ClickException(f"Failed to fetch exclusions: {response.status_code}")
    
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"API request failed: {e}")


@exclusions.command('add')
@click.option('--record-type', help='Add record type exclusion (e.g., Tax, Support)')
@click.option('--service', help='Add service exclusion (e.g., OCBLateFee)')
@click.option('--line-item-type', help='Add line item type exclusion (e.g., Refund, Credit)')
@click.option('--usage-type', help='Add usage type exclusion')
@click.option('--profile', help='Add to profile-specific exclusions (default: global)')
def add_exclusion(record_type, service, line_item_type, usage_type, profile):
    """Add an exclusion"""
    import requests
    
    if not any([record_type, service, line_item_type, usage_type]):
        raise click.ClickException(
            "Must specify at least one of: --record-type, --service, --line-item-type, --usage-type"
        )
    
    api_secret = get_api_secret()
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET"
        )
    
    # Get current exclusions
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get_exclusions', 'profile_name': profile},
            timeout=10
        )
        
        if response.status_code == 200:
            exclusions_data = response.json().get('exclusions', {})
        else:
            exclusions_data = {
                'record_types': [],
                'services': [],
                'line_item_types': [],
                'usage_types': []
            }
        
        # Add new exclusions
        if record_type and record_type not in exclusions_data.get('record_types', []):
            exclusions_data.setdefault('record_types', []).append(record_type)
        
        if service and service not in exclusions_data.get('services', []):
            exclusions_data.setdefault('services', []).append(service)
        
        if line_item_type and line_item_type not in exclusions_data.get('line_item_types', []):
            exclusions_data.setdefault('line_item_types', []).append(line_item_type)
        
        if usage_type and usage_type not in exclusions_data.get('usage_types', []):
            exclusions_data.setdefault('usage_types', []).append(usage_type)
        
        # Update exclusions
        update_response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={
                'operation': 'update_exclusions',
                'profile_name': profile,
                'record_types': exclusions_data.get('record_types', []),
                'services': exclusions_data.get('services', []),
                'line_item_types': exclusions_data.get('line_item_types', []),
                'usage_types': exclusions_data.get('usage_types', [])
            },
            timeout=10
        )
        
        if update_response.status_code == 200:
            scope = profile if profile else "global"
            click.echo(f"✓ Exclusion added to {scope} config")
            if record_type:
                click.echo(f"  Record Type: {record_type}")
            if service:
                click.echo(f"  Service: {service}")
            if line_item_type:
                click.echo(f"  Line Item Type: {line_item_type}")
            if usage_type:
                click.echo(f"  Usage Type: {usage_type}")
        else:
            raise click.ClickException(f"Failed to update exclusions: {update_response.status_code}")
    
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"API request failed: {e}")


@exclusions.command('remove')
@click.option('--record-type', help='Remove record type exclusion')
@click.option('--service', help='Remove service exclusion')
@click.option('--line-item-type', help='Remove line item type exclusion')
@click.option('--usage-type', help='Remove usage type exclusion')
@click.option('--profile', help='Remove from profile-specific exclusions (default: global)')
def remove_exclusion(record_type, service, line_item_type, usage_type, profile):
    """Remove an exclusion"""
    import requests
    
    if not any([record_type, service, line_item_type, usage_type]):
        raise click.ClickException(
            "Must specify at least one of: --record-type, --service, --line-item-type, --usage-type"
        )
    
    api_secret = get_api_secret()
    if not api_secret:
        raise click.ClickException(
            "No API secret configured.\n"
            "Run: cc configure --api-secret YOUR_SECRET"
        )
    
    # Get current exclusions
    try:
        response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={'operation': 'get_exclusions', 'profile_name': profile},
            timeout=10
        )
        
        if response.status_code == 200:
            exclusions_data = response.json().get('exclusions', {})
        else:
            raise click.ClickException("No exclusions found")
        
        # Remove exclusions
        if record_type and record_type in exclusions_data.get('record_types', []):
            exclusions_data['record_types'].remove(record_type)
        
        if service and service in exclusions_data.get('services', []):
            exclusions_data['services'].remove(service)
        
        if line_item_type and line_item_type in exclusions_data.get('line_item_types', []):
            exclusions_data['line_item_types'].remove(line_item_type)
        
        if usage_type and usage_type in exclusions_data.get('usage_types', []):
            exclusions_data['usage_types'].remove(usage_type)
        
        # Update exclusions
        update_response = requests.post(
            PROFILES_API_URL,
            headers={'X-API-Secret': api_secret, 'Content-Type': 'application/json'},
            json={
                'operation': 'update_exclusions',
                'profile_name': profile,
                'record_types': exclusions_data.get('record_types', []),
                'services': exclusions_data.get('services', []),
                'line_item_types': exclusions_data.get('line_item_types', []),
                'usage_types': exclusions_data.get('usage_types', [])
            },
            timeout=10
        )
        
        if update_response.status_code == 200:
            scope = profile if profile else "global"
            click.echo(f"✓ Exclusion removed from {scope} config")
        else:
            raise click.ClickException(f"Failed to update exclusions: {update_response.status_code}")
    
    except requests.exceptions.RequestException as e:
        raise click.ClickException(f"API request failed: {e}")


if __name__ == '__main__':
    cli()

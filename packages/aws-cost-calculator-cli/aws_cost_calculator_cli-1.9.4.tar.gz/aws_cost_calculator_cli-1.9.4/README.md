# AWS Cost Calculator (cc)

A CLI tool to quickly calculate AWS costs across multiple accounts.

## Installation

```bash
pip install aws-cost-calculator-cli
```

Or upgrade to the latest version:
```bash
pip install --upgrade aws-cost-calculator-cli
```

## Quick Start

### Authentication Methods

The CLI supports three authentication methods:

#### 1. SSO (Recommended)
```bash
# The CLI will automatically trigger SSO login if needed
cc calculate --profile myprofile --sso my_sso_profile
```

#### 2. Static Credentials
```bash
cc calculate --profile myprofile \
  --access-key-id ASIA... \
  --secret-access-key ... \
  --session-token ...
```

#### 3. Environment Variables
```bash
# For SSO
export AWS_PROFILE=my_sso_profile
cc calculate --profile myprofile

# For static credentials
export AWS_ACCESS_KEY_ID=ASIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
cc calculate --profile myprofile
```

### Basic Usage

```bash
# Default: Today minus 2 days, going back 30 days
cc calculate --profile myprofile --sso my_sso_profile

# Specific start date
cc calculate --profile myprofile --sso my_sso_profile --start-date 2025-11-04

# Custom offset and window
cc calculate --profile myprofile --sso my_sso_profile --offset 2 --window 30

# JSON output
cc calculate --profile myprofile --sso my_sso_profile --json-output
```

### 4. Analyze cost trends

All commands support the same authentication options:

```bash
# With SSO
cc trends --profile myprofile --sso my_sso_profile

# With static credentials
cc trends --profile myprofile --access-key-id ASIA... --secret-access-key ... --session-token ...

# With environment variables
export AWS_PROFILE=my_sso_profile
cc trends --profile myprofile

# Analyze more weeks
cc trends --profile myprofile --sso my_sso_profile --weeks 5

# Custom output file
cc trends --profile myprofile --sso my_sso_profile --output weekly_trends.md

# JSON output
cc trends --profile myprofile --sso my_sso_profile --json-output
```

### 5. Monthly and drill-down analysis

```bash
# Monthly trends
cc monthly --profile myprofile --sso my_sso_profile

# Drill down by service
cc drill --profile myprofile --sso my_sso_profile --service "EC2 - Other"

# Drill down by account
cc drill --profile myprofile --sso my_sso_profile --account 123456789012
```

### 6. List profiles

```bash
cc list-profiles
```

## Authentication

### Overview

The CLI supports three authentication methods, all of which work with every command (`calculate`, `trends`, `monthly`, `drill`):

### Method 1: SSO (Recommended)

The CLI automatically handles SSO login if your session has expired:

```bash
cc calculate --profile myprofile --sso my_sso_profile
```

**How it works:**
1. CLI checks if SSO session is valid using `aws sts get-caller-identity`
2. If expired, automatically runs `aws sso login --profile my_sso_profile`
3. Opens browser for authentication
4. Proceeds with cost calculation once authenticated

**Benefits:**
- No manual SSO login required
- Automatic session refresh
- Most secure method
- Works with AWS IAM Identity Center

### Method 2: Static Credentials

Pass temporary credentials directly via CLI flags:

```bash
cc calculate --profile myprofile \
  --access-key-id ASIA... \
  --secret-access-key ... \
  --session-token ...
```

**Use cases:**
- CI/CD pipelines
- Temporary credentials from STS
- Automated scripts
- When SSO is not available

### Method 3: Environment Variables

Set credentials in your shell environment:

```bash
# For SSO
export AWS_PROFILE=my_sso_profile
cc calculate --profile myprofile

# For static credentials
export AWS_ACCESS_KEY_ID=ASIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_SESSION_TOKEN=...
cc calculate --profile myprofile
```

**Benefits:**
- No need to pass credentials with each command
- Works with existing AWS CLI configuration
- Can be set in shell profile (~/.zshrc, ~/.bashrc)

### Profile Configuration

Profiles can be stored locally or fetched from a backend API:

**Local storage:** `~/.config/cost-calculator/profiles.json`
```json
{
  "myprofile": {
    "accounts": ["123456789012", "234567890123", ...]
  }
}
```

**Backend API:** Set `COST_API_SECRET` environment variable

Quick setup (saves to shell profile):
```bash
cc setup-api
# Enter your API secret when prompted (input will be hidden)
```

**CUR Configuration (for --resources flag):**

To use resource-level queries, configure CUR settings:
```bash
cc setup-cur
# Enter: Database name, table name, S3 output location
```

This saves configuration to `~/.config/cost-calculator/cur_config.json`

Or set manually:
```bash
export COST_API_SECRET="your-api-secret"
cc calculate --profile myprofile --sso my_sso_profile
```

The CLI will automatically fetch profile configuration from the backend if `COST_API_SECRET` is set.

## How It Works

### Date Calculation
- **Start Date**: Defaults to today, or specify with `--start-date`
- **Offset**: Days to go back from start date (default: 2)
- **Window**: Number of days to analyze (default: 30)

Example: If today is Nov 4, 2025:
- With offset=2, window=30: Analyzes Oct 3 - Nov 2 (30 days)

### Cost Calculation
1. **Operational Costs**: Sum of daily costs ÷ window days
2. **Support Allocation**: 
   - Gets support cost from the analysis month
   - Divides by 2 (50% allocation)
   - Divides by days in that month
3. **Daily Rate**: Operational + Support per day
4. **Annual Projection**: Daily rate × 365

### Filters Applied
- **Billing Entity**: AWS only (excludes marketplace)
- **Excluded**: Tax, Support (calculated separately)
- **Metric**: Net Amortized Cost

## Configuration

Profiles are stored in: `~/.config/cost-calculator/profiles.json`

Example:
```json
{
  "myprofile": {
    "aws_profile": "my_aws_profile",
    "accounts": ["123456789012", "234567890123", "345678901234"]
  }
}
```

## Examples

```bash
# Quick daily check
cc calculate --profile myprofile

# Historical analysis
cc calculate --profile myprofile --start-date 2025-10-01

# Export to JSON for processing
cc calculate --profile myprofile --json-output > costs.json

# Different window size
cc calculate --profile myprofile --window 60

# Weekly cost trends analysis
cc trends --profile myprofile

# Analyze last 8 weeks
cc trends --profile myprofile --weeks 8

# Monthly cost trends analysis
cc monthly --profile myprofile

# Analyze last 12 months
cc monthly --profile myprofile --months 12

# Drill down into specific service
cc drill --profile myprofile --service "EC2 - Other"

# Drill down into specific account
cc drill --profile myprofile --account 123456789012

# Drill down into service within account
cc drill --profile myprofile --service "EC2 - Other" --account 123456789012
```

## Trends Report

The `trends` command generates a markdown report with **two types of analysis**:

### 1. Week-over-Week (WoW)
Compares each week to the previous week - good for catching immediate spikes and changes.

### 2. Trailing 30-Day (T-30)
Compares each week to the same week 4 weeks ago - filters out noise and shows sustained trends.

**Features:**
- **Service-level aggregation**: Shows total cost per service (not individual usage types)
- **Top 10 Increases/Decreases**: For each comparison period
- **Total rows**: Sum of top 10 changes for quick assessment
- **Filters**: Only shows changes >$10 and >5%

Example output:
```
Week of Oct 19 → Week of Oct 26 (WoW)
  Increases: 4, Decreases: 10
  Top: EC2 - Other (+$949.12)

Week of Oct 26 vs Week of Sep 28 (T-30)
  Increases: 10, Decreases: 10
  Top: EC2 - Other (+$886.39)
```

The report is saved to `cost_trends.md` by default and includes:
- Service name
- Previous/baseline cost
- Current cost
- Change amount and percentage
- Total of top 10 changes

## Monthly Report

The `monthly` command generates month-over-month cost comparisons:

**Features:**
- **Service-level aggregation**: Shows total cost per service
- **Calendar month comparisons**: October vs September, September vs August, etc.
- **Top 10 Increases/Decreases**: For each month comparison
- **Total rows**: Sum of top 10 changes
- **Filters**: Only shows changes >$50 and >5%

Example output:
```
October 2025 → November 2025
  Increases: 1, Decreases: 10
  Top: Savings Plans for AWS Compute usage (+$231,161.46)
```

The report is saved to `monthly_trends.md` by default.

## Drill-Down Analysis

The `drill` command allows you to investigate cost changes at different levels of detail:

**Funnel Approach:**
1. **Start broad:** `cc trends` → See EC2 costs up $1000
2. **Drill by service:** `cc drill --service "EC2 - Other"` → See which accounts
3. **Drill deeper:** `cc drill --service "EC2 - Other" --account 123` → See usage types
4. **Resource-level:** `cc drill --service "EC2 - Other" --account 123 --resources` → See individual instance IDs

**Features:**
- **Week-over-week cost analysis**: Compare costs between consecutive weeks
- **Month-over-month cost analysis**: Compare costs between consecutive months
- **Drill-down analysis**: Analyze costs by service, account, or usage type
- **Resource-level analysis**: See individual resource IDs and costs using CUR data (NEW in v1.7.0)
- **Pandas aggregations**: Time series analysis with sum, avg, std across all weeks
- **Volatility detection**: Identify services with high cost variability and outliers
- **Trend detection**: Auto-detect increasing/decreasing cost patterns
- **Search & filter**: Find services by pattern or cost threshold
- **Profile management**: CRUD operations for account profiles in DynamoDB
- **Markdown reports**: Generate formatted reports
- **JSON output**: Machine-readable output for automation
- **Lambda API backend**: Serverless backend with pandas/numpy support

Example output:
```
# Drill by service
cc drill --profile myprofile --service "EC2 - Other"

Showing top accounts:
Week of Oct 19 → Week of Oct 26
  Increases: 3, Decreases: 2
  Top: 123456789012 (+$450.23)
```

The report is saved to `drill_down.md` by default.

## Output

```
Analyzing: 2025-10-03 to 2025-11-02 (30 days)
AWS Profile: my_aws_profile
Accounts: 3

Fetching cost data...
Fetching support costs...
============================================================
Period: 2025-10-03 to 2025-11-02
Days analyzed: 30
============================================================
Total operational cost: $450,000.00
Daily operational: $14,516.13
Support (month): $15,000.00
Support per day (÷2÷days): $241.94
============================================================
DAILY RATE: $14,758.07
ANNUAL PROJECTION: $5,386,695
============================================================
```

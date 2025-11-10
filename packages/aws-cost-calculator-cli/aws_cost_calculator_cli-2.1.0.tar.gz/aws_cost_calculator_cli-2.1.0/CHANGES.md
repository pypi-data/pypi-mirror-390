# Changelog

## Version 1.8.0 (2025-11-07)

### Added
- **New `cc investigate` command** - Multi-stage cost investigation tool
  - Combines cost analysis, resource inventory, and CloudTrail events
  - Automatically finds SSO profiles for accounts
  - Generates comprehensive markdown reports
  - Supports `--no-cloudtrail` flag for faster execution
  - Example: `cc investigate --profile myprofile --account 123456789012`

### Changed
- **Package cleanup** - Excluded backend, tests, and notebooks from PyPI distribution
  - Backend code is only for Lambda deployment, not needed in CLI package
  - Reduces package size and eliminates unnecessary files

### Security
- Verified no sensitive data (company names, account IDs) in PyPI package
- All example data uses generic placeholders

## Version 1.7.0 (2025-11-06)

### Added
- **`--resources` flag for `cc drill` command**: Resource-level cost analysis using CUR data
  - Shows individual resource IDs (EC2 instances, RDS databases, S3 buckets, etc.)
  - Queries AWS Cost and Usage Report via Athena
  - Works with both local execution and Lambda backend
  - Requires `--service` filter to be specified
  - Example: `cc drill --service "EC2 - Other" --account 123456789012 --resources`
  - Displays top 50 resources by cost with usage types and regions
- **`cc setup-cur` command**: Configure CUR settings for resource-level queries
  - Saves configuration to `~/.config/cost-calculator/cur_config.json`
  - Prompts for: Athena database, table name, S3 output location
  - Required before using `--resources` flag

### Security
- **CRITICAL**: Removed all hardcoded sensitive data from CUR queries
  - No hardcoded account IDs
  - No hardcoded database names
  - No hardcoded S3 bucket paths
  - All configuration must be provided by user via `cc setup-cur`

### Technical Details
- New module: `cost_calculator/cur.py` for local CUR queries
- New module: `backend/algorithms/cur.py` for Lambda CUR queries
- Updated `backend/handlers/drill.py` to support resource-level queries
- Service-to-product-code mapping for flexible service name handling
- Athena query execution with automatic polling and result parsing
- CUR configuration loaded from `~/.config/cost-calculator/cur_config.json` or environment variables

## Version 1.6.3 (2025-11-06)

### Added
- **`cc setup-api` command**: Automatically configure COST_API_SECRET
  - Saves to `~/.zshrc` or `~/.bashrc` on Mac/Linux
  - Saves to Windows user environment variables
  - Prompts for secret with hidden input
  - Updates existing configuration if already present

## Version 1.6.2 (2025-11-06)

### Fixed
- Updated installation instructions to use PyPI instead of local editable install

## Version 1.6.1 (2025-11-06)

### Fixed
- Sanitized all documentation to remove company-specific references
- Removed real account IDs and credentials from examples
- Updated all examples to use generic placeholder names

## Version 1.6.0 (2025-11-06) - YANKED

**Note:** This version was yanked due to unsanitized documentation containing company-specific information.

### Added
- **Flexible Authentication**: Multiple authentication methods for all commands
  - `--sso <profile>`: SSO authentication with automatic login if session expired
  - `--access-key-id`, `--secret-access-key`, `--session-token`: Static credentials
  - Environment variable support: `AWS_PROFILE` for SSO, `AWS_ACCESS_KEY_ID` for static
  - Auto SSO login: CLI automatically runs `aws sso login` if session is expired
- Applied authentication flags to all commands: `calculate`, `trends`, `monthly`, `drill`

### Changed
- Enhanced profile loading to check `AWS_PROFILE` environment variable for SSO support
- Updated README with comprehensive authentication documentation

### Benefits
- No manual SSO login required - CLI handles it automatically
- Support for temporary credentials via CLI flags
- Flexible authentication for different use cases (CI/CD, local dev, etc.)

## Version 1.5.0 (2024-11-04)

### Added
- **Analyze Command**: Pandas-based aggregations and statistical analysis
  - `cc analyze --type summary`: Aggregate costs across all weeks (sum, avg, std, min, max)
  - `cc analyze --type volatility`: Identify high-volatility services and outliers
  - `cc analyze --type trends`: Auto-detect increasing/decreasing cost trends
  - `cc analyze --type search`: Filter services by pattern or minimum cost
- **Profile Management**: CRUD operations for account profiles
  - `cc profile list`: List all profiles
  - `cc profile get --name <profile>`: Get profile details
  - `cc profile create/update/delete`: Manage profiles in DynamoDB
- **Lambda Enhancements**:
  - New Analyze Lambda function with AWS Data Wrangler layer (pandas/numpy)
  - New Profiles Lambda function for DynamoDB operations
  - 2GB memory, 900s timeout for analyze function
  - Time series analysis and statistical aggregations

### Changed
- Suppressed progress messages in JSON output mode for cleaner parsing
- Updated API client to support new analyze and profiles endpoints

### Fixed
- JSON output now properly formatted without extra echo statements

## Version 1.4.0 (2025-11-04)

### Features Added

#### Lambda API Backend Support
- **Hybrid execution**: CLI now supports both local and Lambda API execution
- Set `COST_API_URL` and `COST_API_SECRET` environment variables to use Lambda backend
- Falls back to local execution if API not configured
- **Identical results**: API and local execution produce exactly the same output
- No changes to CLI interface - completely transparent to users

#### Configuration
- Environment variables:
  - `COST_API_URL`: Base URL for Lambda API
  - `COST_API_SECRET`: Shared secret for API authentication
- Alternative: `~/.config/cost-calculator/api_config.json`

#### Benefits
- **Centralized logic**: Cost analysis runs on Lambda
- **Multiple interfaces**: Same backend for CLI, web UI, Jupyter
- **No code changes**: Existing CLI commands work identically
- **Flexible deployment**: Choose local or API execution

### Example Usage
```bash
# Use local execution (default)
cc trends --profile myprofile

# Use Lambda API
export COST_API_URL="https://xxx.lambda-url.us-east-1.on.aws"
export COST_API_SECRET="your-secret"
cc trends --profile myprofile  # Same command, uses API
```

### Documentation
- Added API client module
- Added executor module for hybrid execution
- Updated README with API configuration instructions

---

## Version 1.3.0 (2025-11-04)

### Features Added

#### Drill-Down Cost Analysis
- **New command:** `cc drill --profile <name>`
- Investigate cost changes at different levels of detail with automatic grouping
- **Funnel approach**: Start broad, drill deeper based on findings
- Supports three filter types:
  - `--service`: Filter by service name (e.g., "EC2 - Other")
  - `--account`: Filter by account ID
  - `--usage-type`: Filter by usage type
- Filters can be combined for deeper analysis

#### Automatic Grouping Logic
The command automatically shows the next level of detail:
- **No filters** → Shows services (same as trends)
- **Service only** → Shows accounts using that service
- **Account only** → Shows services in that account
- **Service + Account** → Shows usage types within that service/account
- **All three filters** → Shows regions

#### What It Shows
- Week-over-week comparisons (default: 4 weeks)
- Top 10 increases and decreases at the appropriate detail level
- Total rows showing sum of top 10 changes
- Percentage change and dollar amount
- Filters out noise (>$10 and >5% change)
- Most recent comparisons first

#### Use Cases
- **Investigate spikes**: See EC2 costs up? Drill to find which account
- **Account analysis**: Which services are driving costs in a specific account?
- **Service deep-dive**: Which usage types within EC2 are increasing?
- **Root cause analysis**: Follow the funnel from service → account → usage type

### Example Workflow
```bash
# 1. Start broad - see EC2 costs up $1000
cc trends --profile myprofile

# 2. Drill by service - see which accounts
cc drill --profile myprofile --service "EC2 - Other"
# Output: Account 123 is +$800

# 3. Drill deeper - see usage types
cc drill --profile myprofile --service "EC2 - Other" --account 123
# Output: DataTransfer-Regional-Bytes is +$750
```

### Documentation
- Updated README.md with drill-down examples and funnel approach
- Added drill command to CLI help
- Documented automatic grouping logic

---

## Version 1.2.0 (2025-11-04)

### Features Added

#### Month-over-Month Cost Analysis
- **New command:** `cc monthly --profile <name>`
- Analyzes month-over-month cost changes at service level
- Compares consecutive calendar months (October vs September, etc.)
- Generates comprehensive markdown report
- Supports custom number of months: `--months 12`
- JSON output option: `--json-output`
- Custom output file: `--output monthly_trends.md`

#### What It Shows
- Service-level aggregation (total cost per service)
- Top 10 increases and decreases per month comparison
- Total rows showing sum of top 10 changes
- Percentage change and dollar amount for each service
- Filters out noise (>$50 and >5% change)
- Most recent comparisons first (reverse chronological)

#### Use Cases
- Monthly cost review and budget tracking
- Identifying large month-over-month changes
- Understanding seasonal cost patterns
- Tracking major service additions or removals
- Long-term cost trend analysis

### Example Output
```
October 2025 → November 2025
  Increases: 1, Decreases: 10
  Top: Savings Plans for AWS Compute usage (+$231,161.46)
```

### Documentation
- Updated README.md with monthly command examples
- Added monthly report documentation

---

## Version 1.1.0 (2025-11-04)

### Features Added

#### Cost Trends Analysis with Dual Methodology
- **New command:** `cc trends --profile <name>`
- Analyzes cost changes with **two comparison methods**:
  1. **Week-over-Week (WoW)**: Compares consecutive weeks - catches immediate spikes
  2. **Trailing 30-Day (T-30)**: Compares to 4 weeks ago - shows sustained trends
- **Service-level aggregation**: Shows total cost per service (not usage type detail)
- Generates comprehensive markdown report with both methodologies
- Supports custom number of weeks: `--weeks 18`
- JSON output option: `--json-output`
- Custom output file: `--output weekly_trends.md`

#### What It Shows
- **Week-over-Week section**: Consecutive week comparisons (Monday to Sunday)
- **T-30 section**: 30-day baseline comparisons
- Top 10 cost increases and decreases for each comparison
- **Total rows**: Sum of top 10 changes for quick assessment
- Percentage change and dollar amount for each service
- Automatically filters out noise (>$10 and >5% change)
- Most recent comparisons first (reverse chronological)

#### Why Two Methodologies?
- **WoW**: Catches immediate changes, spikes, and weekly volatility
- **T-30**: Filters out noise, reveals sustained trends and real cost changes
- Together they provide both **immediate alerts** and **trend analysis**

#### Use Cases
- Weekly cost monitoring and anomaly detection
- Identifying sudden cost spikes (WoW) vs sustained increases (T-30)
- Understanding which services are trending up or down
- Tracking cost optimization efforts over time
- Distinguishing temporary spikes from permanent cost changes

### Example Output
```
WEEK-OVER-WEEK:
  Week of Oct 19 → Week of Oct 26
    Increases: 4, Decreases: 10
    Top: EC2 - Other (+$949.12)

TRAILING 30-DAY (T-30):
  Week of Oct 26 vs Week of Sep 28
    Increases: 10, Decreases: 10
    Top: EC2 - Other (+$886.39)
```

### Documentation
- Updated README.md with dual methodology explanation
- Added trends report format documentation
- Updated CLI help text

---

## Version 1.0.0 (2025-11-04)

### Features Added

#### 1. Static AWS Credentials Support
- **New command:** `cc configure --profile <name>`
- Allows using static AWS credentials instead of SSO
- Supports temporary credentials with session tokens
- Credentials stored securely in `~/.config/cost-calculator/credentials.json` (600 permissions)

#### 2. Dual Authentication Methods
- **SSO Method:** For interactive use (existing)
  ```bash
  aws sso login --profile my_sso_profile
  cc calculate --profile myprofile
  ```

- **Static Credentials Method:** For automation/CI (new)
  ```bash
  cc configure --profile myprofile
  # Enter: Access Key ID, Secret Access Key, Session Token (optional)
  cc calculate --profile myprofile
  ```

#### 3. Enhanced Help Documentation
- Updated `cc --help` with authentication method examples
- Added comprehensive guides:
  - `COST_CALCULATION_METHODOLOGY.md` - Formula explanation
  - `WEEKLY_COST_HISTORY.md` - Historical cost trends
  - `PYPI_UPLOAD_GUIDE.md` - Publishing instructions

#### 4. PyPI Packaging
- Prepared for PyPI distribution as `aws-cost-calculator-cli`
- Added proper metadata, classifiers, and dependencies
- Created upload script: `./upload_to_pypi.sh`
- Added LICENSE (MIT), MANIFEST.in, .gitignore

### Security Enhancements
- Credentials file permissions set to 600 (owner read/write only)
- Sensitive files excluded from git (.gitignore)
- No credentials leaked in error messages or logs

### Documentation
- **README.md:** Installation and usage guide
- **COST_CALCULATION_METHODOLOGY.md:** Detailed formula explanation
- **WEEKLY_COST_HISTORY.md:** 18 weeks of historical data
- **PYPI_UPLOAD_GUIDE.md:** Publishing instructions

### Commands Available
1. `cc init` - Initialize profile with account list
2. `cc configure` - Configure AWS credentials (NEW)
3. `cc calculate` - Calculate costs
4. `cc list-profiles` - List configured profiles

### Configuration Files
- `~/.config/cost-calculator/profiles.json` - Profile configurations
- `~/.config/cost-calculator/credentials.json` - AWS credentials (NEW)

### Next Steps
1. Test with temporary AWS credentials
2. Upload to PyPI
3. Install from PyPI: `pip install aws-cost-calculator-cli`

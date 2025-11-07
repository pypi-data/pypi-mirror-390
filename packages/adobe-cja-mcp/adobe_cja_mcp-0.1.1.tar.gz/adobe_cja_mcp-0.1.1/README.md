# Adobe Customer Journey Analytics MCP Server

[![PyPI version](https://badge.fury.io/py/adobe-cja-mcp.svg)](https://pypi.org/project/adobe-cja-mcp/)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Model Context Protocol (MCP) server for Adobe Customer Journey Analytics (CJA), enabling AI-powered analytics queries through Claude and other MCP clients.

## ⚡ Quick Start (Simplest Setup)

**No repository cloning required!** Users can run this MCP server with just 2 steps:

### 1. Install `uv` (Python package manager)

```bash
# macOS/Linux
brew install uv

# Or with curl
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### 2. Configure Claude Desktop

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS) or `%APPDATA%\Claude\claude_desktop_config.json` (Windows):

```json
{
  "mcpServers": {
    "Adobe CJA": {
      "command": "uvx",
      "args": ["adobe-cja-mcp"],
      "env": {
        "ADOBE_CLIENT_ID": "your_client_id_here",
        "ADOBE_CLIENT_SECRET": "your_client_secret_here",
        "ADOBE_ORG_ID": "your_org_id@AdobeOrg",
        "ADOBE_DATA_VIEW_ID": "dv_your_dataview_id"
      }
    }
  }
}
```

**That's it!** Restart Claude Desktop and `uvx` will automatically download and run the MCP server from PyPI - just like `npx` for Node.js!

---

## Overview

This MCP server provides tools for querying Adobe CJA data, including:
- Running analytics reports with dimensions and metrics
- Multi-dimensional breakdown analysis
- Time-series trend analysis at various granularities
- Searching and filtering dimension values
- Listing available dimensions and metrics
- Data view configuration access

## Features

**Core Reporting Tools (MVP):**
- Run ranked reports with dimensions and metrics
- Get top N items for any dimension
- List available dimensions and metrics
- Access data view configuration

**Phase 1 - Advanced Reporting:**
- **Breakdown Reports**: Multi-dimensional analysis (e.g., pages by device type)
- **Trended Reports**: Time-series analysis with hourly/daily/weekly/monthly granularity
- **Dimension Search**: Find specific dimension values (pages, products, campaigns)
- **Segment Support**: Filter reports with segment IDs

## Development Installation

For contributors and developers who want to modify the code:

### Prerequisites

- Python 3.10+
- Adobe Developer Console project with CJA API access
- Valid Adobe credentials (Client ID, Client Secret, Organization ID)

### Install from source

[uv](https://docs.astral.sh/uv/) is a fast Python package manager that handles dependencies and virtual environments automatically.

#### 1. Install uv (if not already installed)

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or with homebrew
brew install uv

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 2. Install the package

```bash
# Clone the repository
git clone https://github.com/markhilton/adobe-cja-mcp.git
cd adobe-cja-mcp

# Install dependencies and create virtual environment
uv sync

# Or install in editable mode
uv pip install -e .
```

The package is now installed. Credentials are provided via Claude Desktop MCP configuration (see Usage section below).

## Adobe CJA API Permissions

### Required Permissions Scope

For this MCP server to function, your Adobe API credentials (OAuth 2.0 Server-to-Server) **must** have the following permissions granted in Adobe Admin Console.

### Authentication Scopes

Your API credentials require these OAuth scopes:

```
openid
AdobeID
read_organizations
additional_info.projectedProductContext
cja.reporting         # CRITICAL - Required for all reporting operations
cja.workspace         # Required for workspace objects (projects, filters, etc.)
```

### Critical Permissions (Required for Core Functionality)

Without these permissions, the MCP server **cannot perform analytics queries**:

#### 1. CJA Reporting API - Ranked Reports
- **API Endpoint**: `POST https://cja.adobe.io/reports`
- **Permission**: CJA Reporting API Access
- **Required For**:
  - Running analytical reports with dimensions and metrics
  - Querying website performance data (sessions, page views, conversions)
  - Generating attribution analysis
  - Creating breakdown reports
- **MCP Tools Blocked Without Permission**:
  - `cja_run_report` - Main reporting tool
  - `cja_get_top_items` - Top performers analysis
  - `cja_get_trended_report` - Time-series analysis
  - `cja_get_breakdown_report` - Multi-dimensional breakdowns
  - `cja_get_sessions_data` - Session analytics
  - `cja_get_conversions_data` - Conversion tracking
  - `cja_get_attribution_analysis` - Attribution modeling
  - `cja_get_funnel_analysis` - Funnel analysis

#### 2. CJA Reporting API - Top Items
- **API Endpoint**: `GET https://cja.adobe.io/reports/topItems`
- **Permission**: CJA Reporting API Access
- **Required For**:
  - Ranking dimension items by metrics
  - Finding top pages, products, campaigns
- **MCP Tools Blocked Without Permission**:
  - `cja_get_top_items` (alternative implementation)

### Working Permissions (Read-Only Access)

These permissions are typically granted by default for read-only CJA API access and should already be available:

1. **GET `/data/dataviews/{id}/dimensions`** - List available dimensions
2. **GET `/data/dataviews/{id}/metrics`** - List available metrics
3. **GET `/data/dataviews/{id}`** - Get data view configuration details
4. **GET `/calculatedmetrics`** - List calculated metrics
5. **GET `/filters`** - List filters/segments
6. **GET `/dateranges`** - List date ranges
7. **GET `/annotations`** - List annotations
8. **GET `/projects`** - List Analysis Workspace projects
9. **GET `/data/connections`** - List data connections

### Optional Permissions (Enhanced Features)

These permissions enable additional features but are not required for basic operation:

#### Individual Dimension/Metric Details
- **Endpoints**:
  - `GET /data/dataviews/{id}/dimensions/{dimId}`
  - `GET /data/dataviews/{id}/metrics/{metricId}`
- **Benefit**: Get detailed metadata for specific dimensions/metrics
- **Workaround**: Use list endpoints instead

#### Filter Validation
- **Endpoint**: `POST /filters/validate`
- **Benefit**: Validate filter definitions before use
- **Workaround**: Test filters directly in reports

#### List All Data Views
- **Endpoint**: `GET /dataviews`
- **Benefit**: Discover all available data views
- **Workaround**: Use configured data view ID from environment variables

## Setting Up Permissions in Adobe Admin Console

### Step 1: Navigate to API Credentials

1. Log in to [Adobe Admin Console](https://adminconsole.adobe.com/)
2. Navigate to **Products** → **Customer Journey Analytics**
3. Click on **API Credentials**
4. Select your OAuth Server-to-Server credential (Client ID)

### Step 2: Add Product Profile

1. Click **Add Product Profile**
2. Select a profile that includes **CJA Reporting API Access**
3. Ensure the profile has the following permissions:
   - **Reporting API**: Full access to POST /reports and GET /reports/topItems
   - **Workspace API**: Access to filters, calculated metrics, projects
   - **Data Views**: Read access to configured data views

### Step 3: Verify OAuth Scopes

In the API credential configuration, verify these scopes are enabled:
- `openid`
- `AdobeID`
- `read_organizations`
- `additional_info.projectedProductContext`
- `cja.reporting` ← **CRITICAL**
- `cja.workspace` ← **CRITICAL**

### Step 4: Generate New Credentials (if needed)

If updating an existing credential doesn't enable reporting access:

1. Create a new OAuth Server-to-Server credential
2. Add CJA API as a service
3. Select a Product Profile with full Reporting API access
4. Copy the new Client ID and Client Secret to your `.env` file

## Testing Permissions

Run the permissions test suite to verify your API credentials have the required access:

```bash
pytest tests/integration/test_api_permissions.py -v -s
```

**Expected Results:**
- ✅ **9/15 endpoints** should pass with read-only access
- ❌ **6/15 endpoints** will fail without full Reporting API permissions
- ✅ **15/15 endpoints** should pass after granting Reporting API access

The test will generate a detailed report: `cja_api_permissions_report.json`

## Common Permission Issues

### Issue: 400 Bad Request on POST /reports

**Cause**: Missing `cja.reporting` scope or Reporting API product profile

**Solution**:
1. Add CJA Reporting API product profile to your API credential
2. Verify `cja.reporting` scope is included
3. Regenerate access token

### Issue: 403 Forbidden on any endpoint

**Cause**: OAuth token doesn't have required organization access

**Solution**:
1. Verify `ADOBE_ORG_ID` matches your CJA organization
2. Ensure API credential is added to the correct organization
3. Check that the user who created the credential has CJA access

### Issue: 404 Not Found on specific endpoints

**Cause**: Endpoint requires newer API version or different product profile

**Solution**:
1. Verify you're using the latest CJA API version
2. Check Adobe CJA API documentation for endpoint availability
3. Some endpoints may require Adobe Experience Platform permissions

## Usage

### Quick Start: Testing with Claude Desktop

The fastest way to test the MCP server is with Claude Desktop, which provides a visual interface for natural language queries.

#### 1. Install Claude Desktop

Download from: https://claude.ai/download

#### 2. Configure MCP Server

**Configuration File Location:**

- **macOS/Linux:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `%APPDATA%\Claude\claude_desktop_config.json`

**For Development (from cloned source):**

If you cloned the repository for development, use:

```json
{
  "mcpServers": {
    "Adobe CJA": {
      "command": "uv",
      "args": ["--directory", "/absolute/path/to/adobe-cja-mcp", "run", "adobe-cja-mcp"],
      "env": {
        "ADOBE_CLIENT_ID": "your_client_id_here",
        "ADOBE_CLIENT_SECRET": "your_client_secret_here",
        "ADOBE_ORG_ID": "your_org_id@AdobeOrg",
        "ADOBE_DATA_VIEW_ID": "dv_your_dataview_id"
      }
    }
  }
}
```

Replace `/absolute/path/to/adobe-cja-mcp` with your project path and add your Adobe credentials.

#### 3. Restart Claude Desktop

After saving the config file, completely restart Claude Desktop for changes to take effect.

#### 4. Verify Connection

Open Claude Desktop and look for the MCP indicator (🔌 icon) in the interface. You should see "adobe-cja" listed as a connected server.

#### 5. Test with Natural Language Queries

Try these example queries in Claude Desktop:

**Basic Session Analysis:**
```
Show me session count for the last 30 days
```

**Visualized Trends:**
```
Show my session count in a bar chart for the last 30 days
```

**Top Pages:**
```
What are the top 10 pages by page views this month?
```

**Conversion Analysis:**
```
Show me conversion rate trends for the past week
```

**Multi-dimensional Breakdown:**
```
Break down sessions by marketing channel and device type for last week
```

**Attribution Analysis:**
```
Show me first-touch attribution for conversions in the last 14 days
```

### Development and Testing

#### Run Tests

```bash
# Run all integration tests
uv run pytest tests/integration/ -v

# Run with coverage
uv run pytest tests/integration/ --cov=src/adobe_cja_mcp --cov-report=html
```

Note: Tests require environment variables to be set. Use the same credentials as your Claude Desktop configuration.

### Running the MCP Server Standalone

For debugging or testing the server independently:

```bash
# Set environment variables
export ADOBE_CLIENT_ID="your_client_id"
export ADOBE_CLIENT_SECRET="your_secret"
export ADOBE_ORG_ID="your_org@AdobeOrg"
export ADOBE_DATA_VIEW_ID="dv_your_dataview_id"

# Run the server with uv
uv run adobe-cja-mcp

# The server will start and listen for MCP protocol messages on stdin/stdout
# Press Ctrl+C to stop
```

### Testing MCP Tools Directly

You can test individual tools using the MCP inspector:

```bash
# Install MCP inspector
npm install -g @modelcontextprotocol/inspector

# Run inspector with your server (set env vars first)
mcp-inspector uv run adobe-cja-mcp
```

This opens a web UI where you can:
- See all available tools
- Test tool calls with custom parameters
- View raw JSON requests/responses
- Debug authentication and API calls

## Example Queries and Expected Results

### Session Analysis

**Query:**
```
Show me session count in a bar chart for the last 30 days
```

**What Happens:**
1. Claude identifies you want session metrics over time
2. Calls `cja_get_trended_report` or `cja_run_report` with:
   - Metric: `sessions` or `visits`
   - Date range: Last 30 days
   - Granularity: `day`
3. Formats results as a text-based bar chart or table
4. Returns daily session counts with visualization

**Expected Output:**
```
Session Count - Last 30 Days

Oct 1  ████████████████ 1,245
Oct 2  ██████████████ 1,108
Oct 3  ███████████████ 1,189
...
Oct 30 ████████████████████ 1,523

Total Sessions: 38,420
Average: 1,281 sessions/day
Peak: Oct 30 (1,523 sessions)
```

### Top Pages Analysis

**Query:**
```
What are the top 10 pages by page views this month?
```

**What Happens:**
1. Calls `cja_get_top_items` with:
   - Dimension: `page` or `pageName`
   - Metric: `pageviews`
   - Date range: This month
   - Limit: 10
2. Returns ranked list of pages

**Expected Output:**
```
Top 10 Pages by Page Views - October 2025

1. /home                    15,234 views
2. /products                 8,901 views
3. /about                    6,543 views
4. /contact                  4,321 views
5. /blog/article-123         3,987 views
6. /pricing                  3,456 views
7. /features                 2,890 views
8. /blog                     2,543 views
9. /documentation            2,234 views
10. /support                 1,987 views

Total: 52,096 page views
```

### Conversion Funnel

**Query:**
```
Show me the checkout funnel conversion rates for last week
```

**What Happens:**
1. Calls `cja_get_funnel_analysis` with predefined checkout steps
2. Or calls `cja_run_report` multiple times for each funnel step
3. Calculates drop-off rates between steps

**Expected Output:**
```
Checkout Funnel - Last 7 Days

Step 1: Product Page     → 10,000 visitors (100.0%)
         ↓ 45.0%
Step 2: Add to Cart      →  4,500 visitors ( 45.0%)
         ↓ 66.7%
Step 3: Checkout Started →  3,000 visitors ( 30.0%)
         ↓ 50.0%
Step 4: Payment Info     →  1,500 visitors ( 15.0%)
         ↓ 80.0%
Step 5: Purchase         →  1,200 visitors ( 12.0%)

Overall Conversion Rate: 12.0%
Biggest Drop-off: Product Page → Add to Cart (55%)
```

### Marketing Attribution

**Query:**
```
Show me first-touch attribution for conversions in the last 14 days
```

**What Happens:**
1. Calls `cja_get_attribution_analysis` with:
   - Attribution model: `first_touch`
   - Success event: `orders` or `conversions`
   - Date range: Last 14 days
2. Returns marketing channel credit distribution

**Expected Output:**
```
First-Touch Attribution - Last 14 Days
Total Conversions: 450

Channel              Conversions    % of Total    Revenue
──────────────────────────────────────────────────────────
Organic Search            180         40.0%      $45,000
Paid Search               135         30.0%      $33,750
Direct                     68         15.1%      $17,000
Email                      45         10.0%      $11,250
Social Media               22          4.9%       $5,500

Top First-Touch Channel: Organic Search
Highest Revenue/Conversion: Paid Search ($250 avg)
```

## Troubleshooting Integration

### Claude Desktop Not Showing MCP Server

**Check:**
1. Config file is in the correct location
2. JSON is valid (use a JSON validator)
3. `uv` is installed and in PATH (`uv --version`)
4. Project directory path is absolute and correct
5. Completely restart Claude Desktop (not just close window)

**Debug:**
View Claude Desktop logs:
- macOS: `~/Library/Logs/Claude/`
- Windows: `%APPDATA%\Claude\logs\`

### MCP Server Fails to Start

**Check:**
1. Dependencies are installed: `uv sync` in project directory
2. Credentials are set in `claude_desktop_config.json`
3. Test the server runs:
   ```bash
   cd /path/to/adobe-cja-mcp
   export ADOBE_CLIENT_ID="..." ADOBE_CLIENT_SECRET="..." ADOBE_ORG_ID="..." ADOBE_DATA_VIEW_ID="..."
   uv run adobe-cja-mcp
   ```

### Authentication Errors

**Check:**
1. `ADOBE_CLIENT_ID` and `ADOBE_CLIENT_SECRET` are correct in config JSON
2. `ADOBE_ORG_ID` matches your CJA organization (ends with `@AdobeOrg`)
3. `ADOBE_DATA_VIEW_ID` is correct (starts with `dv_`)

### No Data Returned from Queries

**Check:**
1. Data view has data for the requested date range
2. Dimension/metric names are valid for your data view
3. Run the API permissions test:
   ```bash
   uv run pytest tests/integration/test_api_permissions.py -v
   ```

## Available MCP Tools

### Core Reporting
- `cja_run_report` - Run custom analytics reports
- `cja_get_top_items` - Get top-performing items for a dimension
- `cja_get_trended_report` - Get time-series trends
- `cja_get_breakdown_report` - Get multi-dimensional breakdowns

### Metadata
- `cja_list_dimensions` - List available dimensions
- `cja_list_metrics` - List available metrics
- `cja_list_calculated_metrics` - List calculated metrics
- `cja_list_filters` - List filters/segments
- `cja_list_date_ranges` - List predefined date ranges
- `cja_get_dataview_info` - Get data view configuration

### Advanced Analytics
- `cja_search_dimension_items` - Search for dimension values
- `cja_get_sessions_data` - Analyze session metrics
- `cja_get_conversions_data` - Analyze conversion events
- `cja_get_attribution_analysis` - Run attribution models
- `cja_get_funnel_analysis` - Analyze conversion funnels

## Development

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test suite
uv run pytest tests/unit/
uv run pytest tests/integration/

# Run with coverage
uv run pytest --cov=src/adobe_cja_mcp --cov-report=html
```

### Project Structure

```
adobe-cja-mcp/
├── src/adobe_cja_mcp/
│   ├── auth/              # OAuth authentication
│   ├── client/            # CJA API client
│   ├── models/            # Pydantic schemas
│   ├── tools/             # MCP tool implementations
│   ├── utils/             # Configuration
│   └── server.py          # MCP server
├── tests/
│   └── integration/       # Integration tests
├── pyproject.toml         # Project metadata and dependencies
└── uv.lock                # Locked dependencies
```

## Security Considerations

- **Credentials**: Never commit credentials to version control
- **Configuration**: Credentials are provided via Claude Desktop MCP config only
- **Access Tokens**: Tokens are automatically refreshed and expire after 24 hours
- **Read-Only**: This server only performs read operations on CJA data
- **Audit Logging**: All API calls are logged by Adobe for audit purposes
- **Rate Limits**: Respect Adobe API rate limits (typically 120 requests/minute)

## Troubleshooting

### API Permission Errors

Run the permission test suite:
```bash
# Set environment variables first
export ADOBE_CLIENT_ID="..." ADOBE_CLIENT_SECRET="..." ADOBE_ORG_ID="..." ADOBE_DATA_VIEW_ID="..."

# Run tests
uv run pytest tests/integration/test_api_permissions.py -v
```

Review the generated report in `tmp/api_permissions_report.json` for detailed endpoint status.

## License

MIT License - see [LICENSE](LICENSE) file for details

## Support

For issues or questions:
- Adobe CJA API Documentation: https://developer.adobe.com/cja-apis/docs/
- Adobe Developer Console: https://developer.adobe.com/console
- Model Context Protocol: https://modelcontextprotocol.io/

## Contributing

[Add contribution guidelines if applicable]

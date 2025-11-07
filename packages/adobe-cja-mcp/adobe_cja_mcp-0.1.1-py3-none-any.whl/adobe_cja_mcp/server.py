"""Main MCP server for Adobe Customer Journey Analytics.

This server exposes CJA analytics capabilities through the Model Context Protocol,
allowing LLMs like Claude to perform data queries and analysis.
"""

import asyncio
from contextlib import asynccontextmanager
from typing import AsyncIterator

from mcp.server.fastmcp import FastMCP

from adobe_cja_mcp.auth.oauth import AdobeOAuthClient
from adobe_cja_mcp.client.cja_client import CJAClient
from adobe_cja_mcp.models.schemas import (
    CreateSegmentInput,
    GetDataViewInfoInput,
    GetSegmentDetailsInput,
    GetTopItemsInput,
    ListDimensionsInput,
    ListMetricsInput,
    ListSegmentsInput,
    RunBreakdownReportInput,
    RunReportInput,
    RunTrendedReportInput,
    SearchDimensionItemsInput,
    UpdateSegmentInput,
    ValidateSegmentInput,
    CreateCalculatedMetricInput,
    GetCalculatedMetricDetailsInput,
    ListCalculatedMetricsInput,
    ValidateCalculatedMetricInput,
)
from adobe_cja_mcp.tools.advanced_reporting import (
    run_breakdown_report_tool,
    run_trended_report_tool,
    search_dimension_items_tool,
)
from adobe_cja_mcp.tools.dimensions import list_dimensions_tool
from adobe_cja_mcp.tools.metrics import list_metrics_tool
from adobe_cja_mcp.tools.reporting import (
    get_dataview_info_tool,
    get_top_items_tool,
    run_report_tool,
)
from adobe_cja_mcp.tools.segments import (
    create_segment_tool,
    get_segment_details_tool,
    list_segments_tool,
    update_segment_tool,
    validate_segment_tool,
)
from adobe_cja_mcp.tools.calculated_metrics import (
    create_calculated_metric_tool,
    get_calculated_metric_details_tool,
    list_calculated_metrics_tool,
    validate_calculated_metric_tool,
)
from adobe_cja_mcp.utils.config import get_settings


# Application state
class AppContext:
    """Application context holding shared resources."""

    def __init__(self) -> None:
        self.settings = get_settings()
        self.oauth_client = AdobeOAuthClient(self.settings)
        self.cja_client = CJAClient(self.settings, self.oauth_client)


@asynccontextmanager
async def app_lifespan(server: FastMCP) -> AsyncIterator[AppContext]:
    """Manage application lifecycle and shared resources.

    Args:
        server: FastMCP server instance.

    Yields:
        AppContext: Application context with initialized clients.
    """
    context = AppContext()
    try:
        yield context
    finally:
        # Cleanup
        await context.cja_client.close()


# Initialize FastMCP server with lifespan
mcp = FastMCP("Adobe CJA Analytics", lifespan=app_lifespan)


# Resource 1: Available Dimensions
@mcp.resource("cja://dimensions")
async def get_dimensions_resource() -> str:
    """Provides a list of commonly used CJA dimensions with their IDs.

    This helps Claude understand which dimension IDs to use in reports without
    needing to call the list_dimensions tool first.
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    try:
        # Fetch dimensions from API
        response = await app_context.cja_client.list_dimensions()
        dimensions = response.get("content", [])

        # Format as a helpful reference
        output = "# Available CJA Dimensions\n\n"
        output += "Use these dimension IDs when running reports:\n\n"

        # Show the most commonly used dimensions first
        common_dims = [
            "variables/daterangeday",
            "variables/daterangeweek",
            "variables/daterangemonth",
            "variables/page",
            "variables/mobiledevicetype",
            "variables/device.type",
        ]

        output += "## Most Common Dimensions:\n"
        for dim in dimensions[:20]:  # Show first 20
            dim_id = dim.get("id", "")
            dim_name = dim.get("name", "")
            if dim_id and dim_name:
                output += f"- `{dim_id}` - {dim_name}\n"

        output += f"\n**Total available dimensions: {len(dimensions)}**\n"
        output += "\nUse the cja_list_dimensions tool to see all dimensions."

        return output
    except Exception as e:
        return f"Error loading dimensions: {str(e)}\n\nUse the cja_list_dimensions tool to retrieve dimensions."


# Resource 2: Available Metrics
@mcp.resource("cja://metrics")
async def get_metrics_resource() -> str:
    """Provides a list of commonly used CJA metrics with their IDs.

    This helps Claude understand which metric IDs to use in reports without
    needing to call the list_metrics tool first.
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    try:
        # Fetch metrics from API
        response = await app_context.cja_client.list_metrics()
        metrics = response.get("content", [])

        # Format as a helpful reference
        output = "# Available CJA Metrics\n\n"
        output += "Use these metric IDs when running reports:\n\n"

        output += "## Common Metrics:\n"
        for metric in metrics[:30]:  # Show first 30
            metric_id = metric.get("id", "")
            metric_name = metric.get("name", "")
            if metric_id and metric_name:
                output += f"- `{metric_id}` - {metric_name}\n"

        output += f"\n**Total available metrics: {len(metrics)}**\n"
        output += "\nUse the cja_list_metrics tool to see all metrics."

        return output
    except Exception as e:
        return f"Error loading metrics: {str(e)}\n\nUse the cja_list_metrics tool to retrieve metrics."


# Resource 3: Quick Reference Guide
@mcp.resource("cja://quick-reference")
def get_quick_reference() -> str:
    """Provides a quick reference guide for common CJA reporting patterns.

    This helps Claude understand how to construct reports correctly from the start.
    """
    return """# CJA Reporting Quick Reference

## Common Reporting Patterns

### Time-based Analysis (Daily, Weekly, Monthly)
- **Dimension**: `variables/daterangeday` (for daily data)
- **Dimension**: `variables/daterangeweek` (for weekly data)
- **Dimension**: `variables/daterangemonth` (for monthly data)
- **Common Metrics**: `metrics/visits`, `metrics/pageviews`, `metrics/orders`

### Sessions/Visits Analysis
- **Primary Metric**: `metrics/visits` (Total sessions)
- **Related Metrics**: `metrics/pageviews`, `metrics/bounces`

### E-commerce Analysis
- **Metrics**: `metrics/orders`, `metrics/revenue`, `metrics/units`
- **Common Dimensions**: `variables/product`, `variables/category`

### Device Analysis
- **Dimension**: `variables/mobiledevicetype` or `variables/device.type`
- **Metrics**: Any engagement or conversion metric

### Page Performance
- **Dimension**: `variables/page` or `variables/web.webPageDetails.name`
- **Metrics**: `metrics/pageviews`, `metrics/visits`

## Date Format
- Always use `YYYY-MM-DD` format (e.g., "2025-10-01")

## Common Patterns
1. **Daily trend**: Use `variables/daterangeday` with date range
2. **Top pages**: Use `variables/page` with `metrics/pageviews`
3. **Device breakdown**: Use `variables/mobiledevicetype` with any metric
4. **Monthly summary**: Use `variables/daterangemonth` with date range

## Best Practices
- Limit results appropriately (default: 10, max: 50000)
- Use specific date ranges for better performance
- Combine time dimensions with business metrics for trends
"""


# Tool 1: List Dimensions
@mcp.tool()
async def cja_list_dimensions(
    dataview_id: str | None = None,
    expansion: str | None = None,
) -> dict:
    """List all available dimensions in the CJA data view.

    Dimensions are attributes that can be used to break down and categorize your data,
    such as page names, product categories, marketing channels, date/time components, etc.

    Args:
        dataview_id: Optional data view ID (uses configured default if not provided).
        expansion: Optional additional fields to include (e.g., 'tags,approved').

    Returns:
        Dictionary with dimensions list and total count.

    Example queries:
        - "What dimensions are available in my data view?"
        - "List all dimensions I can use for analysis"
        - "Show me the available breakdowns"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = ListDimensionsInput(
        dataview_id=dataview_id,
        expansion=expansion,
    )

    result = await list_dimensions_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 2: List Metrics
@mcp.tool()
async def cja_list_metrics(
    dataview_id: str | None = None,
    expansion: str | None = None,
) -> dict:
    """List all available metrics in the CJA data view.

    Metrics are quantitative measurements of your data, such as visits, page views,
    revenue, conversion rates, time spent, etc.

    Args:
        dataview_id: Optional data view ID (uses configured default if not provided).
        expansion: Optional additional fields to include.

    Returns:
        Dictionary with metrics list and total count.

    Example queries:
        - "What metrics can I measure?"
        - "List all available metrics"
        - "Show me metrics for measuring website performance"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = ListMetricsInput(
        dataview_id=dataview_id,
        expansion=expansion,
    )

    result = await list_metrics_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 3: Run Report
@mcp.tool()
async def cja_run_report(
    dimension: str,
    metrics: list[str],
    start_date: str,
    end_date: str,
    limit: int = 10,
    dataview_id: str | None = None,
) -> dict:
    """Run a CJA report with specified dimension and metrics over a date range.

    This is the primary tool for analyzing data. It breaks down one or more metrics
    by a dimension over a specified time period.

    IMPORTANT: Before calling this tool, check the 'cja://quick-reference' resource
    for common dimension and metric IDs. For daily trends, use 'variables/daterangeday'.
    For sessions, use 'metrics/visits'. The resources provide commonly used IDs.

    Args:
        dimension: Dimension ID to break down (e.g., 'variables/daterangeday', 'variables/page').
        metrics: List of metric IDs to measure (e.g., ['metrics/visits', 'metrics/pageviews']).
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        limit: Maximum number of dimension items to return (default: 10, max: 50000).
        dataview_id: Optional data view ID (uses configured default if not provided).

    Returns:
        Dictionary with report data including dimension items and metric values.

    Common patterns (check cja://quick-reference resource for more):
        - Daily sessions: dimension='variables/daterangeday', metrics=['metrics/visits']
        - Top pages: dimension='variables/page', metrics=['metrics/pageviews']
        - Device breakdown: dimension='variables/mobiledevicetype', metrics=['metrics/visits']

    Example queries:
        - "Show me daily visits for January 2024"
        - "What are the top pages by pageviews last month?"
        - "Analyze sessions by device type for Q1"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = RunReportInput(
        dimension=dimension,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        dataview_id=dataview_id,
    )

    result = await run_report_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 4: Get Top Items
@mcp.tool()
async def cja_get_top_items(
    dimension: str,
    metric: str,
    start_date: str,
    end_date: str,
    limit: int = 10,
    dataview_id: str | None = None,
) -> dict:
    """Get top N items for a dimension ranked by a metric.

    This tool is optimized for finding the top performing dimension items based on
    a single metric, such as top pages by visits, top products by revenue, etc.

    Args:
        dimension: Dimension ID (e.g., 'variables/page', 'variables/product').
        metric: Metric ID to rank by (e.g., 'metrics/visits', 'metrics/revenue').
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        limit: Number of top items to return (default: 10, max: 500).
        dataview_id: Optional data view ID (uses configured default if not provided).

    Returns:
        Dictionary with top dimension items and their metric values.

    Example queries:
        - "What are the top 10 pages by visits this week?"
        - "Show me the top 20 products by revenue last month"
        - "Which marketing channels drove the most conversions?"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = GetTopItemsInput(
        dimension=dimension,
        metric=metric,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        dataview_id=dataview_id,
    )

    result = await get_top_items_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 5: Get Data View Info
@mcp.tool()
async def cja_get_dataview_info(
    dataview_id: str | None = None,
    expansion: str | None = None,
) -> dict:
    """Get detailed information about a CJA data view.

    This tool retrieves configuration and metadata for the data view, including
    its name, description, owner, and component counts.

    Args:
        dataview_id: Optional data view ID (uses configured default if not provided).
        expansion: Optional additional fields to include (e.g., 'components').

    Returns:
        Dictionary with data view configuration and metadata.

    Example queries:
        - "What data view am I using?"
        - "Show me information about the current data view"
        - "What's configured in my data view?"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = GetDataViewInfoInput(
        dataview_id=dataview_id,
        expansion=expansion,
    )

    result = await get_dataview_info_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 6: Run Breakdown Report (Phase 1)
@mcp.tool()
async def cja_run_breakdown_report(
    primary_dimension: str,
    breakdown_dimension: str,
    metrics: list[str],
    start_date: str,
    end_date: str,
    limit: int = 10,
    breakdown_limit: int = 5,
    segment_ids: list[str] | None = None,
    dataview_id: str | None = None,
) -> dict:
    """Run a multi-dimensional breakdown report.

    This tool performs breakdown analysis where you analyze a primary dimension
    and further break it down by a secondary dimension. For example, analyze pages
    and break them down by device type to understand device distribution per page.

    Args:
        primary_dimension: Primary dimension ID (e.g., 'variables/page', 'variables/campaign').
        breakdown_dimension: Dimension to break down by (e.g., 'variables/mobiledevicetype').
        metrics: List of metric IDs to analyze.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        limit: Maximum number of primary dimension items (default: 10, max: 500).
        breakdown_limit: Maximum breakdown items per primary item (default: 5, max: 50).
        segment_ids: Optional list of segment IDs to filter the report.
        dataview_id: Optional data view ID (uses configured default if not provided).

    Returns:
        Dictionary with nested breakdown report results.

    Example queries:
        - "Break down top pages by device type"
        - "Show me campaigns broken down by browser for last month"
        - "Analyze product performance by marketing channel"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = RunBreakdownReportInput(
        primary_dimension=primary_dimension,
        breakdown_dimension=breakdown_dimension,
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        breakdown_limit=breakdown_limit,
        segment_ids=segment_ids,
        dataview_id=dataview_id,
    )

    result = await run_breakdown_report_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 7: Run Trended Report (Phase 1)
@mcp.tool()
async def cja_run_trended_report(
    metrics: list[str],
    start_date: str,
    end_date: str,
    granularity: str = "day",
    dimension: str | None = None,
    dimension_limit: int = 5,
    segment_ids: list[str] | None = None,
    dataview_id: str | None = None,
) -> dict:
    """Run a time-series trend report.

    This tool analyzes how metrics change over time at a specified granularity
    (hourly, daily, weekly, monthly). Optionally break down trends by a dimension.

    Args:
        metrics: List of metric IDs to trend over time.
        start_date: Start date in YYYY-MM-DD format.
        end_date: End date in YYYY-MM-DD format.
        granularity: Time granularity - 'hour', 'day', 'week', or 'month' (default: 'day').
        dimension: Optional dimension to break down the trend (e.g., 'variables/mobiledevicetype').
        dimension_limit: Maximum dimension items if dimension specified (default: 5, max: 50).
        segment_ids: Optional list of segment IDs to filter the report.
        dataview_id: Optional data view ID (uses configured default if not provided).

    Returns:
        Dictionary with time-series trend data.

    Example queries:
        - "Show me daily visits trend for last 30 days"
        - "Trend pageviews by hour for yesterday"
        - "Show weekly revenue trend broken down by device type"
        - "Monthly orders trend for Q1 2024"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = RunTrendedReportInput(
        metrics=metrics,
        start_date=start_date,
        end_date=end_date,
        granularity=granularity,
        dimension=dimension,
        dimension_limit=dimension_limit,
        segment_ids=segment_ids,
        dataview_id=dataview_id,
    )

    result = await run_trended_report_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 8: Search Dimension Items (Phase 1)
@mcp.tool()
async def cja_search_dimension_items(
    dimension: str,
    search_term: str,
    start_date: str | None = None,
    end_date: str | None = None,
    limit: int = 100,
    dataview_id: str | None = None,
) -> dict:
    """Search for dimension items matching a search term.

    This tool searches within a dimension's values to find items containing
    the search term. Useful for finding specific pages, products, campaigns, etc.

    Args:
        dimension: Dimension ID to search within (e.g., 'variables/page', 'variables/product').
        search_term: Search term to find matching dimension items.
        start_date: Optional start date to scope search results (YYYY-MM-DD format).
        end_date: Optional end date to scope search results (YYYY-MM-DD format).
        limit: Maximum number of matching items to return (default: 100, max: 1000).
        dataview_id: Optional data view ID (uses configured default if not provided).

    Returns:
        Dictionary with matching dimension items.

    Example queries:
        - "Find all pages containing 'checkout'"
        - "Search for products with 'pro' in the name"
        - "Which campaigns contain 'summer'?"
        - "Find pages with 'login' that had activity last week"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = SearchDimensionItemsInput(
        dimension=dimension,
        search_term=search_term,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        dataview_id=dataview_id,
    )

    result = await search_dimension_items_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 9: List Segments (Phase 2)
@mcp.tool()
async def cja_list_segments(
    dataview_id: str | None = None,
    name: str | None = None,
    tag_names: str | None = None,
    include_type: str | None = None,
    limit: int = 10,
    page: int = 0,
    expansion: str | None = None,
) -> dict:
    """List all available segments/filters in CJA.

    Segments (also called filters in CJA) are reusable components that filter data
    in reports and analysis. This tool retrieves all segments you have access to.

    Args:
        dataview_id: Optional data view ID to filter segments (uses configured default if not provided).
        name: Filter segments by name (partial match).
        tag_names: Comma-delimited list of tag names to filter by.
        include_type: Include additional segments: 'shared', 'all', 'templates'.
        limit: Number of results per page (default: 10, max: 1000).
        page: Page number, 0-indexed (default: 0).
        expansion: Additional fields to include: 'definition', 'tags', 'compatibility', 'ownerFullName'.

    Returns:
        Dictionary with segments list and metadata.

    Example queries:
        - "List all available segments"
        - "Show me segments with 'mobile' in the name"
        - "What filters are tagged with 'marketing'?"
        - "List all shared segments"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = ListSegmentsInput(
        dataview_id=dataview_id,
        name=name,
        tag_names=tag_names,
        include_type=include_type,
        limit=limit,
        page=page,
        expansion=expansion,
    )

    result = await list_segments_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 10: Get Segment Details (Phase 2)
@mcp.tool()
async def cja_get_segment_details(
    segment_id: str,
    expansion: str | None = None,
) -> dict:
    """Get detailed information about a specific segment.

    This tool retrieves complete details about a segment including its definition,
    which shows the exact logic and rules used to filter data.

    Args:
        segment_id: Segment ID to retrieve.
        expansion: Additional fields to include: 'definition', 'tags', 'compatibility'.

    Returns:
        Dictionary with complete segment information.

    Example queries:
        - "Show me the definition of segment s300000022_5bb7c94e80f0073611afb35c"
        - "Get details for the Mobile Users segment"
        - "What's the logic in segment XYZ?"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = GetSegmentDetailsInput(
        segment_id=segment_id,
        expansion=expansion,
    )

    result = await get_segment_details_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 11: Create Segment (Phase 2)
@mcp.tool()
async def cja_create_segment(
    name: str,
    definition: dict,
    description: str | None = None,
    dataview_id: str | None = None,
) -> dict:
    """Create a new segment in CJA.

    This tool creates a new segment/filter that can be used in reports. Segment
    definitions use a JSON structure to define filtering rules.

    IMPORTANT: Segment definitions are complex. Best practice:
    1. Create a template segment in the CJA UI
    2. Use cja_get_segment_details to see its definition structure
    3. Modify the definition as needed
    4. Use cja_validate_segment before creating

    Args:
        name: Segment name (required).
        definition: Segment definition object with container and rules (required).
        description: Optional segment description.
        dataview_id: Optional data view ID (uses configured default if not provided).

    Returns:
        Dictionary with created segment including assigned ID.

    Example queries:
        - "Create a segment for mobile users"
        - "Make a new filter for high-value customers"

    Example definition (mobile users):
        {
            "container": {
                "func": "segment",
                "context": "hits",
                "pred": {
                    "func": "exists",
                    "val": {"func": "attr", "name": "variables/mobiledevicetype"}
                }
            },
            "func": "segment-def",
            "version": [1, 0, 0]
        }
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = CreateSegmentInput(
        name=name,
        description=description,
        dataview_id=dataview_id,
        definition=definition,
    )

    result = await create_segment_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 12: Validate Segment (Phase 2)
@mcp.tool()
async def cja_validate_segment(
    definition: dict,
    dataview_id: str | None = None,
) -> dict:
    """Validate a segment definition before creating or updating.

    This tool checks if a segment definition is syntactically correct and compatible
    with the specified data view. Always use this before creating a new segment.

    Args:
        definition: Segment definition to validate (required).
        dataview_id: Optional data view ID to validate against (uses configured default if not provided).

    Returns:
        Dictionary with validation result and compatibility information.

    Example queries:
        - "Validate this segment definition before I create it"
        - "Check if this filter definition is valid"
        - "Is this segment compatible with my data view?"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = ValidateSegmentInput(
        definition=definition,
        dataview_id=dataview_id,
    )

    result = await validate_segment_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Phase 3: Calculated Metrics Tools

# Tool 13: List Calculated Metrics (Phase 3)
@mcp.tool()
async def cja_list_calculated_metrics(
    name: str | None = None,
    tag_names: str | None = None,
    include_type: str | None = None,
    limit: int = 10,
    page: int = 0,
    expansion: str | None = None,
    dataview_id: str | None = None,
) -> dict:
    """List calculated metrics in CJA.

    Retrieve calculated metrics (custom formulas) that can be used in reports.
    You can filter by name, tags, and share type.

    Args:
        name: Optional filter by metric name (partial match).
        tag_names: Optional comma-delimited tag names to filter by.
        include_type: Optional 'shared', 'all', or 'templates' to include additional metrics.
        limit: Maximum results per page (1-1000, default 10).
        page: Page number for pagination (0-indexed, default 0).
        expansion: Optional comma-delimited fields: 'definition', 'tags', 'usedIn', 'compatibility'.
        dataview_id: Optional data view ID to filter metrics (uses configured default if not provided).

    Returns:
        Dictionary with list of calculated metrics and total count.

    Example queries:
        - "Show me all calculated metrics"
        - "List calculated metrics containing 'conversion' in the name"
        - "Get calculated metrics with their definitions"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = ListCalculatedMetricsInput(
        name=name,
        tag_names=tag_names,
        include_type=include_type,
        limit=limit,
        page=page,
        expansion=expansion,
        dataview_id=dataview_id,
    )

    result = await list_calculated_metrics_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 14: Get Calculated Metric Details (Phase 3)
@mcp.tool()
async def cja_get_calculated_metric_details(
    metric_id: str,
    expansion: str | None = None,
) -> dict:
    """Get detailed information about a specific calculated metric.

    Retrieve complete details about a calculated metric including its definition/formula.
    This is useful for understanding how a metric is calculated or copying definitions.

    Args:
        metric_id: Calculated metric ID to retrieve (required).
        expansion: Optional comma-delimited fields: 'definition', 'tags', 'usedIn', 'compatibility'.

    Returns:
        Dictionary with calculated metric details and formula definition.

    Example queries:
        - "Show me the formula for calculated metric a5066209"
        - "Get definition for the conversion rate metric"
        - "What's the formula for metric ID 12345?"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = GetCalculatedMetricDetailsInput(
        metric_id=metric_id,
        expansion=expansion,
    )

    result = await get_calculated_metric_details_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 15: Create Calculated Metric (Phase 3)
@mcp.tool()
async def cja_create_calculated_metric(
    name: str,
    definition: dict,
    description: str | None = None,
    metric_type: str = "decimal",
    polarity: str | None = None,
    precision: int | None = None,
    dataview_id: str | None = None,
) -> dict:
    """Create a new calculated metric in CJA.

    Create a custom metric with formulas and functions that can be used in reports.
    IMPORTANT: Validate the definition first using cja_validate_calculated_metric.

    Args:
        name: Metric name (required).
        definition: Metric definition with formula (required). Should have 'func': 'calc-metric', 'formula': {...}, 'version': [1,0,0].
        description: Optional metric description.
        metric_type: Type: 'decimal', 'percent', 'currency', or 'time' (default 'decimal').
        polarity: Optional 'positive' or 'negative' (indicates if higher values are better/worse).
        precision: Optional decimal places for display (0-10).
        dataview_id: Optional data view ID (uses configured default if not provided).

    Returns:
        Dictionary with created calculated metric details including assigned ID.

    Example queries:
        - "Create a calculated metric named 'Conversion Rate'"
        - "Make a new metric that divides revenue by orders"
        - "Create a metric for visits per visitor"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = CreateCalculatedMetricInput(
        name=name,
        description=description,
        dataview_id=dataview_id,
        type=metric_type,
        polarity=polarity,
        precision=precision,
        definition=definition,
    )

    result = await create_calculated_metric_tool(app_context.cja_client, input_data)
    return result.model_dump()


# Tool 16: Validate Calculated Metric (Phase 3)
@mcp.tool()
async def cja_validate_calculated_metric(
    name: str,
    definition: dict,
    metric_type: str = "decimal",
    description: str | None = None,
    dataview_id: str | None = None,
) -> dict:
    """Validate a calculated metric definition before creating or updating.

    Check if a calculated metric definition is syntactically correct and compatible
    with the data view. Always use this before creating a new metric.

    Args:
        name: Metric name for validation (required).
        definition: Metric definition to validate (required).
        metric_type: Type: 'decimal', 'percent', 'currency', or 'time' (default 'decimal').
        description: Optional metric description for validation.
        dataview_id: Optional data view ID to validate against (uses configured default if not provided).

    Returns:
        Dictionary with validation result, metrics used, and functions detected.

    Example queries:
        - "Validate this calculated metric definition before I create it"
        - "Check if this metric formula is valid"
        - "Is this calculated metric definition compatible?"
    """
    ctx = mcp.get_context()
    app_context: AppContext = ctx.request_context.lifespan_context

    input_data = ValidateCalculatedMetricInput(
        definition=definition,
        name=name,
        type=metric_type,
        dataview_id=dataview_id,
        description=description,
    )

    result = await validate_calculated_metric_tool(app_context.cja_client, input_data)
    return result.model_dump()


def main() -> None:
    """Main entry point for the MCP server."""
    import sys

    # Run the server
    mcp.run()


if __name__ == "__main__":
    main()

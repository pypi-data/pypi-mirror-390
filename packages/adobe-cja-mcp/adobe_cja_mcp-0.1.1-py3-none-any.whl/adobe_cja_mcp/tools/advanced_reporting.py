"""MCP tools for advanced CJA reporting (Phase 1 enhancement)."""

from typing import Any

from adobe_cja_mcp.client.cja_client import CJAClient
from adobe_cja_mcp.models.schemas import (
    BreakdownItem,
    BreakdownReportOutput,
    BreakdownReportRow,
    DimensionItemMatch,
    RunBreakdownReportInput,
    RunTrendedReportInput,
    SearchDimensionItemsInput,
    SearchDimensionItemsOutput,
    TrendDataPoint,
    TrendedReportOutput,
    TrendedReportRow,
)


async def run_breakdown_report_tool(
    client: CJAClient,
    input_data: RunBreakdownReportInput,
) -> BreakdownReportOutput:
    """Run a multi-dimensional breakdown report.

    This tool performs a breakdown analysis where you analyze a primary dimension
    and further break it down by a secondary dimension. For example, analyze pages
    and break them down by device type to understand device distribution per page.

    Args:
        client: CJA API client instance.
        input_data: Breakdown report parameters.

    Returns:
        BreakdownReportOutput: Nested breakdown results.

    Example:
        >>> input_data = RunBreakdownReportInput(
        ...     primary_dimension="variables/page",
        ...     breakdown_dimension="variables/mobiledevicetype",
        ...     metrics=["metrics/visits"],
        ...     start_date="2024-01-01",
        ...     end_date="2024-01-31",
        ...     limit=10,
        ...     breakdown_limit=5
        ... )
        >>> await run_breakdown_report_tool(client, input_data)
    """
    # Build global filters with date range and optional segments
    global_filters = [
        {
            "type": "dateRange",
            "dateRange": f"{input_data.start_date}T00:00:00.000/{input_data.end_date}T23:59:59.999",
        }
    ]

    # Add segment filters if provided
    if input_data.segment_ids:
        for segment_id in input_data.segment_ids:
            global_filters.append({
                "type": "segment",
                "segmentId": segment_id,
            })

    # Build request for primary dimension
    request_body = {
        "globalFilters": global_filters,
        "metricContainer": {
            "metrics": [
                {"columnId": str(idx), "id": metric_id}
                for idx, metric_id in enumerate(input_data.metrics)
            ]
        },
        "dimension": input_data.primary_dimension,
        "settings": {
            "limit": input_data.limit,
            "page": 0,
        },
    }

    # Get primary dimension data
    primary_response = await client.run_report(
        request_body=request_body,
        dataview_id=input_data.dataview_id,
    )

    primary_rows = primary_response.get("rows", [])

    # Now fetch breakdown data for each primary dimension item
    breakdown_rows = []

    for primary_row in primary_rows:
        primary_value = primary_row.get("value", "Unknown")
        primary_item_id = primary_row.get("itemId", primary_value)

        # Extract primary metrics
        primary_data = primary_row.get("data", [])
        primary_metrics = {}
        for idx, metric_id in enumerate(input_data.metrics):
            if idx < len(primary_data):
                primary_metrics[metric_id] = primary_data[idx]

        # Build breakdown request for this primary item
        breakdown_request = {
            "globalFilters": global_filters,
            "metricContainer": {
                "metrics": [
                    {"columnId": str(idx), "id": metric_id}
                    for idx, metric_id in enumerate(input_data.metrics)
                ]
            },
            "dimension": input_data.breakdown_dimension,
            "settings": {
                "limit": input_data.breakdown_limit,
                "page": 0,
            },
            # Add dimension filter for the primary item
            "search": {
                "clause": f"CONTAINS '{primary_item_id}'"
            } if primary_item_id else None,
        }

        # Remove None values
        breakdown_request = {k: v for k, v in breakdown_request.items() if v is not None}

        # Add filter for primary dimension item
        breakdown_request["metricFilters"] = {
            "type": "breakdown",
            "dimension": input_data.primary_dimension,
            "itemId": primary_item_id,
        }

        try:
            breakdown_response = await client.run_report(
                request_body=breakdown_request,
                dataview_id=input_data.dataview_id,
            )

            breakdown_items_data = breakdown_response.get("rows", [])
            breakdown_items = []

            for breakdown_row in breakdown_items_data:
                breakdown_value = breakdown_row.get("value", "Unknown")
                breakdown_data = breakdown_row.get("data", [])
                breakdown_metrics = {}

                for idx, metric_id in enumerate(input_data.metrics):
                    if idx < len(breakdown_data):
                        breakdown_metrics[metric_id] = breakdown_data[idx]

                breakdown_items.append(
                    BreakdownItem(
                        breakdown_value=breakdown_value,
                        metric_values=breakdown_metrics,
                    )
                )
        except Exception:
            # If breakdown fails for this item, continue with empty breakdowns
            breakdown_items = []

        breakdown_rows.append(
            BreakdownReportRow(
                primary_value=primary_value,
                primary_metrics=primary_metrics,
                breakdowns=breakdown_items,
            )
        )

    return BreakdownReportOutput(
        primary_dimension=input_data.primary_dimension,
        breakdown_dimension=input_data.breakdown_dimension,
        date_range={
            "start_date": input_data.start_date,
            "end_date": input_data.end_date,
        },
        rows=breakdown_rows,
        total_rows=len(breakdown_rows),
    )


async def run_trended_report_tool(
    client: CJAClient,
    input_data: RunTrendedReportInput,
) -> TrendedReportOutput:
    """Run a time-series trend report.

    This tool analyzes how metrics change over time at a specified granularity
    (hourly, daily, weekly, monthly). Optionally break down trends by a dimension.

    Args:
        client: CJA API client instance.
        input_data: Trended report parameters.

    Returns:
        TrendedReportOutput: Time-series trend data.

    Example:
        >>> input_data = RunTrendedReportInput(
        ...     metrics=["metrics/visits", "metrics/pageviews"],
        ...     start_date="2024-01-01",
        ...     end_date="2024-01-31",
        ...     granularity="day"
        ... )
        >>> await run_trended_report_tool(client, input_data)
    """
    # Map granularity to CJA dimension
    granularity_map = {
        "hour": "variables/daterangehour",
        "day": "variables/daterangeday",
        "week": "variables/daterangeweek",
        "month": "variables/daterangemonth",
    }

    time_dimension = granularity_map.get(input_data.granularity, "variables/daterangeday")

    # Build global filters
    global_filters = [
        {
            "type": "dateRange",
            "dateRange": f"{input_data.start_date}T00:00:00.000/{input_data.end_date}T23:59:59.999",
        }
    ]

    # Add segment filters if provided
    if input_data.segment_ids:
        for segment_id in input_data.segment_ids:
            global_filters.append({
                "type": "segment",
                "segmentId": segment_id,
            })

    rows = []

    if input_data.dimension:
        # Trended report with dimension breakdown
        # First get the top dimension items
        dimension_request = {
            "globalFilters": global_filters,
            "metricContainer": {
                "metrics": [{"columnId": "0", "id": input_data.metrics[0], "sort": "desc"}]
            },
            "dimension": input_data.dimension,
            "settings": {
                "limit": input_data.dimension_limit,
                "page": 0,
            },
        }

        dim_response = await client.run_report(
            request_body=dimension_request,
            dataview_id=input_data.dataview_id,
        )

        dim_items = dim_response.get("rows", [])

        # For each dimension item, get the trended data
        for dim_item in dim_items:
            dimension_value = dim_item.get("value", "Unknown")
            item_id = dim_item.get("itemId", dimension_value)

            # Build trended request for this dimension item
            trend_request = {
                "globalFilters": global_filters,
                "metricContainer": {
                    "metrics": [
                        {"columnId": str(idx), "id": metric_id}
                        for idx, metric_id in enumerate(input_data.metrics)
                    ]
                },
                "dimension": time_dimension,
                "settings": {
                    "limit": 50000,  # Get all time periods
                    "page": 0,
                },
                "metricFilters": {
                    "type": "breakdown",
                    "dimension": input_data.dimension,
                    "itemId": item_id,
                },
            }

            trend_response = await client.run_report(
                request_body=trend_request,
                dataview_id=input_data.dataview_id,
            )

            trend_points = []
            for trend_row in trend_response.get("rows", []):
                timestamp = trend_row.get("value", "")
                data = trend_row.get("data", [])

                metric_values = {}
                for idx, metric_id in enumerate(input_data.metrics):
                    if idx < len(data):
                        metric_values[metric_id] = data[idx]

                trend_points.append(
                    TrendDataPoint(
                        timestamp=timestamp,
                        metric_values=metric_values,
                    )
                )

            rows.append(
                TrendedReportRow(
                    dimension_value=dimension_value,
                    trend_data=trend_points,
                )
            )
    else:
        # Simple trended report without dimension breakdown
        trend_request = {
            "globalFilters": global_filters,
            "metricContainer": {
                "metrics": [
                    {"columnId": str(idx), "id": metric_id}
                    for idx, metric_id in enumerate(input_data.metrics)
                ]
            },
            "dimension": time_dimension,
            "settings": {
                "limit": 50000,  # Get all time periods
                "page": 0,
            },
        }

        trend_response = await client.run_report(
            request_body=trend_request,
            dataview_id=input_data.dataview_id,
        )

        trend_points = []
        for trend_row in trend_response.get("rows", []):
            timestamp = trend_row.get("value", "")
            data = trend_row.get("data", [])

            metric_values = {}
            for idx, metric_id in enumerate(input_data.metrics):
                if idx < len(data):
                    metric_values[metric_id] = data[idx]

            trend_points.append(
                TrendDataPoint(
                    timestamp=timestamp,
                    metric_values=metric_values,
                )
            )

        rows.append(
            TrendedReportRow(
                dimension_value=None,
                trend_data=trend_points,
            )
        )

    total_data_points = sum(len(row.trend_data) for row in rows)

    return TrendedReportOutput(
        metrics=input_data.metrics,
        date_range={
            "start_date": input_data.start_date,
            "end_date": input_data.end_date,
        },
        granularity=input_data.granularity,
        dimension=input_data.dimension,
        rows=rows,
        total_data_points=total_data_points,
    )


async def search_dimension_items_tool(
    client: CJAClient,
    input_data: SearchDimensionItemsInput,
) -> SearchDimensionItemsOutput:
    """Search for dimension items matching a search term.

    This tool searches within a dimension's values to find items containing
    the search term. Useful for finding specific pages, products, campaigns, etc.

    Args:
        client: CJA API client instance.
        input_data: Search parameters.

    Returns:
        SearchDimensionItemsOutput: Matching dimension items.

    Example:
        >>> input_data = SearchDimensionItemsInput(
        ...     dimension="variables/page",
        ...     search_term="checkout",
        ...     limit=50
        ... )
        >>> await search_dimension_items_tool(client, input_data)
    """
    # Build global filters (required by API)
    global_filters = []

    # Add date range if provided, otherwise use a wide default range
    if input_data.start_date and input_data.end_date:
        global_filters.append({
            "type": "dateRange",
            "dateRange": f"{input_data.start_date}T00:00:00.000/{input_data.end_date}T23:59:59.999",
        })
    else:
        # Use last 90 days as default if no date range specified
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        global_filters.append({
            "type": "dateRange",
            "dateRange": f"{start_date.strftime('%Y-%m-%d')}T00:00:00.000/{end_date.strftime('%Y-%m-%d')}T23:59:59.999",
        })

    # Build search request
    request_body = {
        "globalFilters": global_filters,  # Always include globalFilters
        "dimension": input_data.dimension,
        "settings": {
            "limit": input_data.limit,
            "page": 0,
        },
        "search": {
            "clause": f"CONTAINS '{input_data.search_term}'"
        },
        # Use a simple metric just to get dimension items
        "metricContainer": {
            "metrics": [{"columnId": "0", "id": "metrics/occurrences"}]
        },
    }

    response = await client.run_report(
        request_body=request_body,
        dataview_id=input_data.dataview_id,
    )

    # Parse response to extract matching dimension items
    rows_data = response.get("rows", [])
    matches = []

    for row in rows_data:
        value = row.get("value", "")
        item_id = row.get("itemId")

        # Only include items that match the search term (case-insensitive)
        if input_data.search_term.lower() in value.lower():
            matches.append(
                DimensionItemMatch(
                    value=value,
                    item_id=item_id,
                )
            )

    return SearchDimensionItemsOutput(
        dimension=input_data.dimension,
        search_term=input_data.search_term,
        matches=matches,
        total_matches=len(matches),
    )

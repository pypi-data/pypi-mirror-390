"""MCP tools for CJA reporting."""

from typing import Any

from adobe_cja_mcp.client.cja_client import CJAClient
from adobe_cja_mcp.models.schemas import (
    GetDataViewInfoInput,
    GetTopItemsInput,
    ReportOutput,
    ReportRow,
    RunReportInput,
    DataViewOutput,
)


async def run_report_tool(
    client: CJAClient,
    input_data: RunReportInput,
) -> ReportOutput:
    """Run a CJA report with specified dimension and metrics.

    This tool executes a report query to analyze data across a dimension
    with one or more metrics over a date range.

    Args:
        client: CJA API client instance.
        input_data: Report parameters including dimension, metrics, and date range.

    Returns:
        ReportOutput: Report results with dimension items and metric values.

    Example:
        >>> input_data = RunReportInput(
        ...     dimension="variables/daterangeday",
        ...     metrics=["metrics/visits", "metrics/pageviews"],
        ...     start_date="2024-01-01",
        ...     end_date="2024-01-31",
        ...     limit=10
        ... )
        >>> await run_report_tool(client, input_data)
    """
    # Build report request body for CJA API
    request_body = {
        "globalFilters": [
            {
                "type": "dateRange",
                "dateRange": f"{input_data.start_date}T00:00:00.000/{input_data.end_date}T23:59:59.999",
            }
        ],
        "metricContainer": {
            "metrics": [
                {"columnId": str(idx), "id": metric_id}
                for idx, metric_id in enumerate(input_data.metrics)
            ]
        },
        "dimension": input_data.dimension,
        "settings": {
            "limit": input_data.limit,
            "page": 0,
        },
    }

    response = await client.run_report(
        request_body=request_body,
        dataview_id=input_data.dataview_id,
    )

    # Parse response
    rows_data = response.get("rows", [])
    summary_data = response.get("summaryData", {})

    rows = []
    for row in rows_data:
        dimension_value = row.get("value", "Unknown")
        metric_values = {}

        data = row.get("data", [])
        for idx, metric_id in enumerate(input_data.metrics):
            if idx < len(data):
                metric_values[metric_id] = data[idx]

        rows.append(
            ReportRow(
                dimension_value=dimension_value,
                metric_values=metric_values,
            )
        )

    return ReportOutput(
        dimension=input_data.dimension,
        date_range={
            "start_date": input_data.start_date,
            "end_date": input_data.end_date,
        },
        rows=rows,
        total_rows=len(rows),
        summary=summary_data,
    )


async def get_top_items_tool(
    client: CJAClient,
    input_data: GetTopItemsInput,
) -> ReportOutput:
    """Get top N items for a dimension ranked by a metric.

    This tool retrieves the top performing dimension items based on a specific
    metric, useful for identifying top pages, products, campaigns, etc.

    Args:
        client: CJA API client instance.
        input_data: Parameters including dimension, metric, date range, and limit.

    Returns:
        ReportOutput: Top dimension items with metric values.

    Example:
        >>> input_data = GetTopItemsInput(
        ...     dimension="variables/page",
        ...     metric="metrics/visits",
        ...     start_date="2024-01-01",
        ...     end_date="2024-01-31",
        ...     limit=10
        ... )
        >>> await get_top_items_tool(client, input_data)
    """
    # Build request for top items
    request_body = {
        "globalFilters": [
            {
                "type": "dateRange",
                "dateRange": f"{input_data.start_date}T00:00:00.000/{input_data.end_date}T23:59:59.999",
            }
        ],
        "metricContainer": {
            "metrics": [{"columnId": "0", "id": input_data.metric, "sort": "desc"}]
        },
        "dimension": input_data.dimension,
        "settings": {
            "limit": input_data.limit,
            "page": 0,
        },
    }

    response = await client.run_report(
        request_body=request_body,
        dataview_id=input_data.dataview_id,
    )

    # Parse response
    rows_data = response.get("rows", [])
    summary_data = response.get("summaryData", {})

    rows = []
    for row in rows_data:
        dimension_value = row.get("value", "Unknown")
        data = row.get("data", [])
        metric_value = data[0] if len(data) > 0 else 0

        rows.append(
            ReportRow(
                dimension_value=dimension_value,
                metric_values={input_data.metric: metric_value},
            )
        )

    return ReportOutput(
        dimension=input_data.dimension,
        date_range={
            "start_date": input_data.start_date,
            "end_date": input_data.end_date,
        },
        rows=rows,
        total_rows=len(rows),
        summary=summary_data,
    )


async def get_dataview_info_tool(
    client: CJAClient,
    input_data: GetDataViewInfoInput,
) -> DataViewOutput:
    """Get detailed information about a data view.

    This tool retrieves configuration and metadata for a CJA data view,
    including its components, settings, and ownership information.

    Args:
        client: CJA API client instance.
        input_data: Parameters for data view lookup.

    Returns:
        DataViewOutput: Data view configuration and metadata.

    Example:
        >>> await get_dataview_info_tool(client, GetDataViewInfoInput())
    """
    params = {}
    if input_data.expansion:
        params["expansion"] = input_data.expansion

    response = await client.get_dataview(
        dataview_id=input_data.dataview_id,
    )

    # Parse response
    components_count = 0
    if "componentMetadata" in response:
        components_count = len(response.get("componentMetadata", []))

    return DataViewOutput(
        id=response.get("id", ""),
        name=response.get("name", ""),
        description=response.get("description"),
        owner=response.get("owner"),
        created=response.get("created"),
        modified=response.get("modified"),
        components_count=components_count,
    )

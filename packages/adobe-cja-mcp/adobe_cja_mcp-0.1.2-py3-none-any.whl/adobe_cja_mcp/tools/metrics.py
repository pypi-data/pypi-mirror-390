"""MCP tools for CJA metrics."""

from typing import Any

from adobe_cja_mcp.client.cja_client import CJAClient
from adobe_cja_mcp.models.schemas import ListMetricsInput, MetricInfo, MetricListOutput


async def list_metrics_tool(
    client: CJAClient,
    input_data: ListMetricsInput,
) -> MetricListOutput:
    """List all available metrics in the data view.

    This tool retrieves all metrics that can be used for measuring and analyzing
    data in reports.

    Args:
        client: CJA API client instance.
        input_data: Input parameters for listing metrics.

    Returns:
        MetricListOutput: List of metrics with metadata.

    Example:
        >>> await list_metrics_tool(client, ListMetricsInput())
    """
    params = {}
    if input_data.expansion:
        params["expansion"] = input_data.expansion

    response = await client.list_metrics(
        dataview_id=input_data.dataview_id,
    )

    # Parse response
    metrics_data = response.get("content", [])

    metrics = [
        MetricInfo(
            id=metric.get("id", ""),
            name=metric.get("name", ""),
            type=metric.get("type"),
        )
        for metric in metrics_data
    ]

    return MetricListOutput(
        metrics=metrics,
        total_count=len(metrics),
    )

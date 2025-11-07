"""MCP tools for CJA dimensions."""

from typing import Any

from adobe_cja_mcp.client.cja_client import CJAClient
from adobe_cja_mcp.models.schemas import DimensionInfo, DimensionListOutput, ListDimensionsInput


async def list_dimensions_tool(
    client: CJAClient,
    input_data: ListDimensionsInput,
) -> DimensionListOutput:
    """List all available dimensions in the data view.

    This tool retrieves all dimensions that can be used for breaking down data
    in reports and analytics queries.

    Args:
        client: CJA API client instance.
        input_data: Input parameters for listing dimensions.

    Returns:
        DimensionListOutput: List of dimensions with metadata.

    Example:
        >>> await list_dimensions_tool(client, ListDimensionsInput())
    """
    params = {}
    if input_data.expansion:
        params["expansion"] = input_data.expansion

    response = await client.list_dimensions(
        dataview_id=input_data.dataview_id,
    )

    # Parse response
    dimensions_data = response.get("content", [])

    dimensions = [
        DimensionInfo(
            id=dim.get("id", ""),
            name=dim.get("name", ""),
            type=dim.get("type"),
            hasData=dim.get("hasData"),
        )
        for dim in dimensions_data
    ]

    return DimensionListOutput(
        dimensions=dimensions,
        total_count=len(dimensions),
    )

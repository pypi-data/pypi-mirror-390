"""MCP tools for CJA segment management (Phase 2)."""

from typing import Any

from adobe_cja_mcp.client.cja_client import CJAClient
from adobe_cja_mcp.models.schemas import (
    CreateSegmentInput,
    GetSegmentDetailsInput,
    ListSegmentsInput,
    SegmentDetailsOutput,
    SegmentInfo,
    SegmentListOutput,
    SegmentValidationOutput,
    UpdateSegmentInput,
    ValidateSegmentInput,
)


async def list_segments_tool(
    client: CJAClient,
    input_data: ListSegmentsInput,
) -> SegmentListOutput:
    """List all segments/filters available in CJA.

    This tool retrieves segments (also called filters in CJA) that can be used
    to filter reports and analysis. You can filter by name, tags, and data view.

    Args:
        client: CJA API client instance.
        input_data: Parameters for listing segments.

    Returns:
        SegmentListOutput: List of segments with metadata.

    Example:
        >>> input_data = ListSegmentsInput(
        ...     name="mobile",
        ...     expansion="definition,tags",
        ...     limit=20
        ... )
        >>> await list_segments_tool(client, input_data)
    """
    # Build query parameters
    params = {
        "limit": input_data.limit,
        "page": input_data.page,
    }

    # Add optional filters
    if input_data.name:
        params["name"] = input_data.name
    if input_data.tag_names:
        params["tagNames"] = input_data.tag_names
    if input_data.include_type:
        params["includeType"] = input_data.include_type
    if input_data.expansion:
        params["expansion"] = input_data.expansion

    # Call API
    response = await client.list_segments(
        dataview_id=input_data.dataview_id,
        params=params,
    )

    # Parse response - API returns array of segments
    segments_data = response if isinstance(response, list) else response.get("content", [])

    segments = []
    for seg in segments_data:
        segments.append(
            SegmentInfo(
                id=seg.get("id", ""),
                name=seg.get("name", ""),
                description=seg.get("description"),
                rsid=seg.get("rsid"),
                reportSuiteName=seg.get("reportSuiteName"),
                owner=seg.get("owner"),
                definition=seg.get("definition"),
                compatibility=seg.get("compatibility"),
                tags=seg.get("tags"),
                modified=seg.get("modified"),
                created=seg.get("created"),
            )
        )

    return SegmentListOutput(
        segments=segments,
        total_count=len(segments),
    )


async def get_segment_details_tool(
    client: CJAClient,
    input_data: GetSegmentDetailsInput,
) -> SegmentDetailsOutput:
    """Get detailed information about a specific segment.

    This tool retrieves complete details about a segment including its definition,
    which can be used to understand segment logic or as a template for creating
    similar segments.

    Args:
        client: CJA API client instance.
        input_data: Parameters for getting segment details.

    Returns:
        SegmentDetailsOutput: Complete segment information.

    Example:
        >>> input_data = GetSegmentDetailsInput(
        ...     segment_id="s300000022_5bb7c94e80f0073611afb35c",
        ...     expansion="definition,tags,compatibility"
        ... )
        >>> await get_segment_details_tool(client, input_data)
    """
    # Build query parameters
    params = {}
    if input_data.expansion:
        params["expansion"] = input_data.expansion

    # Call API
    response = await client.get_segment(
        segment_id=input_data.segment_id,
        params=params,
    )

    # Parse response
    segment = SegmentInfo(
        id=response.get("id", ""),
        name=response.get("name", ""),
        description=response.get("description"),
        rsid=response.get("rsid"),
        reportSuiteName=response.get("reportSuiteName"),
        owner=response.get("owner"),
        definition=response.get("definition"),
        compatibility=response.get("compatibility"),
        tags=response.get("tags"),
        modified=response.get("modified"),
        created=response.get("created"),
    )

    return SegmentDetailsOutput(segment=segment)


async def create_segment_tool(
    client: CJAClient,
    input_data: CreateSegmentInput,
) -> SegmentDetailsOutput:
    """Create a new segment in CJA.

    This tool creates a new segment/filter that can be used in reports and analysis.
    The segment definition uses a JSON structure to define rules and conditions.

    IMPORTANT: Segment definitions are complex. It's recommended to:
    1. Use the CJA UI to create a template segment
    2. Retrieve it via get_segment_details_tool to see the definition structure
    3. Modify the definition as needed
    4. Use validate_segment_tool before creating

    Args:
        client: CJA API client instance.
        input_data: Parameters for creating the segment.

    Returns:
        SegmentDetailsOutput: Created segment with assigned ID.

    Example:
        >>> # Simple segment for mobile users
        >>> definition = {
        ...     "func": "segment",
        ...     "version": [1, 0, 0],
        ...     "container": {
        ...         "func": "container",
        ...         "context": "hits",
        ...         "pred": {
        ...             "func": "exists",
        ...             "val": {
        ...                 "func": "attr",
        ...                 "name": "variables/mobiledevicetype"
        ...             }
        ...         }
        ...     }
        ... }
        >>> input_data = CreateSegmentInput(
        ...     name="Mobile Users",
        ...     description="Users on mobile devices",
        ...     definition=definition
        ... )
        >>> await create_segment_tool(client, input_data)
    """
    # Build segment data
    segment_data = {
        "name": input_data.name,
        "definition": input_data.definition,
    }

    if input_data.description:
        segment_data["description"] = input_data.description

    # Add data view ID - CJA API uses dataId, not rsid
    dataview_id = input_data.dataview_id or client.settings.adobe_data_view_id
    segment_data["dataId"] = dataview_id

    # Call API
    response = await client.create_segment(segment_data=segment_data)

    # Parse response
    segment = SegmentInfo(
        id=response.get("id", ""),
        name=response.get("name", ""),
        description=response.get("description"),
        rsid=response.get("rsid"),
        reportSuiteName=response.get("reportSuiteName"),
        owner=response.get("owner"),
        definition=response.get("definition"),
        compatibility=response.get("compatibility"),
        tags=response.get("tags"),
        modified=response.get("modified"),
        created=response.get("created"),
    )

    return SegmentDetailsOutput(segment=segment)


async def update_segment_tool(
    client: CJAClient,
    input_data: UpdateSegmentInput,
) -> SegmentDetailsOutput:
    """Update an existing segment.

    This tool updates a segment's name, description, or definition. The API supports
    partial updates, so you only need to provide the fields you want to change.

    Args:
        client: CJA API client instance.
        input_data: Parameters for updating the segment.

    Returns:
        SegmentDetailsOutput: Updated segment information.

    Example:
        >>> input_data = UpdateSegmentInput(
        ...     segment_id="s300000022_5bb7c94e80f0073611afb35c",
        ...     name="Updated Mobile Users",
        ...     description="Updated description"
        ... )
        >>> await update_segment_tool(client, input_data)
    """
    # Build update data (only include fields that are provided)
    segment_data = {}

    if input_data.name:
        segment_data["name"] = input_data.name
    if input_data.description is not None:  # Allow empty string
        segment_data["description"] = input_data.description
    if input_data.definition:
        segment_data["definition"] = input_data.definition

    # Call API
    response = await client.update_segment(
        segment_id=input_data.segment_id,
        segment_data=segment_data,
    )

    # Parse response
    segment = SegmentInfo(
        id=response.get("id", ""),
        name=response.get("name", ""),
        description=response.get("description"),
        rsid=response.get("rsid"),
        reportSuiteName=response.get("reportSuiteName"),
        owner=response.get("owner"),
        definition=response.get("definition"),
        compatibility=response.get("compatibility"),
        tags=response.get("tags"),
        modified=response.get("modified"),
        created=response.get("created"),
    )

    return SegmentDetailsOutput(segment=segment)


async def validate_segment_tool(
    client: CJAClient,
    input_data: ValidateSegmentInput,
) -> SegmentValidationOutput:
    """Validate a segment definition before creating or updating.

    This tool validates that a segment definition is syntactically correct and
    compatible with the specified data view. Use this before create_segment_tool
    to avoid errors.

    Args:
        client: CJA API client instance.
        input_data: Parameters for validating the segment.

    Returns:
        SegmentValidationOutput: Validation result and compatibility information.

    Example:
        >>> definition = {
        ...     "func": "segment",
        ...     "version": [1, 0, 0],
        ...     "container": {
        ...         "func": "container",
        ...         "context": "visits",
        ...         "pred": {
        ...             "func": "event-exists",
        ...             "evt": {
        ...                 "func": "event",
        ...                 "name": "metrics/visits"
        ...             }
        ...         }
        ...     }
        ... }
        >>> input_data = ValidateSegmentInput(definition=definition)
        >>> await validate_segment_tool(client, input_data)
    """
    # Call API
    response = await client.validate_segment(
        definition=input_data.definition,
        dataview_id=input_data.dataview_id,
    )

    # Parse response
    return SegmentValidationOutput(
        valid=response.get("valid", False),
        message=response.get("message", ""),
        supported_products=response.get("supported_products"),
        validator_version=response.get("validator_version"),
    )

"""MCP tools for CJA calculated metrics management (Phase 3)."""

from typing import Any

from adobe_cja_mcp.client.cja_client import CJAClient
from adobe_cja_mcp.models.schemas import (
    CalculatedMetricDetailsOutput,
    CalculatedMetricInfo,
    CalculatedMetricListOutput,
    CalculatedMetricValidationOutput,
    CreateCalculatedMetricInput,
    GetCalculatedMetricDetailsInput,
    ListCalculatedMetricsInput,
    UpdateCalculatedMetricInput,
    ValidateCalculatedMetricInput,
)


async def list_calculated_metrics_tool(
    client: CJAClient,
    input_data: ListCalculatedMetricsInput,
) -> CalculatedMetricListOutput:
    """List all calculated metrics available in CJA.

    This tool retrieves calculated metrics that can be used in reports and analysis.
    You can filter by name, tags, and data view.

    Args:
        client: CJA API client instance.
        input_data: Parameters for listing calculated metrics.

    Returns:
        CalculatedMetricListOutput: List of calculated metrics with metadata.

    Example:
        >>> input_data = ListCalculatedMetricsInput(
        ...     name="conversion",
        ...     expansion="definition,tags",
        ...     limit=20
        ... )
        >>> await list_calculated_metrics_tool(client, input_data)
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
    response = await client.list_calculated_metrics(
        dataview_id=input_data.dataview_id,
        params=params,
    )

    # Parse response - API returns paginated results with 'content' array
    metrics_data = response.get("content", [])

    metrics = []
    for metric in metrics_data:
        metrics.append(
            CalculatedMetricInfo(
                id=metric.get("id", ""),
                name=metric.get("name", ""),
                description=metric.get("description"),
                data_id=metric.get("dataId"),
                owner=metric.get("owner"),
                type=metric.get("type"),
                polarity=metric.get("polarity"),
                precision=metric.get("precision"),
                definition=metric.get("definition"),
                tags=metric.get("tags"),
                compatibility=metric.get("compatibility"),
                modified=metric.get("modified"),
                created=metric.get("created"),
            )
        )

    return CalculatedMetricListOutput(
        metrics=metrics,
        total_count=response.get("totalElements", len(metrics)),
    )


async def get_calculated_metric_details_tool(
    client: CJAClient,
    input_data: GetCalculatedMetricDetailsInput,
) -> CalculatedMetricDetailsOutput:
    """Get detailed information about a specific calculated metric.

    This tool retrieves complete details about a calculated metric including its
    definition/formula, which can be used to understand the metric logic or as
    a template for creating similar metrics.

    Args:
        client: CJA API client instance.
        input_data: Parameters for getting calculated metric details.

    Returns:
        CalculatedMetricDetailsOutput: Complete calculated metric information.

    Example:
        >>> input_data = GetCalculatedMetricDetailsInput(
        ...     metric_id="a5066209",
        ...     expansion="definition,tags,compatibility"
        ... )
        >>> await get_calculated_metric_details_tool(client, input_data)
    """
    # Build query parameters
    params = {}
    if input_data.expansion:
        params["expansion"] = input_data.expansion

    # Call API
    response = await client.get_calculated_metric(
        metric_id=input_data.metric_id,
        params=params,
    )

    # Parse response
    metric = CalculatedMetricInfo(
        id=response.get("id", ""),
        name=response.get("name", ""),
        description=response.get("description"),
        data_id=response.get("dataId"),
        owner=response.get("owner"),
        type=response.get("type"),
        polarity=response.get("polarity"),
        precision=response.get("precision"),
        definition=response.get("definition"),
        tags=response.get("tags"),
        compatibility=response.get("compatibility"),
        modified=response.get("modified"),
        created=response.get("created"),
    )

    return CalculatedMetricDetailsOutput(metric=metric)


async def create_calculated_metric_tool(
    client: CJAClient,
    input_data: CreateCalculatedMetricInput,
) -> CalculatedMetricDetailsOutput:
    """Create a new calculated metric in CJA.

    This tool creates a new calculated metric that can be used in reports and analysis.
    The metric definition uses a JSON structure to define formulas and functions.

    IMPORTANT: Calculated metric definitions are complex. It's recommended to:
    1. Use the CJA UI to create a template metric
    2. Retrieve it via get_calculated_metric_details_tool to see the definition structure
    3. Modify the definition as needed
    4. Use validate_calculated_metric_tool before creating

    Args:
        client: CJA API client instance.
        input_data: Parameters for creating the calculated metric.

    Returns:
        CalculatedMetricDetailsOutput: Created metric with assigned ID.

    Example:
        >>> # Simple calculated metric: visits / visitors
        >>> definition = {
        ...     "func": "calc-metric",
        ...     "formula": {
        ...         "func": "divide",
        ...         "col1": {
        ...             "func": "metric",
        ...             "name": "metrics/visits"
        ...         },
        ...         "col2": {
        ...             "func": "metric",
        ...             "name": "metrics/visitors"
        ...         }
        ...     },
        ...     "version": [1, 0, 0]
        ... }
        >>> input_data = CreateCalculatedMetricInput(
        ...     name="Visits per Visitor",
        ...     description="Average visits per visitor",
        ...     type="decimal",
        ...     definition=definition
        ... )
        >>> await create_calculated_metric_tool(client, input_data)
    """
    # Build metric data
    metric_data = {
        "name": input_data.name,
        "type": input_data.type,
        "definition": input_data.definition,
    }

    if input_data.description:
        metric_data["description"] = input_data.description
    if input_data.polarity:
        metric_data["polarity"] = input_data.polarity
    if input_data.precision is not None:
        metric_data["precision"] = input_data.precision

    # Add data view ID - CJA API uses dataId
    dataview_id = input_data.dataview_id or client.settings.adobe_data_view_id
    metric_data["dataId"] = dataview_id

    # Call API
    response = await client.create_calculated_metric(metric_data=metric_data)

    # Parse response
    metric = CalculatedMetricInfo(
        id=response.get("id", ""),
        name=response.get("name", ""),
        description=response.get("description"),
        data_id=response.get("dataId"),
        owner=response.get("owner"),
        type=response.get("type"),
        polarity=response.get("polarity"),
        precision=response.get("precision"),
        definition=response.get("definition"),
        tags=response.get("tags"),
        compatibility=response.get("compatibility"),
        modified=response.get("modified"),
        created=response.get("created"),
    )

    return CalculatedMetricDetailsOutput(metric=metric)


async def update_calculated_metric_tool(
    client: CJAClient,
    input_data: UpdateCalculatedMetricInput,
) -> CalculatedMetricDetailsOutput:
    """Update an existing calculated metric.

    This tool updates a calculated metric's name, description, type, or definition.
    The API supports partial updates, so you only need to provide the fields you
    want to change.

    Args:
        client: CJA API client instance.
        input_data: Parameters for updating the calculated metric.

    Returns:
        CalculatedMetricDetailsOutput: Updated calculated metric information.

    Example:
        >>> input_data = UpdateCalculatedMetricInput(
        ...     metric_id="a5066209",
        ...     name="Updated Conversion Rate",
        ...     description="Updated description"
        ... )
        >>> await update_calculated_metric_tool(client, input_data)
    """
    # Build update data (only include fields that are provided)
    metric_data = {}

    if input_data.name:
        metric_data["name"] = input_data.name
    if input_data.description is not None:  # Allow empty string
        metric_data["description"] = input_data.description
    if input_data.type:
        metric_data["type"] = input_data.type
    if input_data.polarity:
        metric_data["polarity"] = input_data.polarity
    if input_data.precision is not None:
        metric_data["precision"] = input_data.precision
    if input_data.definition:
        metric_data["definition"] = input_data.definition

    # Call API
    response = await client.update_calculated_metric(
        metric_id=input_data.metric_id,
        metric_data=metric_data,
    )

    # Parse response
    metric = CalculatedMetricInfo(
        id=response.get("id", ""),
        name=response.get("name", ""),
        description=response.get("description"),
        data_id=response.get("dataId"),
        owner=response.get("owner"),
        type=response.get("type"),
        polarity=response.get("polarity"),
        precision=response.get("precision"),
        definition=response.get("definition"),
        tags=response.get("tags"),
        compatibility=response.get("compatibility"),
        modified=response.get("modified"),
        created=response.get("created"),
    )

    return CalculatedMetricDetailsOutput(metric=metric)


async def validate_calculated_metric_tool(
    client: CJAClient,
    input_data: ValidateCalculatedMetricInput,
) -> CalculatedMetricValidationOutput:
    """Validate a calculated metric definition before creating or updating.

    This tool validates that a calculated metric definition is syntactically correct
    and compatible with the specified data view. Use this before create_calculated_metric_tool
    to avoid errors.

    Args:
        client: CJA API client instance.
        input_data: Parameters for validating the calculated metric.

    Returns:
        CalculatedMetricValidationOutput: Validation result with used metrics and functions.

    Example:
        >>> definition = {
        ...     "func": "calc-metric",
        ...     "formula": {
        ...         "func": "divide",
        ...         "col1": {
        ...             "func": "metric",
        ...             "name": "metrics/visits"
        ...         },
        ...         "col2": {
        ...             "func": "metric",
        ...             "name": "metrics/visitors"
        ...         }
        ...     },
        ...     "version": [1, 0, 0]
        ... }
        >>> input_data = ValidateCalculatedMetricInput(
        ...     name="Test Metric",
        ...     type="decimal",
        ...     definition=definition
        ... )
        >>> await validate_calculated_metric_tool(client, input_data)
    """
    # Call API
    response = await client.validate_calculated_metric(
        definition=input_data.definition,
        name=input_data.name,
        metric_type=input_data.type,
        dataview_id=input_data.dataview_id,
        description=input_data.description,
    )

    # Parse response
    return CalculatedMetricValidationOutput(
        valid=response.get("valid", False),
        identity_metrics=response.get("identityMetrics"),
        functions=response.get("functions"),
        supported_products=response.get("supported_products"),
        supported_schema=response.get("supported_schema"),
        validator_version=response.get("validator_version"),
    )

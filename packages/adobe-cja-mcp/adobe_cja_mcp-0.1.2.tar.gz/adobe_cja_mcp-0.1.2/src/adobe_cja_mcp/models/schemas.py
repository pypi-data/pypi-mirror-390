"""Pydantic models for CJA API requests and responses."""

from datetime import datetime
from typing import Any, Literal, Optional

from pydantic import BaseModel, Field


# Common Models

class DateRange(BaseModel):
    """Date range for report queries."""

    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )


class DimensionInfo(BaseModel):
    """Dimension metadata."""

    id: str = Field(..., description="Dimension ID")
    name: str = Field(..., description="Dimension display name")
    type: Optional[str] = Field(None, description="Dimension type")
    has_data: Optional[bool] = Field(None, alias="hasData", description="Whether dimension has data")


class MetricInfo(BaseModel):
    """Metric metadata."""

    id: str = Field(..., description="Metric ID")
    name: str = Field(..., description="Metric display name")
    type: Optional[str] = Field(None, description="Metric type")


# Tool Input Models

class ListDimensionsInput(BaseModel):
    """Input for listing dimensions."""

    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )
    expansion: Optional[str] = Field(
        None,
        description="Additional fields to include (e.g., 'tags,approved')",
    )


class ListMetricsInput(BaseModel):
    """Input for listing metrics."""

    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )
    expansion: Optional[str] = Field(
        None,
        description="Additional fields to include",
    )


class RunReportInput(BaseModel):
    """Input for running a CJA report."""

    dimension: str = Field(
        ...,
        description="Dimension ID to break down (e.g., 'variables/daterangeday', 'variables/page')",
    )
    metrics: list[str] = Field(
        ...,
        description="List of metric IDs (e.g., ['metrics/visits', 'metrics/pageviews'])",
        min_length=1,
    )
    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    limit: int = Field(
        default=10,
        description="Maximum number of dimension items to return",
        ge=1,
        le=50000,
    )
    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )


class GetTopItemsInput(BaseModel):
    """Input for getting top items for a dimension."""

    dimension: str = Field(
        ...,
        description="Dimension ID (e.g., 'variables/page', 'variables/product')",
    )
    metric: str = Field(
        ...,
        description="Metric ID to rank by (e.g., 'metrics/visits', 'metrics/revenue')",
    )
    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    limit: int = Field(
        default=10,
        description="Number of top items to return",
        ge=1,
        le=500,
    )
    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )


class GetDataViewInfoInput(BaseModel):
    """Input for getting data view information."""

    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )
    expansion: Optional[str] = Field(
        None,
        description="Additional fields to include (e.g., 'components')",
    )


class RunBreakdownReportInput(BaseModel):
    """Input for running a multi-dimensional breakdown report."""

    primary_dimension: str = Field(
        ...,
        description="Primary dimension ID (e.g., 'variables/page', 'variables/campaign')",
    )
    breakdown_dimension: str = Field(
        ...,
        description="Dimension to break down by (e.g., 'variables/devicetype', 'variables/browser')",
    )
    metrics: list[str] = Field(
        ...,
        description="List of metric IDs to analyze",
        min_length=1,
    )
    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    limit: int = Field(
        default=10,
        description="Maximum number of primary dimension items to return",
        ge=1,
        le=500,
    )
    breakdown_limit: int = Field(
        default=5,
        description="Maximum number of breakdown items per primary dimension item",
        ge=1,
        le=50,
    )
    segment_ids: Optional[list[str]] = Field(
        None,
        description="Optional list of segment IDs to filter the report",
    )
    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )


class RunTrendedReportInput(BaseModel):
    """Input for running a time-series trend report."""

    metrics: list[str] = Field(
        ...,
        description="List of metric IDs to trend over time",
        min_length=1,
    )
    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    granularity: Literal["hour", "day", "week", "month"] = Field(
        default="day",
        description="Time granularity for trending",
    )
    dimension: Optional[str] = Field(
        None,
        description="Optional dimension to break down the trend (e.g., 'variables/devicetype')",
    )
    dimension_limit: int = Field(
        default=5,
        description="Maximum number of dimension items if dimension is specified",
        ge=1,
        le=50,
    )
    segment_ids: Optional[list[str]] = Field(
        None,
        description="Optional list of segment IDs to filter the report",
    )
    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )


class SearchDimensionItemsInput(BaseModel):
    """Input for searching dimension values."""

    dimension: str = Field(
        ...,
        description="Dimension ID to search within (e.g., 'variables/page', 'variables/product')",
    )
    search_term: str = Field(
        ...,
        description="Search term to find matching dimension items",
        min_length=1,
    )
    start_date: Optional[str] = Field(
        None,
        description="Optional start date to scope search results (YYYY-MM-DD format)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    end_date: Optional[str] = Field(
        None,
        description="Optional end date to scope search results (YYYY-MM-DD format)",
        pattern=r"^\d{4}-\d{2}-\d{2}$",
    )
    limit: int = Field(
        default=100,
        description="Maximum number of matching items to return",
        ge=1,
        le=1000,
    )
    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )


# Tool Output Models

class DimensionListOutput(BaseModel):
    """Output for dimension list."""

    dimensions: list[DimensionInfo] = Field(..., description="List of dimensions")
    total_count: int = Field(..., description="Total number of dimensions")


class MetricListOutput(BaseModel):
    """Output for metric list."""

    metrics: list[MetricInfo] = Field(..., description="List of metrics")
    total_count: int = Field(..., description="Total number of metrics")


class ReportRow(BaseModel):
    """Single row in a report."""

    dimension_value: str = Field(..., description="Dimension item value")
    metric_values: dict[str, Any] = Field(..., description="Metric values for this dimension item")


class ReportOutput(BaseModel):
    """Output for report query."""

    dimension: str = Field(..., description="Dimension queried")
    date_range: dict[str, str] = Field(..., description="Date range of report")
    rows: list[ReportRow] = Field(..., description="Report data rows")
    total_rows: int = Field(..., description="Total number of rows returned")
    summary: dict[str, Any] = Field(default_factory=dict, description="Summary totals")


class DataViewOutput(BaseModel):
    """Output for data view information."""

    id: str = Field(..., description="Data view ID")
    name: str = Field(..., description="Data view name")
    description: Optional[str] = Field(None, description="Data view description")
    owner: Optional[dict[str, Any]] = Field(None, description="Owner information")
    created: Optional[str] = Field(None, description="Creation timestamp")
    modified: Optional[str] = Field(None, description="Last modified timestamp")
    components_count: Optional[int] = Field(None, description="Number of components")


class BreakdownItem(BaseModel):
    """Single breakdown item within a breakdown report."""

    breakdown_value: str = Field(..., description="Breakdown dimension item value")
    metric_values: dict[str, Any] = Field(..., description="Metric values for this breakdown item")


class BreakdownReportRow(BaseModel):
    """Single row in a breakdown report with nested breakdowns."""

    primary_value: str = Field(..., description="Primary dimension item value")
    primary_metrics: dict[str, Any] = Field(..., description="Metric values for primary dimension")
    breakdowns: list[BreakdownItem] = Field(..., description="Breakdown dimension items")


class BreakdownReportOutput(BaseModel):
    """Output for breakdown report."""

    primary_dimension: str = Field(..., description="Primary dimension queried")
    breakdown_dimension: str = Field(..., description="Breakdown dimension")
    date_range: dict[str, str] = Field(..., description="Date range of report")
    rows: list[BreakdownReportRow] = Field(..., description="Breakdown report rows")
    total_rows: int = Field(..., description="Total number of primary dimension rows")


class TrendDataPoint(BaseModel):
    """Single data point in a trended report."""

    timestamp: str = Field(..., description="Time period identifier")
    metric_values: dict[str, Any] = Field(..., description="Metric values for this time period")


class TrendedReportRow(BaseModel):
    """Single row in a trended report (one dimension item or total)."""

    dimension_value: Optional[str] = Field(None, description="Dimension item value (if dimension specified)")
    trend_data: list[TrendDataPoint] = Field(..., description="Time-series data points")


class TrendedReportOutput(BaseModel):
    """Output for trended report."""

    metrics: list[str] = Field(..., description="Metrics trended")
    date_range: dict[str, str] = Field(..., description="Date range of report")
    granularity: str = Field(..., description="Time granularity")
    dimension: Optional[str] = Field(None, description="Dimension broken down by (if any)")
    rows: list[TrendedReportRow] = Field(..., description="Trend data rows")
    total_data_points: int = Field(..., description="Total number of data points")


class DimensionItemMatch(BaseModel):
    """Single matching dimension item from search."""

    value: str = Field(..., description="Dimension item value")
    item_id: Optional[str] = Field(None, description="Item ID if available")


class SearchDimensionItemsOutput(BaseModel):
    """Output for dimension item search."""

    dimension: str = Field(..., description="Dimension searched")
    search_term: str = Field(..., description="Search term used")
    matches: list[DimensionItemMatch] = Field(..., description="Matching dimension items")
    total_matches: int = Field(..., description="Total number of matches found")


# Phase 2: Segment Management Schemas

class ListSegmentsInput(BaseModel):
    """Input for listing segments."""

    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID to filter segments (uses configured default if not provided)",
    )
    name: Optional[str] = Field(
        None,
        description="Filter segments by name (partial match)",
    )
    tag_names: Optional[str] = Field(
        None,
        description="Comma-delimited list of tag names to filter by",
    )
    include_type: Optional[str] = Field(
        None,
        description="Include additional segments: 'shared', 'all', 'templates'",
    )
    limit: int = Field(
        default=10,
        description="Number of results per page",
        ge=1,
        le=1000,
    )
    page: int = Field(
        default=0,
        description="Page number (0-indexed)",
        ge=0,
    )
    expansion: Optional[str] = Field(
        None,
        description="Comma-delimited list of additional fields: 'definition', 'tags', 'compatibility', 'ownerFullName'",
    )


class GetSegmentDetailsInput(BaseModel):
    """Input for getting segment details."""

    segment_id: str = Field(
        ...,
        description="Segment ID to retrieve",
    )
    expansion: Optional[str] = Field(
        None,
        description="Comma-delimited list of additional fields: 'definition', 'tags', 'compatibility'",
    )


class SegmentDefinition(BaseModel):
    """Segment definition structure."""

    func: str = Field(default="segment-def", description="Function type")
    version: list[int] = Field(default=[1, 0, 0], description="Definition version")
    container: dict[str, Any] = Field(..., description="Segment container with rules")


class CreateSegmentInput(BaseModel):
    """Input for creating a new segment."""

    name: str = Field(
        ...,
        description="Segment name",
        min_length=1,
        max_length=255,
    )
    description: Optional[str] = Field(
        None,
        description="Segment description",
    )
    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )
    definition: dict[str, Any] = Field(
        ...,
        description="Segment definition object with container and rules",
    )


class UpdateSegmentInput(BaseModel):
    """Input for updating an existing segment."""

    segment_id: str = Field(
        ...,
        description="Segment ID to update",
    )
    name: Optional[str] = Field(
        None,
        description="Updated segment name",
    )
    description: Optional[str] = Field(
        None,
        description="Updated segment description",
    )
    definition: Optional[dict[str, Any]] = Field(
        None,
        description="Updated segment definition",
    )


class ValidateSegmentInput(BaseModel):
    """Input for validating a segment definition."""

    definition: dict[str, Any] = Field(
        ...,
        description="Segment definition to validate",
    )
    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID to validate against (uses configured default if not provided)",
    )


class SegmentInfo(BaseModel):
    """Segment metadata and definition."""

    id: str = Field(..., description="Segment ID")
    name: str = Field(..., description="Segment name")
    description: Optional[str] = Field(None, description="Segment description")
    rsid: Optional[str] = Field(None, description="Data view ID")
    report_suite_name: Optional[str] = Field(None, alias="reportSuiteName", description="Data view name")
    owner: Optional[dict[str, Any]] = Field(None, description="Segment owner information")
    definition: Optional[dict[str, Any]] = Field(None, description="Segment definition")
    compatibility: Optional[dict[str, Any]] = Field(None, description="Compatibility information")
    tags: Optional[list[dict[str, Any]]] = Field(None, description="Associated tags")
    modified: Optional[str] = Field(None, description="Last modified timestamp")
    created: Optional[str] = Field(None, description="Creation timestamp")


class SegmentListOutput(BaseModel):
    """Output for segment list."""

    segments: list[SegmentInfo] = Field(..., description="List of segments")
    total_count: int = Field(..., description="Total number of segments")


class SegmentDetailsOutput(BaseModel):
    """Output for segment details."""

    segment: SegmentInfo = Field(..., description="Segment information and definition")


class SegmentValidationOutput(BaseModel):
    """Output for segment validation."""

    valid: bool = Field(..., description="Whether the segment definition is valid")
    message: str = Field(..., description="Validation message or error description")
    supported_products: Optional[list[str]] = Field(None, description="Supported CJA products")
    validator_version: Optional[str] = Field(None, description="Validator version")


# Phase 3: Calculated Metrics Schemas

class ListCalculatedMetricsInput(BaseModel):
    """Input for listing calculated metrics."""

    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID to filter calculated metrics (uses configured default if not provided)",
    )
    name: Optional[str] = Field(
        None,
        description="Filter calculated metrics by name (partial match)",
    )
    tag_names: Optional[str] = Field(
        None,
        description="Comma-delimited list of tag names to filter by",
    )
    include_type: Optional[str] = Field(
        None,
        description="Include additional metrics: 'shared', 'all', 'templates'",
    )
    limit: int = Field(
        default=10,
        description="Number of results per page",
        ge=1,
        le=1000,
    )
    page: int = Field(
        default=0,
        description="Page number (0-indexed)",
        ge=0,
    )
    expansion: Optional[str] = Field(
        None,
        description="Comma-delimited list of additional fields: 'definition', 'tags', 'usedIn', 'compatibility'",
    )


class GetCalculatedMetricDetailsInput(BaseModel):
    """Input for getting calculated metric details."""

    metric_id: str = Field(
        ...,
        description="Calculated metric ID to retrieve",
    )
    expansion: Optional[str] = Field(
        None,
        description="Comma-delimited list of additional fields: 'definition', 'tags', 'usedIn', 'compatibility'",
    )


class CreateCalculatedMetricInput(BaseModel):
    """Input for creating a new calculated metric."""

    name: str = Field(
        ...,
        description="Calculated metric name",
        min_length=1,
        max_length=255,
    )
    description: Optional[str] = Field(
        None,
        description="Calculated metric description",
    )
    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID (uses configured default if not provided)",
    )
    type: str = Field(
        default="decimal",
        description="Metric type: 'decimal', 'percent', 'currency', 'time'",
    )
    polarity: Optional[str] = Field(
        None,
        description="Polarity: 'positive' or 'negative' (indicates if higher is better or worse)",
    )
    precision: Optional[int] = Field(
        None,
        description="Decimal precision for display",
        ge=0,
        le=10,
    )
    definition: dict[str, Any] = Field(
        ...,
        description="Calculated metric definition with formula and functions",
    )


class UpdateCalculatedMetricInput(BaseModel):
    """Input for updating an existing calculated metric."""

    metric_id: str = Field(
        ...,
        description="Calculated metric ID to update",
    )
    name: Optional[str] = Field(
        None,
        description="Updated metric name",
    )
    description: Optional[str] = Field(
        None,
        description="Updated metric description",
    )
    type: Optional[str] = Field(
        None,
        description="Updated metric type: 'decimal', 'percent', 'currency', 'time'",
    )
    polarity: Optional[str] = Field(
        None,
        description="Updated polarity: 'positive' or 'negative'",
    )
    precision: Optional[int] = Field(
        None,
        description="Updated decimal precision",
        ge=0,
        le=10,
    )
    definition: Optional[dict[str, Any]] = Field(
        None,
        description="Updated calculated metric definition",
    )


class ValidateCalculatedMetricInput(BaseModel):
    """Input for validating a calculated metric definition."""

    definition: dict[str, Any] = Field(
        ...,
        description="Calculated metric definition to validate",
    )
    name: str = Field(
        ...,
        description="Metric name for validation",
    )
    type: str = Field(
        default="decimal",
        description="Metric type: 'decimal', 'percent', 'currency', 'time'",
    )
    dataview_id: Optional[str] = Field(
        None,
        description="Data view ID to validate against (uses configured default if not provided)",
    )
    description: Optional[str] = Field(
        None,
        description="Optional metric description for validation",
    )


class CalculatedMetricInfo(BaseModel):
    """Calculated metric metadata and definition."""

    id: str = Field(..., description="Calculated metric ID")
    name: str = Field(..., description="Calculated metric name")
    description: Optional[str] = Field(None, description="Metric description")
    data_id: Optional[str] = Field(None, alias="dataId", description="Data view ID")
    owner: Optional[dict[str, Any]] = Field(None, description="Metric owner information")
    type: Optional[str] = Field(None, description="Metric type (decimal, percent, currency, time)")
    polarity: Optional[str] = Field(None, description="Polarity (positive or negative)")
    precision: Optional[int] = Field(None, description="Decimal precision")
    definition: Optional[dict[str, Any]] = Field(None, description="Metric definition with formula")
    tags: Optional[list[dict[str, Any]]] = Field(None, description="Associated tags")
    compatibility: Optional[dict[str, Any]] = Field(None, description="Compatibility information")
    modified: Optional[str] = Field(None, description="Last modified timestamp")
    created: Optional[str] = Field(None, description="Creation timestamp")


class CalculatedMetricListOutput(BaseModel):
    """Output for calculated metric list."""

    metrics: list[CalculatedMetricInfo] = Field(..., description="List of calculated metrics")
    total_count: int = Field(..., description="Total number of metrics")


class CalculatedMetricDetailsOutput(BaseModel):
    """Output for calculated metric details."""

    metric: CalculatedMetricInfo = Field(..., description="Calculated metric information and definition")


class CalculatedMetricValidationOutput(BaseModel):
    """Output for calculated metric validation."""

    valid: bool = Field(..., description="Whether the metric definition is valid")
    identity_metrics: Optional[list[dict[str, str]]] = Field(None, description="Metrics used in formula")
    functions: Optional[list[str]] = Field(None, description="Functions used in formula")
    supported_products: Optional[list[str]] = Field(None, description="Supported CJA products")
    supported_schema: Optional[list[str]] = Field(None, description="Supported schemas")
    validator_version: Optional[str] = Field(None, description="Validator version")

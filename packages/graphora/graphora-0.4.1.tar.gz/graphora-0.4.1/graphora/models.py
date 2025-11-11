"""
Graphora Models

Data models for the Graphora client library.
"""

from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal
from datetime import datetime, date
from decimal import Decimal

from pydantic import BaseModel, Field


class DocumentType(str, Enum):
    """Document types supported by Graphora."""

    PDF = "pdf"
    TXT = "txt"
    DOCX = "docx"
    MD = "md"
    CSV = "csv"
    JSON = "json"
    YAML = "yaml"
    XML = "xml"


class ProcessingPriority(str, Enum):
    """Processing priority levels for uploads."""

    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"


class DocumentMetadata(BaseModel):
    """Metadata for a document."""

    source: str
    document_type: DocumentType
    tags: List[str] = Field(default_factory=list)
    custom_metadata: Dict[str, Any] = Field(default_factory=dict)
    priority: ProcessingPriority = ProcessingPriority.NORMAL


class DocumentInfo(BaseModel):
    """Information about a document."""

    filename: str
    size: int
    document_type: DocumentType
    metadata: DocumentMetadata


class OntologyResponse(BaseModel):
    """Response from ontology validation."""
    id: str


class TransformationStage(str, Enum):
    """Stages of the transformation process."""

    UPLOAD = "upload"
    PARSE = "parse"
    CHUNK = "chunk"
    TRANSFORM = "transform"
    LOAD = "load"
    FAILED = "failed"


class StageStatus(str, Enum):
    """Status of a transformation stage."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class TransformRunStatus(str, Enum):
    """Overall status of a transform run."""

    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TransformFailureReason(str, Enum):
    """Normalized reasons for transform failure presented to clients."""

    QUALITY_GATE_FAILED = "quality_gate_failed"
    NO_GRAPH_GENERATED = "no_graph_generated"
    LLM_UNAVAILABLE = "llm_unavailable"
    PARSE_FAILED = "parse_failed"
    CHUNKING_FAILED = "chunking_failed"
    TRANSFORM_EXECUTION_FAILED = "transform_execution_failed"
    STORAGE_FAILED = "storage_failed"
    UNKNOWN_ERROR = "unknown_error"


class ResourceMetrics(BaseModel):
    """Resource usage metrics for a transformation."""

    cpu_usage_percent: float = Field(default=0.0, ge=0.0, le=100.0)
    memory_usage_mb: float = Field(default=0.0, ge=0.0)
    peak_memory_mb: float = Field(default=0.0, ge=0.0)
    disk_usage_mb: float = Field(default=0.0, ge=0.0)
    processing_time_ms: float = Field(default=0.0, ge=0.0)
    llm_tokens_used: int = Field(default=0, ge=0)
    api_calls_made: int = Field(default=0, ge=0)

    @property
    def memory_usage_gb(self) -> float:
        return self.memory_usage_mb / 1024

    @property
    def peak_memory_gb(self) -> float:
        return self.peak_memory_mb / 1024


class ErrorSummary(BaseModel):
    """Error details for a transformation stage."""

    stage: TransformationStage
    error_type: str
    error_message: str
    error_timestamp: datetime
    stack_trace: Optional[str] = None
    affected_components: List[str] = Field(default_factory=list)
    retry_count: int = Field(default=0, ge=0)
    is_recoverable: bool = True
    recovery_instructions: Optional[str] = None
    failure_code: Optional[str] = None
    details: Dict[str, Any] = Field(default_factory=dict)
    failure_reason: Optional[TransformFailureReason] = None


class StageProgress(BaseModel):
    """Progress information for a transformation stage."""

    stage: TransformationStage
    status: StageStatus
    percentage_complete: float = Field(default=0.0, ge=0.0, le=100.0)
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    items_total: Optional[int] = None
    items_processed: Optional[int] = None
    error_details: Optional[Dict[str, Any]] = None
    metrics: Dict[str, float] = Field(default_factory=dict)

    @property
    def duration_ms(self) -> Optional[float]:
        if not self.start_time:
            return None
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds() * 1000


class DetailedTransformStatus(BaseModel):
    """Detailed transformation status aligned with the API."""

    transform_id: str
    overall_status: TransformRunStatus
    current_stage: TransformationStage
    stages_progress: Dict[str, StageProgress]
    start_time: datetime
    estimated_completion_time: Optional[datetime] = None
    error_summary: Optional[ErrorSummary] = None
    resource_metrics: ResourceMetrics = Field(default_factory=ResourceMetrics)
    failure_code: Optional[str] = None
    failure_details: Dict[str, Any] = Field(default_factory=dict)
    failure_reason: Optional[TransformFailureReason] = None

    @property
    def percentage_complete(self) -> float:
        if not self.stages_progress:
            return 0.0
        total = sum(progress.percentage_complete for progress in self.stages_progress.values())
        return total / len(self.stages_progress)


# Backwards compatibility alias
TransformStatus = DetailedTransformStatus


class TransformResponse(BaseModel):
    """Response from document upload."""
    id: str
    upload_timestamp: datetime
    status: str
    document_info: DocumentInfo


class MergeState(str, Enum):
    STARTED = "started"
    AUTO_RESOLVE = "auto_resolve"
    HUMAN_REVIEW = "human_review"
    READY_TO_MERGE = "ready_to_merge"
    MERGE_IN_PROGRESS = "merge_in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    NOT_FOUND = "not_found"


class MergeInitResponse(BaseModel):
    merge_id: str
    status: MergeState
    start_time: datetime


class ResolutionStrategy(str, Enum):
    """Strategies for resolving merge conflicts."""

    KEEP_STAGING = "KEEP_STAGING"
    KEEP_PRODUCTION = "KEEP_PRODUCTION"
    MERGE_VALUES = "MERGE_VALUES"
    KEEP_BOTH = "KEEP_BOTH"


class ChangeLog(BaseModel):
    """Human review change log entry for merges."""

    id: str
    prop_changes: Dict[str, List[Any]]
    staging_node: Node
    prod_node: Node
    created_at: datetime
    need_human_review: bool = False
    match_confidence: Optional[float] = None
    match_strategy: Optional[str] = None


class Node(BaseModel):
    """A node in the graph."""

    id: str
    label: Optional[str] = None
    type: Optional[str] = None
    properties: Dict[str, Any] = Field(default_factory=dict)
    labels: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class Edge(BaseModel):
    """A relationship in the graph."""

    id: str
    type: str
    source: str
    target: str
    properties: Dict[str, Any] = Field(default_factory=dict)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class GraphResponse(BaseModel):
    """Response containing graph data."""

    nodes: List[Node] = Field(default_factory=list)
    edges: List[Edge] = Field(default_factory=list)
    total_nodes: Optional[int] = None
    total_edges: Optional[int] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class NodeCreation(BaseModel):
    id: str
    type: str
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class NodeUpdate(BaseModel):
    id: str
    properties: Dict[str, Optional[Any]]


class EdgeCreation(BaseModel):
    id: str
    source: str
    target: str
    type: str
    label: str
    properties: Dict[str, Any] = Field(default_factory=dict)


class EdgeUpdate(BaseModel):
    id: str
    properties: Dict[str, Optional[Any]]


class NodeChanges(BaseModel):
    created: List[NodeCreation] = Field(default_factory=list)
    updated: List[NodeUpdate] = Field(default_factory=list)
    deleted: List[str] = Field(default_factory=list)


class EdgeChanges(BaseModel):
    created: List[EdgeCreation] = Field(default_factory=list)
    updated: List[EdgeUpdate] = Field(default_factory=list)
    deleted: List[str] = Field(default_factory=list)


class SaveGraphRequest(BaseModel):
    nodes: Optional[NodeChanges] = None
    edges: Optional[EdgeChanges] = None


class Message(BaseModel):
    type: Literal["warning", "info"]
    message: str


class SaveGraphResponse(BaseModel):
    data: Dict[str, List[Dict[str, Any]]]
    messages: Optional[List[Message]] = None


# Quality Validation Models

class QualityRuleType(str, Enum):
    """Types of quality rules that can be applied."""
    FORMAT = "format"
    BUSINESS = "business"
    CROSS_ENTITY = "cross_entity"
    DISTRIBUTION = "distribution"
    CONSISTENCY = "consistency"


class QualitySeverity(str, Enum):
    """Severity levels for quality violations."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class QualityViolation(BaseModel):
    """Represents a single quality rule violation."""
    rule_id: str = Field(description="Unique identifier for the rule that was violated")
    rule_type: QualityRuleType = Field(description="Type of quality rule")
    severity: QualitySeverity = Field(description="Severity level of the violation")
    entity_type: Optional[str] = Field(None, description="Type of entity where violation occurred")
    entity_id: Optional[str] = Field(None, description="ID of the specific entity")
    property_name: Optional[str] = Field(None, description="Property name where violation occurred")
    relationship_type: Optional[str] = Field(None, description="Type of relationship if applicable")
    message: str = Field(description="Human-readable description of the violation")
    expected: str = Field(description="What was expected")
    actual: str = Field(description="What was actually found")
    confidence: float = Field(default=1.0, ge=0.0, le=1.0, description="Confidence in this violation detection")
    suggestion: Optional[str] = Field(None, description="Suggested fix for the violation")
    context: Dict[str, Any] = Field(default_factory=dict, description="Additional context for the violation")


class QualityMetrics(BaseModel):
    """Overall quality metrics for an extraction."""
    total_entities: int = Field(description="Total number of entities extracted")
    total_relationships: int = Field(description="Total number of relationships extracted")
    total_properties: int = Field(description="Total number of properties across all entities")
    entities_with_violations: int = Field(description="Number of entities that have violations")
    relationships_with_violations: int = Field(description="Number of relationships that have violations")
    total_violations: int = Field(description="Total number of violations found")
    entity_violation_rate: float = Field(description="Percentage of entities with violations")
    relationship_violation_rate: float = Field(description="Percentage of relationships with violations")
    overall_violation_rate: float = Field(description="Overall violation rate")
    avg_entity_confidence: float = Field(description="Average confidence score for entity extraction")
    avg_relationship_confidence: float = Field(description="Average confidence score for relationship extraction")
    confidence_scores_by_type: Dict[str, float] = Field(default_factory=dict, description="Average confidence by entity type")
    property_completeness_rate: float = Field(description="Percentage of required properties that were filled")
    entity_type_coverage: Dict[str, int] = Field(default_factory=dict, description="Count of entities by type")


class QualityResults(BaseModel):
    """Complete quality validation results for a transform."""
    transform_id: str = Field(description="ID of the transform that was validated")
    overall_score: float = Field(ge=0.0, le=100.0, description="Overall quality score (0-100)")
    grade: str = Field(description="Letter grade (A, B, C, D, F)")
    requires_review: bool = Field(description="Whether human review is required")
    violations: List[QualityViolation] = Field(default_factory=list, description="List of all violations found")
    metrics: QualityMetrics = Field(description="Overall quality metrics")
    violations_by_type: Dict[QualityRuleType, int] = Field(default_factory=dict, description="Violation count by rule type")
    violations_by_severity: Dict[QualitySeverity, int] = Field(default_factory=dict, description="Violation count by severity")
    violations_by_entity_type: Dict[str, int] = Field(default_factory=dict, description="Violation count by entity type")
    entity_quality_summary: Dict[str, Dict[str, int]] = Field(default_factory=dict, description="Quality summary by entity type")
    validation_timestamp: datetime = Field(description="When validation was performed")
    validation_duration_ms: int = Field(description="How long validation took in milliseconds")
    rules_applied: int = Field(description="Number of quality rules that were applied")
    validation_config: Dict[str, Any] = Field(default_factory=dict, description="Configuration used for validation")


class ApprovalRequest(BaseModel):
    """Request to approve quality results."""
    approval_comment: Optional[str] = Field(None, description="Optional comment about the approval")


class RejectQualityRequest(BaseModel):
    """Request to reject quality results."""
    rejection_reason: str = Field(description="Required reason for rejecting the quality results")


class QualityApprovalResponse(BaseModel):
    """Response from approving quality results."""
    message: str = Field(description="Success message")
    transform_id: str = Field(description="ID of the transform")
    status: str = Field(description="Approval status")


class QualityRejectionResponse(BaseModel):
    """Response from rejecting quality results."""
    message: str = Field(description="Success message")
    transform_id: str = Field(description="ID of the transform")
    status: str = Field(description="Rejection status")
    reason: str = Field(description="Reason for rejection")


class QualityViolationsResponse(BaseModel):
    """Response containing filtered quality violations."""
    transform_id: str = Field(description="ID of the transform")
    violations: List[QualityViolation] = Field(description="List of filtered violations")
    total_returned: int = Field(description="Number of violations returned")
    filters_applied: Dict[str, Optional[Union[str, QualityRuleType, QualitySeverity]]] = Field(
        description="Filters that were applied to the results"
    )


class QualitySummaryResponse(BaseModel):
    """Response containing quality summary for a user."""
    user_id: str = Field(description="User ID")
    recent_quality_results: List[Dict[str, Any]] = Field(description="List of recent quality result summaries")
    total_returned: int = Field(description="Number of results returned")


class QualityDeleteResponse(BaseModel):
    """Response from deleting quality results."""
    message: str = Field(description="Success message")
    transform_id: str = Field(description="ID of the transform")


class QualityHealthResponse(BaseModel):
    """Response from quality API health check."""
    status: str = Field(description="Health status (healthy/unavailable)")
    quality_api_available: bool = Field(description="Whether quality API is available")
    message: str = Field(description="Health status message")


class LLMUsageSummary(BaseModel):
    """Aggregated usage information per transform run."""

    total_calls: int = Field(description="Total number of LLM invocations")
    input_tokens: int = Field(description="Total input tokens consumed")
    output_tokens: int = Field(description="Total output tokens produced")
    total_tokens: int = Field(description="Sum of input and output tokens")
    estimated_cost_usd: Optional[float] = Field(
        default=None, description="Estimated total cost in USD"
    )
    models_used: List[str] = Field(
        default_factory=list, description="Distinct provider/model pairs used"
    )


class TransformRunSummary(BaseModel):
    """Summary of a transform run reported on the dashboard."""

    transform_id: str
    session_id: Optional[str] = None
    document_name: str
    document_type: str
    document_size_bytes: int
    page_count: int
    processing_status: str
    processing_started_at: datetime
    processing_completed_at: Optional[datetime] = None
    processing_duration_ms: Optional[int] = None
    chunks_created: int = 0
    nodes_extracted: int = 0
    relationships_extracted: int = 0
    quality_score: Optional[float] = None
    quality_gate_status: Optional[str] = None
    quality_requires_review: Optional[bool] = None
    quality_gate_reasons: List[str] = Field(default_factory=list)
    llm_usage: LLMUsageSummary = Field(default_factory=LLMUsageSummary)


class RecentRunsResponse(BaseModel):
    """Response payload for recent transform runs."""

    runs: List[TransformRunSummary]
    window_start: datetime
    window_end: datetime


class DashboardSummaryResponse(BaseModel):
    """Top-line KPI snapshot for the dashboard."""

    window_start: datetime
    window_end: datetime
    total_runs: int
    completed_runs: int
    failed_runs: int
    running_runs: int
    pass_count: int
    warn_count: int
    fail_count: int
    requires_review_count: int
    average_duration_ms: Optional[float]
    p50_duration_ms: Optional[float]
    p95_duration_ms: Optional[float]
    average_tokens_per_run: Optional[float]
    total_tokens: int
    total_llm_calls: int
    total_estimated_cost_usd: Optional[float]
    runs_per_day: Optional[float]
    recent_gate_reasons: List[str] = Field(default_factory=list)


class PerformanceTimeseriesPoint(BaseModel):
    """Daily performance metrics for dashboard charts."""

    date: date
    runs: int
    average_duration_ms: Optional[float]
    p95_duration_ms: Optional[float]
    total_tokens: int
    total_llm_calls: int
    total_estimated_cost_usd: Optional[float]


class DashboardPerformanceResponse(BaseModel):
    """Performance metrics across the requested window."""

    window_start: datetime
    window_end: datetime
    total_runs: int
    total_tokens: int
    total_llm_calls: int
    total_estimated_cost_usd: Optional[float]
    timeseries: List[PerformanceTimeseriesPoint]


class QualityReasonStat(BaseModel):
    reason: str
    count: int


class QualityRuleStat(BaseModel):
    rule_id: str
    severity: str
    count: int


class EntityCoverageStat(BaseModel):
    entity_type: str
    count: int


class EntityConfidenceStat(BaseModel):
    entity_type: str
    average_confidence: float


class DashboardQualityResponse(BaseModel):
    """Quality metrics aggregation for the dashboard."""

    window_start: datetime
    window_end: datetime
    average_score: Optional[float]
    p50_score: Optional[float]
    p95_score: Optional[float]
    pass_count: int
    warn_count: int
    fail_count: int
    requires_review_count: int
    recent_reasons: List[QualityReasonStat] = Field(default_factory=list)
    top_rules: List[QualityRuleStat] = Field(default_factory=list)
    entity_coverage: List[EntityCoverageStat] = Field(default_factory=list)
    entity_confidence: List[EntityConfidenceStat] = Field(default_factory=list)


# Configuration Models


class DatabaseConfig(BaseModel):
    id: Optional[str] = None
    name: str
    uri: str
    username: str
    password: str


class UserConfig(BaseModel):
    id: Optional[str] = None
    userId: str
    stagingDb: DatabaseConfig
    prodDb: DatabaseConfig
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None


class ConfigRequest(BaseModel):
    stagingDb: DatabaseConfig
    prodDb: DatabaseConfig


class ConnectionTestRequest(BaseModel):
    uri: str
    username: str
    password: str


class ConnectionTestResponse(BaseModel):
    success: bool
    message: str
    error: Optional[str] = None


# AI Configuration Models


class AIProvider(BaseModel):
    id: Optional[str] = None
    name: str
    display_name: str
    is_active: bool = True


class AIModel(BaseModel):
    id: Optional[str] = None
    provider_id: str
    name: str
    display_name: str
    version: Optional[str] = None
    is_active: bool = True


class GeminiConfigRequest(BaseModel):
    api_key: str
    default_model_name: str


class UserAIConfigDisplay(BaseModel):
    id: Optional[str] = None
    user_id: str
    provider_name: str
    provider_display_name: str
    api_key_masked: str
    default_model_name: str
    default_model_display_name: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


# Schema Generation & Storage Models


class QuestionType(str, Enum):
    TEXT = "text"
    SELECT = "select"
    MULTISELECT = "multiselect"
    FILE = "file"
    TEXTAREA = "textarea"


class Question(BaseModel):
    id: str
    type: QuestionType
    prompt: str
    required: bool = True
    options: Optional[List[str]] = None
    placeholder: Optional[str] = None
    help_text: Optional[str] = None
    validation: Optional[Dict[str, Any]] = None


class QuestionSet(BaseModel):
    id: str
    title: str
    description: str
    questions: List[Question]
    conditions: Optional[List[str]] = None


class UserResponse(BaseModel):
    question_id: str
    value: Union[str, List[str]]
    metadata: Optional[Dict[str, Any]] = None


class SchemaGenerationContext(BaseModel):
    domain: Optional[str] = None
    use_case: Optional[str] = None
    data_types: Optional[List[str]] = None
    complexity: Optional[str] = None
    scale: Optional[str] = None
    temporal_requirements: Optional[str] = None


class SchemaGenerationRequest(BaseModel):
    user_responses: List[UserResponse]
    context: Optional[SchemaGenerationContext] = None
    options: Optional[Dict[str, Any]] = None


class RelatedSchema(BaseModel):
    id: str
    title: str
    description: str
    similarity: float
    domain: str
    tags: List[str] = Field(default_factory=list)
    usage_count: int = 0


class SchemaGenerationResponse(BaseModel):
    id: str
    schema_content: str
    confidence: float
    related_schemas: Optional[List[RelatedSchema]] = None
    suggestions: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime


class SchemaSearchRequest(BaseModel):
    query: str
    domain: Optional[str] = None
    limit: int = 10
    threshold: float = 0.5
    include_content: bool = False


class SchemaSearchResult(BaseModel):
    id: str
    title: str
    description: str
    content: Optional[str] = None
    similarity: float
    domain: str
    tags: List[str] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime
    usage_count: int = 0
    user_id: str


class SchemaSearchResponse(BaseModel):
    results: List[SchemaSearchResult]
    total: int
    query: str
    took_ms: int


class StoredSchema(BaseModel):
    id: str
    title: str
    description: str
    content: str
    domain: str
    tags: List[str] = Field(default_factory=list)
    user_id: str
    is_public: bool = False
    usage_count: int = 0
    created_at: datetime
    updated_at: datetime


class CreateSchemaRequest(BaseModel):
    title: str
    description: str
    content: str
    domain: str
    tags: List[str] = Field(default_factory=list)
    is_public: bool = False


class UpdateSchemaRequest(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    content: Optional[str] = None
    domain: Optional[str] = None
    tags: Optional[List[str]] = None
    is_public: Optional[bool] = None


class QuestionConfigResponse(BaseModel):
    question_sets: List[QuestionSet]
    metadata: Optional[Dict[str, Any]] = None


class SchemaRefinementRequest(BaseModel):
    schema_id: str
    user_feedback: str
    current_schema: str
    context: Optional[Dict[str, Any]] = None


class SchemaRefinementResponse(BaseModel):
    refined_schema: str
    changes_made: List[str]
    confidence: float
    explanation: str


# Chunking Models


class ChunkingStrategy(str, Enum):
    SEMANTIC = "semantic"
    STRUCTURAL = "structural"
    HYBRID = "hybrid"
    RECURSIVE = "recursive"


class ChunkingConfig(BaseModel):
    strategy: ChunkingStrategy = ChunkingStrategy.HYBRID
    min_chunk_size: int = 500
    max_chunk_size: int = 6000
    semantic_threshold: float = 0.7
    semantic_min_length: int = 2000
    embedding_model: str = "sentence-transformers/all-mpnet-base-v2"
    preserve_lists: bool = True
    preserve_headings: bool = True
    preserve_quotes: bool = True
    chunk_overlap: int = 150
    force_strategy: bool = False
    quality_threshold: float = 0.6


class ChunkingTestRequest(BaseModel):
    text: str
    config: Optional[ChunkingConfig] = None
    strategy_override: Optional[ChunkingStrategy] = None


class ChunkingTestResponse(BaseModel):
    chunks: List[str]
    num_chunks: int
    total_tokens: int
    document_type: str
    strategy_used: str
    chunk_sizes: List[int]
    avg_chunk_size: float
    quality_scores: List[float]


# Usage & Pricing Models


class ModelProvider(str, Enum):
    GEMINI = "gemini"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    BAML = "other"


class ModelProviderSchema(BaseModel):
    id: Optional[str] = None
    provider_name: str
    display_name: str
    description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ModelPricingSchema(BaseModel):
    id: Optional[str] = None
    provider_id: str
    model_name: str
    model_version: Optional[str] = None
    input_price_per_1k_tokens: Decimal
    output_price_per_1k_tokens: Decimal
    model_context_window: Optional[int] = None
    model_description: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class UsageReport(BaseModel):
    user_id: str
    period_start: datetime
    period_end: datetime
    total_documents: int
    total_pages: int
    total_llm_calls: int
    total_tokens: int
    estimated_total_cost_usd: Decimal
    document_types: Dict[str, int]
    model_usage: Dict[str, Dict[str, Any]]
    daily_usage: List[Dict[str, Any]]
    avg_processing_time_ms: Optional[int] = None
    success_rate: Optional[Decimal] = None


class LimitCheckResult(BaseModel):
    within_limits: bool
    tier_name: str
    current_documents: int
    current_pages: int
    current_tokens: int
    current_cost_usd: Decimal
    document_limit: Optional[int] = None
    page_limit: Optional[int] = None
    token_limit: Optional[int] = None
    cost_limit_usd: Optional[Decimal] = None
    remaining_documents: Optional[int] = None
    remaining_pages: Optional[int] = None
    remaining_tokens: Optional[int] = None
    remaining_cost_usd: Optional[Decimal] = None
    warnings: List[str] = Field(default_factory=list)
    upgrade_recommended: bool = False

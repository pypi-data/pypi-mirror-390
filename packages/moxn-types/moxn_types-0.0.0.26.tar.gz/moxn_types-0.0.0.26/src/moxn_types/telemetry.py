from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING, Any, Generic, Literal, Optional, Protocol, TypeVar
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from moxn_types.base import MessageBase, RenderableModel
from moxn_types.content import Provider
from moxn_types.dto import MessageDTO
from moxn_types.response import ParsedResponseModelBase

# Import at runtime (not TYPE_CHECKING) since these are used in LLMEventModelBase fields
# Import will be deferred via string annotations to avoid circular dependency
if TYPE_CHECKING:
    from moxn_types.request_config import RequestConfig, SchemaDefinition


# Core Domain Types
class ResponseType(str, Enum):
    """Classification of LLM response types for observability and UI rendering."""

    TEXT = "text"  # Pure text completion, no tools/structure
    TOOL_CALLS = "tool_calls"  # One or more tool calls, no text
    TEXT_WITH_TOOLS = "text_with_tools"  # Text + tool calls mixed
    STRUCTURED = "structured"  # Structured generation (JSON schema output)
    STRUCTURED_WITH_TOOLS = "structured_with_tools"  # Structured + tools


# Event type constants (simple strings, not enums)
# These are used as the primary event classification
EVENT_TYPE_SPAN_START = "span_start"
EVENT_TYPE_SPAN_END = "span_end"
EVENT_TYPE_SPAN_ERROR = "span_error"
EVENT_TYPE_LLM_CALL = "llm_call"
EVENT_TYPE_TOOL_CALL = "tool_call"
EVENT_TYPE_VALIDATION = "validation"
EVENT_TYPE_CUSTOM = "custom"


class TelemetryLogRequest(BaseModel):
    """Unified telemetry log request matching backend telemetry_events table schema"""

    # Core identifiers
    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Event classification
    event_type: str  # "span_start", "span_end", "llm_call", etc.

    # Span relationship (required per backend schema - NOT NULL in DB)
    span_id: UUID
    root_span_id: UUID
    parent_span_id: UUID | None = None
    sequence_number: int | None = None

    # Context (gateway populates tenant_id, SDK populates rest)
    tenant_id: UUID | None = None  # Gateway enriches from request.state
    prompt_id: UUID
    task_id: UUID  # SDK gets from prompt.task_id
    commit_id: UUID | None = None  # One of commit_id or branch_id must be set
    branch_id: UUID | None = None

    # Metadata (always in Postgres, searchable)
    system_metadata: dict[str, Any] = Field(
        default_factory=dict, description="Moxn-generated system metadata"
    )
    user_metadata: dict[str, Any] = Field(
        default_factory=dict, description="User-provided searchable metadata"
    )

    # Content (can be delegated to storage if large)
    content: dict[str, Any] | None = None
    content_stored: bool = False
    content_storage_key: str | None = None

    @model_validator(mode="after")
    def validate_version_identifier(self):
        """Ensure exactly one of commit_id or branch_id is provided."""
        if not (bool(self.commit_id) ^ bool(self.branch_id)):
            raise ValueError(
                "Exactly one of commit_id or branch_id must be provided for telemetry"
            )
        return self


class TelemetryLogResponse(BaseModel):
    """Response from telemetry log endpoint"""

    id: UUID
    timestamp: datetime
    status: str = "success"


class ErrorResponse(BaseModel):
    """API error response model - standalone to avoid telemetry validation constraints"""

    id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "error"
    error_message: str
    details: dict[str, Any] = Field(default_factory=dict)


class Entity(BaseModel):
    entity_type: str
    entity_id: UUID
    entity_version_id: UUID | None = None


class SignedURLRequest(BaseModel):
    """Request to get a signed URL for storing large payload data"""

    id: UUID = Field(default_factory=uuid4)
    file_path: str
    entity: Entity | None = None
    log_request: TelemetryLogRequest
    media_type: Literal[
        "image/jpeg",
        "image/png",
        "image/gif",
        "image/webp",
        "application/pdf",
        "application/json",
    ]


class SignedURLResponse(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    url: str
    file_path: str
    expiration: datetime
    message: str = "Signed URL generated successfully"


MAX_INLINE_CONTENT_SIZE = 10 * 1024  # 10KB threshold for inline content


# Transport Protocol
class TelemetryTransport(Protocol):
    """Protocol for sending telemetry data"""

    async def send_log(self, log_request: TelemetryLogRequest) -> TelemetryLogResponse:
        """Send a telemetry log event"""
        ...

    async def send_telemetry_log_and_get_signed_url(
        self, log_request: SignedURLRequest
    ) -> SignedURLResponse:
        """Get a signed URL for storing large payload data"""
        ...


ParsedResponseT = TypeVar("ParsedResponseT", bound=ParsedResponseModelBase)
MessageT = TypeVar("MessageT", bound=MessageBase)


class LLMEventModelBase(BaseModel, Generic[ParsedResponseT, MessageT]):
    """Domain model for LLM interactions"""

    prompt_id: UUID = Field(..., alias="promptId")
    branch_id: UUID | None = Field(..., alias="branchId")
    commit_id: UUID | None = Field(
        ..., alias="commitId"
    )  # Changed from prompt_commit_id
    messages: list[MessageT] = Field(..., alias="messages")
    provider: Provider | None = Field(default=None, alias="provider")
    raw_response: dict[str, Any] = Field(..., alias="rawResponse")
    parsed_response: ParsedResponseT = Field(..., alias="parsedResponse")
    session_data: RenderableModel | None = Field(default=None, alias="sessionData")
    rendered_input: Optional[dict[str, Any]] = Field(
        default=None, alias="renderedInput"
    )
    attributes: Optional[dict[str, Any]] = Field(default=None, alias="attributes")
    is_uncommitted: bool = Field(
        default=False,
        alias="isUncommitted",
        description="True when prompt is from branch working state (commit_id is None)",
    )

    # Enhanced telemetry fields for function calling and structured generation
    response_type: ResponseType = Field(
        default=ResponseType.TEXT,
        alias="responseType",
        description="Classification of response type for observability",
    )
    request_config: Optional["RequestConfig"] = Field(
        default=None,
        alias="requestConfig",
        description="Provider-specific request configuration (tools, schemas, etc.)",
    )
    schema_definition: Optional["SchemaDefinition"] = Field(
        default=None,
        alias="schemaDefinition",
        description="Schema or tool definitions used in the request",
    )
    tool_calls_count: int = Field(
        default=0,
        alias="toolCallsCount",
        description="Number of parallel tool calls in the response",
    )
    validation_errors: Optional[list[str]] = Field(
        default=None,
        alias="validationErrors",
        description="Schema validation errors if any occurred",
    )

    @field_serializer("request_config", when_used="json")
    def serialize_request_config(
        self, value: Optional["RequestConfig"]
    ) -> Optional[dict[str, Any]]:
        """Serialize RequestConfig subclasses with all their provider-specific fields.

        Without this, Pydantic only serializes base RequestConfig fields,
        losing provider-specific fields like response_format, tools, etc.
        """
        if value is None:
            return None
        # Call model_dump on the actual subclass instance to get all fields
        return value.model_dump(mode="json", by_alias=True)

    @field_serializer("schema_definition", when_used="json")
    def serialize_schema_definition(
        self, value: Optional["SchemaDefinition"]
    ) -> Optional[dict[str, Any]]:
        """Serialize SchemaDefinition with proper field serializers applied."""
        if value is None:
            return None
        return value.model_dump(mode="json", by_alias=True)

    model_config = ConfigDict(
        arbitrary_types_allowed=True,
    )


class LLMEventModel(LLMEventModelBase[ParsedResponseModelBase, MessageDTO]):
    """Domain model for LLM interactions"""

    messages: list[MessageDTO] = Field(..., alias="messages")
    parsed_response: ParsedResponseModelBase = Field(..., alias="parsedResponse")

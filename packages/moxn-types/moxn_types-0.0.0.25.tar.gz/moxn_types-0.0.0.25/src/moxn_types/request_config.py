"""Request configuration models for capturing provider-specific LLM call parameters.

These models capture the configuration used when making requests to LLM providers,
enabling better observability and debugging of structured generation and tool calling.
"""

from typing import Any, Literal, Type

from pydantic import BaseModel, Field, field_serializer

from moxn_types.content import Provider


def _is_pydantic_model(obj: Any) -> bool:
    """Check if an object is a Pydantic model class (not instance)."""
    try:
        return isinstance(obj, type) and issubclass(obj, BaseModel)
    except TypeError:
        return False


def _convert_pydantic_to_schema(value: Any) -> Any:
    """Recursively convert Pydantic model classes to JSON schemas.

    Args:
        value: Any value that might contain Pydantic model classes

    Returns:
        The same value with all Pydantic model classes converted to JSON schemas
    """
    if value is None:
        return None

    # Handle Pydantic model class
    if _is_pydantic_model(value):
        return value.model_json_schema()

    # Handle dict (might contain nested Pydantic models)
    if isinstance(value, dict):
        return {k: _convert_pydantic_to_schema(v) for k, v in value.items()}

    # Handle list (might contain nested Pydantic models)
    if isinstance(value, list):
        return [_convert_pydantic_to_schema(item) for item in value]

    # Return as-is for other types
    return value


class RequestConfig(BaseModel):
    """Base configuration for all providers.

    Captures common parameters shared across LLM providers.
    """

    provider: Provider
    temperature: float | None = None
    max_tokens: int | None = None


class OpenAIChatRequestConfig(RequestConfig):
    """OpenAI Chat API specific configuration.

    Captures parameters specific to OpenAI's Chat Completions API,
    including structured outputs and function calling.
    """

    provider: Literal[Provider.OPENAI_CHAT] = Provider.OPENAI_CHAT
    response_format: dict[str, Any] | None = Field(
        default=None,
        description="Response format config: {type: 'json_object'} or {type: 'json_schema', json_schema: {...}}",
    )
    tools: list[dict[str, Any]] | None = Field(
        default=None, description="Tool/function definitions for function calling"
    )
    tool_choice: str | dict[str, Any] | None = Field(
        default=None,
        description="Tool choice: 'auto', 'none', 'required', or specific tool",
    )
    parallel_tool_calls: bool | None = Field(
        default=None, description="Whether to allow parallel tool calls"
    )

    @field_serializer("response_format")
    def serialize_response_format(
        self, value: dict[str, Any] | None
    ) -> dict[str, Any] | None:
        """Convert Pydantic models in response_format to JSON schemas."""
        return _convert_pydantic_to_schema(value)

    @field_serializer("tools")
    def serialize_tools(
        self, value: list[dict[str, Any]] | None
    ) -> list[dict[str, Any]] | None:
        """Convert Pydantic models in tool definitions to JSON schemas."""
        return _convert_pydantic_to_schema(value)


class OpenAIResponsesRequestConfig(RequestConfig):
    """OpenAI Responses API specific configuration.

    Captures parameters specific to OpenAI's Responses API,
    which uses items-based input/output model.
    """

    provider: Literal[Provider.OPENAI_RESPONSES] = Provider.OPENAI_RESPONSES
    tools: list[dict[str, Any]] | None = Field(
        default=None, description="Tool/function definitions for function calling"
    )
    tool_choice: str | dict[str, Any] | None = Field(
        default=None,
        description="Tool choice: 'auto', 'none', 'required', or specific tool",
    )
    parallel_tool_calls: bool | None = Field(
        default=None, description="Whether to allow parallel tool calls"
    )

    @field_serializer("tools")
    def serialize_tools(
        self, value: list[dict[str, Any]] | None
    ) -> list[dict[str, Any]] | None:
        """Convert Pydantic models in tool definitions to JSON schemas."""
        return _convert_pydantic_to_schema(value)


class AnthropicRequestConfig(RequestConfig):
    """Anthropic Claude specific configuration.

    Captures parameters specific to Anthropic's Messages API,
    including tool use for both function calling and structured generation.
    """

    provider: Literal[Provider.ANTHROPIC] = Provider.ANTHROPIC
    tools: list[dict[str, Any]] | None = Field(
        default=None,
        description="Tool definitions for both tool use and structured generation",
    )
    tool_choice: dict[str, Any] | None = Field(
        default=None, description="Tool choice: {type: 'auto'|'any'|'tool', name: ...}"
    )

    @field_serializer("tools")
    def serialize_tools(
        self, value: list[dict[str, Any]] | None
    ) -> list[dict[str, Any]] | None:
        """Convert Pydantic models in tool definitions to JSON schemas."""
        return _convert_pydantic_to_schema(value)


class GoogleRequestConfig(RequestConfig):
    """Google Gemini/Vertex specific configuration.

    Captures parameters specific to Google's generative AI APIs,
    including native structured generation via response_schema.
    """

    provider: Literal[Provider.GOOGLE_GEMINI, Provider.GOOGLE_VERTEX]
    response_schema: dict[str, Any] | Type[BaseModel] | None = Field(
        default=None,
        description="OpenAPI 3.0 schema for structured generation (dict or Pydantic model)",
    )
    response_mime_type: str | None = Field(
        default=None, description="MIME type for response (e.g., 'application/json')"
    )
    function_declarations: list[dict[str, Any]] | None = Field(
        default=None, description="Function declarations for function calling"
    )
    tool_config: dict[str, Any] | None = Field(
        default=None, description="Tool configuration (mode, allowed_functions, etc.)"
    )

    @field_serializer("response_schema")
    def serialize_response_schema(
        self, value: dict[str, Any] | Type[BaseModel] | None
    ) -> dict[str, Any] | None:
        """Convert Pydantic models in response_schema to JSON schemas."""
        return _convert_pydantic_to_schema(value)

    @field_serializer("function_declarations")
    def serialize_function_declarations(
        self, value: list[dict[str, Any]] | None
    ) -> list[dict[str, Any]] | None:
        """Convert Pydantic models in function declarations to JSON schemas."""
        return _convert_pydantic_to_schema(value)


class SchemaDefinition(BaseModel):
    """Captures schema/model used for structured generation or tool definitions.

    This model stores the actual schema or tool definitions used in a request,
    enabling traceability and debugging of structured generation and function calling.
    """

    definition_type: Literal[
        "json_schema", "pydantic", "tools", "functions", "response_schema"
    ]
    definition: dict[str, Any] | list[dict[str, Any]] | Type[BaseModel] = Field(
        description="The actual JSON Schema, tool definitions, or response schema (dict/list for JSON schema, or Pydantic model class)"
    )
    pydantic_model_name: str | None = Field(
        default=None, description="Name of the Pydantic model if one was used"
    )
    is_structured_output: bool = Field(
        default=False,
        description="True if used for structured generation, False if used for tools/functions",
    )

    @field_serializer("definition")
    def serialize_definition(
        self, value: dict[str, Any] | list[dict[str, Any]] | Type[BaseModel]
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Convert Pydantic models in definition to JSON schemas."""
        return _convert_pydantic_to_schema(value)

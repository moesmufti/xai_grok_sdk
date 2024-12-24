"""Data models for XAI API interactions."""

from typing import List, Dict, Any, Optional, Union, Literal
from dataclasses import dataclass


# Supported xAI models
ModelType = Literal["grok-2-1212", "grok-beta"]


@dataclass
class ChatCompletionRequest:
    """Request structure for chat completions API."""

    messages: List[
        Dict[str, Any]
    ]  # Required: List of messages in the chat conversation
    model: str  # Required: Model name to use

    # Optional parameters with defaults
    frequency_penalty: Optional[float]  # Range: -2.0 to 2.0
    logit_bias: Optional[Dict[Any, Any]]
    logprobs: Optional[bool]  # Whether to return log probabilities
    max_tokens: Optional[int]  # Maximum tokens to generate
    n: Optional[int]  # Number of chat completion choices
    presence_penalty: Optional[float]  # Range: -2.0 to 2.0
    response_format: Optional[Any]
    seed: Optional[int]  # For deterministic sampling
    stop: Optional[List[Any]]  # Up to 4 sequences to stop generation
    stream: Optional[bool]  # Whether to stream partial message deltas
    stream_options: Optional[Any]
    temperature: Optional[float]  # Range: 0 to 2
    tool_choice: Optional[Union[str, Dict[str, Any]]]
    tools: Optional[List[Dict[str, Any]]]  # List of available tools
    top_logprobs: Optional[int]  # Range: 0 to 20
    top_p: Optional[float]  # Range: 0 to 1
    user: Optional[str]  # Unique end-user identifier

    def __post_init__(self):
        """Validate and normalize the request parameters."""
        if not self.messages:
            raise ValueError("messages is required and cannot be empty")
        if not self.model:
            raise ValueError("model is required and cannot be empty")

        # Initialize defaults if None
        self.logit_bias = self.logit_bias or {}
        self.stop = self.stop or []
        self.tools = self.tools or []
        if not self.tools:
            self.tool_choice = None

        # Clamp values to their valid ranges
        if self.frequency_penalty:
            self.frequency_penalty = max(-2.0, min(2.0, self.frequency_penalty))
        if self.presence_penalty:
            self.presence_penalty = max(-2.0, min(2.0, self.presence_penalty))
        if self.temperature:
            self.temperature = max(0.0, min(2.0, self.temperature))
        if self.top_p:
            self.top_p = max(0.0, min(1.0, self.top_p))
        if self.top_logprobs:
            self.top_logprobs = max(0, min(20, self.top_logprobs))

        # Ensure stop sequences don't exceed limit
        if len(self.stop) > 4:
            self.stop = self.stop[:4]


@dataclass
class Function:
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolCall:
    """Represents a tool call in the chat completion response."""

    id: str
    function: Function
    type: str


@dataclass
class ToolResult:
    """Represents a tool result in the chat completion response."""

    tool_call_id: str
    role: str
    name: str
    content: Any


@dataclass
class Message:
    """Represents a message in the chat completion response."""

    role: str
    content: str
    tool_calls: Optional[List[ToolCall]] = None
    tool_results: Optional[List[ToolResult]] = None
    refusal: Optional[Any] = None


@dataclass
class Usage:
    """Usage information for the API response."""

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int
    prompt_tokens_details: Optional[Dict[str, Any]]


@dataclass
class Choice:
    """Represents a single completion choice in the API response."""

    index: int
    message: Optional[Message] = None
    delta: Optional[Message] = None
    finish_reason: Optional[str] = None
    logprobs: Optional[Dict[str, Any]] = None


@dataclass
class ChatCompletionResponse:
    """Response structure for chat completions API."""

    id: str
    choices: List[Choice]
    created: Optional[int] = None
    model: Optional[str] = None
    object: Optional[str] = None
    system_fingerprint: Optional[str] = None
    usage: Optional[Usage] = None

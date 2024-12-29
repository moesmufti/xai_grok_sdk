# xAI Grok SDK

A lightweight Python SDK for interacting with the xAI API, designed with minimal dependencies. All you need is your xAI API key and the model you want to use.

You can get your API key [here](https://console.x.ai/). Currently, they provide $25 free credits for new users for December 2024!

## Installation

```bash
pip install xai-grok-sdk
```

## Features

- Simple and intuitive interface for xAI API interactions
- Support for chat completions with the latest xAI models
- Built-in function calling capabilities with support for auto, required, and none modes
- Streaming support for real-time responses
- Minimal dependencies (only requires `requests`)
- Secure API key handling
- Customizable base URL for API endpoints
- Comprehensive error handling for API responses

## Supported Models

Currently, the following text-only models are supported:

- `grok-2-1212`
- `grok-beta`

## Roadmap

The following features are planned for future releases:

- **Multimodal Support**: Adding support for image and other media types as xAI releases multimodal capabilities for their models
- **Streaming Tool Call Support**: Enhancing the streaming functionality to support real-time tool/function calling responses

## Quick Start

```python
from xai_grok_sdk import XAI

# Initialize the client
xai = XAI(
    api_key="your_api_key",  # Required
    model="grok-2-1212"      # Required - must be one of the supported models
)

# Basic chat completion
response = xai.invoke(
    messages=[
        {"role": "user", "content": "Hello, what can you help me with today?"}
    ]
)

response_message = response.choices[0].message
print(response_message)
# Response: Message(role='assistant', content="Hello! I can help you with a wide range of tasks and questions. Whether you need assistance with information, problem-solving, learning something new, or just want to have a conversation, I'm here to help. What specifically would you like assistance with today?", tool_calls=None, tool_results=None, refusal=None)
```

### Streaming Support

The SDK supports streaming responses for real-time output. Here's how to use it:

```python
from xai_grok_sdk import XAI

# Initialize the client (do not provide tools when using streaming)
llm = XAI(
    api_key="your_api_key",
    model="grok-2-1212"
)

# Make a streaming request
response = llm.invoke(
    messages=[
        {"role": "user", "content": "Tell me a story about a brave astronaut."}
    ],
    stream=True
)

# Process the streaming response
for chunk in response:
    if chunk.choices[0].delta and chunk.choices[0].delta.content:
        print(chunk.choices[0].delta.content, end="", flush=True)
print()  # New line at the end
```

> **Important Streaming Notes**:
>
> - Streaming mode currently does not support response formats or tool calling. These features are only available in non-streaming mode.
> - When using streaming:
>   - Do not provide tools during XAI initialization
>   - Set `tool_choice="none"` in the invoke call, or omit it entirely
>   - The response will be a generator yielding chunks with `delta` content
>   - Each chunk follows the same structure as a normal response, but uses the `delta` field instead of `message`

## Parameters

### Required Parameters

#### Initialization

- `api_key` (str): Your xAI API key
- `model` (str): Model to use. Must be one of: "grok-2-1212", "grok-beta"

#### Invoke Method

- `messages` (List[Dict[str, Any]]): List of conversation messages

### Optional Parameters

The `invoke` method supports various optional parameters to customize the model's behavior. Some commonly used parameters include `max_tokens` to limit response length, `tool_choice` to control function calling behavior ('auto', 'required', 'none'), and others. For a complete list of optional parameters and their descriptions, see the [API Reference](#api-reference) section.

## Function (Tool) Calling

The SDK supports function calling through tools and function implementations. When using function calling, you need to provide both the tool definitions and their implementations through the `function_map` parameter.

Here's a complete example:

```python
from xai_grok_sdk import XAI

# Define your tools
tools = [
    {
        "name": "get_weather",
        "description": "Get the weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g., San Francisco, CA",
                }
            },
            "required": ["location"],
        },
    }
]

# Implement the tool function
def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny."

# Initialize the client with tools and function implementations
llm = XAI(
    api_key=api_key,
    model="grok-2-1212",
    tools=tools,
    function_map={"get_weather": get_weather}
)

# Make a request that will use function calling
response = llm.invoke(
    messages=[
        {"role": "user", "content": "What is the weather in San Francisco?"},
    ],
    tool_choice="auto"  # Can be "auto", "required", or "none"
)

response_message = response.choices[0].message
print(response_message)
# Response: Message(role='assistant', content='I am retrieving the weather for San Francisco.', tool_calls=[{'id': '0', 'function': {'name': 'get_weather', 'arguments': '{"location":"San Francisco, CA"}'}, 'type': 'function'}], tool_results=[{'tool_call_id': '0', 'role': 'tool', 'name': 'get_weather', 'content': 'The weather in San Francisco, CA is sunny.'}], refusal=None)

tool_result_content = response_message.tool_results[0].content
print(tool_result_content)
# Response: The weather in San Francisco, CA is sunny.
```

The SDK supports various function calling modes through the `tool_choice` parameter:

- `"auto"`: The model decides whether to call functions
- `"none"`: Function calling is disabled
- `"required"`: The model must call a function
- Specific function: Force the model to call a particular function using:
  ```python
  tool_choice={"type": "function", "function": {"name": "function_name"}}
  ```

For more details, see the [xAI Function Calling Guide](https://docs.x.ai/docs/guides/function-calling) and the [API Reference](https://docs.x.ai/api/endpoints#chat-completions).

### Required Parameters for Function Calling

When using function calling, you need to provide:

- `tools`: List of tool definitions with their schemas

### Function Map

The `function_map` optional parameter maps tool names to their Python implementations. This allows you to actually invoke the function and append its result to the response. Each function in the map must:

- Have a name matching a tool definition
- Accept the parameters specified in the tool's JSON Schema
- Return a value that can be converted to a string

> **Note**: The `function_map` parameter is not required when tools are provided. However, when omitted, only the tool call with the parameters used by the model will be included in the response.

## Structured JSON Output

The SDK supports structured JSON output through the `response_format` parameter. This allows you to enforce a specific JSON schema for the model's responses, making them more predictable and easier to parse.

Here's an example:

```python
from xai_grok_sdk import XAI

llm = XAI(
    api_key=api_key,
    model="grok-2-1212",
)

# Request with structured JSON output
response = llm.invoke(
    messages=[
        {"role": "user", "content": "What is the weather in San Francisco?"},
    ],
    tool_choice="none",
    response_format={
        "type": "json_schema",
        "json_schema": {
            "name": "weather_response",
            "schema": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "weather": {"type": "string"},
                },
                "required": ["location", "weather"],
                "additionalProperties": False,
            },
            "strict": True,
        },
    },
)

response_message = response.choices[0].message
print(response_message)
```

The response will be a JSON object that strictly follows the defined schema. For more advanced schema options, including Pydantic types and formats, refer to the [xAI API documentation on structured outputs](https://docs.x.ai/docs/guides/structured-outputs).

## API Reference

### XAI Class

The main class for interacting with the xAI API.

#### Constructor Parameters

- `api_key` (str, required): Your xAI API key
- `model` (ModelType, required): Model to use ("grok-2-1212" or "grok-beta")
- `tools` (List[Dict[str, Any]], optional): List of available tools (should not be provided if stream is set to True upon invoking the model)
- `function_map` (Dict[str, Callable], optional): Map of function names to implementations

#### Methods

##### invoke

Makes a chat completion request to the xAI API.

```python
def invoke(
    messages: List[Dict[str, Any]], # REQUIRED
    frequency_penalty: Optional[float] = None,  # Range: -2.0 to 2.0
    logit_bias: Optional[Dict[Any, Any]] = None,
    logprobs: Optional[bool] = None,
    max_tokens: Optional[int] = None,
    n: Optional[int] = None,
    presence_penalty: Optional[float] = None,  # Range: -2.0 to 2.0
    response_format: Optional[Any] = None,  # Not supported in streaming mode
    seed: Optional[int] = None,
    stop: Optional[List[Any]] = None,
    stream: Optional[bool] = None,  # Set to True for streaming responses
    stream_options: Optional[Any] = None,
    temperature: Optional[float] = None,  # Range: 0 to 2
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None, # "auto", "required", "none", or specific function. Should not be provided if stream is set to True (or set to "none")
    top_logprobs: Optional[int] = None,  # Range: 0 to 20
    top_p: Optional[float] = None,  # Range: 0 to 1
    user: Optional[str] = None
) -> Union[ChatCompletionResponse, Generator[ChatCompletionResponse, None, None]]
```

Returns either:

- A `ChatCompletionResponse` for normal requests
- A generator yielding `ChatCompletionResponse` objects for streaming requests, where each chunk contains delta content

#### Invoke Method Optional Parameters

The `invoke` method supports the following optional parameters:

- `frequency_penalty` (float, default=0): Penalty for token frequency. Higher values decrease the model's likelihood to repeat the same information.
- `logit_bias` (Dict[Any, Any], default=None): Token bias dictionary to influence token selection.
- `logprobs` (bool, default=False): Whether to return log probabilities of the output tokens.
- `max_tokens` (int, default=0): Maximum number of tokens to generate in the response.
- `n` (int, default=0): Number of chat completion choices to generate.
- `presence_penalty` (float, default=0): Penalty for token presence. Higher values increase the model's likelihood to talk about new topics.
- `response_format` (Dict[str, str], default=None): Format specification for the response output.
- `seed` (int, default=0): Random seed for deterministic outputs.
- `stop` (Union[str, List[str]], default=None): Sequences where the model should stop generating.
- `stream` (bool, default=False): Whether to stream the response tokens as they're generated.
- `stream_options` (Dict[str, Any], default=None): Additional options for streaming responses.
- `temperature` (float, default=0): Sampling temperature. Higher values make output more random.
- `tool_choice` (Union[str, Dict[str, Any]], default=None): Function calling mode ('auto', 'required', 'none', or specific function).
- `top_logprobs` (int, default=0): Number of most likely tokens to return probabilities for.
- `top_p` (float, default=0): Top-p sampling parameter. Lower values make output more focused.
- `user` (str, default=""): End-user identifier for monitoring and rate limiting.

### Response Models

The SDK uses several dataclasses to represent the API response structure:

#### ChatCompletionResponse

```python
@dataclass
class ChatCompletionResponse:
    id: str                                  # Unique identifier for the completion
    choices: List[Choice]                    # List of completion choices
    created: Optional[int] = None            # Unix timestamp of creation
    model: Optional[str] = None              # Model used for completion
    object: Optional[str] = None             # Object type, typically "chat.completion"
    system_fingerprint: Optional[str] = None # System fingerprint for the response
    usage: Optional[Usage] = None            # Token usage statistics
```

#### Choice

```python
@dataclass
class Choice:
    index: int                              # Index of the choice
    message: Optional[Message] = None        # Message content for non-streaming responses
    delta: Optional[Message] = None          # Delta content for streaming responses
    finish_reason: Optional[str] = None      # Reason for completion
    logprobs: Optional[Dict[str, Any]] = None # Log probabilities if requested
```

#### Message

Represents a message in the chat completion response.

```python
@dataclass
class Message:
    role: str                                      # Role of the message sender (e.g., "assistant", "user")
    content: str                                   # Content of the message
    tool_calls: Optional[List[ToolCall]] = None    # List of tool calls made by the model
    tool_results: Optional[List[ToolResult]] = None # Results from tool executions
    refusal: Optional[Any] = None                  # Information about message refusal if applicable
```

#### ToolCall

Represents a tool call in the chat completion response.

```python
@dataclass
class ToolCall:
    id: str          # Unique identifier for the tool call
    function: Function # Function details
    type: str        # Type of the tool call
```

#### Function

Represents a function in a tool call.

```python
@dataclass
class Function:
    name: str                # Name of the function
    arguments: Dict[str, Any] # Arguments passed to the function
```

#### ToolResult

Represents a tool result in the chat completion response.

```python
@dataclass
class ToolResult:
    tool_call_id: str  # ID of the associated tool call
    role: str          # Role (typically "tool")
    name: str          # Name of the tool
    content: Any       # Result content from the tool execution
```

#### Usage

Contains token usage statistics for the request.

```python
@dataclass
class Usage:
    prompt_tokens: int        # Tokens in the prompt
    completion_tokens: int    # Tokens in the completion
    total_tokens: int         # Total tokens used
    prompt_tokens_details: Optional[Dict[str, Any]]  # Detailed token usage
```

### Example Response

Here's an example of a typical response when using function calling:

```python
ChatCompletionResponse(
    id='...',
    choices=[
        Choice(
            index=0,
            message=Message(
                role='assistant',
                content='I am retrieving the weather for San Francisco.',
                tool_calls=[{
                    'id': '0',
                    'function': {
                        'name': 'get_weather',
                        'arguments': '{"location":"San Francisco, CA"}'
                    },
                    'type': 'function'
                }],
                tool_results=[{
                    'tool_call_id': '0',
                    'role': 'tool',
                    'name': 'get_weather',
                    'content': 'The weather in San Francisco, CA is sunny.'
                }],
                refusal=None
            ),
            finish_reason='stop',
            logprobs=None
        )
    ],
    created=1703...,
    model='grok-2-1212',
    object='chat.completion',
    system_fingerprint='...',
    usage=Usage(
        prompt_tokens=50,
        completion_tokens=20,
        total_tokens=70,
        prompt_tokens_details=None
    )
)
```

## Security Best Practices

When using this SDK, follow these security best practices:

1. **API Key Management**

   - Never hardcode your API key directly in your code
   - Use environment variables to store your API key:

     ```python
     import os

     api_key = os.getenv("XAI_API_KEY")
     xai = XAI(api_key=api_key, model="grok-2-1212")
     ```

   - Consider using a secure secrets management service in production
   - Keep your API key private and never commit it to version control

2. **Environment Variables**

   - Create a `.env` file for local development (and add it to `.gitignore`)
   - Example `.env` file:
     ```
     XAI_API_KEY=your_api_key_here
     ```

3. **Request Validation**
   - The SDK automatically validates all parameters before making API calls
   - Always handle potential exceptions in your code:
     ```python
     try:
         response = xai.invoke(messages=[{"role": "user", "content": "Hello"}])
     except Exception as e:
         # Handle the error appropriately
         print(f"An error occurred: {e}")
     ```

## License

This project is licensed under the terms included in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

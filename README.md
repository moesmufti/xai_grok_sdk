# xAI Grok SDK

A lightweight Python SDK for interacting with the x.AI API, designed with minimal dependencies. All you need is your xAI API key and the model you want to use.

You can get your API key [here](https://console.x.ai/). Currently, they provide $25 free credits for new users for December 2024!

## Installation

```bash
pip install xai-grok-sdk
```

## Features

- Simple and intuitive interface for x.AI API interactions
- Support for chat completions with the latest x.AI models
- Built-in function calling capabilities with support for auto, required, and none modes
- Minimal dependencies (only requires `requests`)
- Secure API key handling
- Customizable base URL for API endpoints
- Comprehensive error handling for API responses

## Supported Models

Currently, the following text-only models are supported:

- `grok-2-1212`
- `grok-beta`

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

print(response["message"])
```

## Parameters

### Required Parameters

#### Initialization

- `api_key` (str): Your xAI API key
- `model` (str): Model to use. Must be one of: "grok-2-1212", "grok-beta"

#### Invoke Method

- `messages` (List[Dict[str, Any]]): List of conversation messages

### Optional Parameters

The `invoke` method supports the following optional parameters:

- `frequency_penalty` (float, default=0): Penalty for token frequency
- `logit_bias` (Dict[str, float], default=None): Token bias dictionary
- `logprobs` (bool, default=False): Whether to return log probabilities
- `max_tokens` (int, default=0): Maximum number of tokens to generate
- `n` (int, default=0): Number of completions to generate
- `presence_penalty` (float, default=0): Penalty for token presence
- `response_format` (Dict[str, str], default=None): Format of the response
- `seed` (int, default=0): Random seed for reproducibility
- `stop` (Union[str, List[str]], default=None): Stop sequences
- `stream` (bool, default=False): Whether to stream the response
- `stream_options` (Dict[str, Any], default=None): Options for streaming
- `temperature` (float, default=0): Sampling temperature
- `tool_choice` (Union[str, Dict[str, Any]], default=None): Function calling mode ('auto', 'required', 'none', or specific function)
- `top_logprobs` (int, default=0): Number of top log probabilities to return
- `top_p` (float, default=0): Top-p sampling parameter
- `user` (str, default=""): End-user identifier

## Function Calling

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

# Implement the function
def get_weather(location: str) -> str:
    return f"The weather in {location} is sunny."

# Initialize the client with tools and function implementations
xai = XAI(
    api_key="your_api_key",
    model="grok-2-1212",
    tools=tools,
    function_map={"get_weather": get_weather}  # Map function names to implementations
)

# Make a request that might trigger function calling
response = xai.invoke(
    messages=[
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ],
    tool_choice="auto"  # Can be 'auto', 'required', 'none', or a specific function
)

print(response["message"])
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

> **Note**: Currently, using `"required"` or specific function calls may produce unexpected outputs. It is recommended to use either `"auto"` or `"none"` for more reliable results.

### Required Parameters for Function Calling

When using function calling, you need to provide:

- `tools`: List of tool definitions with their schemas
- `function_map`: Dictionary mapping function names to their actual implementations

> **Note**: The `function_map` parameter is required when tools are provided. Each tool name must have a corresponding implementation in the function map.

## API Reference

### XAI Class

#### `__init__(api_key: str, model: str, tools: Optional[List[Dict[str, Any]]] = None, function_map: Optional[Dict[str, Any]] = None)`

Initialize the XAI client.

- `api_key`: Your x.AI API key
- `model`: The model to use for chat completions
- `tools`: Optional list of tools available for the model to use
- `function_map`: Optional dictionary mapping function names to their implementations

#### `invoke(messages: List[Dict[str, Any]], tool_choice: str = "auto") -> Dict[str, Any]`

Run a conversation with the model.

- `messages`: List of conversation messages
- `tool_choice`: Function calling mode ('auto', 'required', 'none', or specific function)
- Returns: Dictionary containing the model's response

## License

This project is licensed under the terms included in the LICENSE file.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

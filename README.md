# XAI SDK

A lightweight Python SDK for interacting with the xAI API, designed with minimal dependencies.

## Installation

```bash
pip install xai-grok-sdk
```

## Features

- Simple and intuitive interface for x.AI API interactions
- Support for chat completions with the latest x.AI models
- Built-in function calling capabilities
- Minimal dependencies (only requires `requests`)

## Quick Start

```python
from xai_grok_sdk import XAI

# Initialize the client
xai = XAI(
    api_key="your_api_key",
    model="your_chosen_model"
)

# Basic chat completion
response = xai.invoke(
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ]
)

# Using function calling - THIS IS A WORK IN PROGRESS, DOESN'T WORK YET IN THE RELEASED VERSION
tools = [
    {
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a location",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g., San Francisco, CA"
                    }
                },
                "required": ["location"]
            }
        }
    }
]

xai = XAI(
    api_key="your_api_key",
    model="your_chosen_model",
    tools=tools
)

response = xai.invoke(
    messages=[
        {"role": "user", "content": "What's the weather like in San Francisco?"}
    ]
)
```

## API Reference

### XAI Class

#### `__init__(api_key: str, model: str, tools: Optional[List[Dict[str, Any]]] = None)`

Initialize the XAI client.

- `api_key`: Your x.AI API key
- `model`: The model to use for chat completions
- `tools`: Optional list of tools available for the model to use

#### `invoke(messages: List[Dict[str, Any]], tool_choice: str = "auto") -> Dict[str, Any]`

Run a conversation with the model.

- `messages`: List of conversation messages
- `tool_choice`: Function calling mode ('auto', 'required', 'none', or specific function)
- Returns: Dictionary containing the model's response

## License

[License information here]

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
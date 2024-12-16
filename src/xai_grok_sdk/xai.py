"""Module for handling XAI API interactions."""

import json
import requests
from typing import List, Dict, Any, Optional, Callable, Union, Literal

# Supported xAI models
ModelType = Literal["grok-2-1212", "grok-beta"]


class XAI:
    """Class for handling XAI API interactions."""

    def __init__(
        self,
        api_key: str,
        model: ModelType,
        tools: Optional[List[Dict[str, Any]]] = None,
        function_map: Optional[Dict[str, Callable]] = None,
    ):
        """
        Initialize the XAI client.

        Args:
            api_key: API key for XAI (required).
            model: Model to use for chat completions (required). Must be one of: "grok-2-1212", "grok-beta"
            tools: List of tools available for the model to use. Each tool should have a
                'name' field.
            function_map: Dictionary mapping function names to actual implementation functions.
                Required if tools are provided.
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.x.ai/v1"
        self.tools = []
        self.function_map = {}

        if tools:
            if not function_map:
                raise ValueError(
                    "function_map must be provided when tools are specified"
                )

            for tool in tools:
                if "name" not in tool:
                    raise ValueError("Each tool must have a 'name' field")

                func_name = tool["name"]
                if func_name not in function_map:
                    raise ValueError(
                        f"Function '{func_name}' not found in function_map"
                    )
                self.tools.append({"type": "function", "function": tool})
                self.function_map[func_name] = function_map[func_name]

    def _make_api_call(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Make an API call to XAI."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            f"{self.base_url}/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()
        return response.json()

    def invoke(
        self,
        messages: List[Dict[str, Any]],
        frequency_penalty: float = 0,
        logit_bias: Dict[str, float] = None,
        logprobs: bool = False,
        max_tokens: int = 0,
        n: int = 0,
        presence_penalty: float = 0,
        response_format: Optional[Dict[str, str]] = None,
        seed: int = 0,
        stop: Optional[Union[str, List[str]]] = None,
        stream: bool = False,
        stream_options: Optional[Dict[str, Any]] = None,
        temperature: float = 0,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = "auto",
        top_logprobs: int = 0,
        top_p: float = 0,
        user: str = "",
    ) -> Dict[str, Any]:
        """
        Run a conversation with the model.

        Args:
            messages: List of conversation messages (required)
            frequency_penalty: Frequency penalty parameter
            logit_bias: Token bias dictionary
            logprobs: Whether to return log probabilities
            max_tokens: Maximum number of tokens to generate
            n: Number of completions to generate
            presence_penalty: Presence penalty parameter
            response_format: Format of the response
            seed: Random seed for reproducibility
            stop: Stop sequences
            stream: Whether to stream the response
            stream_options: Options for streaming
            temperature: Sampling temperature
            tool_choice: Function calling mode ('auto', 'required', 'none', or specific function)
            top_logprobs: Number of top log probabilities to return
            top_p: Top-p sampling parameter
            user: End-user identifier

        Returns:
            Dict containing the model's response
        """
        # Prepare initial payload
        payload = {
            "model": self.model,
            "messages": messages,
            "tool_choice": tool_choice, 
        }

        # Add optional parameters if they differ from defaults
        if frequency_penalty != 0:
            payload["frequency_penalty"] = frequency_penalty
        if logit_bias:
            payload["logit_bias"] = logit_bias
        if logprobs:
            payload["logprobs"] = logprobs
        if max_tokens != 0:
            payload["max_tokens"] = max_tokens
        if n != 0:
            payload["n"] = n
        if presence_penalty != 0:
            payload["presence_penalty"] = presence_penalty
        if response_format is not None:
            payload["response_format"] = response_format
        if seed != 0:
            payload["seed"] = seed
        if stop:
            payload["stop"] = stop
        if stream:
            payload["stream"] = stream
        if stream_options is not None:
            payload["stream_options"] = stream_options
        if temperature != 0:
            payload["temperature"] = temperature
        if top_logprobs != 0:
            payload["top_logprobs"] = top_logprobs
        if top_p != 0:
            payload["top_p"] = top_p
        if user:
            payload["user"] = user

        # Include tools if configured
        if len(self.tools) > 0:
            payload["tools"] = self.tools


        # Make API call
        response_data = self._make_api_call(payload)

        # Handle tool calls if present
        if "choices" in response_data and len(response_data["choices"]) > 0:
            choice = response_data["choices"][0]
            if "message" in choice and "tool_calls" in choice["message"]:
                message = choice["message"]
                tool_calls = message["tool_calls"]

                # Execute each tool call and collect results
                tool_results = []
                for tool_call in tool_calls:
                    if tool_call["type"] == "function":
                        function_name = tool_call["function"]["name"]
                        if function_name in self.function_map:
                            # Parse arguments and call function
                            arguments = json.loads(tool_call["function"]["arguments"])
                            result = self.function_map[function_name](**arguments)
                            tool_results.append(
                                {
                                    "tool_call_id": tool_call["id"],
                                    "role": "tool",
                                    "name": function_name,
                                    "content": str(result),
                                }
                            )

                # Add tool results to the message if any were generated
                if tool_results:
                    message["tool_results"] = tool_results

        return response_data["choices"][0]

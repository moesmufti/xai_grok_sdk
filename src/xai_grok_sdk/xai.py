"""Module for handling XAI API interactions."""

import json
import requests
from typing import List, Dict, Any, Optional, Callable, Union, Generator
from xai_grok_sdk.models import (
    ModelType,
    ChatCompletionRequest,
    Message,
    Usage,
    Choice,
    ChatCompletionResponse,
    ToolCall,
    ToolResult,
    Function,
)


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
            for tool in tools:
                if "name" not in tool:
                    raise ValueError("Each tool must have a 'name' field")
                self.tools.append({"type": "function", "function": tool})

                if function_map:
                    func_name = tool["name"]
                    if func_name not in function_map:
                        raise ValueError(
                            f"Function '{func_name}' not found in function_map"
                        )
                    self.function_map[func_name] = function_map[func_name]

    def _make_api_call(
        self, payload: Dict[str, Any]
    ) -> Union[Dict[str, Any], requests.Response]:
        """Make an API call to XAI."""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        response = requests.post(
            f"{self.base_url}/chat/completions",
            headers=headers,
            json=payload,
            stream=payload.get("stream", False),
        )
        response.raise_for_status()

        if payload.get("stream", False):
            return response
        return response.json()

    def _process_stream_response(
        self, response: requests.Response
    ) -> Generator[ChatCompletionResponse, None, None]:
        """Process a streaming response from the API."""
        for line in response.iter_lines():
            if not line:
                continue

            # Remove 'data: ' prefix
            line = line.decode("utf-8")
            if not line.startswith("data: "):
                continue

            line = line[6:]  # Remove 'data: ' prefix

            if line == "[DONE]":
                break

            try:
                chunk = json.loads(line)
                # Convert chunk to ChatCompletionResponse
                yield ChatCompletionResponse(
                    id=chunk["id"],
                    choices=[
                        Choice(
                            index=choice["index"],
                            delta=(
                                Message(
                                    role=choice["delta"].get("role"),
                                    content=choice["delta"].get("content", ""),
                                )
                                if "delta" in choice
                                else None
                            ),
                            message=None,
                        )
                        for choice in chunk["choices"]
                    ],
                    usage=Usage(**chunk["usage"]) if "usage" in chunk else None,
                    system_fingerprint=chunk.get("system_fingerprint"),
                )
            except json.JSONDecodeError:
                continue

    def invoke(
        self,
        messages: List[Dict[str, Any]],
        frequency_penalty: Optional[float] = None,
        logit_bias: Optional[Dict[Any, Any]] = None,
        logprobs: Optional[bool] = None,
        max_tokens: Optional[int] = None,
        n: Optional[int] = None,
        presence_penalty: Optional[float] = None,
        response_format: Optional[Any] = None,
        seed: Optional[int] = None,
        stop: Optional[List[Any]] = None,
        stream: Optional[bool] = None,
        stream_options: Optional[Any] = None,
        temperature: Optional[float] = None,
        tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
        top_logprobs: Optional[int] = None,
        top_p: Optional[float] = None,
        user: Optional[str] = None,
    ) -> Union[ChatCompletionResponse, Generator[ChatCompletionResponse, None, None]]:
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
            Choice containing the model's response
        """
        # Prepare initial payload
        payload = ChatCompletionRequest(
            messages=messages,
            model=self.model,
            frequency_penalty=frequency_penalty,
            logit_bias=logit_bias,
            logprobs=logprobs,
            max_tokens=max_tokens,
            n=n,
            presence_penalty=presence_penalty,
            response_format=response_format,
            seed=seed,
            stop=stop,
            stream=stream,
            stream_options=stream_options,
            temperature=temperature,
            tools=self.tools,
            tool_choice=tool_choice,
            top_logprobs=top_logprobs,
            top_p=top_p,
            user=user,
        ).__dict__

        # Make API call
        response_data = self._make_api_call(payload)

        if stream:
            return self._process_stream_response(response_data)

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
                                ToolResult(
                                    tool_call_id=tool_call["id"],
                                    role="tool",
                                    name=function_name,
                                    content=str(result),
                                )
                            )

                # Add tool results to the message if any were generated
                if tool_results:
                    message["tool_results"] = tool_results

        # Convert response to ChatCompletionResponse
        response = ChatCompletionResponse(
            id=response_data["id"],
            choices=[
                Choice(
                    index=choice["index"] if "index" in choice else 0,
                    message=Message(
                        role=choice["message"]["role"],
                        content=choice["message"]["content"],
                        tool_calls=(
                            [
                                ToolCall(
                                    id=tc["id"],
                                    type=tc["type"],
                                    function=Function(
                                        name=tc["function"]["name"],
                                        arguments=json.loads(
                                            tc["function"]["arguments"]
                                        ),
                                    ),
                                )
                                for tc in choice["message"].get("tool_calls", []) or []
                            ]
                            if "tool_calls" in choice["message"]
                            else None
                        ),
                        tool_results=(
                            tool_results
                            if "tool_results" in choice["message"]
                            else None
                        ),
                    ),
                    finish_reason=choice["finish_reason"],
                    logprobs=choice["logprobs"] if "logprobs" in choice else None,
                )
                for choice in response_data["choices"]
            ],
            created=response_data["created"],
            model=response_data["model"],
            object=response_data["object"],
            system_fingerprint=response_data["system_fingerprint"],
            usage=Usage(**response_data["usage"]) if "usage" in response_data else None,
        )

        return response

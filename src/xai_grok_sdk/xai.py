"""Module for handling XAI API interactions."""

import json
import requests
from typing import List, Dict, Any, Optional, Callable


class XAI:
    """Class for handling XAI API interactions."""

    def __init__(
        self,
        api_key: str,
        model: str,
        tools: Optional[List[Dict[str, Any]]] = None,
    ):
        """
        Initialize the XAI client.

        Args:
            api_key: API key for XAI.
            model: Model to use for chat completions.
            tools: List of tools available for the model to use. Each tool should have a
                'function' field with 'name' and an actual implementation function.
        """
        self.api_key = api_key
        self.model = model
        self.base_url = "https://api.x.ai/v1"
        self.tools = []
        self.function_map: Dict[str, Callable] = {}

        if tools:
            for tool in tools:
                if "function" in tool and "name" in tool["function"]:
                    if hasattr(self, tool["function"]["name"]):
                        self.tools.append(tool)
                        self.function_map[tool["function"]["name"]] = getattr(
                            self, tool["function"]["name"]
                        )

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
        tool_choice: str = "auto",
    ) -> Dict[str, Any]:
        """
        Run a conversation with the model.

        Args:
            messages: List of conversation messages
            tool_choice: Function calling mode ('auto', 'required', 'none', or specific function)

        Returns:
            Dict containing the model's response
        """
        # Prepare initial payload
        payload = {
            "model": self.model,
            "messages": messages,
        }
        
        # Only include tools-related parameters if tools are configured
        if self.tools:
            payload["tools"] = self.tools
            payload["tool_choice"] = tool_choice

        # Make initial API call
        response_data = self._make_api_call(payload)

        # Check if tool was called
        if (
            "choices" in response_data
            and response_data["choices"]
            and "message" in response_data["choices"][0]
            and "tool_calls" in response_data["choices"][0]["message"]
        ):
            tool_call = response_data["choices"][0]["message"]["tool_calls"][0]
            function_name = tool_call["function"]["name"]
            function_args = json.loads(tool_call["function"]["arguments"])

            # Execute the function if it exists in the function map
            if function_name in self.function_map:
                function_result = self.function_map[function_name](**function_args)

                # Add function result to messages
                messages.append(
                    {
                        "tool_call_id": tool_call["id"],
                        "role": "tool",
                        "name": function_name,
                        "content": str(function_result),
                    }
                )

                # Get final response from the model
                final_payload = {"model": self.model, "messages": messages}
                return self._make_api_call(final_payload)

        return response_data

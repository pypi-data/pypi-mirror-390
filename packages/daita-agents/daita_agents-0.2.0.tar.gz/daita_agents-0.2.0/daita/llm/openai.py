"""
OpenAI LLM provider implementation with integrated tracing.
"""
import os
import logging
from typing import Dict, Any, Optional

from ..core.exceptions import LLMError
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class OpenAIProvider(BaseLLMProvider):
    """OpenAI LLM provider implementation with automatic call tracing."""
    
    def __init__(
        self,
        model: str = "gpt-4",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize OpenAI provider.
        
        Args:
            model: OpenAI model name (e.g., "gpt-4", "gpt-3.5-turbo")
            api_key: OpenAI API key
            **kwargs: Additional OpenAI-specific parameters
        """
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        super().__init__(model=model, api_key=api_key, **kwargs)
        
        # OpenAI-specific default parameters
        self.default_params.update({
            'frequency_penalty': kwargs.get('frequency_penalty', 0.0),
            'presence_penalty': kwargs.get('presence_penalty', 0.0),
            'timeout': kwargs.get('timeout', 60)
        })
        
        # Lazy-load OpenAI client
        self._client = None
    
    @property
    def client(self):
        """Lazy-load OpenAI client."""
        if self._client is None:
            try:
                import openai
                self._validate_api_key()
                self._client = openai.AsyncOpenAI(api_key=self.api_key)
                logger.debug("OpenAI client initialized")
            except ImportError:
                raise LLMError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
        return self._client
    
    async def _generate_impl(self, prompt: str, **kwargs) -> str:
        """
        Provider-specific implementation of text generation for OpenAI.
        
        This method contains the actual OpenAI API call logic and is automatically
        wrapped with tracing by the base class generate() method.
        
        Args:
            prompt: Input prompt
            **kwargs: Optional parameters
            
        Returns:
            Generated text response
        """
        try:
            # Merge parameters
            params = self._merge_params(kwargs)
            
            # Make API call
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=params.get('max_tokens'),
                temperature=params.get('temperature'),
                top_p=params.get('top_p'),
                frequency_penalty=params.get('frequency_penalty'),
                presence_penalty=params.get('presence_penalty'),
                timeout=params.get('timeout')
            )
            
            # Store usage for base class token extraction
            self._last_usage = response.usage
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"OpenAI generation failed: {str(e)}")
            raise LLMError(f"OpenAI generation failed: {str(e)}")

    def _convert_messages_to_openai(
        self,
        messages: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Convert universal flat format to OpenAI's nested format.

        OpenAI expects tool_calls in nested format:
        {"id": "x", "type": "function", "function": {"name": "...", "arguments": "..."}}

        Our internal format is flat:
        {"id": "x", "name": "...", "arguments": {...}}
        """
        import json

        openai_messages = []
        for msg in messages:
            if msg.get("role") == "assistant" and msg.get("tool_calls"):
                # Convert flat format to OpenAI's nested format
                converted_tool_calls = []
                for tc in msg["tool_calls"]:
                    converted_tool_calls.append({
                        "id": tc.get("id", ""),
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"]) if isinstance(tc["arguments"], dict) else tc["arguments"]
                        }
                    })

                openai_messages.append({
                    "role": "assistant",
                    "tool_calls": converted_tool_calls
                })
            else:
                # Pass through other messages unchanged
                openai_messages.append(msg)

        return openai_messages

    async def _generate_with_tools_single(
        self,
        messages: list[Dict[str, Any]],
        tools: list[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        OpenAI-specific tool calling implementation.

        Args:
            messages: Conversation history in universal flat format
            tools: Tool specifications in OpenAI format
            **kwargs: Optional parameters

        Returns:
            {
                "tool_calls": [...],  # If LLM wants to call tools
                "content": "...",      # If LLM has final answer
            }
        """
        import json

        try:
            # Merge parameters
            params = self._merge_params(kwargs)

            # Convert flat format to OpenAI's nested format
            openai_messages = self._convert_messages_to_openai(messages)

            # Make API call with tools
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=params.get('max_tokens'),
                temperature=params.get('temperature'),
                top_p=params.get('top_p'),
                frequency_penalty=params.get('frequency_penalty'),
                presence_penalty=params.get('presence_penalty'),
                timeout=params.get('timeout')
            )

            message = response.choices[0].message

            # Store usage for token tracking
            if hasattr(response, 'usage'):
                self._last_usage = response.usage

            if message.tool_calls:
                # LLM wants to call tools
                return {
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "name": tc.function.name,
                            "arguments": json.loads(tc.function.arguments)
                        }
                        for tc in message.tool_calls
                    ]
                }
            else:
                # LLM has final answer
                return {
                    "content": message.content
                }

        except Exception as e:
            logger.error(f"OpenAI tool calling failed: {str(e)}")
            raise LLMError(f"OpenAI tool calling failed: {str(e)}")

    @property
    def info(self) -> Dict[str, Any]:
        """Get information about the OpenAI provider."""
        base_info = super().info
        base_info.update({
            'provider_name': 'OpenAI',
            'api_compatible': 'OpenAI'
        })
        return base_info
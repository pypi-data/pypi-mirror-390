"""
Grok (xAI) LLM provider implementation with integrated tracing.
"""
import os
import logging
from typing import Dict, Any, Optional, List

from ..core.exceptions import LLMError
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class GrokProvider(BaseLLMProvider):
    """Grok (xAI) LLM provider implementation with automatic call tracing."""
    
    def __init__(
        self,
        model: str = "grok-3",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Grok provider.

        Args:
            model: Grok model name (e.g., "grok-3", "grok-vision-beta")
            api_key: xAI API key
            **kwargs: Additional Grok-specific parameters
        """
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
        
        super().__init__(model=model, api_key=api_key, **kwargs)
        
        # Grok-specific default parameters
        self.default_params.update({
            'stream': kwargs.get('stream', False),
            'timeout': kwargs.get('timeout', 60)
        })
        
        # Base URL for xAI API
        self.base_url = kwargs.get('base_url', 'https://api.x.ai/v1')
        
        # Lazy-load OpenAI client (Grok uses OpenAI-compatible API)
        self._client = None
    
    @property
    def client(self):
        """Lazy-load OpenAI client configured for xAI."""
        if self._client is None:
            try:
                import openai
                self._validate_api_key()
                self._client = openai.AsyncOpenAI(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                logger.debug("Grok client initialized")
            except ImportError:
                raise LLMError(
                    "OpenAI package not installed. Install with: pip install openai"
                )
        return self._client
    
    def _convert_messages_to_openai(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert universal flat format to OpenAI's nested format.

        Grok uses OpenAI-compatible API, so we need the same conversion.
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
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Grok tool calling implementation (uses OpenAI-compatible API).

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

            # Make API call with tools (Grok uses OpenAI-compatible interface)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=openai_messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=params.get('max_tokens'),
                temperature=params.get('temperature'),
                top_p=params.get('top_p'),
                timeout=params.get('timeout')
            )

            message = response.choices[0].message

            # Store usage for token tracking
            if hasattr(response, 'usage'):
                self._last_usage = response.usage

            if message.tool_calls:
                # LLM wants to call tools - return in flat format
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
            logger.error(f"Grok tool calling failed: {str(e)}")
            raise LLMError(f"Grok tool calling failed: {str(e)}")

    async def _generate_impl(self, prompt: str, **kwargs) -> str:
        """
        Provider-specific implementation of text generation for Grok.
        
        This method contains the actual Grok API call logic and is automatically
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
            
            # Make API call using OpenAI-compatible interface
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=params.get('max_tokens'),
                temperature=params.get('temperature'),
                top_p=params.get('top_p'),
                stream=params.get('stream'),
                timeout=params.get('timeout')
            )
            
            # Store usage for base class token extraction
            self._last_usage = response.usage
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Grok generation failed: {str(e)}")
            raise LLMError(f"Grok generation failed: {str(e)}")
    
    @property
    def info(self) -> Dict[str, Any]:
        """Get information about the Grok provider."""
        base_info = super().info
        base_info.update({
            'base_url': self.base_url,
            'provider_name': 'Grok (xAI)',
            'api_compatible': 'OpenAI'
        })
        return base_info
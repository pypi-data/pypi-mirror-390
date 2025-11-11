"""
Anthropic LLM provider implementation with integrated tracing.
"""
import os
import logging
from typing import Dict, Any, Optional

from ..core.exceptions import LLMError
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class AnthropicProvider(BaseLLMProvider):
    """Anthropic LLM provider implementation with automatic call tracing."""
    
    def __init__(
        self,
        model: str = "claude-3-sonnet-20240229",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Anthropic provider.
        
        Args:
            model: Anthropic model name
            api_key: Anthropic API key
            **kwargs: Additional Anthropic-specific parameters
        """
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("ANTHROPIC_API_KEY")
        
        super().__init__(model=model, api_key=api_key, **kwargs)
        
        # Anthropic-specific default parameters
        self.default_params.update({
            'timeout': kwargs.get('timeout', 60)
        })
        
        # Lazy-load Anthropic client
        self._client = None
    
    @property
    def client(self):
        """Lazy-load Anthropic client."""
        if self._client is None:
            try:
                import anthropic
                self._validate_api_key()
                self._client = anthropic.AsyncAnthropic(api_key=self.api_key)
                logger.debug("Anthropic client initialized")
            except ImportError:
                raise LLMError(
                    "Anthropic package not installed. Install with: pip install anthropic"
                )
        return self._client
    
    async def _generate_impl(self, prompt: str, **kwargs) -> str:
        """
        Provider-specific implementation of text generation for Anthropic.
        
        This method contains the actual Anthropic API call logic and is automatically
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
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=params.get('max_tokens'),
                temperature=params.get('temperature'),
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=params.get('timeout')
            )
            
            # Store usage for base class token extraction
            self._last_usage = response.usage
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic generation failed: {str(e)}")
            raise LLMError(f"Anthropic generation failed: {str(e)}")
    
    async def generate_with_system(self, prompt: str, system_message: str, **kwargs) -> str:
        """
        Generate text with a system message using Anthropic's system parameter.
        
        Note: This method bypasses automatic tracing since it's not part of the 
        base interface. If you want tracing for system messages, call the base
        generate() method with a formatted prompt instead.
        
        Args:
            prompt: User prompt
            system_message: System message to set context
            **kwargs: Optional parameters
            
        Returns:
            Generated text
        """
        try:
            # Merge parameters
            params = self._merge_params(kwargs)
            
            # Make API call with system parameter
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=params.get('max_tokens'),
                temperature=params.get('temperature'),
                system=system_message,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                timeout=params.get('timeout')
            )
            
            # Store usage for potential token extraction
            self._last_usage = response.usage
            
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Anthropic generation with system message failed: {str(e)}")
            raise LLMError(f"Anthropic generation failed: {str(e)}")
    
    def _get_last_token_usage(self) -> Dict[str, int]:
        """
        Override base class method to handle Anthropic's token format.
        
        Anthropic uses input_tokens and output_tokens format, different from OpenAI.
        """
        if self._last_usage:
            # Anthropic format: input_tokens + output_tokens
            input_tokens = getattr(self._last_usage, 'input_tokens', 0)
            output_tokens = getattr(self._last_usage, 'output_tokens', 0)
            total_tokens = input_tokens + output_tokens
            
            return {
                'total_tokens': total_tokens,
                'prompt_tokens': input_tokens,  # Map input_tokens to prompt_tokens
                'completion_tokens': output_tokens  # Map output_tokens to completion_tokens
            }
        
        # Fallback to base class estimation
        return super()._get_last_token_usage()

    def _convert_tools_to_format(self, tools: list['AgentTool']) -> list[Dict[str, Any]]:
        """
        Convert AgentTool list to Anthropic tool format.

        Anthropic uses a different tool format than OpenAI.
        """
        return [tool.to_anthropic_tool() for tool in tools]

    async def _generate_with_tools_single(
        self,
        messages: list[Dict[str, Any]],
        tools: list[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Anthropic-specific tool calling implementation.

        Args:
            messages: Conversation history in OpenAI format
            tools: Tool specifications in Anthropic format
            **kwargs: Optional parameters

        Returns:
            {
                "tool_calls": [...],  # If LLM wants to call tools
                "content": "...",      # If LLM has final answer
            }
        """
        try:
            # Merge parameters
            params = self._merge_params(kwargs)

            # Convert messages to Anthropic format
            anthropic_messages = self._convert_messages_to_anthropic(messages)

            # Make API call with tools
            response = await self.client.messages.create(
                model=self.model,
                messages=anthropic_messages,
                tools=tools,
                max_tokens=params.get('max_tokens', 4096),
                temperature=params.get('temperature'),
                timeout=params.get('timeout')
            )

            # Store usage for token tracking
            if hasattr(response, 'usage'):
                self._last_usage = response.usage

            # Check for tool use blocks
            tool_use_blocks = [
                block for block in response.content
                if hasattr(block, 'type') and block.type == "tool_use"
            ]

            if tool_use_blocks:
                # LLM wants to call tools
                return {
                    "tool_calls": [
                        {
                            "id": block.id,
                            "name": block.name,
                            "arguments": block.input
                        }
                        for block in tool_use_blocks
                    ]
                }
            else:
                # LLM has final answer
                text_blocks = [
                    block.text for block in response.content
                    if hasattr(block, 'type') and block.type == "text"
                ]
                return {
                    "content": "".join(text_blocks)
                }

        except Exception as e:
            logger.error(f"Anthropic tool calling failed: {str(e)}")
            raise LLMError(f"Anthropic tool calling failed: {str(e)}")

    def _convert_messages_to_anthropic(
        self,
        messages: list[Dict[str, Any]]
    ) -> list[Dict[str, Any]]:
        """
        Convert OpenAI-style messages to Anthropic format.

        Anthropic uses a different message format, especially for tool results.
        """
        anthropic_messages = []

        for msg in messages:
            if msg["role"] == "tool":
                # Tool result - convert to Anthropic format
                anthropic_messages.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg["tool_call_id"],
                            "content": msg["content"]
                        }
                    ]
                })
            elif msg["role"] == "assistant" and msg.get("tool_calls"):
                # Assistant with tool calls (already in flat format)
                content_blocks = []
                for tc in msg["tool_calls"]:
                    content_blocks.append({
                        "type": "tool_use",
                        "id": tc["id"],
                        "name": tc["name"],
                        "input": tc["arguments"]
                    })
                anthropic_messages.append({
                    "role": "assistant",
                    "content": content_blocks
                })
            else:
                # Regular message
                anthropic_messages.append(msg)

        return anthropic_messages

    @property
    def info(self) -> Dict[str, Any]:
        """Get information about the Anthropic provider."""
        base_info = super().info
        base_info.update({
            'provider_name': 'Anthropic',
            'api_compatible': 'Anthropic'
        })
        return base_info
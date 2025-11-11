"""
Google Gemini LLM provider implementation with integrated tracing.
"""
import os
import logging
import asyncio
from typing import Dict, Any, Optional, List

from ..core.exceptions import LLMError
from .base import BaseLLMProvider

logger = logging.getLogger(__name__)

class GeminiProvider(BaseLLMProvider):
    """Google Gemini LLM provider implementation with automatic call tracing."""
    
    def __init__(
        self,
        model: str = "gemini-2.5-flash",
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize Gemini provider.

        Args:
            model: Gemini model name (e.g., "gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash")
            api_key: Google AI API key
            **kwargs: Additional Gemini-specific parameters
        """
        # Get API key from parameter or environment
        api_key = api_key or os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
        
        super().__init__(model=model, api_key=api_key, **kwargs)
        
        # Gemini-specific default parameters
        self.default_params.update({
            'timeout': kwargs.get('timeout', 60),
            'safety_settings': kwargs.get('safety_settings', None),
            'generation_config': kwargs.get('generation_config', None)
        })
        
        # Lazy-load Gemini client
        self._client = None
    
    @property
    def client(self):
        """Lazy-load Google Generative AI client."""
        if self._client is None:
            try:
                import google.generativeai as genai
                self._validate_api_key()
                
                # Configure the API key
                genai.configure(api_key=self.api_key)
                
                # Create the generative model
                self._client = genai.GenerativeModel(self.model)
                logger.debug("Gemini client initialized")
            except ImportError:
                raise LLMError(
                    "Google Generative AI package not installed. Install with: pip install google-generativeai"
                )
        return self._client
    
    async def _generate_impl(self, prompt: str, **kwargs) -> str:
        """
        Provider-specific implementation of text generation for Gemini.
        
        This method contains the actual Gemini API call logic and is automatically
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

            # Prepare generation config
            generation_config = params.get('generation_config', {})
            if not generation_config:
                # Gemini requires max_output_tokens to be set explicitly
                max_tokens = params.get('max_tokens')
                if max_tokens is None:
                    max_tokens = 2048  # Reasonable default for Gemini

                generation_config = {
                    'max_output_tokens': max_tokens,
                    'temperature': params.get('temperature'),
                    'top_p': params.get('top_p')
                }

            # Make API call (Gemini's generate_content can be sync or async)
            # For consistency with other providers, we'll run in executor if needed
            if asyncio.iscoroutinefunction(self.client.generate_content):
                response = await self.client.generate_content(
                    prompt,
                    generation_config=generation_config,
                    safety_settings=params.get('safety_settings')
                )
            else:
                # Run synchronous method in executor
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.client.generate_content(
                        prompt,
                        generation_config=generation_config,
                        safety_settings=params.get('safety_settings')
                    )
                )
            
            # Store usage info if available (Gemini's usage tracking varies)
            if hasattr(response, 'usage_metadata'):
                self._last_usage = response.usage_metadata

            # Handle blocked or empty responses
            if not response.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else None
                if finish_reason == 2:  # MAX_TOKENS
                    logger.warning("Gemini response hit max_tokens limit, returning partial response")
                    return "[Response truncated due to token limit]"
                elif finish_reason == 3:  # SAFETY
                    logger.warning("Gemini response blocked by safety filters")
                    return "[Response blocked by safety filters]"
                else:
                    logger.warning(f"Gemini returned empty response with finish_reason: {finish_reason}")
                    return "[Empty response from Gemini]"

            return response.text
            
        except Exception as e:
            logger.error(f"Gemini generation failed: {str(e)}")
            raise LLMError(f"Gemini generation failed: {str(e)}")
    
    def _get_last_token_usage(self) -> Dict[str, int]:
        """
        Override base class method to handle Gemini's token format.
        
        Gemini uses different token field names in usage_metadata.
        """
        if self._last_usage:
            # Gemini format varies, try to extract what we can
            prompt_tokens = getattr(self._last_usage, 'prompt_token_count', 0)
            completion_tokens = getattr(self._last_usage, 'candidates_token_count', 0)
            total_tokens = getattr(self._last_usage, 'total_token_count', prompt_tokens + completion_tokens)
            
            return {
                'total_tokens': total_tokens,
                'prompt_tokens': prompt_tokens,
                'completion_tokens': completion_tokens
            }
        
        # Fallback to base class estimation
        return super()._get_last_token_usage()

    def _convert_tools_to_format(self, tools: List['AgentTool']) -> List[Dict[str, Any]]:
        """
        Convert AgentTool list to Gemini function declaration format.

        Gemini uses a simpler format than OpenAI.
        """
        gemini_tools = []
        for tool in tools:
            openai_format = tool.to_openai_function()

            # Convert OpenAI format to Gemini format
            gemini_tools.append({
                "name": openai_format["function"]["name"],
                "description": openai_format["function"]["description"],
                "parameters": openai_format["function"]["parameters"]
            })

        return gemini_tools

    def _convert_messages_to_gemini(
        self,
        messages: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Convert universal flat format to Gemini's format.

        Gemini uses "user" and "model" roles (not "assistant").
        """
        import google.generativeai.types as genai_types

        gemini_messages = []

        for msg in messages:
            if msg["role"] == "user":
                gemini_messages.append({
                    "role": "user",
                    "parts": [msg["content"]]
                })
            elif msg["role"] == "assistant":
                if msg.get("tool_calls"):
                    # Assistant with tool calls
                    parts = []
                    for tc in msg["tool_calls"]:
                        parts.append(genai_types.FunctionCall(
                            name=tc["name"],
                            args=tc["arguments"]
                        ))
                    gemini_messages.append({
                        "role": "model",
                        "parts": parts
                    })
                else:
                    # Regular assistant message
                    gemini_messages.append({
                        "role": "model",
                        "parts": [msg.get("content", "")]
                    })
            elif msg["role"] == "tool":
                # Tool result
                gemini_messages.append({
                    "role": "function",
                    "parts": [genai_types.FunctionResponse(
                        name=msg.get("name", ""),
                        response={"result": msg["content"]}
                    )]
                })

        return gemini_messages

    async def _generate_with_tools_single(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Gemini-specific tool calling implementation.

        Args:
            messages: Conversation history in universal flat format
            tools: Tool specifications in Gemini format
            **kwargs: Optional parameters

        Returns:
            {
                "tool_calls": [...],  # If LLM wants to call tools
                "content": "...",      # If LLM has final answer
            }
        """
        try:
            import google.generativeai as genai
            from google.generativeai.types import FunctionDeclaration, Tool

            # Merge parameters
            params = self._merge_params(kwargs)

            # Convert tools to Gemini FunctionDeclaration format
            function_declarations = [
                FunctionDeclaration(
                    name=tool["name"],
                    description=tool["description"],
                    parameters=tool["parameters"]
                )
                for tool in tools
            ]

            # Create Tool object
            gemini_tool = Tool(function_declarations=function_declarations)

            # Prepare generation config
            generation_config = params.get('generation_config', {})
            if not generation_config:
                # Gemini requires max_output_tokens to be set explicitly
                max_tokens = params.get('max_tokens')
                if max_tokens is None:
                    max_tokens = 2048  # Reasonable default for Gemini

                generation_config = {
                    'max_output_tokens': max_tokens,
                    'temperature': params.get('temperature'),
                    'top_p': params.get('top_p')
                }

            # Convert messages to Gemini format
            gemini_messages = self._convert_messages_to_gemini(messages)

            # Build conversation content
            # For Gemini, we need to structure the chat differently
            # The first message should be the system/user prompt
            if gemini_messages:
                # Start a chat with history
                chat = self.client.start_chat(history=gemini_messages[:-1] if len(gemini_messages) > 1 else [])
                last_message = gemini_messages[-1]["parts"][0] if gemini_messages else ""
            else:
                chat = self.client.start_chat()
                last_message = ""

            # Make API call with tools
            if asyncio.iscoroutinefunction(chat.send_message):
                response = await chat.send_message(
                    last_message,
                    tools=[gemini_tool],
                    generation_config=generation_config
                )
            else:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: chat.send_message(
                        last_message,
                        tools=[gemini_tool],
                        generation_config=generation_config
                    )
                )

            # Store usage for token tracking
            if hasattr(response, 'usage_metadata'):
                self._last_usage = response.usage_metadata

            # Check for function calls in response
            function_calls = []
            for part in response.parts:
                if hasattr(part, 'function_call') and part.function_call:
                    fc = part.function_call
                    function_calls.append({
                        "id": f"call_{len(function_calls)}",
                        "name": fc.name,
                        "arguments": dict(fc.args)
                    })

            if function_calls:
                # LLM wants to call tools
                return {
                    "tool_calls": function_calls
                }
            else:
                # LLM has final answer
                return {
                    "content": response.text
                }

        except Exception as e:
            logger.error(f"Gemini tool calling failed: {str(e)}")
            raise LLMError(f"Gemini tool calling failed: {str(e)}")

    @property
    def info(self) -> Dict[str, Any]:
        """Get information about the Gemini provider."""
        base_info = super().info
        base_info.update({
            'provider_name': 'Google Gemini',
            'api_compatible': 'Google AI'
        })
        return base_info
"""
Updated BaseLLMProvider with Unified Tracing Integration

This replaces the old BaseLLMProvider to use the unified tracing system.
All LLM calls are automatically traced without user configuration.

Key Changes:
- Removed old token tracking system completely
- Integrated automatic LLM call tracing
- Simple cost estimation  
- Automatic provider/model/token capture
- Zero configuration required
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
import logging
import time
import asyncio

from ..core.tracing import get_trace_manager, TraceType, TraceStatus
from ..core.interfaces import LLMProvider

logger = logging.getLogger(__name__)

class BaseLLMProvider(LLMProvider, ABC):
    """
    Base class for LLM providers with automatic call tracing.
    
    Every LLM call is automatically traced with:
    - Provider and model details
    - Token usage and costs
    - Latency and performance
    - Input/output content (preview)
    - Error tracking
    
    Users get full LLM observability without any configuration.
    """
    
    def __init__(
        self,
        model: str,
        api_key: Optional[str] = None,
        **kwargs
    ):
        """
        Initialize the LLM provider with automatic tracing.
        
        Args:
            model: Model identifier
            api_key: API key for authentication
            **kwargs: Additional provider-specific options
        """
        self.model = model
        self.api_key = api_key
        self.config = kwargs
        
        # Default parameters
        self.default_params = {
            'temperature': kwargs.get('temperature', 0.7),
            'max_tokens': kwargs.get('max_tokens', 1000),
            'top_p': kwargs.get('top_p', 1.0),
        }
        
        # Agent ID for tracing (set by agent)
        self.agent_id = kwargs.get('agent_id')
        
        # Get trace manager for automatic tracing
        self.trace_manager = get_trace_manager()
        
        # Provider name for tracing
        self.provider_name = self.__class__.__name__.replace('Provider', '').lower()
        
        # Last usage for cost estimation
        self._last_usage = None
        
        logger.debug(f"Initialized {self.__class__.__name__} with model {model} (automatic tracing enabled)")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from prompt with automatic LLM call tracing.
        
        Every call is automatically traced with full metadata.
        
        Args:
            prompt: Input prompt
            **kwargs: Optional parameters to override defaults
            
        Returns:
            Generated text response
        """
        # Merge parameters
        params = self._merge_params(kwargs)
        
        # Automatically trace the LLM call
        async with self.trace_manager.span(
            operation_name=f"llm_{self.provider_name}_{self.model}",
            trace_type=TraceType.LLM_CALL,
            agent_id=self.agent_id,
            input_data=prompt,
            llm_provider=self.provider_name,
            llm_model=self.model,
            temperature=str(params.get('temperature', 0.7)),
            max_tokens=str(params.get('max_tokens', 1000))
        ) as span_id:
            
            try:
                start_time = time.time()
                
                # Execute the actual LLM call
                response = await self._generate_impl(prompt, **params)
                
                end_time = time.time()
                duration_ms = (end_time - start_time) * 1000
                
                # Get token usage from the call
                token_usage = self._get_last_token_usage()
                
                # Record LLM call details in the trace
                self.trace_manager.record_llm_call(
                    span_id=span_id,
                    provider=self.provider_name,
                    model=self.model,
                    tokens=token_usage
                )
                
                # Add cost estimation if available
                cost = self._estimate_cost(token_usage)
                if cost and span_id in self.trace_manager._active_spans:
                    span = self.trace_manager._active_spans[span_id]
                    span.metadata['estimated_cost_usd'] = cost
                    span.metadata['duration_ms'] = duration_ms
                
                logger.debug(f"LLM call completed: {token_usage.get('total_tokens', 0)} tokens in {duration_ms:.1f}ms")
                return response
                
            except Exception as e:
                # LLM call failed - error automatically recorded by span context
                logger.warning(f"LLM call failed: {str(e)}")
                raise
    
    @abstractmethod
    async def _generate_impl(self, prompt: str, **kwargs) -> str:
        """
        Provider-specific implementation of text generation.
        
        This method must be implemented by each provider (OpenAI, Anthropic, etc.)
        and contains the actual LLM API call logic.
        
        Args:
            prompt: Input prompt
            **kwargs: Optional parameters
            
        Returns:
            Generated text response
        """
        pass
    
    def _get_last_token_usage(self) -> Dict[str, int]:
        """
        Get token usage from the last API call.
        
        This should be overridden by each provider to return actual
        token usage from their last API response.
        """
        if self._last_usage:
            # Try to extract from stored usage object
            if hasattr(self._last_usage, 'total_tokens'):
                # OpenAI format
                return {
                    'total_tokens': getattr(self._last_usage, 'total_tokens', 0),
                    'prompt_tokens': getattr(self._last_usage, 'prompt_tokens', 0),
                    'completion_tokens': getattr(self._last_usage, 'completion_tokens', 0)
                }
            elif hasattr(self._last_usage, 'input_tokens'):
                # Anthropic format
                input_tokens = getattr(self._last_usage, 'input_tokens', 0)
                output_tokens = getattr(self._last_usage, 'output_tokens', 0)
                return {
                    'total_tokens': input_tokens + output_tokens,
                    'prompt_tokens': input_tokens,
                    'completion_tokens': output_tokens
                }
        
        # Default fallback
        return {
            'total_tokens': 0,
            'prompt_tokens': 0,
            'completion_tokens': 0
        }
    
    def _estimate_cost(self, token_usage: Dict[str, int]) -> Optional[float]:
        """
        Simple cost estimation for MVP.
        
        Providers can override with specific pricing.
        """
        total_tokens = token_usage.get('total_tokens', 0)
        if total_tokens == 0:
            return None
        
        # Generic estimation for MVP - providers should override
        cost_per_1k_tokens = 0.002  # $0.002 per 1K tokens
        return (total_tokens / 1000) * cost_per_1k_tokens
    
    def _merge_params(self, override_params: Dict[str, Any]) -> Dict[str, Any]:
        """Merge default parameters with overrides."""
        params = self.default_params.copy()
        params.update(override_params)
        return params
    
    def _validate_api_key(self) -> None:
        """Validate that API key is available."""
        if not self.api_key:
            raise ValueError(f"API key required for {self.__class__.__name__}")
    
    def set_agent_id(self, agent_id: str):
        """
        Set the agent ID for tracing context.
        
        This is called automatically by BaseAgent during initialization.
        """
        self.agent_id = agent_id
        logger.debug(f"Set agent ID {agent_id} for {self.provider_name} provider")
    
    def get_recent_calls(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent LLM calls for this provider's agent from unified tracing."""
        if not self.agent_id:
            return []
        
        operations = self.trace_manager.get_recent_operations(agent_id=self.agent_id, limit=limit * 2)
        
        # Filter for LLM calls from this provider
        llm_calls = [
            op for op in operations 
            if (op.get('type') == 'llm_call' and 
                op.get('metadata', {}).get('llm_provider') == self.provider_name)
        ]
        
        return llm_calls[:limit]
    
    def get_token_stats(self) -> Dict[str, Any]:
        """Get token usage statistics from unified tracing."""
        if not self.agent_id:
            return {
                'total_calls': 0,
                'total_tokens': 0,
                'estimated_cost': 0.0
            }
        
        metrics = self.trace_manager.get_agent_metrics(self.agent_id)
        
        # Get actual token usage from the most recent call
        last_usage = self._get_last_token_usage()
        
        return {
            'total_calls': metrics.get('total_operations', 0),  # All operations
            'total_tokens': last_usage.get('total_tokens', 0),  # From last API call
            'prompt_tokens': last_usage.get('prompt_tokens', 0),
            'completion_tokens': last_usage.get('completion_tokens', 0),
            'estimated_cost': self._estimate_cost(last_usage) or 0.0,
            'success_rate': metrics.get('success_rate', 0),
            'avg_latency_ms': metrics.get('avg_latency_ms', 0)
        }
    
    async def generate_with_tools(
        self,
        prompt: str,
        tools: List['AgentTool'],
        max_iterations: int = 5,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Execute LLM with function calling loop.

        The LLM can autonomously call tools over multiple iterations until
        it has enough information to provide a final answer.

        Args:
            prompt: User instruction/question
            tools: List of tools LLM can call
            max_iterations: Max number of turns (default 5)
            **kwargs: Provider-specific options

        Returns:
            {
                "result": str,  # Final answer from LLM
                "tool_calls": [  # List of all tools called
                    {
                        "tool": str,
                        "arguments": dict,
                        "result": any
                    }
                ],
                "iterations": int  # Number of turns taken
            }
        """
        import json

        conversation = [{"role": "user", "content": prompt}]
        tools_called = []

        for iteration in range(max_iterations):
            # Convert tools to provider-specific format
            tool_specs = self._convert_tools_to_format(tools)

            # Call LLM with tools
            response = await self._generate_with_tools_single(
                messages=conversation,
                tools=tool_specs,
                **kwargs
            )

            # Check if LLM wants to call tools
            if response.get("tool_calls"):
                # Execute each tool call
                for tool_call in response["tool_calls"]:
                    tool_result = await self._execute_tool_call(
                        tool_call=tool_call,
                        tools=tools
                    )

                    tools_called.append({
                        "tool": tool_call["name"],
                        "arguments": tool_call["arguments"],
                        "result": tool_result
                    })

                    # Add to conversation history
                    # Use universal flat format (provider-agnostic)
                    formatted_tool_call = {
                        "id": tool_call.get("id", str(len(tools_called))),
                        "name": tool_call["name"],
                        "arguments": tool_call["arguments"]
                    }

                    conversation.append({
                        "role": "assistant",
                        "tool_calls": [formatted_tool_call]
                    })
                    conversation.append({
                        "role": "tool",
                        "tool_call_id": tool_call.get("id", str(len(tools_called))),
                        "content": json.dumps(tool_result)
                    })
            else:
                # LLM returned final answer
                return {
                    "result": response["content"],
                    "tool_calls": tools_called,
                    "iterations": iteration + 1
                }

        # Exceeded max iterations
        return {
            "result": f"Exceeded maximum iterations ({max_iterations}). Last response: {response.get('content', 'No response')}",
            "tool_calls": tools_called,
            "iterations": max_iterations,
            "error": "max_iterations_exceeded"
        }

    def _convert_tools_to_format(self, tools: List['AgentTool']) -> List[Dict[str, Any]]:
        """
        Convert AgentTool list to provider-specific format.

        Default implementation uses OpenAI format. Providers can override
        to use their own format (e.g., Anthropic).
        """
        return [tool.to_openai_function() for tool in tools]

    async def _execute_tool_call(
        self,
        tool_call: Dict[str, Any],
        tools: List['AgentTool']
    ) -> Any:
        """Execute a single tool call with timeout and error handling."""
        tool_name = tool_call["name"]
        arguments = tool_call["arguments"]

        # Find the tool
        tool = next((t for t in tools if t.name == tool_name), None)
        if not tool:
            return {"error": f"Tool '{tool_name}' not found"}

        # Execute with timeout
        try:
            result = await asyncio.wait_for(
                tool.handler(arguments),
                timeout=tool.timeout_seconds
            )
            return result
        except asyncio.TimeoutError:
            return {"error": f"Tool '{tool_name}' timed out after {tool.timeout_seconds}s"}
        except Exception as e:
            return {"error": f"Tool '{tool_name}' failed: {str(e)}"}

    @abstractmethod
    async def _generate_with_tools_single(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        **kwargs
    ) -> Dict[str, Any]:
        """
        Single LLM call with tools (provider-specific).

        This method must be implemented by each provider (OpenAI, Anthropic, etc.)
        to handle their specific tool calling format.

        Args:
            messages: Conversation history in OpenAI format
            tools: Tool specifications in provider format
            **kwargs: Optional parameters

        Returns:
            {
                "tool_calls": [...],  # If LLM wants to call tools
                "content": "...",      # If LLM has final answer
            }
        """
        pass

    @property
    def info(self) -> Dict[str, Any]:
        """Get information about this LLM provider."""
        return {
            'provider': self.provider_name,
            'model': self.model,
            'agent_id': self.agent_id,
            'config': {k: v for k, v in self.config.items() if 'key' not in k.lower()},
            'default_params': self.default_params,
            'tracing_enabled': True
        }



# Context manager for batch LLM operations
@asynccontextmanager
async def traced_llm_batch(llm_provider: BaseLLMProvider, batch_name: str = "llm_batch"):
    """
    Context manager for tracing batch LLM operations.
    
    Usage:
        async with traced_llm_batch(llm, "document_analysis"):
            summary = await llm.generate("Summarize: " + doc1)
            analysis = await llm.generate("Analyze: " + doc2)
    """
    trace_manager = get_trace_manager()
    
    async with trace_manager.span(
        operation_name=f"llm_batch_{batch_name}",
        trace_type=TraceType.LLM_CALL,
        agent_id=llm_provider.agent_id,
        llm_provider=llm_provider.provider_name,
        batch_operation=batch_name
    ):
        try:
            yield llm_provider
        except Exception as e:
            logger.error(f"LLM batch {batch_name} failed: {e}")
            raise


# Utility functions
def get_llm_traces(agent_id: Optional[str] = None, provider: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
    """Get recent LLM call traces from unified tracing."""
    trace_manager = get_trace_manager()
    operations = trace_manager.get_recent_operations(agent_id=agent_id, limit=limit * 2)
    
    # Filter for LLM operations
    llm_ops = [
        op for op in operations 
        if op.get('type') == 'llm_call'
    ]
    
    # Filter by provider if specified
    if provider:
        llm_ops = [
            op for op in llm_ops
            if op.get('metadata', {}).get('llm_provider') == provider
        ]
    
    return llm_ops[:limit]


def get_llm_stats(agent_id: Optional[str] = None, provider: Optional[str] = None) -> Dict[str, Any]:
    """Get LLM usage statistics from unified tracing."""
    traces = get_llm_traces(agent_id, provider, limit=50)
    
    if not traces:
        return {"total_calls": 0, "success_rate": 0, "avg_latency_ms": 0}
    
    total_calls = len(traces)
    successful_calls = len([t for t in traces if t.get('status') == 'success'])
    
    # Calculate averages
    latencies = [t.get('duration_ms', 0) for t in traces if t.get('duration_ms')]
    avg_latency = sum(latencies) / len(latencies) if latencies else 0
    
    # Token aggregation (simplified for MVP)
    total_tokens = 0
    for trace in traces:
        metadata = trace.get('metadata', {})
        total_tokens += metadata.get('tokens_total', 0)
    
    return {
        "total_calls": total_calls,
        "successful_calls": successful_calls,
        "failed_calls": total_calls - successful_calls,
        "success_rate": successful_calls / total_calls if total_calls > 0 else 0,
        "avg_latency_ms": avg_latency,
        "total_tokens": total_tokens,
        "agent_id": agent_id,
        "provider": provider
    }


# Export everything
__all__ = [
    # Base class
    "BaseLLMProvider",
    
    # Context managers
    "traced_llm_batch",
    
    # Utility functions
    "get_llm_traces",
    "get_llm_stats"
]
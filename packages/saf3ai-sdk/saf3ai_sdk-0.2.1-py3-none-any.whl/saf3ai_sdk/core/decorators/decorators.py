"""Decorators for Saf3AI SDK instrumentation."""

import functools
import inspect
from typing import Any, Callable, Dict, Optional, Union

from opentelemetry.trace import Status, StatusCode

from saf3ai_sdk.core.tracer import tracer
from saf3ai_sdk.logging import logger


def _create_span_decorator(span_kind: str, default_name: Optional[str] = None):
    """Create a span decorator for the given span kind."""
    
    def decorator(
        func_or_name: Optional[Union[str, Callable]] = None,
        name: Optional[str] = None,
        tags: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        """
        Decorator to create a span for the decorated function.
        
        Args:
            func_or_name: Function to decorate or name for the span
            name: Name for the span (if func_or_name is a function)
            tags: Additional tags to add to the span
            **kwargs: Additional span attributes
        """
        def actual_decorator(func: Callable) -> Callable:
            @functools.wraps(func)
            def wrapper(*args, **func_kwargs):
                if not tracer.initialized:
                    logger.warning("Tracer not initialized, executing function without instrumentation")
                    return func(*args, **func_kwargs)
                
                # Determine span name
                span_name = name or default_name or func.__name__
                
                # Build attributes
                attributes = {
                    "span.kind": span_kind,
                    "function.name": func.__name__,
                    "function.module": func.__module__,
                }
                
                if tags:
                    attributes.update(tags)
                
                attributes.update(kwargs)
                
                # Create span
                span, context_token = tracer._create_span(
                    operation_name=span_name,
                    span_kind=span_kind,
                    attributes=attributes
                )
                
                try:
                    # Execute function
                    result = func(*args, **func_kwargs)
                    
                    # Add result information if available
                    if result is not None:
                        span.set_attribute("function.result_type", type(result).__name__)
                        if hasattr(result, '__len__') and not isinstance(result, str):
                            span.set_attribute("function.result_length", len(result))
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    logger.error(f"Error in {span_name}: {e}")
                    raise
                    
                finally:
                    # End span
                    span.end()
                    if context_token:
                        from opentelemetry import context as context_api
                        context_api.detach(context_token)
            
            @functools.wraps(func)
            async def async_wrapper(*args, **func_kwargs):
                if not tracer.initialized:
                    logger.warning("Tracer not initialized, executing function without instrumentation")
                    return await func(*args, **func_kwargs)
                
                # Determine span name
                span_name = name or default_name or func.__name__
                
                # Build attributes
                attributes = {
                    "span.kind": span_kind,
                    "function.name": func.__name__,
                    "function.module": func.__module__,
                }
                
                if tags:
                    attributes.update(tags)
                
                attributes.update(kwargs)
                
                # Create span
                span, context_token = tracer._create_span(
                    operation_name=span_name,
                    span_kind=span_kind,
                    attributes=attributes
                )
                
                try:
                    # Execute async function
                    result = await func(*args, **func_kwargs)
                    
                    # Add result information if available
                    if result is not None:
                        span.set_attribute("function.result_type", type(result).__name__)
                        if hasattr(result, '__len__') and not isinstance(result, str):
                            span.set_attribute("function.result_length", len(result))
                    
                    span.set_status(Status(StatusCode.OK))
                    return result
                    
                except Exception as e:
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("error.message", str(e))
                    span.set_attribute("error.type", type(e).__name__)
                    logger.error(f"Error in {span_name}: {e}")
                    raise
                    
                finally:
                    # End span
                    span.end()
                    if context_token:
                        from opentelemetry import context as context_api
                        context_api.detach(context_token)
            
            # Return appropriate wrapper based on function type
            if inspect.iscoroutinefunction(func):
                return async_wrapper
            else:
                return wrapper
        
        # Handle both @decorator and @decorator(name="...") syntax
        if callable(func_or_name):
            return actual_decorator(func_or_name)
        else:
            return actual_decorator
    
    return decorator


# Create specific decorators
trace = _create_span_decorator("session", "trace")
agent = _create_span_decorator("agent", "agent")
task = _create_span_decorator("task", "task")
tool = _create_span_decorator("tool", "tool")
workflow = _create_span_decorator("workflow", "workflow")

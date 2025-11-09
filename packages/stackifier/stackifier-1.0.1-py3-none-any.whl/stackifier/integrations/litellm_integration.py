from typing import Optional, Dict, Any, List
import time

from ..trace import TraceHook
from ..models import Message, TimingMetrics, TokenMetrics, ToolCall


class LiteLLMTracer:
    def __init__(self, trace_hook: Optional[TraceHook] = None):
        self.trace = trace_hook or TraceHook()
        self._start_time = None
    
    def log_completion(
        self,
        messages: List[Dict[str, Any]],
        response: Any,
        start_time: Optional[float] = None,
        model: Optional[str] = None
    ) -> None:
        parsed_messages = []
        for msg in messages:
            role = msg.get("role", "user")
            content = msg.get("content")
            tool_calls = msg.get("tool_calls")
            
            tool_calls_objs = None
            if tool_calls:
                tool_calls_objs = [
                    ToolCall(
                        id=tc.get("id", ""),
                        name=tc.get("function", {}).get("name", ""),
                        arguments=tc.get("function", {}).get("arguments", {})
                    )
                    for tc in tool_calls
                ]
            
            parsed_messages.append(Message(
                role=role,
                content=content,
                tool_calls=tool_calls_objs
            ))
        
        if hasattr(response, "choices") and response.choices:
            choice = response.choices[0]
            assistant_content = None
            assistant_tool_calls = None
            
            if hasattr(choice, "message"):
                assistant_content = getattr(choice.message, "content", None)
                if hasattr(choice.message, "tool_calls") and choice.message.tool_calls:
                    assistant_tool_calls = [
                        ToolCall(
                            id=tc.id,
                            name=tc.function.name,
                            arguments=tc.function.arguments
                        )
                        for tc in choice.message.tool_calls
                    ]
            
            parsed_messages.append(Message(
                role="assistant",
                content=assistant_content,
                tool_calls=assistant_tool_calls
            ))
        
        timing = None
        if start_time:
            timing = TimingMetrics(
                total_latency_ms=(time.time() - start_time) * 1000
            )
        
        tokens = None
        if hasattr(response, "usage"):
            tokens = TokenMetrics(
                prompt_tokens=getattr(response.usage, "prompt_tokens", None),
                completion_tokens=getattr(response.usage, "completion_tokens", None),
                total_tokens=getattr(response.usage, "total_tokens", None)
            )
        
        event = self.trace.create_event(
            messages=parsed_messages,
            timing=timing,
            tokens=tokens,
            metadata={"model": model or getattr(response, "model", None)}
        )
        self.trace.on_event(event)
    
    def wrap_completion(self, completion_func):
        def wrapper(*args, **kwargs):
            start = time.time()
            response = completion_func(*args, **kwargs)
            
            messages = kwargs.get("messages", args[0] if args else [])
            model = kwargs.get("model")
            
            self.log_completion(messages, response, start, model)
            return response
        return wrapper

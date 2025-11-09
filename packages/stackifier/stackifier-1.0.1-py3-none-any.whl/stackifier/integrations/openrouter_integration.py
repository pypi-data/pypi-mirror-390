from typing import Optional, Dict, Any, List
import time
import json

from ..trace import TraceHook
from ..models import Message, TimingMetrics, TokenMetrics, ToolCall


class OpenRouterTracer:
    def __init__(self, trace_hook: Optional[TraceHook] = None):
        self.trace = trace_hook or TraceHook()
    
    def log_completion(
        self,
        messages: List[Dict[str, Any]],
        response: Dict[str, Any],
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
                            if isinstance(tc.get("function", {}).get("arguments"), dict)
                            else json.loads(tc.get("function", {}).get("arguments", "{}"))
                    )
                    for tc in tool_calls
                ]
            
            parsed_messages.append(Message(
                role=role,
                content=content,
                tool_calls=tool_calls_objs
            ))
        
        if "choices" in response and response["choices"]:
            choice = response["choices"][0]
            message = choice.get("message", {})
            
            assistant_content = message.get("content")
            assistant_tool_calls = None
            
            if "tool_calls" in message and message["tool_calls"]:
                assistant_tool_calls = [
                    ToolCall(
                        id=tc.get("id", ""),
                        name=tc.get("function", {}).get("name", ""),
                        arguments=tc.get("function", {}).get("arguments", {})
                            if isinstance(tc.get("function", {}).get("arguments"), dict)
                            else json.loads(tc.get("function", {}).get("arguments", "{}"))
                    )
                    for tc in message["tool_calls"]
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
        if "usage" in response:
            usage = response["usage"]
            tokens = TokenMetrics(
                prompt_tokens=usage.get("prompt_tokens"),
                completion_tokens=usage.get("completion_tokens"),
                total_tokens=usage.get("total_tokens")
            )
        
        metadata = {"model": model or response.get("model")}
        if "id" in response:
            metadata["openrouter_id"] = response["id"]
        
        event = self.trace.create_event(
            messages=parsed_messages,
            timing=timing,
            tokens=tokens,
            metadata=metadata
        )
        self.trace.on_event(event)
    
    def wrap_completion(self, completion_func):
        def wrapper(*args, **kwargs):
            start = time.time()
            response = completion_func(*args, **kwargs)
            
            messages = kwargs.get("messages", [])
            model = kwargs.get("model")
            
            self.log_completion(messages, response, start, model)
            return response
        return wrapper

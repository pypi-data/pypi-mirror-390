from typing import Optional, Dict, Any, List
import time

from ..trace import TraceHook
from ..models import Message, TimingMetrics, TokenMetrics, ToolCall


class LangChainTracer:
    def __init__(self, trace_hook: Optional[TraceHook] = None):
        self.trace = trace_hook or TraceHook()
        self._run_data = {}
    
    def log_chain_start(self, run_id: str, inputs: Dict[str, Any]) -> None:
        self._run_data[run_id] = {
            "start_time": time.time(),
            "inputs": inputs,
            "messages": []
        }
    
    def log_chain_end(self, run_id: str, outputs: Dict[str, Any]) -> None:
        if run_id not in self._run_data:
            return
        
        run_info = self._run_data.pop(run_id)
        elapsed = (time.time() - run_info["start_time"]) * 1000
        
        messages = run_info.get("messages", [])
        if outputs.get("output"):
            messages.append(Message(role="assistant", content=str(outputs["output"])))
        
        event = self.trace.create_event(
            messages=messages,
            timing=TimingMetrics(total_latency_ms=elapsed),
            metadata={"inputs": run_info["inputs"], "outputs": outputs}
        )
        self.trace.on_event(event)
    
    def log_llm_start(self, run_id: str, prompts: List[str], **kwargs) -> None:
        if run_id not in self._run_data:
            self._run_data[run_id] = {"messages": [], "start_time": time.time()}
        
        for prompt in prompts:
            self._run_data[run_id]["messages"].append(
                Message(role="user", content=prompt)
            )
    
    def log_llm_end(self, run_id: str, response: Any) -> None:
        if run_id not in self._run_data:
            return
        
        if hasattr(response, "generations"):
            for gen_list in response.generations:
                for gen in gen_list:
                    content = gen.text if hasattr(gen, "text") else str(gen)
                    self._run_data[run_id]["messages"].append(
                        Message(role="assistant", content=content)
                    )
        
        tokens = None
        if hasattr(response, "llm_output") and response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})
            if token_usage:
                tokens = TokenMetrics(
                    prompt_tokens=token_usage.get("prompt_tokens"),
                    completion_tokens=token_usage.get("completion_tokens"),
                    total_tokens=token_usage.get("total_tokens")
                )
    
    def get_callback_handler(self):
        try:
            from langchain.callbacks.base import BaseCallbackHandler
            
            class StackifierCallbackHandler(BaseCallbackHandler):
                def __init__(self, tracer):
                    self.tracer = tracer
                
                def on_chain_start(self, serialized, inputs, run_id=None, **kwargs):
                    self.tracer.log_chain_start(str(run_id), inputs)
                
                def on_chain_end(self, outputs, run_id=None, **kwargs):
                    self.tracer.log_chain_end(str(run_id), outputs)
                
                def on_llm_start(self, serialized, prompts, run_id=None, **kwargs):
                    self.tracer.log_llm_start(str(run_id), prompts, **kwargs)
                
                def on_llm_end(self, response, run_id=None, **kwargs):
                    self.tracer.log_llm_end(str(run_id), response)
            
            return StackifierCallbackHandler(self)
        except ImportError:
            raise ImportError("langchain is required for LangChainTracer. Install with: pip install langchain")

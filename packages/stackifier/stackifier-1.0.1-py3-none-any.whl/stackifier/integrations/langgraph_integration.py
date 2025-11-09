from typing import Optional, Dict, Any, List
import time

from ..trace import TraceHook
from ..models import Message, TimingMetrics, TokenMetrics, GraphMetadata, ToolCall


class LangGraphTracer:
    def __init__(self, trace_hook: Optional[TraceHook] = None):
        self.trace = trace_hook or TraceHook()
        self._graph_data = {}
    
    def log_node_start(
        self,
        graph_id: str,
        node_name: str,
        step_index: int,
        inputs: Dict[str, Any]
    ) -> None:
        key = f"{graph_id}:{step_index}"
        self._graph_data[key] = {
            "start_time": time.time(),
            "node_name": node_name,
            "step_index": step_index,
            "graph_id": graph_id,
            "inputs": inputs,
            "messages": []
        }
    
    def log_node_end(
        self,
        graph_id: str,
        step_index: int,
        outputs: Dict[str, Any]
    ) -> None:
        key = f"{graph_id}:{step_index}"
        if key not in self._graph_data:
            return
        
        node_data = self._graph_data.pop(key)
        elapsed = (time.time() - node_data["start_time"]) * 1000
        
        messages = node_data.get("messages", [])
        if "messages" in outputs:
            for msg in outputs["messages"]:
                if isinstance(msg, dict):
                    messages.append(Message(
                        role=msg.get("role", "assistant"),
                        content=msg.get("content")
                    ))
                elif hasattr(msg, "content"):
                    role = getattr(msg, "type", "assistant")
                    messages.append(Message(role=role, content=msg.content))
        
        event = self.trace.create_event(
            messages=messages,
            timing=TimingMetrics(total_latency_ms=elapsed),
            graph=GraphMetadata(
                node_path=node_data["node_name"],
                step_index=node_data["step_index"],
                graph_id=node_data["graph_id"]
            ),
            metadata={"inputs": node_data["inputs"], "outputs": outputs}
        )
        self.trace.on_event(event)
    
    def log_tool_call(
        self,
        graph_id: str,
        step_index: int,
        tool_name: str,
        tool_input: Dict[str, Any],
        tool_output: Any,
        latency_ms: float
    ) -> None:
        key = f"{graph_id}:{step_index}"
        if key in self._graph_data:
            if "tool_latencies" not in self._graph_data[key]:
                self._graph_data[key]["tool_latencies"] = {}
            self._graph_data[key]["tool_latencies"][tool_name] = latency_ms
    
    def create_checkpoint_callback(self):
        class StackifierCheckpoint:
            def __init__(self, tracer):
                self.tracer = tracer
                self.graph_id = None
                self.step_index = 0
            
            def __call__(self, state, config):
                if self.graph_id is None:
                    self.graph_id = config.get("run_id", str(time.time()))
                
                node_name = config.get("tags", [None])[0] if config.get("tags") else "unknown"
                
                self.tracer.log_node_start(
                    self.graph_id,
                    node_name,
                    self.step_index,
                    state
                )
                self.step_index += 1
                
                return state
        
        return StackifierCheckpoint(self)

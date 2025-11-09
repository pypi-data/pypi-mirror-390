from typing import Optional, List, Dict, Any
import uuid
import time
from contextlib import contextmanager

from .models import Event, Message, TimingMetrics, TokenMetrics, WhatsAppMetadata, GraphMetadata
from .storage import Writer, FileWriter


class TraceHook:
    def __init__(self, storage: Optional[Writer] = None, conversation_id: Optional[str] = None):
        self.storage = storage or FileWriter()
        self.conversation_id = conversation_id or str(uuid.uuid4())
        self.run_id = str(int(time.time() * 1000))
        self._start_time = None
        self._current_event: Optional[Event] = None
    
    def on_event(self, event: Event) -> None:
        self.storage.write(event)
    
    def create_event(
        self,
        messages: List[Message],
        timing: Optional[TimingMetrics] = None,
        tokens: Optional[TokenMetrics] = None,
        wa_meta: Optional[WhatsAppMetadata] = None,
        graph: Optional[GraphMetadata] = None,
        metadata: Optional[Dict[str, Any]] = None,
        conversation_id: Optional[str] = None,
        run_id: Optional[str] = None
    ) -> Event:
        return Event(
            conversation_id=conversation_id or self.conversation_id,
            run_id=run_id or self.run_id,
            messages=messages,
            timing=timing,
            tokens=tokens,
            wa_meta=wa_meta,
            graph=graph,
            metadata=metadata or {}
        )
    
    def log_message(
        self,
        role: str,
        content: Optional[str] = None,
        tool_calls: Optional[List[Dict[str, Any]]] = None,
        tool_call_id: Optional[str] = None,
        name: Optional[str] = None,
        **kwargs
    ) -> None:
        from .models import ToolCall
        
        tool_calls_objs = None
        if tool_calls:
            tool_calls_objs = [
                ToolCall(
                    id=tc.get("id", str(uuid.uuid4())),
                    name=tc.get("name", tc.get("function", {}).get("name", "")),
                    arguments=tc.get("arguments", tc.get("function", {}).get("arguments", {}))
                )
                for tc in tool_calls
            ]
        
        msg = Message(
            role=role,
            content=content,
            tool_calls=tool_calls_objs,
            tool_call_id=tool_call_id,
            name=name
        )
        
        event = self.create_event(messages=[msg], **kwargs)
        self.on_event(event)
    
    @contextmanager
    def trace_span(self, name: str):
        start = time.time()
        span_data = {"name": name, "start": start}
        
        try:
            yield span_data
        finally:
            span_data["duration_ms"] = (time.time() - start) * 1000
    
    def flush(self) -> None:
        self.storage.flush()
    
    def new_conversation(self, conversation_id: Optional[str] = None) -> "TraceHook":
        self.flush()
        return TraceHook(
            storage=self.storage,
            conversation_id=conversation_id or str(uuid.uuid4())
        )

from typing import Any, Dict, List, Optional, Literal
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone
import json


@dataclass
class ToolCall:
    id: str
    name: str
    arguments: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Message:
    role: Literal["system", "user", "assistant", "tool"]
    content: Optional[str] = None
    tool_calls: Optional[List[ToolCall]] = None
    tool_call_id: Optional[str] = None
    name: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        data = {"role": self.role}
        if self.content is not None:
            data["content"] = self.content
        if self.tool_calls:
            data["tool_calls"] = [tc.to_dict() for tc in self.tool_calls]
        if self.tool_call_id:
            data["tool_call_id"] = self.tool_call_id
        if self.name:
            data["name"] = self.name
        return data


@dataclass
class TimingMetrics:
    time_to_first_token_ms: Optional[float] = None
    total_latency_ms: Optional[float] = None
    tool_latencies_ms: Optional[Dict[str, float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class TokenMetrics:
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    cost_usd: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class WhatsAppMetadata:
    direction: Literal["in", "out"]
    template_category: Optional[Literal["service", "utility", "marketing"]] = None
    delivered: Optional[bool] = None
    read: Optional[bool] = None
    blocked_reported: Optional[bool] = None
    message_id: Optional[str] = None
    phone_number: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class GraphMetadata:
    node_path: Optional[str] = None
    step_index: Optional[int] = None
    graph_id: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class Event:
    conversation_id: str
    run_id: str
    timestamp: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    messages: List[Message] = field(default_factory=list)
    timing: Optional[TimingMetrics] = None
    tokens: Optional[TokenMetrics] = None
    wa_meta: Optional[WhatsAppMetadata] = None
    graph: Optional[GraphMetadata] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        data = {
            "conversation_id": self.conversation_id,
            "run_id": self.run_id,
            "timestamp": self.timestamp,
            "messages": [m.to_dict() for m in self.messages],
        }
        if self.timing:
            data["timing"] = self.timing.to_dict()
        if self.tokens:
            data["tokens"] = self.tokens.to_dict()
        if self.wa_meta:
            data["wa_meta"] = self.wa_meta.to_dict()
        if self.graph:
            data["graph"] = self.graph.to_dict()
        if self.metadata:
            data["metadata"] = self.metadata
        return data
    
    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False, separators=(',', ':'))

from typing import Dict, Any, Optional, List
from .models import Event, Message, WhatsAppMetadata, ToolCall


class WhatsAppMetaAdapter:
    @staticmethod
    def to_event(payload: Dict[str, Any], conversation_id: Optional[str] = None, run_id: Optional[str] = None) -> Event:
        from .trace import TraceHook
        import uuid
        import time
        
        conversation_id = conversation_id or str(uuid.uuid4())
        run_id = run_id or str(int(time.time() * 1000))
        
        messages = []
        wa_meta = None
        
        if "entry" in payload:
            for entry in payload["entry"]:
                for change in entry.get("changes", []):
                    value = change.get("value", {})
                    
                    for msg in value.get("messages", []):
                        phone = msg.get("from", "")
                        content = None
                        
                        if msg.get("type") == "text":
                            content = msg.get("text", {}).get("body", "")
                        elif msg.get("type") == "image":
                            content = f"[Image: {msg.get('image', {}).get('id', '')}]"
                        elif msg.get("type") == "document":
                            content = f"[Document: {msg.get('document', {}).get('filename', '')}]"
                        
                        messages.append(Message(role="user", content=content))
                        wa_meta = WhatsAppMetadata(
                            direction="in",
                            message_id=msg.get("id"),
                            phone_number=phone
                        )
                    
                    for status in value.get("statuses", []):
                        wa_meta = WhatsAppMetadata(
                            direction="out",
                            message_id=status.get("id"),
                            delivered=status.get("status") == "delivered",
                            read=status.get("status") == "read"
                        )
        
        trace = TraceHook(conversation_id=conversation_id)
        return trace.create_event(
            messages=messages,
            wa_meta=wa_meta,
            conversation_id=conversation_id,
            run_id=run_id
        )


class BspWebhookAdapter:
    @staticmethod
    def to_event(payload: Dict[str, Any], conversation_id: Optional[str] = None, run_id: Optional[str] = None) -> Event:
        from .trace import TraceHook
        import uuid
        import time
        
        conversation_id = conversation_id or str(uuid.uuid4())
        run_id = run_id or str(int(time.time() * 1000))
        
        messages = []
        wa_meta = None
        
        phone = payload.get("From", "").replace("whatsapp:", "")
        body = payload.get("Body", "")
        msg_sid = payload.get("MessageSid", "")
        status = payload.get("MessageStatus", "")
        
        if body:
            messages.append(Message(role="user", content=body))
        
        wa_meta = WhatsAppMetadata(
            direction="in" if body else "out",
            message_id=msg_sid,
            phone_number=phone,
            delivered=status == "delivered",
            read=status == "read"
        )
        
        trace = TraceHook(conversation_id=conversation_id)
        return trace.create_event(
            messages=messages,
            wa_meta=wa_meta,
            conversation_id=conversation_id,
            run_id=run_id
        )


class TwilioAdapter(BspWebhookAdapter):
    pass

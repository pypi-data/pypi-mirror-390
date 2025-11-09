import pytest
import os
import tempfile
import json
from stackifier import TraceHook, FileWriter, Message, TimingMetrics, TokenMetrics


def test_basic_functionality():
    """Test basic TraceHook functionality"""
    with tempfile.TemporaryDirectory() as temp_dir:
        test_file = os.path.join(temp_dir, "test.jsonl")
        
        # Initialize TraceHook
        trace = TraceHook(storage=FileWriter(path=test_file))
        
        # Log a message
        trace.log_message(role="user", content="Test message")
        
        # Create and log an event
        event = trace.create_event(
            messages=[Message(role="assistant", content="Response")],
            timing=TimingMetrics(total_latency_ms=100),
            tokens=TokenMetrics(prompt_tokens=5, completion_tokens=10)
        )
        trace.on_event(event)
        
        # Flush data
        trace.flush()
        
        # Verify file was created and contains data
        assert os.path.exists(test_file)
        with open(test_file, 'r') as f:
            lines = f.readlines()
            assert len(lines) >= 2  # At least message and event
            
        # Verify JSON structure
        for line in lines:
            data = json.loads(line.strip())
            assert "timestamp" in data
            assert "conversation_id" in data
            assert "run_id" in data


def test_adapters():
    """Test adapter initialization"""
    from stackifier import WhatsAppMetaAdapter, TwilioAdapter
    
    # Test WhatsApp adapter
    whatsapp_adapter = WhatsAppMetaAdapter()
    assert whatsapp_adapter is not None
    
    # Test Twilio adapter
    twilio_adapter = TwilioAdapter()
    assert twilio_adapter is not None

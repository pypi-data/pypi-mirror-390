# Stackifier

[![PyPI version](https://badge.fury.io/py/stackifier.svg)](https://pypi.org/project/stackifier/)
[![Python versions](https://img.shields.io/pypi/pyversions/stackifier.svg)](https://pypi.org/project/stackifier/)
[![License](https://img.shields.io/github/license/BryanTheLai/pip-stackifier.svg)](https://github.com/BryanTheLai/pip-stackifier/blob/main/LICENSE)
[![Documentation](https://img.shields.io/badge/docs-mkdocs-blue.svg)](https://bryanthel.github.io/pip-stackifier)
[![Downloads](https://pepy.tech/badge/stackifier)](https://pepy.tech/project/stackifier)

**Lightweight data collection library for WhatsApp AI agents** - Log conversations, tool calls, timing, and metrics to JSONL or S3 with OpenAI-compatible schema.

## Features

- **OpenAI Chat Schema**: Store every turn using standard `{system,user,assistant,tool}` roles with function calling support
- **Local First**: Append to JSONL files by default, zero-ops setup
- **S3 Optional**: Drop-in cloud storage with boto3
- **WhatsApp Adapters**: Normalize Meta Cloud API and Twilio webhooks to unified events
- **LLM Integrations**: Native support for LiteLLM, LangChain, LangGraph, OpenRouter
- **Rich Metrics**: Capture timing, tokens, costs, tool latencies, graph step info
- **Simple API**: One `TraceHook`, call `on_event()`, done

[Github](https://github.com/BryanTheLai/pip-stackifier)

## Installation

```bash
pip install stackifier

# Optional: For S3 storage
pip install stackifier[s3]

# Optional: For LangChain integration
pip install stackifier[langchain]

# Optional: For LangGraph integration
pip install stackifier[langgraph]

# Optional: For LiteLLM integration
pip install stackifier[litellm]

# Install all optional dependencies
pip install stackifier[all]
```

## Quick Start

### Basic Logging

```python
from stackifier import TraceHook, FileWriter

trace = TraceHook(storage=FileWriter(path="logs/conversations.jsonl"))

trace.log_message(
    role="user",
    content="Hello! What's the weather?"
)

trace.log_message(
    role="assistant",
    content="Let me check that for you.",
    tool_calls=[{"id": "call_1", "name": "get_weather", "arguments": {"city": "NYC"}}]
)

trace.log_message(
    role="tool",
    content="Sunny, 72°F",
    tool_call_id="call_1",
    name="get_weather"
)

trace.flush()
```

### S3 Storage

```python
from stackifier import TraceHook, S3Writer

trace = TraceHook(
    storage=S3Writer(
        bucket="my-logs",
        key_template="app/{env}/date={date}/conv_id={conv_id}/run_id={run_id}/log.jsonl",
        env="production"
    )
)

trace.log_message(role="user", content="Hello")
trace.flush()
```

### WhatsApp Webhook Adapters

```python
from stackifier import TraceHook, WhatsAppMetaAdapter

trace = TraceHook()
adapter = WhatsAppMetaAdapter()

event = adapter.to_event(webhook_payload)
trace.on_event(event)
trace.flush()
```

## Integrations

### LiteLLM

```python
from stackifier import TraceHook, LiteLLMTracer
import litellm
import time

trace = TraceHook()
tracer = LiteLLMTracer(trace)

messages = [{"role": "user", "content": "Hello"}]
start = time.time()
response = litellm.completion(model="gpt-4", messages=messages)
tracer.log_completion(messages, response, start, model="gpt-4")
trace.flush()
```

### LangChain

```python
from stackifier import TraceHook, LangChainTracer
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage

trace = TraceHook()
tracer = LangChainTracer(trace)

chat = ChatOpenAI(callbacks=[tracer.get_callback_handler()])
response = chat([HumanMessage(content="Hello")])
trace.flush()
```

### LangGraph

```python
from stackifier import TraceHook, LangGraphTracer

trace = TraceHook()
tracer = LangGraphTracer(trace)

tracer.log_node_start(
    graph_id="graph_1",
    node_name="agent",
    step_index=0,
    inputs={"messages": [{"role": "user", "content": "Hi"}]}
)

tracer.log_node_end(
    graph_id="graph_1",
    step_index=0,
    outputs={"messages": [{"role": "assistant", "content": "Hello!"}]}
)

trace.flush()
```

### OpenRouter

```python
from stackifier import TraceHook, OpenRouterTracer
import requests
import time

trace = TraceHook()
tracer = OpenRouterTracer(trace)

messages = [{"role": "user", "content": "Hello"}]
start = time.time()

response = requests.post(
    "https://openrouter.ai/api/v1/chat/completions",
    headers={"Authorization": f"Bearer {api_key}"},
    json={"model": "openai/gpt-4", "messages": messages}
).json()

tracer.log_completion(messages, response, start)
trace.flush()
```

## Event Schema

Each event logged follows the OpenAI chat message format:

```json
{
  "conversation_id": "uuid",
  "run_id": "timestamp",
  "timestamp": "2024-01-01T12:00:00",
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    },
    {
      "role": "assistant",
      "content": "Hi there!",
      "tool_calls": [
        {
          "id": "call_1",
          "name": "search",
          "arguments": {"query": "weather"}
        }
      ]
    },
    {
      "role": "tool",
      "content": "Result",
      "tool_call_id": "call_1",
      "name": "search"
    }
  ],
  "timing": {
    "time_to_first_token_ms": 150,
    "total_latency_ms": 500,
    "tool_latencies_ms": {"search": 200}
  },
  "tokens": {
    "prompt_tokens": 10,
    "completion_tokens": 20,
    "total_tokens": 30,
    "cost_usd": 0.001
  },
  "wa_meta": {
    "direction": "in",
    "message_id": "msg_123",
    "phone_number": "+1234567890",
    "delivered": true,
    "read": false
  },
  "graph": {
    "node_path": "agent_node",
    "step_index": 0,
    "graph_id": "graph_1"
  },
  "metadata": {
    "model": "gpt-4",
    "custom_field": "value"
  }
}
```

## API Reference

### TraceHook

Main interface for logging events.

```python
TraceHook(storage: Optional[Writer] = None, conversation_id: Optional[str] = None)
```

**Methods:**
- `on_event(event: Event)` - Log an event
- `log_message(role, content, tool_calls, ...)` - Quick log a message
- `create_event(messages, timing, tokens, ...)` - Create event object
- `flush()` - Force write buffered data
- `new_conversation(conversation_id)` - Start new conversation

### Storage Writers

**FileWriter**
```python
FileWriter(path: str = "dataset/whatsapp_agent/convos.jsonl")
```

**S3Writer**
```python
S3Writer(
    bucket: str,
    key_template: str = "app/{env}/date={date}/conv_id={conv_id}/run_id={run_id}/log.jsonl",
    env: str = "dev",
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    region_name: str = "us-east-1"
)
```

### Adapters

**WhatsAppMetaAdapter**
```python
WhatsAppMetaAdapter.to_event(payload: Dict) -> Event
```

**TwilioAdapter / BspWebhookAdapter**
```python
TwilioAdapter.to_event(payload: Dict) -> Event
```

## Architecture

```
┌─────────────────┐
│  Your AI Agent  │
│  (LangGraph/    │
│   LangChain/    │
│   LiteLLM)      │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   TraceHook     │
│  (on_event)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│     Writer      │
│  ┌───────────┐  │
│  │ FileWriter│  │
│  └───────────┘  │
│  ┌───────────┐  │
│  │ S3Writer  │  │
│  └───────────┘  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  JSONL Storage  │
│  (OpenAI Schema)│
└─────────────────┘
```

## Use Cases

- **Debug production issues**: Replay exact conversation flows
- **Improve prompts**: Analyze real user interactions
- **Monitor costs**: Track token usage and API costs
- **Optimize latency**: Identify slow tool calls or LLM responses
- **Compliance**: Keep audit logs of all AI interactions
- **A/B testing**: Compare different agent configurations

## Design Principles

1. **Zero overhead by default**: JSONL files, no external dependencies
2. **OpenAI compatible**: Works with any tool expecting OpenAI format
3. **Drop-in integrations**: Minimal code changes to existing agents
4. **Production ready**: Buffering, error handling, proper cleanup
5. **Future proof**: Clean separation for adding RL/eval layers later

## Build & Publish

```bash
python -m pip install build twine
python -m build
python -m twine upload dist/*
```

## Contributing

Contributions welcome! Please:
1. Keep it simple and focused on data collection
2. Follow OpenAI chat schema standards
3. Add tests for new integrations
4. Update README with examples

## License

MIT License - See LICENSE file for details

## Acknowledgments

Inspired by production needs in WhatsApp AI agents. Built for simplicity and reliability.

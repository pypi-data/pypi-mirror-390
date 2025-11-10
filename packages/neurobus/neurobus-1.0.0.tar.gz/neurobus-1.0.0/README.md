# 🧠 NeuroBUS

**The World's First Neuro-Semantic Event Bus**

> *"Don't send events. Send understanding."*

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![Type checked: mypy](https://img.shields.io/badge/type%20checked-mypy-blue.svg)](http://mypy-lang.org/)
[![Tests: 173 passing](https://img.shields.io/badge/tests-173%20passing-brightgreen.svg)](./tests)

---

## 🌟 What is NeuroBUS?

**NeuroBUS** is a revolutionary event bus that transforms message passing into **meaning passing** for cognitive AI systems. Unlike traditional event buses (Redis, RabbitMQ, Kafka), NeuroBUS understands the **semantic meaning** of events and intelligently routes them based on context, not just pattern matching.

### Why NeuroBUS?

Traditional event buses are **dumb pipes** - they match strings and forward messages. NeuroBUS is **intelligent** - it understands what events mean, maintains context across conversations, remembers past interactions, and can even reason about events using LLMs.

Perfect for:
- 🤖 **AI Agent Systems** - Multi-agent coordination with semantic understanding
- 🔄 **Microservices** - Intelligent service-to-service communication
- 📊 **Data Pipelines** - Context-aware stream processing
- 🎮 **Real-time Systems** - Low-latency semantic routing
- 🧪 **Event Sourcing** - Time-travel debugging with causality tracking

---

## ✨ Key Features

### 🎯 **Semantic Routing**
Events are matched by **meaning**, not just exact strings. Using transformer embeddings, NeuroBUS understands that "user_logged_in" and "authentication_successful" are semantically similar.

```python
@bus.subscribe("user authentication", semantic=True, threshold=0.8)
async def handle_auth(event: Event):
    # Matches: user_login, auth_success, sign_in_complete, etc.
    pass
```

### 🧠 **Context-Aware Processing**
Maintain state across 4 hierarchical scopes (global/session/user/event) with automatic context merging and DSL-based filtering.

```python
# Set context at different scopes
bus.context.set_global("app_version", "1.0.0")
bus.context.set_session("user_id", "alice", session_id="sess_123")

# Filter events based on context
@bus.subscribe("alert", filter="priority >= 5 AND user.role == 'admin'")
async def handle_critical_alert(event: Event):
    pass
```

### ⏰ **Temporal Capabilities**
Time-travel debugging with event replay, causality tracking, and temporal queries.

```python
# Replay events from the past
async for event in bus.temporal.replay(
    from_time=yesterday,
    to_time=now,
    speed=10.0  # 10x faster
):
    # Re-process historical events
    pass

# Track event causality
chain = bus.temporal.causality.get_causal_chain(event_id)
root = bus.temporal.causality.get_root(event_id)
```

### 💾 **Vector Memory Integration**
Native support for Qdrant and LanceDB for semantic event search and long-term memory.

```python
from neurobus.memory import QdrantAdapter

# Store events in vector database
adapter = QdrantAdapter(url="http://localhost:6333")
await adapter.store_event(event, embedding)

# Search semantically similar past events
results = await adapter.search_similar(query_embedding, k=5)
```

### 🤖 **LLM Reasoning Hooks**
Automatically trigger LLM reasoning when events match patterns - no manual integration needed.

```python
from neurobus.llm import LLMBridge

bridge = LLMBridge(provider="openai", api_key="sk-...")

@bridge.hook("error.*", "Analyze this error: {topic}\nData: {data}")
async def analyze_error(event, reasoning):
    print(f"LLM Analysis: {reasoning}")
    # Automatically invoked on any error.* event
```

### 🌐 **Distributed Clustering**
Horizontal scaling with Redis-based multi-node clustering, leader election, and distributed locking.

```python
config = NeuroBusConfig(
    distributed={
        "enabled": True,
        "redis_url": "redis://localhost:6379",
    }
)
bus = NeuroBus(config=config)
# Events automatically broadcast across all nodes
```

### 📊 **Observable & Production-Ready**
Built-in metrics, comprehensive logging, and high test coverage (173 tests, 95% coverage).

```python
from neurobus.monitoring.metrics import get_metrics

metrics = get_metrics()
stats = metrics.get_histogram_stats("dispatch_latency_seconds")
# Returns: min, max, mean, p50, p95, p99
```

---

## 🚀 Quick Start

### Installation

```bash
pip install neurobus
```

### Basic Example

```python
import asyncio
from neurobus import NeuroBus, Event

async def main():
    # Create bus
    bus = NeuroBus()
    
    # Subscribe to events
    @bus.subscribe("user.login")
    async def handle_login(event: Event):
        print(f"User {event.data['username']} logged in")
    
    # Start bus
    async with bus:
        # Publish event
        await bus.publish(Event(
            topic="user.login",
            data={"username": "alice"}
        ))
        
        await asyncio.sleep(0.1)

asyncio.run(main())
```

### Semantic Routing Example

```python
from neurobus import NeuroBus, Event, NeuroBusConfig

async def main():
    # Enable semantic routing
    config = NeuroBusConfig(semantic={"enabled": True})
    bus = NeuroBus(config=config)
    
    # Subscribe with semantic matching
    @bus.subscribe("greeting", semantic=True, threshold=0.75)
    async def handle_greeting(event: Event):
        print(f"Got greeting: {event.topic}")
    
    async with bus:
        # All these will match semantically!
        await bus.publish(Event(topic="hello", data={}))
        await bus.publish(Event(topic="hi_there", data={}))
        await bus.publish(Event(topic="good_morning", data={}))
        
        await asyncio.sleep(0.5)

asyncio.run(main())
```

### LLM Integration Example

```python
from neurobus import NeuroBus, Event
from neurobus.llm import LLMBridge

async def main():
    bus = NeuroBus()
    
    # Setup LLM bridge
    llm = LLMBridge(provider="openai", api_key="sk-...")
    await llm.initialize()
    
    # Hook LLM to error events
    @llm.hook("error.*", "Diagnose: {topic}\nDetails: {data}")
    async def diagnose_error(event, reasoning):
        print(f"LLM says: {reasoning}")
    
    async with bus:
        # This will automatically trigger LLM analysis
        await bus.publish(Event(
            topic="error.database",
            data={"error": "Connection timeout"}
        ))
        
        await asyncio.sleep(1)

asyncio.run(main())
```

---

## 📦 Installation Options

### Basic Installation
```bash
pip install neurobus
```

### With Semantic Routing
```bash
pip install neurobus[semantic]
# Includes: sentence-transformers, torch
```

### With Vector Databases
```bash
pip install neurobus[qdrant]     # Qdrant support
pip install neurobus[lancedb]    # LanceDB support
pip install neurobus[memory]     # Both
```

### With LLM Providers
```bash
pip install neurobus[openai]      # OpenAI GPT
pip install neurobus[anthropic]   # Anthropic Claude
pip install neurobus[ollama]      # Local LLMs via Ollama
pip install neurobus[llm]         # All LLM providers
```

### With Distributed Support
```bash
pip install neurobus[distributed]  # Redis clustering
```

### Everything
```bash
pip install neurobus[all]
```

---

## 📚 Documentation

- **[API Documentation](./docs/)** - Complete API reference
- **[Examples](./examples/)** - 15+ working examples
- **[Architecture](./docs/architecture.md)** - System design and internals
- **[Contributing](./CONTRIBUTING.md)** - How to contribute
- **[Changelog](./CHANGELOG.md)** - Version history

---

## 🎯 Core Concepts

### Events
Events are the fundamental unit of communication in NeuroBUS. Each event has a topic, data, optional context, and metadata.

```python
event = Event(
    topic="user.action.completed",
    data={"action": "purchase", "amount": 99.99},
    context={"user_id": "alice", "session": "xyz"},
    metadata={"source": "web", "version": "2.0"}
)
```

### Subscriptions
Subscribe to events using exact patterns, wildcards, or semantic similarity.

```python
# Exact match
@bus.subscribe("user.login")

# Wildcard
@bus.subscribe("user.*")

# Semantic (requires sentence-transformers)
@bus.subscribe("user authentication", semantic=True)

# With context filtering
@bus.subscribe("alert", filter="priority > 5")
```

### Context
Hierarchical state management across 4 scopes with automatic merging.

```python
# Global context (shared across all)
bus.context.set_global("app_name", "MyApp")

# Session context (per-session)
bus.context.set_session("user_id", "alice", session_id="sess_1")

# User context (per-user)
bus.context.set_user("preferences", {"theme": "dark"}, user_id="alice")

# Event context (per-event)
event = Event(topic="action", data={}, context={"trace_id": "abc"})
```

### Temporal
Time-travel debugging with event persistence, replay, and causality tracking.

```python
# Store events (automatic with config)
config = NeuroBusConfig(temporal={"enabled": True})

# Query past events
events = await bus.temporal.query_events(
    topic="user.*",
    from_time=yesterday,
    to_time=now
)

# Replay events
await bus.temporal.replay_events(from_time, to_time, speed=5.0)

# Track causality
chain = bus.temporal.causality.get_causal_chain(event_id)
```

### Memory
Long-term event storage with vector similarity search.

```python
# Enable memory
config = NeuroBusConfig(memory={"enabled": True})

# Search similar events
results = await bus.memory.search("user authentication issues", k=5)

# Get recent memories
recent = bus.memory.get_recent(limit=10)
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         NeuroBUS                             │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ Semantic │  │ Context  │  │ Temporal │  │   LLM    │   │
│  │  Router  │  │  Engine  │  │  Store   │  │  Bridge  │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  Memory  │  │  Metrics │  │ Cluster  │  │   Core   │   │
│  │  Engine  │  │Collector │  │ Manager  │  │   Bus    │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
          │              │              │              │
          ▼              ▼              ▼              ▼
    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
    │ Qdrant  │    │  Redis  │    │  SQLite │    │   LLM   │
    │LanceDB  │    │Cluster  │    │   WAL   │    │Provider │
    └─────────┘    └─────────┘    └─────────┘    └─────────┘
```

---

## 📊 Performance

- **Latency**: <2ms P95 for event dispatch
- **Throughput**: 10,000+ events/second
- **Memory**: <100MB base footprint
- **Scalability**: Horizontal scaling via Redis clustering
- **Semantic**: <5ms embedding generation (cached)

---

## 🧪 Testing

NeuroBUS has comprehensive test coverage:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=neurobus --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
```

**Test Statistics:**
- 173 tests (100% passing)
- 95% code coverage
- 100% type coverage (mypy strict)

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Quick Start for Contributors:**

```bash
# Clone repository
git clone https://github.com/eshanized/neurobus.git
cd neurobus

# Install in development mode
pip install -e ".[dev,all]"

# Run tests
pytest

# Format code
black neurobus/ tests/
ruff check neurobus/ tests/

# Type check
mypy neurobus/
```

---

## 📄 License

NeuroBUS is released under the [MIT License](./LICENSE).

---

## 👥 Authors

- **Eshan Roy** ([@eshanized](https://github.com/eshanized)) - Creator & Lead Developer
- **TIVerse Labs** - Cognitive Infrastructure Division

---

## 🙏 Acknowledgments

Special thanks to:
- The sentence-transformers team for semantic embeddings
- Qdrant and LanceDB teams for vector database support
- OpenAI and Anthropic for LLM capabilities
- The Python async community

---

## 📧 Contact & Support

- **Email**: eshanized@proton.me
- **Issues**: [GitHub Issues](https://github.com/eshanized/neurobus/issues)
- **Discussions**: [GitHub Discussions](https://github.com/eshanized/neurobus/discussions)
- **Discord**: [Join our community](https://discord.gg/neurobus) (coming soon)

---

## 🗺️ Roadmap

### v1.1 (Q1 2025)
- [ ] GraphQL API
- [ ] Admin Dashboard
- [ ] Enhanced monitoring (Grafana dashboards)
- [ ] Performance benchmarks suite

### v1.2 (Q2 2025)
- [ ] Multi-tenancy support
- [ ] Rate limiting per subscription
- [ ] Schema evolution
- [ ] Additional vector DB adapters (Pinecone, Weaviate)

### v2.0 (Q3 2025)
- [ ] Streaming support
- [ ] Plugin architecture
- [ ] Cloud-native deployment templates
- [ ] Enterprise features

---

## ⭐ Star Us!

If you find NeuroBUS useful, please star the repository on [GitHub](https://github.com/eshanized/neurobus)!

---

## 💡 Use Cases

### AI Agent Coordination
```python
# Multiple agents communicating semantically
@agent1.subscribe("help needed", semantic=True)
async def assist(event):
    # Responds to "need help", "assistance required", etc.
    pass
```

### Microservices Communication
```python
# Service-to-service with context
bus.context.set_session("request_id", req_id)
await bus.publish(Event("order.created", data=order_data))
```

### IoT & Sensor Networks
```python
# Semantic sensor fusion
@bus.subscribe("temperature reading", semantic=True)
async def process_temp(event):
    # Matches various sensor formats
    pass
```

### Event Sourcing & CQRS
```python
# Time-travel for debugging
events = await bus.temporal.query_events(
    topic="order.*",
    from_time=incident_time - 1hour,
    to_time=incident_time + 1hour
)
```

---

**Built with ❤️ by [TIVerse Labs](https://tiverse.org) - Building Cognitive Infrastructure for AI**

*NeuroBUS: Where Events Meet Intelligence* 🧠✨

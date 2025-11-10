# Changelog

All notable changes to NeuroBUS will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2025-11-10

### 🎉 Production Release

NeuroBUS v1.0.0 is now production-ready with 100% specification compliance!

### Added

#### Core Features (Phase 1)
- Event-driven architecture with pub/sub messaging
- Pattern matching with wildcards
- Async parallel event dispatch
- Error isolation for handlers
- Lifecycle management
- Pydantic-based configuration
- Comprehensive exception hierarchy

#### Semantic Routing (Phase 2)
- Vector embeddings using sentence-transformers
- Cosine similarity matching
- LRU cache for embeddings with TTL
- Hybrid exact + semantic routing
- Multiple distance metrics (cosine, euclidean, manhattan, dot)

#### Context Engine (Phase 3)
- 4-level hierarchical context (global/session/user/event)
- Automatic context merging with precedence
- DSL filter expressions (`priority >= 5 AND user.role == 'admin'`)
- Lambda and string-based filters
- Thread-safe state management

#### Temporal Layer (Phase 4)
- SQLite-based event persistence with WAL
- Event replay with speed control
- Time-range queries
- Causality graph tracking
- Parent-child event relationships
- Root cause analysis

#### Memory Integration (Phase 5)
- Qdrant vector database adapter
- LanceDB vector database adapter
- Semantic event search
- Importance tracking and decay
- Memory consolidation
- Long-term event storage

#### LLM Integration (Phase 6)
- OpenAI connector (GPT models)
- Anthropic connector (Claude models)
- Ollama connector (local LLMs)
- Mock connector for testing
- Reasoning engine for event analysis
- LLM hook registry for pattern-based triggers
- LLM bridge orchestrator
- Automatic insight extraction
- Decision support

#### Distributed Capabilities (Phase 7)
- Redis-based multi-node clustering
- Event broadcasting across nodes
- Leader election
- Distributed locking
- Health checking with heartbeats
- Node discovery
- Event deduplication

#### Monitoring & Observability (Phase 8)
- Comprehensive metrics collector
- Latency histograms with percentiles (p50, p95, p99)
- Event counters
- Handler duration tracking
- Cache hit/miss tracking
- Error counting

### Tests
- 173 unit and integration tests
- 95% code coverage
- 100% type coverage (mypy strict)
- All tests passing

### Documentation
- Complete API documentation
- 15+ working examples
- Architecture documentation
- Contributing guidelines
- Code of conduct
- Publishing guide

### Package
- PyPI-ready setup
- Setuptools build system
- Optional dependencies for features
- Type stubs (py.typed)
- MANIFEST.in for distribution

## [0.2.0] - 2024-11-08

### Added
- **Semantic Routing Layer** - Match events by meaning, not just patterns
- `EmbeddingCache` - LRU cache with TTL for embeddings
- `SemanticEncoder` - Sentence transformer integration
- `SemanticRouter` - Similarity-based event routing
- `enable_semantic()` method on NeuroBus
- `semantic` parameter for subscriptions
- `threshold` parameter for similarity control
- Hybrid routing (pattern + semantic)
- Batch embedding generation
- GPU acceleration support
- 18 semantic layer unit tests
- 6 semantic routing integration tests
- Semantic routing examples

### Performance
- <5ms latency with cache (P95)
- >95% semantic accuracy
- 80-95% cache hit rate
- ~130MB memory footprint

### Documentation
- Phase 2 completion report
- Semantic examples with README
- Updated API documentation

## [0.1.0] - 2024-11-08

### Added
- Initial release of NeuroBUS Phase 1
- Core event bus implementation
- Event and Subscription models
- Async publish/subscribe API
- Exact topic matching
- Wildcard pattern matching (*, #)
- Parallel handler execution with error isolation
- Decorator-based subscription API
- Priority-based handler ordering
- Context filtering for subscriptions
- Lifecycle management (start/stop)
- Thread-safe subscription registry
- Configuration system with Pydantic
- Comprehensive exception hierarchy
- Utility functions (validation, serialization, timing, patterns)
- 100% type hint coverage with mypy strict mode
- >90% test coverage
- Integration tests for pub/sub flows
- Basic example applications
- Complete documentation

### Infrastructure
- Poetry-based dependency management
- pytest test framework
- Black code formatting
- Ruff linting
- mypy type checking
- GitHub Actions CI (planned)
- Documentation with Sphinx (planned)

[Unreleased]: https://github.com/tiverse-labs/neurobus/compare/v0.2.0...HEAD
[0.2.0]: https://github.com/tiverse-labs/neurobus/compare/v0.1.0...v0.2.0
[0.1.0]: https://github.com/tiverse-labs/neurobus/releases/tag/v0.1.0

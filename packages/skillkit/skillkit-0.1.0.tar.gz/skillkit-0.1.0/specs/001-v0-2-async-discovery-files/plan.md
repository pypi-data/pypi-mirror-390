# Implementation Plan: v0.2 - Async Support, Advanced Discovery & File Resolution

**Branch**: `001-v0-2-async-discovery-files` | **Date**: 2025-11-06 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-v0-2-async-discovery-files/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

This feature completes v0.2 of skillkit by adding async support for non-blocking operations, advanced discovery across multiple skill sources (project, anthropic, plugins), and file reference resolution with security validation. The implementation builds on v0.1's sync foundation with additive async APIs, plugin manifest parsing, nested skill structure support, and path traversal prevention for bundled skill resources.

## Technical Context

**Language/Version**: Python 3.10+ (minimum), Python 3.11+ (recommended for optimal memory efficiency via slots + cached_property)
**Primary Dependencies**: PyYAML 6.0+, aiofiles (new for v0.2), langchain-core 0.1.0+, pydantic 2.0+
**Storage**: Filesystem-based (.claude/skills/, ./skills/, ./plugins/ directories with SKILL.md files)
**Testing**: pytest 7.0+, pytest-asyncio (new for v0.2), pytest-cov 4.0+, 70% coverage target
**Target Platform**: Cross-platform Python (Linux, macOS, Windows) for CLI and library usage
**Project Type**: Single Python library with optional framework integrations
**Performance Goals**: Async discovery <200ms for 500 skills, async invocation overhead <2ms, event loop blocking <5ms
**Constraints**: Backward compatible with v0.1 sync API, zero framework dependencies in core, memory efficient (lazy loading)
**Scale/Scope**: Support 500+ skills across multiple sources, 5-level nested structures, 10+ concurrent async invocations

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Status**: ⚠️ No project constitution found at `.specify/memory/constitution.md` (template only)

**Proceeding with**: Standard Python library best practices as documented in v0.1 architectural decisions:
- Framework-agnostic core (stdlib + PyYAML only)
- Optional integrations via extras
- Backward compatibility with v0.1
- Progressive disclosure pattern (lazy loading)
- Security-first design (path traversal prevention)
- 70% test coverage minimum
- Type safety with mypy strict mode

**Re-evaluation required**: After Phase 1 design artifacts are generated

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
skillkit/
├── src/
│   └── skillkit/
│       ├── __init__.py             # Public API exports
│       ├── core/                   # Framework-agnostic core (v0.1 existing)
│       │   ├── __init__.py
│       │   ├── discovery.py        # SkillDiscovery: filesystem scanning (ADD async methods)
│       │   ├── parser.py           # SkillParser: YAML parsing (ADD plugin manifest parsing)
│       │   ├── models.py           # SkillMetadata, Skill dataclasses (ADD PluginManifest, SkillSource)
│       │   ├── manager.py          # SkillManager: orchestration (ADD async methods, multi-source)
│       │   ├── processors.py       # ContentProcessor strategies (ADD file resolution)
│       │   └── exceptions.py       # Exception hierarchy (ADD SecurityError, StateError)
│       ├── integrations/           # Framework-specific adapters (v0.1 existing)
│       │   ├── __init__.py
│       │   └── langchain.py        # LangChain StructuredTool adapter (ADD ainvoke support)
│       └── py.typed                # PEP 561 type hints marker
├── tests/                          # Test suite (mirrors src/)
│   ├── conftest.py                 # Shared fixtures
│   ├── test_discovery.py           # Discovery tests (ADD async tests)
│   ├── test_parser.py              # Parser tests (ADD plugin manifest tests)
│   ├── test_models.py              # Dataclass tests (ADD new models)
│   ├── test_processors.py          # Processor tests (ADD file resolution tests)
│   ├── test_manager.py             # Manager tests (ADD async, multi-source tests)
│   ├── test_langchain.py           # LangChain integration tests (ADD async tests)
│   ├── test_security.py            # NEW: Path traversal security tests
│   └── fixtures/
│       └── skills/                 # Test SKILL.md files
│           ├── valid-skill/
│           ├── nested-skill/       # NEW: nested structure testing
│           ├── plugin-skill/       # NEW: plugin structure testing
│           └── with-files-skill/   # NEW: supporting files testing
├── examples/                       # Usage examples
│   ├── basic_usage.py              # Standalone usage (v0.1 existing)
│   ├── langchain_agent.py          # LangChain integration (v0.1 existing)
│   ├── async_usage.py              # NEW: Async usage examples
│   └── multi_source_usage.py       # NEW: Multi-source configuration
├── pyproject.toml                  # Package configuration (UPDATE dependencies)
├── README.md                       # Installation + quick start (UPDATE for v0.2)
└── LICENSE                         # MIT license
```

**Structure Decision**: Single Python library structure (Option 1). The project follows standard Python packaging with src-layout for clean imports and test isolation. v0.2 adds async capabilities and new models to existing v0.1 modules while maintaining backward compatibility.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

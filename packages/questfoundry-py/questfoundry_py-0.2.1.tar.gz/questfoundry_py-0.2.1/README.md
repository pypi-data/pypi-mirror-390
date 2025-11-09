# QuestFoundry-Py

**Python library for QuestFoundry protocol and artifact management (Layer 6).**

QuestFoundry is a system for creating rich, interactive narratives using LLM-powered agents and structured workflows. This library provides the core implementation of state management, protocol communication, provider integration, and quality assurance.

[![Tests](https://img.shields.io/badge/tests-819%20passed-success)](https://github.com/pvliesdonk/questfoundry-py)
[![Coverage](https://codecov.io/gh/pvliesdonk/questfoundry-py/branch/main/graph/badge.svg)](https://codecov.io/gh/pvliesdonk/questfoundry-py)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green)](./LICENSE)

## Features

✨ **Complete Layer 6 Implementation**
- 🏗️ **State Management**: Hot/cold storage with SQLite and file-based workspace
- 📨 **Protocol Client**: Layer 4 envelope-based message passing
- 🤖 **Provider System**: Pluggable LLM and image providers (OpenAI, Ollama, DALL-E, Stable Diffusion)
- 🎭 **Role System**: 14+ specialized agent roles with prompt management
- 🔄 **Loop Orchestration**: Multi-step workflows coordinating roles
- ✅ **Quality Gates**: 8 quality bars for content validation
- 📤 **Export System**: View generation, Git export, HTML/Markdown rendering

## Quick Start

### Installation

```bash
pip install questfoundry-py[openai]
```

### Initialize a Project

```python
from questfoundry.state import WorkspaceManager

ws = WorkspaceManager("./my-adventure")
ws.init_workspace(
    name="Dragon's Legacy",
    description="An epic fantasy adventure",
    author="Alice"
)
```

### Create and Validate Content

```python
from questfoundry.models import Artifact
from questfoundry.validation import Gatekeeper

# Create a hook
hook = Artifact(
    type="hook_card",
    data={
        "hook_id": "HOOK-001",
        "title": "The Dragon's Awakening",
        "concept": "Ancient dragon stirs after 1000 years",
        "stakes": "Kingdom faces destruction",
        "twist": "The dragon was protecting the kingdom"
    },
    metadata={"temperature": "hot"}
)

ws.save_hot_artifact(hook)

# Validate
gatekeeper = Gatekeeper()
report = gatekeeper.run_gatecheck([hook])

if report.passed:
    ws.promote_to_cold("HOOK-001")
```

### Generate Views and Export

```python
from questfoundry.export import ViewGenerator, BookBinder

# Create player-safe view
view_gen = ViewGenerator(ws.cold_store)
view = view_gen.generate_view("SNAP-2025-11-07")

# Render to HTML
binder = BookBinder()
html = binder.render_html(view, title="Chapter 1")
binder.save_html(html, "./output/chapter1.html")
```

## Architecture

```
Layer 3: Schemas (JSON Schema validation)
    ↓
Layer 4: Protocol & Envelopes (Message passing)
    ↓
Layer 5: Prompts (Role definitions)
    ↓
Layer 6: Python Library (questfoundry-py) ← You are here
    ├── State Management (Hot/Cold SoT)
    ├── Protocol Client (Envelope communication)
    ├── Providers (LLM/Image/Audio)
    ├── Roles (14+ specialized agents)
    ├── Loops (Multi-step workflows)
    ├── Validation (8 quality bars)
    └── Export (Views, Git, Book binding)
    ↓
Layer 7: CLI & UI (questfoundry-cli)
```

## Core Concepts

### Hot/Cold Source of Truth

- **Hot Workspace**: Work-in-progress, file-based, human-editable (`.questfoundry/hot/`)
- **Cold Storage**: Curated, stable, SQLite database (`project.qfproj`)

Content flows: `Hot → Validation → Cold → Export`

### Quality Bars

8 quality bars ensure content meets standards before promotion:

1. **Integrity** - References resolve correctly
2. **Reachability** - Keystones are reachable
3. **Style** - Voice and register are consistent
4. **Gateways** - Conditions are diegetic
5. **Nonlinearity** - Hubs and loops are meaningful
6. **Determinism** - Assets are reproducible
7. **Presentation** - No spoilers on player surfaces
8. **Spoiler Hygiene** - PN boundaries maintained

### Provider System

Pluggable architecture for AI services:

```yaml
# .questfoundry/config.yml
providers:
  text:
    default: openai
    openai:
      api_key: ${OPENAI_API_KEY}
      model: gpt-4o
    ollama:
      base_url: http://localhost:11434
      model: llama3

  image:
    default: dalle
    dalle:
      api_key: ${OPENAI_API_KEY}
      model: dall-e-3
```

## Documentation

- 📘 **[Getting Started](./docs/guides/getting-started.md)** - Complete tutorial
- 📚 **[API Reference](./docs/api/)** - Detailed API documentation
  - [Protocol](./docs/api/protocol.md)
  - [State Management](./docs/api/state.md)
  - [Providers](./docs/api/providers.md)
  - [Validation](./docs/api/validation.md)
  - [Export](./docs/api/export.md)
  - [Roles & Loops](./docs/api/roles_and_loops.md)
- 🏛️ **[Architecture](./ARCHITECTURE.md)** - System design overview
- 🔧 **[Development](./CONTRIBUTING.md)** - Contributing guide

## Development

### Setup

```bash
git clone https://github.com/pvliesdonk/questfoundry-py
cd questfoundry-py
git submodule add https://github.com/pvliesdonk/questfoundry-spec spec
uv sync
```

### Run Tests

```bash
uv run pytest tests/
# 819 tests, all passing ✓
```

### Generate Coverage Report

```bash
uv run pytest --cov=src tests/
# Generates coverage report (submitted to codecov on CI)

# View HTML report
uv run pytest --cov=src --cov-report=html tests/
# Open htmlcov/index.html in your browser
```

### Type Checking

```bash
uv run mypy src/questfoundry/
```

### Linting

```bash
uv run ruff check src/questfoundry/ tests/
uv run ruff format src/questfoundry/ tests/
```

### Pre-commit Hooks

```bash
pre-commit install
pre-commit run --all-files
```

## Project Status

**Current Version**: 0.1.0

**Completed Epics (1-10)**:
- ✅ Project Foundation
- ✅ Layer 3/4 Integration (17 artifact types, protocol validation)
- ✅ State Management (SQLite + file-based)
- ✅ Artifact Types & Lifecycles
- ✅ Protocol Client
- ✅ Provider System (OpenAI, Ollama, DALL-E, A1111)
- ✅ Role Execution (14 roles, prompt system)
- ✅ Orchestration (Showrunner, Story Spark loop)
- ✅ Safety & Quality (PN guard, 8 quality bars, Gatekeeper)
- ✅ Export & Views (View generation, Git export, book binder)

**In Progress (Epic 11)**:
- 📝 Documentation & Polish

**Planned**:
- Epic 12: Additional loop implementations
- Epic 13: Session management & interactive mode
- Epic 14: Additional providers (audio, Gemini, Bedrock)
- Epic 15: Advanced features (caching, rate limiting, per-role config)

See [gap-analysis.md](./.claude/gap-analysis.md) and [completion-plan.md](./.claude/completion-plan.md) for details.

## Examples

### Complete Workflow

```python
from questfoundry.state import WorkspaceManager
from questfoundry.validation import Gatekeeper
from questfoundry.export import ViewGenerator, GitExporter, BookBinder
from questfoundry.models import Artifact

# 1. Initialize
ws = WorkspaceManager("./project")
ws.init_workspace("My Adventure")

# 2. Create content
hook = Artifact(type="hook_card", data={"hook_id": "HOOK-001", ...})
ws.save_hot_artifact(hook)

# 3. Validate
gk = Gatekeeper()
report = gk.run_gatecheck(ws.list_hot_artifacts())

# 4. Promote
if report.passed:
    hook_id = hook.data.get("hook_id")
    ws.promote_to_cold(hook_id)

# 5. Create snapshot
from questfoundry.state import SnapshotInfo
snapshot = SnapshotInfo(
    snapshot_id="SNAP-001",
    tu_id="TU-001",
    description="Chapter 1"
)
ws.save_snapshot(snapshot)

# 6. Export
view_gen = ViewGenerator(ws.cold_store)
view = view_gen.generate_view("SNAP-001")

# 7. Render
binder = BookBinder()
html = binder.render_html(view)
binder.save_html(html, "./output.html")

# 8. Git export
git_exp = GitExporter(ws.cold_store)
git_exp.export_snapshot("SNAP-001", "./export")
```

### Using Providers

```python
from questfoundry.providers import ProviderRegistry, ProviderConfig

config = ProviderConfig()
registry = ProviderRegistry(config)

# Text generation
text_provider = registry.get_text_provider("openai")
response = text_provider.generate_text(
    prompt="Write a fantasy scene",
    max_tokens=500,
    temperature=0.8
)

# Image generation
image_provider = registry.get_image_provider("dalle")
image_data = image_provider.generate_image(
    prompt="A mystical forest",
    width=1024,
    height=1024
)
```

## Related Repositories

- **[questfoundry-spec](https://github.com/pvliesdonk/questfoundry-spec)** - Specification and schemas (Layers 0-5)
- **[questfoundry-cli](https://github.com/pvliesdonk/questfoundry-cli)** - Command-line interface (Layer 7)

## License

MIT License - see [LICENSE](./LICENSE) for details.

## Contributing

Contributions welcome! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

## Credits

Developed by [pvliesdonk](https://github.com/pvliesdonk)

Built with:
- [Pydantic](https://pydantic.dev/) for data validation
- [SQLite](https://www.sqlite.org/) for cold storage
- [OpenAI](https://openai.com/), [Ollama](https://ollama.ai/) for LLM providers
- [UV](https://docs.astral.sh/uv/) for package management

---

**🎮 Happy Quest Building! ✨**

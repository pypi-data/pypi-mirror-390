# Alprina CLI - Context Engineering Guide

> **Last Updated**: 2025-11-06
> **Claude Code Version**: 2.0+
> **Target Context Window**: 100-200 lines (per file)

## Project Identity

**Alprina CLI** is a context-engineered, AI-powered cybersecurity command-line tool that combines intelligent security scanning with production-ready developer tooling.

**Core Philosophy**: Treat context as a precious, finite resource. Every token must earn its place.

## Quick Start for Claude Code

```bash
# This is a Python CLI project
cd /Users/maltewagenbach/Notes/Projects/Alprina/Alprina_dev/cli

# Virtual environment is at ./venv
source venv/bin/activate

# Install in development mode
pip install -e .

# Run CLI
alprina --help
```

## Architecture Overview

```
User → CLI Shell (Typer)
    ↓
┌─────────────────────────────────────┐
│ CONTEXT-ENGINEERED LAYERS           │
├─────────────────────────────────────┤
│ Tools (Not Agents!)                 │ ← Callable utilities with clear interfaces
│ ├── Security Tools (scan, recon)    │
│ ├── File Tools (glob, grep)         │
│ └── MCP Tools (extensibility)       │
├─────────────────────────────────────┤
│ Memory Layer (Mem0.ai + Hybrid)     │ ← Just-in-time context retrieval
│ ├── User/Session Memory             │
│ ├── Episodic (per-target)           │
│ └── Semantic (cross-target)         │
├─────────────────────────────────────┤
│ Guardrails (Input/Output)           │ ← Security validation
│ ├── Prompt injection detection      │
│ └── Command execution validation    │
├─────────────────────────────────────┤
│ Auth & API (FastAPI)                │ ← Multi-user with billing
└─────────────────────────────────────┘
```

## Critical Context Engineering Principles

### 1. Just-in-Time Context Retrieval
- **Never** pre-load entire codebases into context
- Use file paths as lightweight identifiers
- Retrieve specific files only when needed via tools
- Let agents discover context progressively through exploration

### 2. Tool-First Architecture (NOT Agent-Based)
```python
# ❌ WRONG: Agents (LLM personas with prompts)
agents/
├── malware_agent.py      # Full LLM with system prompt
├── recon_agent.py        # Full LLM with system prompt
└── vuln_scan_agent.py    # Full LLM with system prompt

# ✅ CORRECT: Tools (callable utilities)
tools/
├── security/
│   ├── scan.py           # def scan(target, options) -> Result
│   ├── recon.py          # def recon(target) -> Result
│   └── exploit.py        # def exploit(vuln_id) -> Result
```

### 3. Context Compaction Strategy
- **Clear context after task completion** (`/clear` in Claude Code)
- **Summarize** long conversations before hitting limits
- **Remove tool outputs** from deep history (agents don't need to reprocess)
- **Structured note-taking** for multi-session tasks

### 4. Multi-Agent for Separation of Concerns
- **Writing Agent**: Implements features
- **Review Agent**: Tests and validates
- **Memory Agent**: Manages context summaries
- Each agent gets clean, focused context

## File Organization for Context Engineering

### CLAUDE.md Files (This File)
- **Root CLAUDE.md** (you're reading it): Project overview, architecture, principles
- **Subdirectory CLAUDE.md files**: Module-specific context
- **Keep each under 200 lines**: Split into focused files if larger

### Directory Structure

```
cli/
├── CLAUDE.md                          ← You are here (project context)
├── README.md                          ← User-facing documentation
├── pyproject.toml                     ← Dependencies and metadata
│
├── src/alprina_cli/
│   ├── CLAUDE.md                      ← Main implementation context
│   │
│   ├── tools/                         ← NEW: Tool-first architecture
│   │   ├── CLAUDE.md                  ← Tool development guide
│   │   ├── base.py                    ← CallableTool2 base class
│   │   ├── security/                  ← Security scanning tools
│   │   │   ├── CLAUDE.md
│   │   │   ├── scan.py
│   │   │   ├── recon.py
│   │   │   └── exploit.py
│   │   ├── file/                      ← File manipulation tools
│   │   │   ├── glob.py
│   │   │   ├── grep.py
│   │   │   ├── patch.py
│   │   │   └── replace.py
│   │   └── mcp/                       ← MCP integration
│   │       └── wrapper.py
│   │
│   ├── memory/                        ← NEW: Memory management
│   │   ├── CLAUDE.md                  ← Memory architecture guide
│   │   ├── manager.py                 ← Hybrid memory orchestration
│   │   ├── mem0_client.py             ← Mem0.ai integration
│   │   ├── episodic.py                ← Per-target memory (from CAI)
│   │   └── semantic.py                ← Cross-target memory (from CAI)
│   │
│   ├── security/                      ← NEW: Guardrails
│   │   ├── CLAUDE.md                  ← Guardrail patterns
│   │   ├── guardrails.py              ← Main guardrail implementations
│   │   ├── exceptions.py              ← Security exceptions
│   │   └── patterns.py                ← Injection detection patterns
│   │
│   ├── api/                           ← FastAPI backend (existing)
│   │   ├── CLAUDE.md
│   │   ├── main.py
│   │   ├── routes/
│   │   └── middleware/
│   │
│   ├── cli/                           ← CLI commands (existing)
│   │   ├── CLAUDE.md
│   │   └── commands.py
│   │
│   └── config/                        ← Configuration (enhanced)
│       ├── CLAUDE.md
│       └── settings.py                ← Pydantic settings
│
├── tests/                             ← NEW: Comprehensive tests
│   ├── CLAUDE.md                      ← Testing strategy
│   ├── conftest.py                    ← Pytest fixtures
│   ├── unit/
│   │   ├── test_tools/
│   │   ├── test_memory/
│   │   └── test_security/
│   ├── integration/
│   └── e2e/
│
└── docs/                              ← Documentation (minimal in context)
    └── CLAUDE.md                      ← Documentation guide
```

## Context Loading Strategy

### On Task Start
1. **Auto-loaded**: Root `CLAUDE.md` (this file)
2. **On-demand**: Specific module `CLAUDE.md` when working in that area
3. **Progressive**: Individual files via glob/grep tools

### During Development
```python
# Example: Working on memory integration
# Claude Code will:
# 1. Read cli/CLAUDE.md (project overview)
# 2. Read src/alprina_cli/memory/CLAUDE.md (module context)
# 3. Glob for relevant files: **/*memory*.py
# 4. Read specific files as needed
# 5. Never load entire codebase at once
```

## Development Workflow (Context-Aware)

### Small Batch Approach
```bash
# ✅ GOOD: Small, focused task
"Implement the SecurityScanTool in tools/security/scan.py
following the CallableTool2 pattern from tools/base.py"

# ❌ BAD: Large, unfocused task
"Refactor the entire agent system to tools and add memory
and guardrails and tests"
```

### Context Clearing
```bash
# After completing each focused task:
/clear  # In Claude Code

# Start new task with fresh context
```

### Checkpoint-Driven Development
```bash
# Step 1: Plan (request plan first)
"Propose a 3-step plan to add Mem0.ai integration"

# Step 2: Implement checkpoint 1
"Implement step 1: Create mem0_client.py wrapper"

# Step 3: Test checkpoint 1
pytest tests/unit/test_memory/test_mem0_integration.py

# Step 4: Clear context, continue to checkpoint 2
/clear
"Implement step 2: Integrate mem0_client into manager.py"
```

## Key Technical Decisions

### Why Mem0.ai for Memory?
- 13M+ downloads, 41K+ GitHub stars (production-ready)
- 26% better accuracy than OpenAI Memory
- 91% faster responses, 90% lower token usage
- Multi-level memory (user, session, agent)
- Semantic search with vectors
- **Saves context window tokens** by persisting memory outside context

### Why Tools over Agents?
- **Agents** = Full LLM instances with prompts (heavy, inflexible)
- **Tools** = Callable functions (lightweight, composable, testable)
- Tools can be called by multiple agents
- Tools have clear interfaces (Pydantic schemas)
- Tools are MCP-compatible

### Why Guardrails are Critical?
- Prevent prompt injection attacks
- Block malicious command execution
- Detect Unicode bypass attempts
- Validate tool outputs before execution
- **Security-first** for cybersecurity CLI

## Integration Roadmap (Context-Engineered)

### Phase 1: Tool Architecture (Weeks 1-2)
**Focus**: Convert agents → tools
**Context Strategy**: Work on one tool at a time, clear context between tools
**Validation**: Each tool has unit tests before moving to next

### Phase 2: Memory Layer (Weeks 3-4)
**Focus**: Integrate Mem0.ai, implement hybrid memory
**Context Strategy**: Separate tasks for Mem0 vs episodic/semantic
**Validation**: Memory persistence working, search <500ms

### Phase 3: Guardrails (Week 5)
**Focus**: Add input/output security validation
**Context Strategy**: Clone from CAI, adapt incrementally
**Validation**: 95%+ test coverage, <1% false positives

### Phase 4: Testing (Weeks 6-7)
**Focus**: Comprehensive test suite
**Context Strategy**: Test one module at a time
**Validation**: 70%+ overall coverage

### Phase 5: MCP Integration (Week 8)
**Focus**: True MCP server support
**Context Strategy**: Reference Kimi-CLI patterns, implement incrementally
**Validation**: External MCP tools loadable

## Common Patterns

### Adding a New Tool
```python
# 1. Create tool file: src/alprina_cli/tools/security/new_tool.py
from alprina_cli.tools.base import AlprinaToolBase
from pydantic import BaseModel, Field
from typing import override

class NewToolParams(BaseModel):
    target: str = Field(description="Target to scan")
    options: dict = Field(default={})

class NewTool(AlprinaToolBase[NewToolParams]):
    name: str = "NewTool"
    description: str = "Description of what this tool does"
    params: type[NewToolParams] = NewToolParams

    @override
    async def execute(self, params: NewToolParams):
        # Implementation
        return ToolOk(content="Success")

# 2. Register in tools/__init__.py
# 3. Write tests in tests/unit/test_tools/test_new_tool.py
# 4. Document in tools/CLAUDE.md
```

### Using Memory
```python
from alprina_cli.memory.manager import AlprinaMemoryManager

memory = AlprinaMemoryManager()

# Store context outside LLM context window
await memory.add_memory(
    content=f"Scan completed on {target}",
    user_id=user_id,
    metadata={"type": "scan", "target": target}
)

# Retrieve relevant context just-in-time
past_scans = await memory.search_memory(
    query=f"previous scans on {target}",
    user_id=user_id,
    limit=3  # Only top 3 most relevant
)
```

### Applying Guardrails
```python
from alprina_cli.security.guardrails import (
    prompt_injection_guardrail,
    command_execution_guardrail
)

# Apply to tools or agents
tool = SecurityScanTool(
    input_guardrails=[prompt_injection_guardrail],
    output_guardrails=[command_execution_guardrail]
)
```

## Testing Strategy

### Context-Aware Testing
- **Unit tests**: One module at a time, isolated
- **Integration tests**: Small component interactions
- **E2E tests**: Full workflows with context clearing between scenarios

### Coverage Goals
- Tools: 85%+
- Memory: 90%+
- Guardrails: 95%+ (security critical)
- Overall: 70%+

## Environment Configuration

```bash
# Required
export DATABASE_URL="postgresql://..."
export OPENAI_API_KEY="sk-..."

# Memory (Mem0.ai)
export MEM0_VECTOR_STORE="qdrant"  # or chroma, postgres
export QDRANT_HOST="localhost"
export QDRANT_PORT="6333"

# Security
export ALPRINA_GUARDRAILS="true"
export ALPRINA_GUARDRAILS_STRICT="false"

# Development
export ALPRINA_ENV="development"
export LOG_LEVEL="INFO"
```

## Reference Projects (Read-Only)

These projects are reference implementations. **Do not modify them**.

- `../cai/` - Reference for guardrails, memory patterns
- `../kimi-cli-base/` - Reference for tool architecture, MCP integration

When implementing features, read from these projects but write to `./cli/`. goal is to be fully independedn on KIMI and CAI and everyhting is integrated in alprina.

## Anti-Patterns to Avoid

❌ Loading entire codebase into context
❌ Vague, multi-file tasks without focus
❌ Overly prescriptive if-else logic in prompts
❌ Agent-based architecture (use tools instead)
❌ Pre-processing all data upfront
❌ Aggressive context compaction (losing critical details)
❌ Edge case saturation in prompts

## Success Metrics

✅ Context window usage: <50% on average
✅ Task completion: Single-session for focused tasks
✅ Memory retrieval: <500ms response time
✅ Test coverage: 70%+ overall, 95%+ for security
✅ Tool reusability: Each tool used by multiple commands
✅ False positive rate: <1% for guardrails

---

**Remember**: Context is precious. Every token must earn its place. Build small, test frequently, clear context often.

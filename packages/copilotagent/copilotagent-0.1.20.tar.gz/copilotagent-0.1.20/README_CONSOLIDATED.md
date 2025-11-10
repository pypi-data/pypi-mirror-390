# 🧠 CopilotAgent - Deep Planning Agents Framework

**A Python package for building deep, planning-capable AI agents with file systems, subagent spawning, and customizable planning strategies.**

[![PyPI](https://img.shields.io/badge/PyPI-0.1.8-blue)](https://pypi.org/project/copilotagent/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📦 Package Information

| Property | Value |
|----------|-------|
| **Package Name** | `copilotagent` |
| **Latest Version** | `0.1.8` |
| **PyPI** | https://pypi.org/project/copilotagent/ |
| **GitHub** | https://github.com/FintorAI/copilotBase |
| **License** | MIT |
| **Python** | >=3.11,<4.0 |

---

## 🚀 Quick Start

### Installation

```bash
# Using pip
pip install copilotagent

# Using uv
uv add copilotagent

# Using poetry
poetry add copilotagent
```

### Basic Usage

```python
from copilotagent import create_deep_agent

# Create a deep agent
agent = create_deep_agent(
    model="claude-sonnet-4-5-20250929",
    agent_type="ITP-Princeton",
    system_prompt="You are an Intent to Proceed processor",
)

# Invoke the agent
result = agent.invoke({
    "messages": [{"role": "user", "content": "Process ITP for Princeton"}]
})
```

---

## ✨ Core Features

### 1. **Planning & Task Decomposition**
Built-in `write_todos` tool enables agents to break down complex tasks, track progress, and adapt plans.

### 2. **Context Management**
File system tools (`ls`, `read_file`, `write_file`, `edit_file`) for managing large contexts and preventing overflow.

### 3. **Subagent Spawning**
`task` tool enables spawning specialized subagents for context isolation and parallel execution.

### 4. **Cloud Subagent Integration**
Connect to deployed LangGraph Cloud services as subagents with built-in helpers.

### 5. **Customizable Planning** (NEW in v0.1.8)
Agents can provide custom `planning_prompt` for tailored planning strategies.

### 6. **Long-term Memory**
Persistent memory across threads using LangGraph's Store.

---

## 📚 API Reference

### Main Factory

#### `create_deep_agent()`

```python
def create_deep_agent(
    model: str | BaseChatModel | None = None,
    tools: Sequence[BaseTool | Callable | dict] | None = None,
    *,
    system_prompt: str | None = None,
    middleware: Sequence[AgentMiddleware] = (),
    subagents: list[SubAgent | CompiledSubAgent] | None = None,
    agent_type: Literal["ITP-Princeton", "DrawDoc-AWM", "research"] | None = None,
    planning_prompt: str | None = None,  # NEW in v0.1.8
    use_longterm_memory: bool = False,
    interrupt_on: dict[str, bool | InterruptOnConfig] | None = None,
    # ... other parameters
) -> CompiledStateGraph:
```

**Key Parameters:**
- `model` - LangChain model (default: Claude Sonnet 4.5)
- `agent_type` - Type of agent for built-in planning ("ITP-Princeton", "DrawDoc-AWM", "research")
- `planning_prompt` - **NEW**: Custom planning prompt (overrides built-in)
- `subagents` - List of subagent specifications or pre-compiled subagents
- `tools` - Custom tools for the agent
- `system_prompt` - Additional instructions for the agent

### Cloud Subagents

#### `create_remote_subagent()` (NEW in v0.1.8)

```python
def create_remote_subagent(
    name: str,
    url: str,
    graph_id: str,
    description: str,
    api_key: str | None = None,
) -> CompiledSubAgent:
```

**Create custom cloud subagents:**
```python
from copilotagent import create_deep_agent, create_remote_subagent

# Create custom subagent
validator = create_remote_subagent(
    name="document-validator",
    url="https://my-service.us.langgraph.app",
    graph_id="validatorGraph",
    description="Validates mortgage documents for compliance"
)

# Use it
agent = create_deep_agent(
    subagents=[validator],
)
```

#### Built-in Subagent Helpers

```python
from copilotagent import (
    get_cute_linear_subagent,      # Data extraction from GUI
    get_cute_finish_itp_subagent,  # ITP workflow completion
)
```

---

## 🎯 Agent Types

### ITP-Princeton
Optimized for Intent to Proceed document processing workflows.

**Features:**
- Structured ITP workflow planning
- Integration with GUI automation subagents
- Document compliance checking

### DrawDoc-AWM
Tailored for document drawing and annotation workflows.

**Features:**
- 5-phase workflow (Analysis → Markup → Drawing → QA → Delivery)
- Document annotation and visual elements
- Quality assurance tracking

### Research
Specialized for research and comprehensive report generation.

**Features:**
- Parallel research subagents
- Source citation tracking
- Critique and refinement workflow

---

## 🔧 Advanced Usage

### Custom Planning Prompts (v0.1.8+)

```python
from pathlib import Path
from copilotagent import create_deep_agent

# Load custom planning prompt
planning_prompt = Path("my_custom_prompt.md").read_text()

agent = create_deep_agent(
    agent_type="ITP-Princeton",
    planning_prompt=planning_prompt,  # Use custom prompt
)
```

**Benefits:**
- ✅ Edit planning strategies without updating PyPI package
- ✅ Agent-specific customization
- ✅ Fast iteration (edit → commit → deploy)

### Custom Cloud Subagents (v0.1.8+)

```python
from copilotagent import create_deep_agent, create_remote_subagent

# Create custom subagents
data_processor = create_remote_subagent(
    name="data-processor",
    url="https://processor.us.langgraph.app",
    graph_id="processorGraph",
    description="Processes external data sources"
)

validator = create_remote_subagent(
    name="validator",
    url="https://validator.us.langgraph.app",
    graph_id="validatorGraph",
    description="Validates processed data"
)

# Use both
agent = create_deep_agent(
    subagents=[data_processor, validator],
)
```

### Middleware Customization

```python
from copilotagent import (
    create_deep_agent,
    PlanningMiddleware,
    FilesystemMiddleware,
    SubAgentMiddleware,
)

# Use middleware directly for custom agents
from langchain.agents import create_agent

agent = create_agent(
    model="claude-sonnet-4-5-20250929",
    middleware=[
        PlanningMiddleware(agent_type="ITP-Princeton"),
        FilesystemMiddleware(long_term_memory=False),
        SubAgentMiddleware(
            default_model="claude-sonnet-4-5-20250929",
            subagents=[my_custom_subagent],
        ),
    ],
)
```

---

## 📦 Dependencies

### Required
- `langchain-anthropic>=1.0.0,<2.0.0`
- `langchain>=1.0.0,<2.0.0`
- `langchain-core>=1.0.0,<2.0.0`
- `langgraph-sdk>=0.1.0,<1.0.0`
- `python-dotenv>=0.19.0`

### Optional (dev)
- `pytest` - Testing
- `pytest-cov` - Coverage
- `build` - Build tool
- `twine` - PyPI upload
- `langchain-openai` - OpenAI integration

---

## 🏗️ Package Development

### Project Structure

```
baseCopilotAgent/
├── .github/workflows/
│   ├── auto-release.yml    # Auto-creates releases from tags
│   └── pypi.yml            # Auto-publishes to PyPI
├── src/copilotagent/
│   ├── __init__.py         # Public API exports
│   ├── graph.py            # create_deep_agent()
│   ├── cloud_subagents.py  # Cloud subagent factories
│   └── middleware/
│       ├── planning.py     # Planning middleware
│       ├── filesystem.py   # File system tools
│       ├── subagents.py    # Subagent middleware
│       ├── initial_message.py # Default messages
│       ├── patch_tool_calls.py # Tool call patching
│       └── planner_prompts/
│           ├── itp_princeton.md
│           ├── drawdoc_awm.md
│           └── research.md
├── deploy.sh              # One-command deployment
├── pyproject.toml         # Package configuration
├── MANIFEST.in            # Package data files
└── LICENSE                # MIT License
```

### Making Changes

```bash
cd baseCopilotAgent

# 1. Make your code changes...

# 2. Deploy (auto bumps version, publishes to PyPI)
./deploy.sh "Add new feature X"

# That's it! Package is live on PyPI automatically
```

### Deployment Workflow

```
./deploy.sh "message"
       ↓
Commit + Bump Version + Create Tag
       ↓
Push to GitHub
       ↓
GitHub Actions: Create Release
       ↓
GitHub Actions: Publish to PyPI
       ↓
✅ Package Available on PyPI
```

---

## 🔐 GitHub Secrets Required

For automated PyPI publishing, set these secrets at:
https://github.com/FintorAI/copilotBase/settings/secrets/actions

- `PYPI_USERNAME` = `__token__`
- `PYPI_PASSWORD` = Your PyPI API token from https://pypi.org/manage/account/token/

---

## 📖 Exported API

```python
from copilotagent import (
    # Main factory
    create_deep_agent,
    
    # Cloud subagent factories (NEW in v0.1.8)
    create_remote_subagent,
    get_cute_linear_subagent,
    get_cute_finish_itp_subagent,
    
    # Defaults
    DEFAULT_AGENT_TYPE,
    DEFAULT_STARTING_MESSAGES,
    get_default_starting_message,
    
    # Middleware
    FilesystemMiddleware,
    PlanningMiddleware,
    SubAgentMiddleware,
    InitialMessageMiddleware,
    
    # Types
    CompiledSubAgent,
    SubAgent,
)
```

---

## 🔄 Version History

### v0.1.8 (Current)
- ✨ Added `planning_prompt` parameter to `create_deep_agent()`
- ✨ Added `create_remote_subagent()` factory for custom cloud subagents
- 📝 Agents can now use local planning prompts
- 🔧 Easier customization without package updates

### v0.1.7
- 🐛 Added `python-dotenv` dependency (required for cloud_subagents)

### v0.1.6
- ✨ Package renamed from `deepagents` to `copilotagent`
- 📦 First public release on PyPI

### v0.1.5
- 🔧 Initial package structure
- 📦 GitHub Actions workflows

---

## 🌐 LangGraph Cloud Integration

This package is designed to work seamlessly with LangGraph Cloud deployments.

### Environment Variables

**Required for agents using cloud subagents:**
- `ANTHROPIC_API_KEY` - For Claude model
- `LANGCHAIN_API_KEY` - For connecting to cloud subagents

**Optional:**
- `TAVILY_API_KEY` - For research agents with web search

### Deployment

Agents using `copilotagent` can be deployed to LangGraph Cloud:

1. Push agent to GitHub
2. Connect repo in LangSmith dashboard (https://smith.langchain.com/deployments)
3. LangGraph Cloud installs `copilotagent` from PyPI automatically
4. Agent deploys and runs!

---

## 🤝 Contributing

This package powers multiple agent types. When making changes:

1. Test locally with `python -m build`
2. Run tests (if available)
3. Deploy with `./deploy.sh "description"`
4. Update dependent agents to use new version

---

## 📞 Support

- **Issues**: https://github.com/FintorAI/copilotBase/issues
- **PyPI Package**: https://pypi.org/project/copilotagent/
- **Documentation**: This file

---

## 📝 License

MIT License - Copyright (c) 2025 Harrison Chase

See [LICENSE](LICENSE) file for details.

---

## 🎓 Example Agents

Example agents using this package:

- **ITP-Princeton**: https://github.com/FintorAI/itp-princeton-agent
- **DrawDoc-AWM**: https://github.com/FintorAI/drawdoc-awm-agent
- **Research**: https://github.com/FintorAI/research-agent

---

## 🔗 Links

- **PyPI Package**: https://pypi.org/project/copilotagent/
- **GitHub Repository**: https://github.com/FintorAI/copilotBase
- **Latest Release**: https://github.com/FintorAI/copilotBase/releases/latest
- **LangGraph Cloud**: https://smith.langchain.com/

---

**Built with LangGraph and LangChain** 🦜🔗



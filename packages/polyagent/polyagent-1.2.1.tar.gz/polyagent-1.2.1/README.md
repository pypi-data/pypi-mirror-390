# PolyCLI

[中文版](README_ZH.md)

Unified Python interface for AI coding assistants (Claude Code, Qwen Code, Codex CLI, MiniSWE-Agent) with pattern-based multi-agent orchestration, real-time web monitoring, and REST API integration.

**Key Features:**
- 🔄 Seamless switching between AI coding assistants with unified message format
- 🎭 Pattern-based orchestration for trackable multi-agent workflows  
- 🌐 Web control panel with real-time debugging and intervention
- 🔌 REST API for third-party integration and automation
- 🏛️ Agent Hall system for persistent AI teams (coming soon)

📚 **Learn More:** For a deeper understanding of AI agents and their capabilities, check out [Understanding AI Agents](https://github.com/Supie-Agent-Lab/Understanding-AI-Agents).

## Installation

```bash
pip install polyagent
```

### CLI Tools Setup

**Claude Code**: Follow official Anthropic installation

**Qwen Code**:
```bash
# Remove original version if installed
npm uninstall -g @qwen-code/qwen-code

# Install special version with --save/--resume support and loop detection disabled
npm install -g @lexicalmathical/qwen-code@0.0.8-polycli.1
```

**Codex CLI**: Follow [official Codex installation](https://github.com/Supie-Agent-Lab/codex)

**Mini-SWE Agent**:
```bash
pip install mini-swe-agent
```

## Quick Start

```python
from polycli import PolyAgent

# Create a unified agent that works with all backends
agent = PolyAgent(debug=True)

# Automatic backend selection based on task
result = agent.run("What is 2+2?")  # Uses Claude by default
print(result.content)  # 4

# Explicit backend control
result = agent.run("Write a function", cli="claude-code")  # Claude with tools
result = agent.run("Analyze this", cli="qwen-code")       # Qwen with tools
result = agent.run("Debug code", cli="codex")             # Codex CLI
result = agent.run("Fix bug", cli="mini-swe")             # Mini-SWE Agent
result = agent.run("Just chat", cli="no-tools")           # Direct API, no tools

# Multi-model support via models.json
result = agent.run("Explain recursion", model="gpt-4o")
if result:  # Check success
    print(result.content)

# Structured outputs with Pydantic
from pydantic import BaseModel, Field

class MathResult(BaseModel):
    answer: int = Field(description="The numerical answer")
    explanation: str = Field(description="Step-by-step explanation")

result = agent.run("What is 15+27?", model="gpt-4o", schema_cls=MathResult)
if result.has_data():
    print(result.data['answer'])  # 42

# System prompts
agent = PolyAgent(system_prompt="You are a helpful Python tutor")
result = agent.run("Explain list comprehensions")

# Token management with auto-compaction
agent = PolyAgent(max_tokens=50000)  # Set token limit
# Automatically compacts conversation when approaching limit

# Real-time token streaming
result = agent.run("Write a story", stream=True)  # Stream tokens as they arrive
# Tokens are automatically published to session's SSE endpoint if in orchestration context

# State persistence
agent.save_state("conversation.jsonl")  # Save in any format
new_agent = PolyAgent()
new_agent.load_state("conversation.jsonl")  # Load and continue
```

## Session Registry & Control Panel

The Session Registry system allows you to define reusable sessions as functions and automatically generates a web control panel for triggering and monitoring them.

### Defining Sessions

```python
from polycli.orchestration.session_registry import session_def, get_registry
from polycli import PolyAgent
from polycli.orchestration import batch

@session_def(
    name="Code Analyzer",
    description="Analyze Python code quality",
    params={"file_path": str, "depth": int},
    category="Analysis"
)
def analyze_code(file_path: str, depth: int = 3):
    """Analyze code with configurable depth."""
    agent = PolyAgent(id="analyzer")
    
    # Use tracked=True to ensure tracking in session
    result = agent.run(
        f"Analyze {file_path} with depth {depth}", 
        cli="claude-code",
        tracked=True
    )
    
    return {
        "file": file_path,
        "analysis": result.content,
        "status": "completed"
    }

@session_def(
    name="Multi-Agent Research", 
    description="Research with multiple specialized agents",
    params={"topic": str},
    category="Research"
)
def research_topic(topic: str):
    """Coordinate multiple agents for research."""
    researcher = PolyAgent(id="researcher")
    analyst = PolyAgent(id="analyst")
    writer = PolyAgent(id="writer")
    
    # Parallel execution with tracking
    with batch():
        facts = researcher.run(f"Research facts about {topic}", tracked=True)
        analysis = analyst.run(f"Analyze trends in {topic}", tracked=True)
    
    # Sequential synthesis with tracking
    report = writer.run(
        f"Write report combining: {facts.content} and {analysis.content}",
        tracked=True
    )
    
    return {"topic": topic, "report": report.content}
```

### Starting the Control Panel

```python
from polycli.orchestration.session_registry import get_registry

# Get the registry (sessions auto-register via decorator)
registry = get_registry()

# Start the web control panel
registry.serve_control_panel(port=8765)
print("Control panel at http://localhost:8765")

# Keep running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Shutting down...")
```

### Control Panel Features

![Session Control Panel](assets/session-control-panel.png)

- **Web UI**: Clean interface with sidebar navigation
- **Session Library**: Browse all registered sessions by category
- **Parameter Forms**: Auto-generated forms for session parameters
- **Real-time Monitoring**: Each session gets its own monitoring port
- **Session Control**: Start, monitor, and cancel sessions
- **Resource Management**: Automatic port allocation and cleanup
- **Iframe Integration**: Monitor sessions without leaving the control panel

![Session Monitoring](assets/session-monitoring.png)

### Session Registry API

The control panel exposes REST APIs for third-party integration:

#### Available Endpoints

**List registered sessions:**
```bash
GET http://localhost:8765/api/sessions
```

**Get running sessions:**
```bash
GET http://localhost:8765/api/running
```

**Trigger a session:**
```bash
POST http://localhost:8765/api/trigger
Content-Type: application/json

{
  "session_id": "code_analyzer",
  "params": {
    "file_path": "/path/to/file.py",
    "depth": 3
  }
}
```

**Stop a session:**
```bash
POST http://localhost:8765/api/stop
Content-Type: application/json

{"exec_id": "code_analyzer-abc123"}
```

**Get session status:**
```bash
GET http://localhost:8765/api/status/{exec_id}
```

Sessions triggered via API appear in the web UI in real-time, allowing monitoring from both API clients and the control panel simultaneously.

## Multi-Agent Orchestration

PolyCLI includes a powerful orchestration system for managing multi-agent interactions with real-time monitoring.

![Session Web UI](assets/session-webui.png)

### Patterns & Sessions

Use the `@pattern` decorator to create trackable, reusable agent workflows:

```python
from polycli import PolyAgent
from polycli.orchestration import session, pattern, serve_session
from polycli.orchestration.builtin_patterns import notify, tell, get_status

# Create agents with unique IDs for tracking
agent1 = PolyAgent(id="Researcher")
agent2 = PolyAgent(id="Writer")

# Start a monitoring session with web UI
with session() as s:
    server, _ = serve_session(s, port=8765)
    print("Monitor at http://localhost:8765")
    
    # Use built-in patterns
    notify(agent1, "Research quantum computing basics")
    tell(agent1, agent2, "Share your research findings")
    
    # Get status summaries
    status = get_status(agent2, n_exchanges=3)
    print(status.content)
    
    input("Press Enter to stop...")
```

### Built-in Patterns

**`notify(agent, message)`** - Send notifications to agents
```python
notify(agent, "Your task is to analyze this code", source="System")
```

**`tell(speaker, listener, instruction)`** - Agent-to-agent communication
```python
tell(agent1, agent2, "Explain your findings about the bug")
```

**`get_status(agent, n_exchanges=3)`** - Generate work summaries
```python
status = get_status(agent, n_exchanges=5, model="gpt-4o")
```

### Batch Execution

Execute multiple patterns in parallel:

```python
from polycli.orchestration import batch

@pattern
def analyze(agent: PolyAgent, file: str):
    """Analyze a single file"""
    return agent.run(f"Analyze {file}").content

# Parallel execution (fast!)
with session() as s:
    with batch():
        result1 = analyze(agent1, "file1.py")  # Queued
        result2 = analyze(agent2, "file2.py")  # Queued
        result3 = analyze(agent3, "file3.py")  # Queued
    # All execute simultaneously here
```

### Creating Custom Patterns

```python
@pattern
def code_review(developer: PolyAgent, reviewer: PolyAgent, code_file: str):
    """Custom pattern for code review workflow"""
    # Pattern automatically tracks execution when used in a session
    code_content = developer.run(f"Read and explain {code_file}").content
    review = reviewer.run(f"Review this code: {code_content}").content
    return review

# Use with monitoring
with session() as s:
    serve_session(s, port=8765)
    result = code_review(agent1, agent2, "main.py")  # Tracked in web UI
```

### Web UI Features

- **Real-time Monitoring**: Watch patterns execute live
- **Pause & Resume**: Pause before next pattern execution
- **Message Injection**: Add messages to any agent while paused
- **Agent History**: View complete conversation history per agent
- **Pattern Timeline**: Track all pattern executions with inputs/outputs
- **Session Cancellation**: Stop running sessions and free resources

## Claude Code Hooks Integration

PolyCLI can capture real-time events from Claude Code, providing visibility into every tool use (Read, Edit, Bash, etc.) as it happens, not just the final result.

### Setup (One-time)

Install PolyCLI hooks into Claude Code to enable event streaming:

```bash
# Install hooks globally (recommended)
polycli cchook install --scope global

# Or install for current project only
polycli cchook install --scope local

# Check installation status
polycli cchook check --scope global

# Uninstall if needed
polycli cchook uninstall --scope global
```

### Event Streaming

Once hooks are installed, use event streaming to see Claude's actions in real-time:

```python
from polycli import PolyAgent

agent = PolyAgent()

# Enable event streaming
for item in agent.run("implement a todo app", cli='claude-code', stream_events=True):
    if hasattr(item, 'event_type'):  # It's a ClaudeEvent
        print(f"⚡ {item.event_type}: {item.tool_name or ''}")
        # Access full event data
        if item.tool_input:
            print(f"   Input: {item.tool_input}")
    else:  # It's the final RunResult
        result = item
        print(f"✅ Complete: {result.content}")
```

### SSE Broadcasting with Patterns

Use the built-in `claude_run_stream` pattern (or implement your own based on it) to broadcast events to web UI via Server-Sent Events:

```python
from polycli.orchestration import session, serve_session
from polycli.orchestration.builtin_patterns import claude_run_stream

with session() as s:
    serve_session(s, port=8765)  # Start monitoring server
    
    agent = PolyAgent(id="claude-agent")
    # Events automatically broadcast to connected browsers
    result = claude_run_stream(agent, "analyze this codebase")
```

### Event Structure

Each `ClaudeEvent` contains:
- `session_id`: Claude's session identifier
- `event_type`: Type of event (PreToolUse, PostToolUse, SessionStart, etc.)
- `timestamp`: When the event occurred  
- `tool_name`: Which tool was used (if applicable)
- `tool_input`: Input parameters (for PreToolUse)
- `tool_response`: Output (for PostToolUse)

## LLM Call Caching

PolyCLI includes intelligent caching to eliminate redundant API calls during development, especially useful for debugging complex multi-step workflows.

### How It Works

- **Cache Key**: Generated from prompt + model + backend + conversation history
- **Cache Value**: Both the result AND the agent's post-run state
- **Perfect Resumption**: On cache hit, restores exact state for continuation

### Usage

```bash
# Enable globally via environment variable
export POLYCLI_CACHE=true
```

```python
from polycli import PolyAgent

agent = PolyAgent()

# Cache enabled globally
result = agent.run("Analyze this data")  # First call: hits API

# Re-run with same prompt and history
result = agent.run("Analyze this data")  # Cache hit: instant, no API call

# Override cache per-call
result = agent.run("Get latest news", use_cache=False)  # Force fresh call
```

### Workflow Development Example

```python
# 20-step data pipeline
for step in range(20):
    result = agent.run(f"Process step {step}")
    
# Step 14 fails due to bug
# Fix bug and re-run: steps 1-13 are instant cache hits
# Only step 14+ make API calls
```

Cache stored in `.polycache/` directory (add to `.gitignore`).

## Sandbox Testing

Test your PolyCLI workflows in isolated Docker environments with persistent workspaces and automatic caching.

### Quick Start

```bash
# 1. Initialize sandbox structure
polycli sandbox init

# 2. Build Docker image (one-time setup)
docker build -t polycli-sandbox .

# 3. Set up Claude authentication (one-time setup)
claude setup-token
# This gives you a long-lived OAuth token (valid for 1 year)
# Add the token to .polyconfig

# 4. Run sandbox tests
polycli sandbox run                           # Run all test cases
polycli sandbox run --testcase example        # Run specific test case
polycli sandbox run --clean                    # Fresh start (clear workspace/cache)
polycli sandbox run --no-cache                 # Disable PolyCLI cache
polycli sandbox run --ports 8000:8000          # Port mapping for services
polycli sandbox run --image custom-image       # Use custom Docker image

# 5. List test cases and their status
polycli sandbox ls
```

### Project Structure

```
your-project/
├── .polyconfig              # Configuration (entry point, ports, tokens)
├── workflow/                # Your code (read-only in container)
│   └── main.py             # Entry point script
├── testcases/              # Test configurations (read-only in container)  
│   ├── example/            # Example test case
│   │   └── config.json     # Test configuration
│   └── test2/              # Another test case
│       └── config.json     
├── .workspaces/            # Persistent workspaces (auto-created)
│   ├── example/            # Workspace for example test
│   │   ├── .polycache/     # LLM response cache
│   │   ├── results.txt     # Generated files persist
│   │   └── run_counter.txt # State persists between runs
│   └── test2/              # Workspace for test2
└── logs/                   # Console output from runs
    ├── example_20250829_062711.log
    └── test2_20250829_063015.log
```

### Key Concepts

1. **Persistent Workspaces**: Each test case gets its own workspace that persists between runs
2. **Resume by Default**: Workspaces and cache are preserved unless you use `--clean`
3. **Isolated Testing**: Each test case runs in isolation with its own workspace
4. **Read-only Code**: Your workflow and test configurations are mounted read-only
5. **Cache Integration**: PolyCLI cache persists in each workspace's `.polycache/`

### Configuration (.polyconfig)

```ini
# PolyCLI Sandbox Configuration
entry: main.py                    # Entry point in workflow directory
ports: 8765:8765,8766:8766       # Port mappings for services
image: polycli-sandbox            # Docker image to use (optional)
claude_token: sk-ant-oat01-xxxxx  # Your Claude OAuth token
```

### Example Workflow

```python
# workflow/main.py
import json
from pathlib import Path
from polycli import PolyAgent

# Test configuration is always at /app/testcase/
with open("/app/testcase/config.json") as f:
    config = json.load(f)

print(f"Running test: {config['name']}")

# Process with agent (cache persists in workspace)
agent = PolyAgent()
result = agent.run(config["prompt"])

# Save results (workspace is current directory)
output = Path("results.txt")
output.write_text(result.content)

# State persists between runs
counter_file = Path("run_counter.txt")
if counter_file.exists():
    count = int(counter_file.read_text()) + 1
else:
    count = 1
counter_file.write_text(str(count))
print(f"This is run #{count} for this test case")
```

### Test Case Configuration

```json
// testcases/example/config.json
{
  "name": "example",
  "description": "Example test case",
  "prompt": "Generate a Python function for sorting"
}
```

### Features

- **Automatic Caching**: LLM responses cached per workspace
- **State Persistence**: Files and cache survive between runs
- **Clean Runs**: Use `--clean` to start fresh
- **Port Forwarding**: Map container ports to host
- **Custom Images**: Support for custom Docker images
- **Streaming Output**: Real-time console output
- **Comprehensive Logging**: All runs logged with timestamps

### Tips

1. **Initial Setup**: Files won't overwrite on `init` - safe to run multiple times
2. **Cache Location**: Each workspace has `.polycache/` for LLM response caching
3. **File Access**: Current directory in container is the workspace
4. **Test Data**: Access test configs at `/app/testcase/`
5. **Debugging**: Check logs in `logs/` directory for detailed output

For detailed documentation, see [docs/caching-and-sandbox.md](docs/caching-and-sandbox.md).

## Configuration

Create `models.json` in project root:
```json
{
  "models": {
    "gpt-4o": {
      "endpoint": "https://api.openai.com/v1",
      "api_key": "sk-...",
      "model": "gpt-4o"
    },
    "glm-4.5": {
      "endpoint": "https://api.example.com/v1",
      "api_key": "glm-...",
      "model": "glm-4.5"
    }
  }
}
```

## Architecture

![PolyCLI Architecture](assets/architecture.png)

### Core Components

- **PolyAgent**: Unified agent supporting all backends through a single interface
- **MessageList**: Single source of truth for conversation history with format auto-conversion
- **Session Registry**: Define and manage reusable sessions with web control panel
- **Orchestration**: Pattern execution with real-time monitoring and batch support
- **Token Management**: Automatic compaction when approaching limits

### Message Format Unification

The new `Message` and `MessageList` classes provide seamless conversion between:
- **Claude format**: JSONL with full metadata and tool tracking
- **Qwen format**: JSON with parts array
- **Codex format**: JSONL with session metadata and response items
- **Standard format**: Simple role/content pairs

```python
# Messages are automatically converted to the right format for each backend
agent = PolyAgent()
agent.run("Hello", cli="claude-code")  # Converts to Claude format
agent.run("Hi", cli="qwen-code")       # Converts to Qwen format
agent.run("Hey", cli="codex")          # Converts to Codex format
agent.save_state("chat.jsonl")         # Preserves original formats
```

## RunResult Interface

All agent `.run()` calls return a unified `RunResult`:

```python
result = agent.run("Calculate 5 * 8")

# Basic usage
print(result.content)        # Always a string
print(result.is_success)     # Boolean status
if not result:               # Pythonic error checking
    print(result.error_message)

# Structured data
if result.has_data():
    data = result.data       # Dictionary access

# Metadata
print(result.get_claude_cost())    # Cost tracking
print(result.get_session_id())     # Session ID
```

## Requirements
- Python 3.11+
- One or more CLI tools installed
- models.json for LLM configuration

## Roadmap
- [ ] Agent & LLM Integration
    - [x] Mini SWE-agent Integration
    - [x] Qwen Code Integration
    - [x] Codex CLI Integration
    - [x] streaming mode for no-tools
    - [ ] Local LLM support (Ollama, LM Studio, llama.cpp)
    - [ ] Handling LLM thinking mode
    - [ ] Improve Mini-SWE integration on message history
    - [ ] Use Gemini Core for integration instead of commands
    - [ ] Async support for agent operations
- [x] Native Multi-agent Orchestration
    - [x] Agent registration and tracing
    - [x] Pattern & Session System
    - [x] Web UI for monitoring
    - [x] Pause/Resume with message injection
    - [x] Session Registry with Control Panel
    - [x] Future/Promise pattern for batch results (access via `a.result` after batch execution)
- [ ] Context Management
    - [x] Token management with auto-compaction
    - [ ] Refine memory compact strategy

---

*Simple. Stable. Universal.*

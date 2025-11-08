# Agency-Code: Complete Documentation

> 📖 **This is the detailed documentation file for Agency-Code.**
> For quick setup and installation instructions, see [README.md](README.md)

---

## About Agency-Code

**An intelligent, self-contained AI development assistant powered by Claude with production-ready safety guardrails.**

> **Forked from**: [VRSEN/Agency-Code](https://github.com/VRSEN/Agency-Code.git)
> Enhanced with production-ready safety architecture, auto-termination, and webhook-ready integration.

Agency-Code is a fully open-sourced multi-agent system built with [Agency Swarm](https://agency-swarm.ai/welcome/overview) that acts as your AI software developer. It researches, plans, codes, debugs, and delivers production-ready solutions—all while monitoring itself for runaway processes and timeouts.

Perfect for rapid prototyping, code generation, or as the backend intelligence for your web application.

**📌 Quick Links:**
- [Installation Guide (README.md)](README.md#-quick-start)
- [Configuration (README.md)](README.md#-configuration)
- [Run Instructions (README.md)](README.md#%EF%B8%8F-run-agency-code)

---

## ✨ Key Features

### 🧠 **Intelligent Multi-Agent System**
- **Coder Agent**: Writes code, debugs errors, implements features with 14+ tools
- **Planner Agent**: Breaks down complex tasks, asks clarifying questions
- **Web Intelligence**: Integrated WebSearch and WebFetch for real-time research
- **Context-Aware**: Reads your codebase, understands project structure
- **Flexible Architecture**: Easy subagent creation, customizable communication flows

### 🛡️ **Production-Ready Safety Architecture**
- **Timeout Monitoring**: Session (30min), turn (5min), and tool (2min) limits
- **Runaway Detection**: Catches infinite loops, excessive reasoning, escalation spirals
- **Auto-Termination**: Optional auto-kill on timeout or runaway patterns
- **Graceful Cancellation**: Ctrl+C handler that saves state before exit
- **Background Monitoring**: Non-blocking safety checks in separate thread

### 🔌 **Webhook-Ready API Architecture**
- **Hook System**: Pre/post execution hooks trigger on every tool call and agent handoff
- **Webhook Integration**: Perfect for front-end/back-end communication via webhooks
- **Session Tracking**: Real-time session metrics (tool calls, duration, reasoning steps)
- **Sandboxed Execution**: Safe tool execution with configurable limits
- **Backend Intelligence**: Drop-in AI backend for your web application

### 🎯 **Developer-Friendly**
- **One Command Setup**: Clone, install, run
- **Environment-Based Config**: `.env` file configuration
- **Extensive Testing**: 181+ passing unit tests, 44 safety architecture tests
- **Open Source**: Fully open-source, build and refine as needed

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** (recommended)
- **Git**
- **Anthropic API Key** (Claude)

### Installation

#### **Mac/Linux**

```bash
# Clone the repository
git clone https://github.com/joeyjoe808/Agent-C.git
cd Agent-C

# Create virtual environment
python3.13 -m venv .venv
source .venv/bin/activate

# Upgrade pip and install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Fix LiteLLM bug (if needed)
python -m pip install git+https://github.com/openai/openai-agents-python.git@main

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
nano .env
```

#### **Windows (PowerShell)**

```powershell
# Clone the repository
git clone https://github.com/joeyjoe808/Agent-C.git
cd Agent-C

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate.ps1

# Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

# Fix LiteLLM bug (if needed)
python -m pip install git+https://github.com/openai/openai-agents-python.git@main

# Configure environment
copy .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
notepad .env
```

#### **Windows (Command Prompt)**

```cmd
REM Clone the repository
git clone https://github.com/joeyjoe808/Agent-C.git
cd Agent-C

REM Create virtual environment
python -m venv .venv
.venv\Scripts\activate.bat

REM Install dependencies
python -m pip install --upgrade pip
python -m pip install -r requirements.txt

REM Fix LiteLLM bug (if needed)
python -m pip install git+https://github.com/openai/openai-agents-python.git@main

REM Configure environment
copy .env.example .env
REM Edit .env and add your ANTHROPIC_API_KEY
notepad .env
```

### Configuration

Create a `.env` file in the root directory:

```env
# Required: Anthropic API Key
ANTHROPIC_API_KEY=your_anthropic_api_key_here

# Optional: Safety Features (default: enabled)
USE_SAFE_SESSION=true

# Optional: Model Selection (default: claude-haiku-4-5)
MODEL=anthropic/claude-haiku-4-5-20251001
```

### Run Agency-Code

```bash
# Mac/Linux
sudo python agency.py

# Windows
python agency.py
```

> **Note**: On macOS, use `sudo` to allow file editing in the current directory. 

**You'll see:**
```
[SafeSession] [OK] Session tracking enabled
[SafeSession] Session ID: abc123...

User: [Type your request here]
```

---

## 🛡️ Safety Features in Detail

### Timeout Monitoring

**Default Timeouts:**
- Session: 30 minutes
- Turn: 5 minutes
- Tool: 2 minutes

**Warning System:**
- 75% threshold: Warning message
- 90% threshold: Urgent warning
- 100%: Timeout exceeded

### Runaway Detection

**Patterns Automatically Detected:**
1. **Infinite Tool Loop**: Same tool called 5+ times in a row
2. **Excessive Reasoning**: 50+ reasoning steps without progress
3. **Escalation Spiral**: 10+ agent handoffs

### Auto-Termination (Opt-In)

Enable auto-kill on timeout or runaway:

```python
from safety import SafeSession, TimeoutConfig, BackgroundMonitor

session = SafeSession()
config = TimeoutConfig(max_session_duration=1800)  # 30 min

# Enable auto-termination
monitor = BackgroundMonitor(
    session,
    config,
    auto_terminate=True  # ⚠️ Enables auto-kill
)

monitor.start()
# ... agent runs with automatic protection ...
monitor.stop()
```

**Default behavior**: Detection only (no auto-kill) - you get warnings but the agent continues.

---

## 🔌 Webhook Integration for Web Applications

### Use as Backend Intelligence

Agency-Code is designed as a drop-in AI backend for your web application with built-in webhook support.

**FastAPI + Webhooks Example:**

```python
from fastapi import FastAPI
from safety import SafeSession, BackgroundMonitor, TimeoutConfig
from agency import agency
import httpx

app = FastAPI()

@app.post("/api/code-request")
async def code_request(prompt: str, webhook_url: str):
    """API endpoint for code generation with webhook callbacks"""
    session = SafeSession()
    config = TimeoutConfig(max_session_duration=600)  # 10 min
    monitor = BackgroundMonitor(session, config, auto_terminate=True)

    # Configure hook to send webhook on every tool execution
    async def send_webhook(event_type: str, data: dict):
        async with httpx.AsyncClient() as client:
            await client.post(webhook_url, json={
                "event": event_type,
                "session_id": session.session_id,
                "data": data
            })

    monitor.start()
    try:
        response = await agency.get_response(prompt)

        # Send final webhook
        await send_webhook("completed", {
            "response": response,
            "metrics": {
                "duration": session.metrics.get_duration(),
                "tool_calls": len(session.metrics.tool_calls)
            }
        })

        return {"session_id": session.session_id, "status": "completed"}
    finally:
        monitor.stop()
```

### Hook System for Webhook Triggers

Agency-Code includes a powerful hook system in `shared/system_hooks.py` that triggers on every action:

```python
def on_tool_execution(tool_name: str, args: dict):
    """Called BEFORE every tool execution - perfect for webhooks"""
    # Send webhook to your front-end
    # Log to database
    # Track API costs
    # Apply custom validation
    pass

def on_tool_completion(tool_name: str, result: dict):
    """Called AFTER every tool execution"""
    # Send completion webhook
    # Update front-end in real-time
    pass

def on_agent_handoff(from_agent: str, to_agent: str):
    """Called on agent handoffs"""
    # Track agent interactions
    # Send routing updates to front-end
    pass
```

### Real-Time Session Tracking

Stream session metrics to your front-end via WebSocket or webhooks:

```python
# Get real-time session metrics
session_data = {
    "session_id": session.session_id,
    "status": session.status,
    "duration": session.metrics.get_duration(),
    "tool_calls": len(session.metrics.tool_calls),
    "reasoning_steps": session.metrics.reasoning_steps
}

# Send to front-end via webhook
await webhook_client.post(webhook_url, json=session_data)
```

### Integration Benefits

✅ **Webhook-First Design**: Hooks trigger on every tool execution
✅ **Real-time Updates**: Stream progress to your front-end
✅ **Session Management**: Track and resume sessions
✅ **Safety Monitoring**: Timeout/runaway alerts via webhooks
✅ **Cost Tracking**: Monitor API usage per session
✅ **User Control**: Allow users to cancel long-running tasks

**Perfect for:**
- SaaS AI coding platforms
- Developer productivity tools
- Code generation APIs
- Educational coding platforms
- AI-powered IDEs

---

## 🔧 Adding Subagents

Create custom subagents for specialized tasks:

**Method 1: Let Agency-Code create it**

```
User: Ask me questions until you have enough context to create a QA tester subagent for my project
```

Agency-Code will create a new folder (`qa_tester_agent/`) and modify `agency.py` automatically.

**Method 2: Use the template**

See `subagent_example/` folder for a template you can customize.

---

## 🏗️ Architecture

### Multi-Agent System

```
┌─────────────────────────────────────────┐
│         Agency-Code (Main)              │
│                                         │
│  ┌──────────┐      ┌──────────┐        │
│  │  Coder   │◄────►│ Planner  │        │
│  │  Agent   │      │  Agent   │        │
│  └──────────┘      └──────────┘        │
│       │                  │              │
│       └──────┬───────────┘              │
│              │                          │
│       ┌──────▼──────┐                   │
│       │   Tools     │                   │
│       │  (14+ tools)│                   │
│       └─────────────┘                   │
└─────────────────────────────────────────┘
```

### Safety Architecture

```
SafeSession (Core)
    ├── SessionMetrics (tracking)
    ├── TimeoutMonitor (detection)
    ├── RunawayDetector (pattern detection)
    ├── BackgroundMonitor (enforcement) ⭐
    └── CancellationHandler (Ctrl+C) ⭐
```

### Available Tools

- **Code Tools**: Read, Write, Edit, Grep, Glob, MultiEdit
- **System Tools**: Bash (sandboxed), Git, Ls
- **AI Tools**: WebSearch, WebFetch, Thinking
- **Notebook Tools**: NotebookRead, NotebookEdit

---

## 🧪 Testing

**Run all tests:**
```bash
pytest tests/ -v
```

**Run safety architecture tests (44 tests):**
```bash
pytest tests/test_session_metrics.py \
       tests/test_safe_session.py \
       tests/test_timeout_monitor.py \
       tests/test_runaway_detector.py \
       tests/test_background_monitor.py \
       tests/test_cancellation.py -v
```


---

## 🌟 Why Agency-Code?

**Other AI coding assistants:**
- Rely on you to monitor them
- No built-in safety mechanisms
- Limited integration options
- Black-box operation

**Agency-Code:**
- ✅ Monitors itself (timeout, runaway detection)
- ✅ Production-ready safety architecture
- ✅ API-ready with hooks for custom integration
- ✅ Transparent operation with full session tracking
- ✅ Open-source and extensible
- ✅ WebSearch/WebFetch intelligence built-in

**Built for developers who need an AI coding assistant that won't run away with their API budget or get stuck in infinite loops.**

---

## 📝 Demo Tasks

### 🌌 Particle Galaxy Simulator

```
Create a full-screen interactive particle galaxy simulator using HTML5 Canvas and JavaScript. Include:
  - 2000 glowing particles that form a spiral galaxy shape
  - Particles should have different colors (blues, purples, pinks, whites) and sizes
  - Mouse movement creates gravitational pull that attracts/repels particles
  - Click to create a "supernova" explosion effect that pushes particles outward
  - Add trailing effects for particle movement
  - Include controls to adjust: particle count, rotation speed, color themes (nebula/aurora/cosmic)
  - Add background stars that twinkle
  - Display FPS counter and particle count
  - Make it responsive and add a glow/bloom effect to particles
  All in a single HTML file with inline CSS and JavaScript. Make it mesmerizing and cinematic.
```

### 🎨 Multiplayer Pixel Art Board

```
Create a shared pixel art canvas like r/place using Next.js and Socket.io:

- 50x50 grid where each player can color one pixel at a time
- 16 color palette at the bottom
- See other players' cursors moving in real-time with their names
- 5-second cooldown between placing pixels (show countdown on cursor)
- Minimap in corner showing full canvas
- Chat box for players to coordinate
- Download canvas as image button
- Show "Player X placed a pixel" notifications
- Persist canvas state in JSON file
- Mobile friendly with pinch to zoom

Simple and fun - just a shared canvas everyone can draw on together. Add rainbow gradient background.
```

### 📚 Agency Swarm PDF Chat App

```
Create a Streamlit PDF chat app using PyPDF2 and OpenAI API with Agency Swarm framework:
- File uploader accepting multiple PDFs
- Extract and display PDF text in expandable sections
- Chat interface where users ask questions about the PDFs
- Use agency-swarm to create an agent that can answer questions about the PDFs. (Reference below)
   - Use file_ids parameter in agency.get_response_sync method for allowing the agent to use the uploaded files.
- Create an endpoint for uploading files to openai. (Reference below)
   - Set purpose to "user_data".
   - Attach file in file_ids parameter of get_response method in agency-swarm. (Check reference.)
- OPENAI_API_KEY is provided in the ./.env file. Copy it to the .env file in the backend server folder.
- Export conversation as markdown
Include sample questions and nice chat UI with user/assistant message bubbles.

References:
- agency-swarm quick start: https://agency-swarm.ai/welcome/getting-started/from-scratch
- Openai API file upload reference: https://platform.openai.com/docs/api-reference/files/create

Before starting the task make sure to first use the WebSearch tool to read the references above.

**Important**: The agency-swarm integration must **actually** work. Do not use any placeholder messages and do not come back to me until it's fully tested and completed. Run the backend server and test the integration.
```

---

## 📂 Project Structure

```
Agency-Code/
├── agency.py                 # Main entry point
├── .env                      # Configuration (API keys)
├── requirements.txt          # Python dependencies
│
├── agency_code_agent/        # Coder agent implementation
├── planner_agent/            # Planner agent implementation
│
├── safety/                   # Safety architecture
│   ├── session_metrics.py    # Metrics tracking
│   ├── safe_session.py       # Session wrapper
│   ├── timeout_monitor.py    # Timeout detection
│   ├── runaway_detector.py   # Runaway pattern detection
│   ├── background_monitor.py # Auto-termination
│   └── cancellation.py       # Ctrl+C handler
│
├── tools/                    # 14+ tool implementations
├── shared/                   # Shared utilities & hooks
└── tests/                    # 181+ automated tests
```

---

## 🤝 Contributing

We welcome contributions! This is fully open-source software - build, refine, and improve as needed.

**Development Workflow:**
1. Fork the repository
2. Create a feature branch
3. Write tests first (TDD approach)
4. Implement your feature
5. Run test suite (`pytest tests/ -v`)
6. Submit pull request

**Areas for Contribution:**
- Additional safety features
- New tools and integrations
- Performance optimizations
- Documentation improvements
- Bug fixes and testing

**Developer Guidelines:**

For detailed coding standards, testing conventions, and repository structure, see [AGENTS.md](AGENTS.md):
- Project structure and module organization
- Build and test commands
- Coding style and naming conventions
- Testing guidelines
- Commit and PR guidelines
- Configuration and secrets management

We're actively supporting and improving this repo. All contributions welcome!

---

## 📝 License

MIT License - see [LICENSE](LICENSE) for details.

---

## 🔗 Links

- **Repository**: https://github.com/joeyjoe808/Agent-C
- **Issues**: https://github.com/joeyjoe808/Agent-C/issues
- **Original Fork**: https://github.com/VRSEN/Agency-Code
- **Agency Swarm Framework**: https://agency-swarm.ai/

---

**Ready to get started?**

```bash
git clone https://github.com/joeyjoe808/Agent-C.git
cd Agent-C
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python agency.py
```

**Questions? Open an issue on GitHub!**

# Integrating NLIP with Agent Development Frameworks

The agent development frameworks such as LangChain, AutoGen, and LlamaIndex have significantly facilitated the development of large language model (LLM) based applications. However, this diversity has led to a fragmented ecosystem where agents lack a shared communication protocol, limiting interoperability between agents across domain and across devlopment frameworks. To address this challenge, we show the convenient integration of the Natural Language Interaction Protocol (NLIP) with agent development frameworks to enable seamless, standardized communication among heterogeneous agents.

NLIP operates as an external communication layer, allowing it to encapsulate standalone agent applications or bridge agents built using different development frameworks. It provides a non-intrusive interface for message passing and task delegation, without requiring modification of the agent's application logic or the underlying framework's tool-calling mechanisms. Using NLIP, agents developed under different frameworks can interact, exchange information, and coordinate tasks across domain boundaries, supporting the construction of more flexible and interconnected multi-agent ecosystems.

In the following, this approach is demonstrated through a weather query task. In this demonstration, a coordinator agent based on LangChain receives a compound user query and delegates specialized subtasks to a worker agent built with LlamaIndex, which accesses an external weather API. The agents use NLIP messages for all interactions, allowing the coordinator to aggregate responses from the worker and return a synthesized answer to the user. This workflow validates NLIP as an effective solution for enabling secure and efficient collaboration in heterogeneous agent environments.

In summary, NLIP seamlessly integrates with existing agent development frameworks and establishes a foundation for scalable, interoperable communication, facilitating a unified and capable multi-agent ecosystem.

Demonstrates **NLIP** integration with AI agent frameworks, showcasing inter-agent communication capabilities.

📹 **[Watch Demo Video](https://drive.google.com/file/d/1C4p6kMPOgLltAx3djye8xrbSvJ4KQlbg/view?usp=sharing)** - See the demo in action!

📄 **[Presentation Slides: "Integrating NLIP with Agent Development Frameworks (July 23, '25).pdf"](https://github.com/computersystemspfdl/integrating-nlip-with-agent-dev-frameworks/blob/main/NLIP%20demo%20(July%2023%2C%202025).pdf)**

## 🎯 What This Shows

1. **🔄 Inter-Agent Communication**: LangChain coordinator agent delegates to LlamaIndex worker agent via NLIP
2. **🏠 Standalone Integration**: NLIP integration with individual agent development frameworks

**Key Capabilities:**
- Cross-framework communication via NLIP protocol
- Task delegation between specialized agents

## 🏗️ Project Structure

```
nlip-with-agent-frameworks/
├── README.md                    # This file
├── pyproject.toml              # Dependencies and project config
├── requirements.txt         
├── .env                        # Environment variables 
├── demo/
│   ├── inter_agent/           # Inter-agent communication demo
│   │   ├── langchain_coordinator.py
│   │   ├── llamaindex_worker.py
│   │   └── README.md
│   ├── standalone/            # Standalone framework demos
│   │   ├── langchain_standalone.py
│   │   ├── llamaindex_standalone.py
│   │   └── README.md
│   └── shared/               # Shared utilities
│       ├── weather_tools.py
│       ├── nlip_client.py
│       └── __init__.py
```

## 🚀 Quick Start

**Prerequisites:** Python 3.10+, Poetry (recommended) or pip

**Setup:**
```bash
git clone <repository-url>
cd nlip-with-agent-frameworks

# Clone the nlip-server dependency into the project directory
git clone https://github.com/nlip-project/nlip_server.git

# Install project dependencies
poetry install  # or: pip install -r requirements.txt

# Configure API key
cp .env.example .env
# Edit .env with: OPENROUTER_API_KEY=your-key-from-https://openrouter.ai/
```

### Run Inter-Agent Demo

Open two terminals in the project directory:

**Terminal 1 - Start LlamaIndex Agent:**
```bash
poetry run uvicorn demo.inter_agent.llamaindex_worker:app --host 0.0.0.0 --port 8013 --reload
```

**Terminal 2 - Start LangChain Agent:**
```bash
poetry run uvicorn demo.inter_agent.langchain_coordinator:app --host 0.0.0.0 --port 8012 --reload
```

**Terminal 3 - NLIP client:**
```bash
curl -X POST http://localhost:8012/nlip/ \
  -H "Content-Type: application/json" \
  -d '{"format": "text", "subformat": "english", "content": "Weather alerts for California?"}'
```

### Run Standalone Demo
```bash
poetry run uvicorn demo.standalone.langchain_standalone:app --port 8014
# Or: poetry run uvicorn demo.standalone.llamaindex_standalone:app --port 8015

# Test:
curl -X POST http://localhost:8014/nlip/ \
  -H "Content-Type: application/json" \
  -d '{"format": "text", "subformat": "english", "content": "Weather alerts for California?"}'
```

## 📊 Demo Scenarios

**Inter-Agent:** Client → LangChain → (NLIP) → LlamaIndex → Weather APIs  
**Standalone:** Client → NLIP Server → Weather APIs  


## 📋 Dependencies

This demo requires:
- **Python 3.10+** (required for NLIP SDK)
- **NLIP SDK & Server** (installed from PyPI: `nlip-sdk>=0.1.2`, `nlip-server`)
- **OpenRouter API Key** (for AI model access)

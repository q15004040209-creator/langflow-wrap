# Langflow Wrapper🤖

> A powerful platform for building and deploying AI-powered agents and workflows — visual builder + Python API.

## What is Langflow?

**Langflow** is an open-source platform for building and deploying AI-powered agents and workflows. It provides a visual drag-and-drop builder for designing AI pipelines, with built-in support for all major LLMs, vector databases, RAG pipelines, and MCP servers.

This wrapper provides a Pythonic interface for programmatically creating, managing, and deploying Langflow workflows.

##⭐ Key Features

- **Visual Builder** — Drag-and-drop AI workflow designer
- **Python-first** — Customize any component with Python code
- **Interactive Playground** — Test flows step-by-step
- **Multi-agent Orchestration** — Conversation management and retrieval
- **RAG Pipeline** — Document ingestion to retrieval, out-of-the-box
- **API Deployment** — Export as REST API for any framework
- **MCP Server** — Turn flows into tools for MCP clients
- **Observability** — LangSmith, LangFuse integrations
- **Enterprise-ready** — Security and scalability

## 📦 Installation

```bash
pip install langflow-wrap
```

Or from source:

```bash
git clone https://github.com/q15004040209-creator/langflow-wrap.git
cd langflow-wrap
pip install -e .
```

##🚀 Quick Start

```python
from langflow import LangFlowClient, Flow, Component

# Connect to a Langflow instance
client = LangFlowClient(
    base_url="http://localhost:7860",
    api_key="your-api-key"  # Optional, for authenticated deployments
)

# List available flows
flows = client.flows.list()
for flow in flows:
    print(f"- {flow.name} ({flow.id})")

# Load a flow
flow = client.flows.load("my-rag-flow")
print(f"Loaded: {flow.name} with {len(flow.components)} components")

# Run a flow
result = flow.run(
    input_value="What are the main topics in our documentation?",
    tweaks={"embedder": {"model": "text-embedding-3-small"}}
)
print(result.message)
```

## 🔧 Configuration

```python
from langflow import LangFlowClient

client = LangFlowClient(
    base_url="http://localhost:7860",
    api_key="your-api-key",
    timeout=120,
    verify_ssl=True
)

# Switch between environments
client.env = "production"  # or "development", "staging"
```

## 📚 API Reference

### Flows

```python
# List all flows
flows = client.flows.list(tags=["production", "rag"])

# Create a new flow from a template
flow = client.flows.create(
    name="My RAG Pipeline",
    description="Document Q&A with retrieval",
    template="rag-basic"  # or build from scratch
)

# Run a flow
result = flow.run(
    input_value="What is Langflow?",
    input_type="chat",  # chat / input / text
    tweaks={
        "llm": {"temperature": 0.7, "model": "gpt-4o"},
        "embedder": {"model": "text-embedding-3-small"},
        "retriever": {"top_k": 5}
    }
)
print(result.message)
print(f"Tokens: {result.usage}")

# Export flow as JSON
flow_json = flow.export()
with open("my-flow.json", "w") as f:
    json.dump(flow_json, f, indent=2)

# Import flow from JSON
with open("my-flow.json") as f:
    imported = client.flows.import_from_json(json.load(f))
```

### Components

```python
# List available components
components = client.components.list()
for c in components:
    print(f"{c.type}: {c.name}")

# Create a custom component
custom = client.components.create(
    name="MyVectorStore",
    code="""
from langflow import Component, text
from langchain.vectorstores import Chroma

class MyVectorStore(Component):
    display_name = "My Vector Store"
    description = "Custom vector store with filtering"

    def build(self):
        return Chroma()
    """,
    library="custom"
)

# Add component to a flow
flow.add_component(custom, position={"x": 100, "y": 200})
```

### Agents

```python
# Create a ReAct agent
agent = client.agents.create(
    name="Research Agent",
    model="gpt-4o",
    tools=["web_search", "wikipedia", "calculator"],
    max_iterations=10
)

# Run the agent
response = agent.run("Research the latest developments in quantum computing")
print(response.output)
print(f"Steps: {response.iterations}")
```

### RAG Pipelines

```python
# Build a RAG pipeline
pipeline = client.rag.build(
    embedder="text-embedding-3-small",
    chunker="recursive-character",
    vectorstore="chroma",
    retriever="semantic-search"
)

# Index documents
pipeline.index(
    documents=["./docs/*.pdf", "./docs/*.md"],
    metadata={"source": "documentation"}
)

# Query
result = pipeline.query("How do I deploy Langflow?")
print(result.answer)
print(f"Sources: {result.sources}")
```

### Observability

```python
# Enable LangSmith tracing
client.observability.configure(
    provider="langsmith",
    api_key="your-langsmith-key",
    project="production-flows"
)

# View traces
traces = client.observability.list_traces(
    flow_id=flow.id,
    limit=50,
    status="error"
)
for trace in traces:
    print(f"{trace.timestamp}: {trace.duration_ms}ms - {trace.status}")
```

### MCP Server

```python
# Deploy a flow as an MCP server
mcp = client.mcp.deploy(
    flow_id=flow.id,
    name="document-qa",
    description="Answer questions about our documentation",
    tools=["retrieve", "generate"]
)

# Connect to the MCP server
client.mcp.connect(
    url=f"http://localhost:3000/mcp/{mcp.server_id}",
    api_key=mcp.api_key
)
```

## 🌐 Deployment Options

### Docker (Recommended)

```bash
docker run -p 7860:7860 langflowai/langflow:latest
```

### Python Package

```bash
uv pip install langflow -U
uv run langflow run
```

### Desktop App

Download Langflow Desktop for Windows/macOS at [langflow.org/desktop](https://langflow.org/desktop).

## 📄 License

- **This wrapper**: MIT License
- **Langflow**: MIT License — [langflow-ai/langflow](https://github.com/langflow-ai/langflow)

## 🔗 Links

- 🌐 [Langflow Official](https://langflow.org)
- 📖 [Documentation](https://docs.langflow.org)
- 💬 [Discord](https://discord.gg/EqksyE2EX9)
- 🐛 [Report Issues](https://github.com/langflow-ai/langflow/issues)
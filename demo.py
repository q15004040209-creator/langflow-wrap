#!/usr/bin/env python3
"""
Langflow Wrapper - Demo Script
A Pythonic interface for building AI workflows with Langflow.

This demo showcases the main features of the langflow-wrap library.
Run with: python demo.py
"""

from langflow import LangFlowClient, Flow


def demo_list_flows():
    """List available flows in the Langflow instance."""
    print("\n" + "=" * 60)
    print("DEMO 1: List Available Flows")
    print("=" * 60)

    client = LangFlowClient(base_url="http://localhost:7860")

    flows = client.flows.list(tags=["production"])
    print(f"\n📋 Found {len(flows)} production flows:")
    for flow in flows:
        print(f"  • {flow.name} ({flow.id})")
        print(f"    Description: {flow.description[:80]}...")
        print(f"    Components: {len(flow.components)}")
        print()


def demo_run_flow():
    """Run a loaded flow with custom inputs."""
    print("\n" + "=" * 60)
    print("DEMO 2: Run a Flow")
    print("=" * 60)

    client = LangFlowClient(base_url="http://localhost:7860")

    flows = client.flows.list(limit=5)
    if not flows:
        print("No flows found. Create one first at http://localhost:7860")
        return

    flow = client.flows.load(flows[0].id)
    print(f"\n🔄 Running flow: {flow.name}")

    result = flow.run(
        input_value="What is Langflow and what can I build with it?",
        input_type="chat",
        tweaks={
            "llm": {"temperature": 0.7, "model": "gpt-4o"},
            "embedder": {"model": "text-embedding-3-small"},
        }
    )

    print(f"\n💬 Response:\n{result.message}")
    print(f"\n📊 Stats: {result.iterations} iterations, tokens: {result.usage}")


def demo_build_rag():
    """Build and query a RAG pipeline."""
    print("\n" + "=" * 60)
    print("DEMO 3: RAG Pipeline")
    print("=" * 60)

    client = LangFlowClient(base_url="http://localhost:7860")

    # Build RAG pipeline
    pipeline = client.rag.build(
        embedder="text-embedding-3-small",
        chunker="recursive-character",
        vectorstore="chroma",
        retriever="semantic-search"
    )

    print("\n📚 Indexing documents...")
    pipeline.index(
        documents=["./docs/*.pdf", "./docs/*.md"],
        metadata={"source": "documentation"}
    )
    print("  ✅ Documents indexed")

    # Query
    print("\n🔍 Querying the knowledge base...")
    result = pipeline.query(
        question="How do I deploy Langflow in production?",
        top_k=5
    )

    print(f"\n💬 Answer:\n{result.message}")
    if result.artifacts.get("sources"):
        print(f"\n📄 Sources:")
        for src in result.artifacts["sources"]:
            print(f"  • {src}")


def demo_create_agent():
    """Create and run an AI agent with tools."""
    print("\n" + "=" * 60)
    print("DEMO 4: AI Agent with Tools")
    print("=" * 60)

    client = LangFlowClient(base_url="http://localhost:7860")

    print("\n🤖 Creating research agent...")
    agent = client.agents.create(
        name="Research Assistant",
        model="gpt-4o",
        tools=["web_search", "wikipedia", "calculator", "code_executor"],
        max_iterations=10
    )
    print(f"  ✅ Agent created: {agent.name} ({agent.id})")

    print("\n⏳ Running agent task...\n")
    response = agent.run(
        "Research the latest developments in LLM agents. "
        "Find at least 3 recent papers or projects and summarize each."
    )

    print(f"💬 Agent Response:\n{response.message}")
    print(f"\n📊 Completed in {response.iterations} iterations")


def demo_components():
    """Browse available components."""
    print("\n" + "=" * 60)
    print("DEMO 5: Browse Components")
    print("=" * 60)

    client = LangFlowClient(base_url="http://localhost:7860")

    components = client.components.list(library="langflow")
    print(f"\n🔧 Found {len(components)} Langflow components:")

    for c in components[:10]:
        print(f"  • [{c.type}] {c.name}")
        print(f"    {c.description[:70]}...")


def demo_mcp_deploy():
    """Deploy a flow as an MCP server."""
    print("\n" + "=" * 60)
    print("DEMO 6: Deploy Flow as MCP Server")
    print("=" * 60)

    client = LangFlowClient(base_url="http://localhost:7860")

    flows = client.flows.list(limit=1)
    if not flows:
        print("No flows available to deploy.")
        return

    flow_id = flows[0].id
    print(f"\n🚀 Deploying flow '{flows[0].name}' as MCP server...")

    mcp = client.mcp.deploy(
        flow_id=flow_id,
        name="document-qa",
        description="Answer questions about our documentation",
        tools=["retrieve", "generate"]
    )

    print(f"  ✅ MCP server deployed!")
    print(f"📡 Server URL: {mcp.get('url', 'N/A')}")
    print(f"  🔑 API Key: {mcp.get('api_key', 'N/A')[:20]}...")


def demo_observability():
    """Configure observability and view traces."""
    print("\n" + "=" * 60)
    print("DEMO 7: Observability & Traces")
    print("=" * 60)

    client = LangFlowClient(base_url="http://localhost:7860")

    # Configure LangSmith
    print("\n📊 Configuring LangSmith tracing...")
    result = client.observability.configure(
        provider="langsmith",
        api_key="your-langsmith-key",
        project="production-flows"
    )
    print(f"  ✅ {result}")

    # List traces
    print("\n📜 Recent traces:")
    traces = client.observability.list_traces(limit=10)
    for trace in traces:
        print(f"  • {trace.get('timestamp', 'N/A')[:19]}")
        print(f"    Duration: {trace.get('duration_ms', 0)}ms")
        print(f"    Status: {trace.get('status', 'unknown')}")


def main():
    print("\n" + "🎯" * 30)
    print("\n  Langflow Wrapper - Demo Suite")
    print("\n" + "🎯" * 30)
    print("\nMake sure Langflow is running at http://localhost:7860")
    print("Create some flows at http://localhost:7860 first!\n")

    demos = [
        ("List Flows", demo_list_flows),
        ("Run Flow", demo_run_flow),
        ("Build RAG", demo_build_rag),
        ("Create Agent", demo_create_agent),
        ("Browse Components", demo_components),
        ("Deploy MCP", demo_mcp_deploy),
        ("Observability", demo_observability),
    ]

    for name, fn in demos:
        try:
            fn()
        except Exception as e:
            print(f"\n⚠️  Demo '{name}' failed: {e}\n")

    print("\n" + "🏁" * 30)
    print("\n Demo suite complete!")
    print("\n📚 For more examples, see the README.md")
    print("🌐 https://github.com/q15004040209-creator/langflow-wrap")


if __name__ == "__main__":
    main()
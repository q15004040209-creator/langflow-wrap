"""
Langflow Wrapper - Python Interface
A Pythonic wrapper for Langflow AI workflow platform.

Usage:
    from langflow import LangFlowClient, Flow

    client = LangFlowClient(base_url="http://localhost:7860")
    flows = client.flows.list()
    result = client.flows.load("my-flow").run(input_value="Hello")
"""

import urllib.request
import urllib.error
import json
import time
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from typing_extensions import TypedDict


__version__ = "0.1.0"
__all__ = ["LangFlowClient", "Flow", "Component", "Agent", "RAGPipeline"]


@dataclass
class FlowInfo:
    id: str
    name: str
    description: str
    components: List[Dict]
    created_at: str
    updated_at: str
    tags: List[str] = field(default_factory=list)


@dataclass
class RunResult:
    message: str
    outputs: Dict[str, Any]
    usage: Dict[str, int]
    iterations: int
    artifacts: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ComponentInfo:
    type: str
    name: str
    description: str
    inputs: List[str]
    outputs: List[str]


class LangFlowClient:
    """Python client for Langflow."""

    def __init__(
        self,
        base_url: str = "http://localhost:7860",
        api_key: Optional[str] = None,
        timeout: int = 120,
        verify_ssl: bool = True,
        env: str = "development"
    ):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout
        self.verify_ssl = verify_ssl
        self.env = env
        self._flows = FlowsInterface(self)
        self._components = ComponentsInterface(self)
        self._agents = AgentsInterface(self)
        self._rag = RAGInterface(self)
        self._mcp = MCPInterface(self)
        self._observability = ObservabilityInterface(self)

    def _request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ):
        """Make an HTTP request."""
        url = f"{self.base_url}{path}"
        if params:
            query = "&".join(f"{k}={v}" for k, v in params.items())
            url = f"{url}?{query}"

        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = urllib.request.Request(url, headers=headers, method=method)
        if data:
            req.data = json.dumps(data).encode()

        try:
            resp = urllib.request.urlopen(req, timeout=self.timeout)
            content = resp.read()
            return json.loads(content) if content else {}
        except urllib.error.HTTPError as e:
            return {"error": f"HTTP {e.code}", "detail": e.read().decode()}
        except Exception as e:
            return {"error": str(e)}

    @property
    def flows(self):
        return self._flows

    @property
    def components(self):
        return self._components

    @property
    def agents(self):
        return self._agents

    @property
    def rag(self):
        return self._rag

    @property
    def mcp(self):
        return self._mcp

    @property
    def observability(self):
        return self._observability


class FlowsInterface:
    def __init__(self, client: LangFlowClient):
        self._client = client

    def list(self, tags: Optional[List[str]] = None, limit: int = 50) -> List[FlowInfo]:
        params = {"limit": limit}
        if tags:
            params["tags"] = ",".join(tags)

        result = self._client._request("GET", "/api/v1/flows", params=params)
        flows = result.get("flows", result.get("error", []))
        if isinstance(flows, str):
            return []
        return [
            FlowInfo(
                id=f.get("id", ""),
                name=f.get("name", ""),
                description=f.get("description", ""),
                components=f.get("components", []),
                created_at=f.get("created_at", ""),
                updated_at=f.get("updated_at", ""),
                tags=f.get("tags", []),
            )
            for f in flows
        ]

    def load(self, flow_id: str) -> "Flow":
        result = self._client._request("GET", f"/api/v1/flows/{flow_id}")
        if "error" in result:
            raise ValueError(f"Flow not found: {flow_id}")
        return Flow(self._client, result)

    def create(
        self,
        name: str,
        description: str = "",
        template: Optional[str] = None,
    ) -> FlowInfo:
        data = {"name": name, "description": description}
        if template:
            data["template"] = template

        result = self._client._request("POST", "/api/v1/flows", data=data)
        return FlowInfo(
            id=result.get("id", ""),
            name=name,
            description=description,
            components=[],
            created_at=result.get("created_at", ""),
            updated_at=result.get("updated_at", ""),
            tags=[],
        )

    def import_from_json(self, flow_json: Dict) -> Flow:
        result = self._client._request("POST", "/api/v1/flows/import", data=flow_json)
        return Flow(self._client, result)


class Flow:
    """A Langflow workflow."""

    def __init__(self, client: LangFlowClient, data: Dict):
        self._client = client
        self.data = data
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.description = data.get("description", "")
        self.components = data.get("components", {})

    def run(
        self,
        input_value: str,
        input_type: str = "chat",
        tweaks: Optional[Dict[str, Dict]] = None,
        stream: bool = False,
    ) -> RunResult:
        data = {
            "input_value": input_value,
            "input_type": input_type,
            "tweaks": tweaks or {},
            "stream": stream,
        }

        # Add any flow-level tweaks from self.data
        if "tweaks" in self.data and not tweaks:
            data["tweaks"] = self.data["tweaks"]

        result = self._client._request(
            "POST",
            f"/api/v1/flows/{self.id}/run",
            data=data
        )

        if "error" in result:
            return RunResult(
                message=f"Error: {result['error']}",
                outputs={},
                usage={},
                iterations=0,
            )

        return RunResult(
            message=result.get("message", result.get("outputs", {}).get("message", "")),
            outputs=result.get("outputs", {}),
            usage=result.get("usage", {}),
            iterations=result.get("iterations", 1),
            artifacts=result.get("artifacts", {}),
        )

    def export(self) -> Dict:
        return self.data

    def add_component(self, component: "Component", position: Dict[str, int]):
        self.components[component.id] = {
            "type": component.type,
            "data": component.data,
            "position": position,
        }
        return self


class Component:
    """A Langflow component."""

    def __init__(self, client: LangFlowClient, data: Dict):
        self._client = client
        self.id = data.get("id", "")
        self.type = data.get("type", "")
        self.name = data.get("name", "")
        self.data = data.get("data", {})
        self.description = data.get("description", "")

    @classmethod
    def create(
        cls,
        client: LangFlowClient,
        name: str,
        code: str,
        library: str = "custom",
    ):
        data = {
            "name": name,
            "code": code,
            "library": library,
        }
        result = client._request("POST", "/api/v1/components", data=data)
        return cls(client, result)


class ComponentsInterface:
    def __init__(self, client: LangFlowClient):
        self._client = client

    def list(
        self,
        library: Optional[str] = None,
        type: Optional[str] = None,
    ) -> List[ComponentInfo]:
        params = {}
        if library:
            params["library"] = library
        if type:
            params["type"] = type

        result = self._client._request("GET", "/api/v1/components", params=params)
        comps = result.get("components", result.get("error", []))
        if isinstance(comps, str):
            return []
        return [
            ComponentInfo(
                type=c.get("type", ""),
                name=c.get("name", ""),
                description=c.get("description", ""),
                inputs=c.get("inputs", []),
                outputs=c.get("outputs", []),
            )
            for c in comps
        ]


class AgentsInterface:
    def __init__(self, client: LangFlowClient):
        self._client = client

    def create(
        self,
        name: str,
        model: str = "gpt-4o",
        tools: Optional[List[str]] = None,
        max_iterations: int = 10,
    ) -> "Agent":
        data = {
            "name": name,
            "model": model,
            "tools": tools or [],
            "max_iterations": max_iterations,
        }
        result = self._client._request("POST", "/api/v1/agents", data=data)
        return Agent(self._client, result)

    def list(self) -> List[Dict]:
        result = self._client._request("GET", "/api/v1/agents")
        return result.get("agents", [])


class Agent:
    def __init__(self, client: LangFlowClient, data: Dict):
        self._client = client
        self.id = data.get("id", "")
        self.name = data.get("name", "")
        self.model = data.get("model", "")
        self.tools = data.get("tools", [])

    def run(self, task: str) -> RunResult:
        result = self._client._request(
            "POST",
            f"/api/v1/agents/{self.id}/run",
            data={"task": task}
        )
        return RunResult(
            message=result.get("output", result.get("error", "")),
            outputs={},
            usage=result.get("usage", {}),
            iterations=result.get("iterations", 1),
        )


class RAGInterface:
    def __init__(self, client: LangFlowClient):
        self._client = client

    def build(
        self,
        embedder: str = "text-embedding-3-small",
        chunker: str = "recursive-character",
        vectorstore: str = "chroma",
        retriever: str = "semantic-search",
    ) -> "RAGPipeline":
        return RAGPipeline(
            self._client,
            embedder=embedder,
            chunker=chunker,
            vectorstore=vectorstore,
            retriever=retriever,
        )


class RAGPipeline:
    def __init__(
        self,
        client: LangFlowClient,
        embedder: str,
        chunker: str,
        vectorstore: str,
        retriever: str,
    ):
        self._client = client
        self.embedder = embedder
        self.chunker = chunker
        self.vectorstore = vectorstore
        self.retriever = retriever
        self._flow = None

    def index(self, documents: List[str], metadata: Optional[Dict] = None):
        """Index documents into the RAG pipeline."""
        data = {
            "documents": documents,
            "metadata": metadata or {},
            "embedder": self.embedder,
            "chunker": self.chunker,
            "vectorstore": self.vectorstore,
        }
        return self._client._request("POST", "/api/v1/rag/index", data=data)

    def query(self, question: str, top_k: int = 5) -> RunResult:
        """Query the RAG pipeline."""
        data = {
            "question": question,
            "top_k": top_k,
            "embedder": self.embedder,
            "retriever": self.retriever,
            "vectorstore": self.vectorstore,
        }
        result = self._client._request("POST", "/api/v1/rag/query", data=data)
        return RunResult(
            message=result.get("answer", result.get("error", "")),
            outputs=result,
            usage=result.get("usage", {}),
            iterations=1,
            artifacts={"sources": result.get("sources", [])},
        )


class MCPInterface:
    def __init__(self, client: LangFlowClient):
        self._client = client

    def deploy(
        self,
        flow_id: str,
        name: str,
        description: str = "",
        tools: Optional[List[str]] = None,
    ) -> Dict:
        data = {
            "flow_id": flow_id,
            "name": name,
            "description": description,
            "tools": tools or ["retrieve", "generate"],
        }
        return self._client._request("POST", "/api/v1/mcp/deploy", data=data)

    def connect(self, url: str, api_key: Optional[str] = None):
        """Connect to an MCP server."""
        data = {"url": url, "api_key": api_key}
        return self._client._request("POST", "/api/v1/mcp/connect", data=data)


class ObservabilityInterface:
    def __init__(self, client: LangFlowClient):
        self._client = client

    def configure(self, provider: str, api_key: str, project: str):
        data = {"provider": provider, "api_key": api_key, "project": project}
        return self._client._request("POST", "/api/v1/observability/configure", data=data)

    def list_traces(
        self,
        flow_id: Optional[str] = None,
        limit: int = 50,
        status: Optional[str] = None,
    ) -> List[Dict]:
        params = {"limit": limit}
        if flow_id:
            params["flow_id"] = flow_id
        if status:
            params["status"] = status

        result = self._client._request("GET", "/api/v1/observability/traces", params=params)
        return result.get("traces", [])
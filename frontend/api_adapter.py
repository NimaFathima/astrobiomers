"""FastAPI adapter exposing the endpoints expected by the new frontend while
bridging to the existing backend stack and Neo4j database.

This service intentionally lives outside the backend codebase so that the
original backend remains untouched.  It reuses the existing `QueryEngine`
utility to talk to Neo4j and translates responses into the shapes required by
`frontend/new frontend`.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from pathlib import Path
import sys

# Ensure backend modules are importable without modifying PYTHONPATH globally.
BACKEND_PATH = Path(__file__).resolve().parents[1] / "backend"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

try:
    from knowledge_graph.query_engine import QueryEngine  # type: ignore
except ImportError as exc:  # pragma: no cover - surfaced during startup
    raise RuntimeError(
        "Unable to import QueryEngine from backend. Did you install backend dependencies?"
    ) from exc

LOGGER = logging.getLogger("frontend.api_adapter")

app = FastAPI(title="Frontend Adapter", version="1.0.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@lru_cache
def get_query_engine() -> QueryEngine:
    return QueryEngine()


class GraphNode(BaseModel):
    id: str
    label: str
    type: str
    group: int
    paperId: Optional[str] = None
    url: Optional[str] = None
    fullTitle: Optional[str] = None


class GraphLink(BaseModel):
    source: str
    target: str
    value: float


class GraphResponse(BaseModel):
    query: str
    rootEntity: str
    nodes: List[GraphNode]
    links: List[GraphLink]
    paperCount: int


class PaperResponse(BaseModel):
    id: str
    title: str
    url: Optional[str]
    year: Optional[int]
    entities: List[str]


@app.get("/api/health")
async def adapter_health() -> Dict[str, str]:
    return {"status": "ok", "message": "Adapter is running"}


@app.get("/api/knowledge-graph", response_model=GraphResponse)
async def knowledge_graph(q: str = Query(..., min_length=1)) -> GraphResponse:
    """Query the knowledge graph for an entity and return its neighborhood."""
    qe = get_query_engine()
    lowered = q.lower()

    finder = (
        "MATCH (n) "
        "WHERE any(prop IN [n.name, n.title] "
        "WHERE prop IS NOT NULL AND toLower(prop) CONTAINS $query) "
        "RETURN n LIMIT 1"
    )
    root_candidates = qe.execute_query(finder, {"query": lowered})

    if not root_candidates:
        raise HTTPException(status_code=404, detail=f"No entity found matching '{query}'")

    root_node = root_candidates[0]["n"]
    root_id = root_node.element_id  # type: ignore[attr-defined]

    relations_cypher = (
        "MATCH (root) WHERE elementId(root) = $root_id "
        "OPTIONAL MATCH (root)-[r]-(neighbor) "
        "RETURN root, r, neighbor"
    )
    records = qe.execute_query(relations_cypher, {"root_id": root_id})

    nodes: Dict[str, GraphNode] = {}
    links: List[GraphLink] = []

    def label_for(node: Any) -> str:
        props = dict(node)
        return (
            props.get("name")
            or props.get("title")
            or props.get("label")
            or props.get("id")
            or node.element_id[:8]
        )

    def node_type(node: Any) -> str:
        labels = list(node.labels)
        return "paper" if "Paper" in labels else "entity"

    root_entry = GraphNode(
        id=root_id,
        label=label_for(root_node),
        type=node_type(root_node),
        group=1,
        paperId=root_id if node_type(root_node) == "paper" else None,
        url=dict(root_node).get("url"),
        fullTitle=dict(root_node).get("title"),
    )
    nodes[root_entry.id] = root_entry

    for record in records:
        neighbor = record.get("neighbor")
        rel = record.get("r")

        if neighbor is None or rel is None:
            continue

        nid = neighbor.element_id
        if nid not in nodes:
            ntype = node_type(neighbor)
            props = dict(neighbor)
            nodes[nid] = GraphNode(
                id=nid,
                label=label_for(neighbor),
                type=ntype,
                group=2 if ntype == "paper" else 3,
                paperId=nid if ntype == "paper" else None,
                url=props.get("url"),
                fullTitle=props.get("title"),
            )

        links.append(GraphLink(source=root_id, target=nid, value=1.0))

    # Fetch additional paper-to-paper relationships for context
    neighbor_ids = [node.id for node in nodes.values() if node.id != root_id]
    if neighbor_ids:
        edges_cypher = (
            "UNWIND $ids as sourceId "
            "MATCH (a) WHERE elementId(a) = sourceId "
            "MATCH (a)-[r]-(b) WHERE elementId(b) IN $ids "
            "RETURN elementId(a) AS source, elementId(b) AS target"
        )
        extra_edges = qe.execute_query(edges_cypher, {"ids": neighbor_ids})
        for edge in extra_edges:
            source = edge["source"]
            target = edge["target"]
            if source == root_id or target == root_id:
                continue
            links.append(GraphLink(source=source, target=target, value=0.5))

    paper_count = sum(1 for node in nodes.values() if node.type == "paper")

    return GraphResponse(
        query=q,
        rootEntity=label_for(root_node),
        nodes=list(nodes.values()),
        links=links,
        paperCount=paper_count,
    )


@app.get("/api/paper/{paper_id}", response_model=PaperResponse)
async def paper_details(paper_id: str) -> PaperResponse:
    qe = get_query_engine()

    paper_query = (
        "MATCH (p) WHERE elementId(p) = $pid "
        "OPTIONAL MATCH (p)-[:MENTIONS|:ASSOCIATED_WITH|:HAS_ENTITY]->(e) "
        "RETURN p, collect(DISTINCT e.name) AS entities"
    )
    result = qe.execute_query(paper_query, {"pid": paper_id})

    if not result:
        raise HTTPException(status_code=404, detail="Paper not found")

    record = result[0]
    node = record["p"]
    props = dict(node)

    return PaperResponse(
        id=paper_id,
        title=props.get("title") or props.get("name") or paper_id,
        url=props.get("url") or props.get("link"),
        year=props.get("year") or props.get("publication_year"),
        entities=[name for name in record.get("entities", []) if name],
    )


@app.get("/api/health/full")
async def full_health() -> Dict[str, Any]:
    """Extended health check that also verifies Neo4j connectivity."""
    qe = get_query_engine()
    try:
        qe.execute_query("RETURN 1 AS ok")
    except Exception as exc:  # pragma: no cover - surfaced on runtime issues
        LOGGER.exception("Neo4j health check failed")
        raise HTTPException(status_code=500, detail=str(exc))
    return {"status": "ok"}


# ========================================
# EVIDENCE ENDPOINTS (Priority 3)
# ========================================

class EdgeEvidenceRequest(BaseModel):
    """Request model for edge evidence"""
    source_id: str
    target_id: str
    relationship_type: Optional[str] = None


@app.post("/api/evidence/edge")
async def get_edge_evidence(request: EdgeEvidenceRequest):
    """Get papers that provide evidence for a specific edge/relationship"""
    try:
        backend_api_path = BACKEND_PATH / "api"
        if str(backend_api_path) not in sys.path:
            sys.path.insert(0, str(backend_api_path.parent))
        
        from api.services.evidence_service import EvidenceService
        
        service = EvidenceService()
        evidence = service.get_edge_evidence(
            source_id=request.source_id,
            target_id=request.target_id,
            relationship_type=request.relationship_type
        )
        service.close()
        return evidence
    
    except Exception as exc:
        LOGGER.error(f"Evidence error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/evidence/all-edges")
async def get_all_edges_evidence(limit: int = Query(100, ge=1, le=500)):
    """Get evidence counts for all edges in the graph"""
    try:
        backend_api_path = BACKEND_PATH / "api"
        if str(backend_api_path) not in sys.path:
            sys.path.insert(0, str(backend_api_path.parent))
        
        from api.services.evidence_service import EvidenceService
        
        service = EvidenceService()
        edges = service.get_all_edge_evidence(limit=limit)
        service.close()
        return edges
    
    except Exception as exc:
        LOGGER.error(f"Evidence error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ========================================
# TRENDS ENDPOINTS (Priority 4)
# ========================================

@app.get("/api/trends/timeline")
async def get_timeline(
    topic: Optional[str] = Query(None),
    start_year: int = Query(2000, ge=1900, le=2025),
    end_year: int = Query(2025, ge=1900, le=2025)
):
    """Get publication timeline for a topic"""
    try:
        backend_api_path = BACKEND_PATH / "api"
        if str(backend_api_path) not in sys.path:
            sys.path.insert(0, str(backend_api_path.parent))
        
        from api.services.trend_analysis import TrendAnalysisService
        
        service = TrendAnalysisService()
        timeline = service.get_topic_timeline(topic=topic, start_year=start_year, end_year=end_year)
        service.close()
        return timeline
    
    except Exception as exc:
        LOGGER.error(f"Timeline error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/trends/emerging")
async def get_emerging_topics(
    timeframe_years: int = Query(5, ge=1, le=20),
    min_papers: int = Query(3, ge=1)
):
    """Get emerging topics with increasing publication rates"""
    try:
        backend_api_path = BACKEND_PATH / "api"
        if str(backend_api_path) not in sys.path:
            sys.path.insert(0, str(backend_api_path.parent))
        
        from api.services.trend_analysis import TrendAnalysisService
        
        service = TrendAnalysisService()
        emerging = service.get_emerging_topics(timeframe_years=timeframe_years, min_papers=min_papers)
        service.close()
        return emerging
    
    except Exception as exc:
        LOGGER.error(f"Emerging topics error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/trends/collaborations")
async def get_collaborations(
    author: Optional[str] = Query(None),
    depth: int = Query(2, ge=1, le=3)
):
    """Get author collaboration network"""
    try:
        backend_api_path = BACKEND_PATH / "api"
        if str(backend_api_path) not in sys.path:
            sys.path.insert(0, str(backend_api_path.parent))
        
        from api.services.trend_analysis import TrendAnalysisService
        
        service = TrendAnalysisService()
        network = service.get_collaboration_network(author_name=author, depth=depth)
        service.close()
        return network
    
    except Exception as exc:
        LOGGER.error(f"Collaborations error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/trends/top-authors")
async def get_top_authors(
    topic: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100)
):
    """Get top authors by publication count"""
    try:
        backend_api_path = BACKEND_PATH / "api"
        if str(backend_api_path) not in sys.path:
            sys.path.insert(0, str(backend_api_path.parent))
        
        from api.services.trend_analysis import TrendAnalysisService
        
        service = TrendAnalysisService()
        authors = service.get_top_authors(topic=topic, limit=limit)
        service.close()
        return authors
    
    except Exception as exc:
        LOGGER.error(f"Top authors error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/trends/co-occurrence")
async def get_topic_co_occurrence(min_papers: int = Query(2, ge=1)):
    """Get topics that frequently appear together"""
    try:
        backend_api_path = BACKEND_PATH / "api"
        if str(backend_api_path) not in sys.path:
            sys.path.insert(0, str(backend_api_path.parent))
        
        from api.services.trend_analysis import TrendAnalysisService
        
        service = TrendAnalysisService()
        co_occ = service.get_topic_co_occurrence(min_papers=min_papers)
        service.close()
        return co_occ
    
    except Exception as exc:
        LOGGER.error(f"Co-occurrence error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


# ========================================
# RAG CHAT ENDPOINTS (Priority 2)
# ========================================

class QuestionRequest(BaseModel):
    """Request model for asking questions"""
    question: str
    max_papers: int = 10


@app.post("/api/chat/ask")
async def ask_question(request: QuestionRequest):
    """
    RAG-powered Q&A endpoint.
    Answers questions using Knowledge Graph + LLM.
    """
    try:
        # Import RAG service with correct path
        backend_api_path = BACKEND_PATH / "api"
        if str(backend_api_path) not in sys.path:
            sys.path.insert(0, str(backend_api_path.parent))
        
        from api.services.rag_service import KnowledgeGraphRAG
        
        rag = KnowledgeGraphRAG()
        response = rag.answer_question(
            user_question=request.question,
            max_papers=request.max_papers,
            include_snippets=True
        )
        
        return response
    
    except Exception as exc:
        LOGGER.error(f"RAG error: {exc}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/chat/health")
async def chat_health():
    """Check if RAG service is available"""
    try:
        backend_api_path = BACKEND_PATH / "api"
        if str(backend_api_path) not in sys.path:
            sys.path.insert(0, str(backend_api_path.parent))
        
        from api.services.rag_service import KnowledgeGraphRAG
        
        rag = KnowledgeGraphRAG()
        return {
            "status": "ok",
            "llm_provider": rag.llm_provider or "none",
            "has_llm": rag.llm_client is not None
        }
    except Exception as exc:
        LOGGER.error(f"RAG health check error: {exc}", exc_info=True)
        return {"status": "error", "detail": str(exc)}


@app.get("/api/chat/examples")
async def get_examples():
    """Get example questions to try"""
    return {
        "examples": [
            "What are the effects of microgravity on bone density?",
            "How does spaceflight affect the cardiovascular system?",
            "What countermeasures exist for muscle atrophy?",
            "How does cosmic radiation affect human cells?",
            "What genes are affected by spaceflight?"
        ]
    }


def start():
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=5000)


if __name__ == "__main__":  # pragma: no cover
    start()

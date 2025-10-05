"""
Knowledge Graph API Routes
Provides endpoints for querying the Neo4j knowledge graph
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from knowledge_graph.query_engine import QueryEngine
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api", tags=["knowledge-graph"])

# Initialize query engine
query_engine = None


def get_query_engine():
    """Get or initialize query engine"""
    global query_engine
    if query_engine is None:
        query_engine = QueryEngine()
    return query_engine


# Pydantic models
class Node(BaseModel):
    id: str
    type: str
    properties: Dict[str, Any]


class Edge(BaseModel):
    source: str
    target: str
    type: str
    properties: Optional[Dict[str, Any]] = {}


class CytoscapeNode(BaseModel):
    data: Dict[str, Any]


class CytoscapeEdge(BaseModel):
    data: Dict[str, Any]


class GraphData(BaseModel):
    nodes: List[CytoscapeNode]
    edges: List[CytoscapeEdge]


class Statistics(BaseModel):
    total_papers: int
    total_relationships: int
    total_stressors: int
    total_phenotypes: int


class Entity(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None
    paper_count: Optional[int] = 0


@router.get("/statistics", response_model=Statistics)
async def get_statistics():
    """Get overview statistics of the knowledge graph"""
    try:
        qe = get_query_engine()
        
        # Count nodes by type
        papers_query = "MATCH (n:Paper) RETURN count(n) as count"
        stressors_query = "MATCH (n:Stressor) RETURN count(n) as count"
        phenotypes_query = "MATCH (n:Phenotype) RETURN count(n) as count"
        relationships_query = "MATCH ()-[r]->() RETURN count(r) as count"
        
        papers = qe.execute_query(papers_query)[0]["count"] if qe.execute_query(papers_query) else 0
        stressors = qe.execute_query(stressors_query)[0]["count"] if qe.execute_query(stressors_query) else 0
        phenotypes = qe.execute_query(phenotypes_query)[0]["count"] if qe.execute_query(phenotypes_query) else 0
        relationships = qe.execute_query(relationships_query)[0]["count"] if qe.execute_query(relationships_query) else 0
        
        return Statistics(
            total_papers=papers,
            total_relationships=relationships,
            total_stressors=stressors,
            total_phenotypes=phenotypes
        )
    except Exception as e:
        logger.error(f"Error getting statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/graph/cytoscape", response_model=GraphData)
async def get_cytoscape_graph(limit: int = Query(100, ge=1, le=1000)):
    """Get graph data in Cytoscape.js format"""
    try:
        qe = get_query_engine()
        
        # Get nodes and relationships
        query = f"""
        MATCH (n)
        WITH n LIMIT {limit}
        OPTIONAL MATCH (n)-[r]->(m)
        RETURN n, r, m
        """
        
        results = qe.execute_query(query)
        
        nodes_dict = {}
        edges = []
        
        for record in results:
            # Process source node
            if record.get("n"):
                node = record["n"]
                node_id = str(node.element_id)
                if node_id not in nodes_dict:
                    labels = list(node.labels)
                    props = dict(node)
                    nodes_dict[node_id] = {
                        "data": {
                            "id": node_id,
                            "label": props.get("name", props.get("title", node_id[:8])),
                            "type": labels[0] if labels else "Unknown",
                            **props
                        }
                    }
            
            # Process target node
            if record.get("m"):
                node = record["m"]
                node_id = str(node.element_id)
                if node_id not in nodes_dict:
                    labels = list(node.labels)
                    props = dict(node)
                    nodes_dict[node_id] = {
                        "data": {
                            "id": node_id,
                            "label": props.get("name", props.get("title", node_id[:8])),
                            "type": labels[0] if labels else "Unknown",
                            **props
                        }
                    }
            
            # Process relationship
            if record.get("r"):
                rel = record["r"]
                edges.append({
                    "data": {
                        "id": str(rel.element_id),
                        "source": str(rel.start_node.element_id),
                        "target": str(rel.end_node.element_id),
                        "type": rel.type,
                        **dict(rel)
                    }
                })
        
        return GraphData(
            nodes=list(nodes_dict.values()),
            edges=edges
        )
        
    except Exception as e:
        logger.error(f"Error getting graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stressors", response_model=List[Entity])
async def get_stressors():
    """Get all stressors"""
    try:
        qe = get_query_engine()
        
        query = """
        MATCH (s:Stressor)
        OPTIONAL MATCH (s)<-[:HAS_STRESSOR]-(p:Paper)
        RETURN s, count(p) as paper_count
        ORDER BY paper_count DESC
        """
        
        results = qe.execute_query(query)
        
        stressors = []
        for record in results:
            node = record["s"]
            props = dict(node)
            stressors.append(Entity(
                id=str(node.element_id),
                name=props.get("name", "Unknown"),
                type="STRESSOR",
                description=props.get("description"),
                paper_count=record.get("paper_count", 0)
            ))
        
        return stressors
        
    except Exception as e:
        logger.error(f"Error getting stressors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/phenotypes", response_model=List[Entity])
async def get_phenotypes():
    """Get all phenotypes"""
    try:
        qe = get_query_engine()
        
        query = """
        MATCH (p:Phenotype)
        OPTIONAL MATCH (p)<-[:HAS_PHENOTYPE]-(paper:Paper)
        RETURN p, count(paper) as paper_count
        ORDER BY paper_count DESC
        """
        
        results = qe.execute_query(query)
        
        phenotypes = []
        for record in results:
            node = record["p"]
            props = dict(node)
            phenotypes.append(Entity(
                id=str(node.element_id),
                name=props.get("name", "Unknown"),
                type="PHENOTYPE",
                description=props.get("description"),
                paper_count=record.get("paper_count", 0)
            ))
        
        return phenotypes
        
    except Exception as e:
        logger.error(f"Error getting phenotypes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class SearchResult(BaseModel):
    id: str
    name: str
    type: str
    excerpt: Optional[str] = None
    relevance: float


@router.post("/search", response_model=List[SearchResult])
async def search_entities(query: str = Query(..., min_length=1)):
    """Search for entities by name or description"""
    try:
        qe = get_query_engine()
        
        cypher_query = """
        MATCH (n)
        WHERE n.name CONTAINS $query OR n.title CONTAINS $query OR n.description CONTAINS $query
        RETURN n, labels(n) as types
        LIMIT 20
        """
        
        results = qe.execute_query(cypher_query, {"query": query})
        
        search_results = []
        for record in results:
            node = record["n"]
            props = dict(node)
            types = record["types"]
            
            name = props.get("name", props.get("title", "Unknown"))
            relevance = 1.0 if query.lower() in name.lower() else 0.5
            
            search_results.append(SearchResult(
                id=str(node.element_id),
                name=name,
                type=types[0] if types else "Unknown",
                excerpt=props.get("description", props.get("abstract", ""))[:200],
                relevance=relevance
            ))
        
        # Sort by relevance
        search_results.sort(key=lambda x: x.relevance, reverse=True)
        
        return search_results
        
    except Exception as e:
        logger.error(f"Error searching: {e}")
        raise HTTPException(status_code=500, detail=str(e))

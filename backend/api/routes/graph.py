"""
API Routes - Graph Query Endpoint
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any

from api.models.schemas import GraphQueryRequest, GraphQueryResponse
from api.services.neo4j_service import Neo4jService
from knowledge_graph.config import config

router = APIRouter(prefix="/api/graph", tags=["graph"])


def get_neo4j_service() -> Neo4jService:
    """Dependency injection for Neo4j service"""
    return Neo4jService(
        uri=config.neo4j_uri,
        user=config.neo4j_user,
        password=config.neo4j_password
    )


@router.post("/query", response_model=GraphQueryResponse)
async def execute_graph_query(
    request: GraphQueryRequest,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Execute a Cypher query or natural language query on the graph
    
    - **query**: Cypher query string or natural language question
    - **query_type**: "cypher" for Cypher queries, "natural" for NL (not yet implemented)
    - **parameters**: Optional query parameters
    - **limit**: Maximum number of results
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    if request.query_type == "natural":
        # TODO: Implement natural language to Cypher translation
        raise HTTPException(
            status_code=501,
            detail="Natural language queries not yet implemented. Use query_type='cypher'"
        )
    
    try:
        # Execute Cypher query
        result = neo4j.execute_cypher(
            query=request.query,
            parameters=request.parameters,
            limit=request.limit
        )
        
        return GraphQueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Query execution failed: {str(e)}"
        )


@router.get("/subgraph/{entity_id}")
async def get_entity_subgraph(
    entity_id: str,
    depth: int = 1,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get a subgraph centered on an entity
    
    - **entity_id**: Entity ID or name
    - **depth**: Number of hops from the entity (1-3)
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    if depth < 1 or depth > 3:
        raise HTTPException(
            status_code=400,
            detail="Depth must be between 1 and 3"
        )
    
    # Build subgraph query
    query = f"""
    MATCH path = (center)-[*1..{depth}]-(neighbor)
    WHERE center.id = $entity_id OR center.name = $entity_id
    WITH nodes(path) as path_nodes, relationships(path) as path_rels
    UNWIND path_nodes as n
    WITH collect(DISTINCT n) as nodes, path_rels
    UNWIND path_rels as r
    RETURN nodes, collect(DISTINCT r) as relationships
    """
    
    try:
        result = neo4j.execute_cypher(query, {"entity_id": entity_id})
        return GraphQueryResponse(**result)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Subgraph query failed: {str(e)}"
        )


@router.get("/path/{source_id}/{target_id}")
async def find_shortest_path(
    source_id: str,
    target_id: str,
    max_length: int = 5,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Find the shortest path between two entities
    
    - **source_id**: Source entity ID or name
    - **target_id**: Target entity ID or name
    - **max_length**: Maximum path length to search
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    query = """
    MATCH path = shortestPath(
        (source)-[*..%d]-(target)
    )
    WHERE (source.id = $source_id OR source.name = $source_id)
      AND (target.id = $target_id OR target.name = $target_id)
    RETURN path
    """ % max_length
    
    try:
        result = neo4j.execute_cypher(
            query,
            {"source_id": source_id, "target_id": target_id}
        )
        
        if not result["nodes"]:
            return {
                "found": False,
                "message": f"No path found between {source_id} and {target_id}"
            }
        
        return {
            "found": True,
            "source_id": source_id,
            "target_id": target_id,
            "path_length": len(result["edges"]),
            "nodes": result["nodes"],
            "edges": result["edges"]
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Path finding failed: {str(e)}"
        )


@router.get("/statistics")
async def get_graph_statistics(
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get overall graph statistics
    
    Returns node counts, edge counts, density, degree distribution, etc.
    """
    if not neo4j.is_connected():
        # Return empty stats if not connected
        stats = neo4j._empty_stats()
    else:
        stats = neo4j.get_statistics()
    
    return stats

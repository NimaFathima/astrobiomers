"""
API Routes - Entities Endpoint
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from api.models.schemas import Entity, EntityListResponse, EntityType
from api.services.neo4j_service import Neo4jService
from knowledge_graph.config import config

router = APIRouter(prefix="/api/entities", tags=["entities"])


def get_neo4j_service() -> Neo4jService:
    """Dependency injection for Neo4j service"""
    return Neo4jService(
        uri=config.neo4j_uri,
        user=config.neo4j_user,
        password=config.neo4j_password
    )


@router.get("/", response_model=EntityListResponse)
async def list_entities(
    entity_type: Optional[EntityType] = Query(None, description="Filter by entity type"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    List all entities in the knowledge graph
    
    - **entity_type**: Optional filter by entity type (GENE, PROTEIN, DISEASE, etc.)
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    """
    skip = (page - 1) * page_size
    entities, total = neo4j.get_entities(
        entity_type=entity_type,
        skip=skip,
        limit=page_size
    )
    
    return EntityListResponse(
        entities=entities,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{entity_id}", response_model=Entity)
async def get_entity(
    entity_id: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get a specific entity by ID
    
    - **entity_id**: Entity ID or name
    """
    entity = neo4j.get_entity_by_id(entity_id)
    
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    return Entity(**entity)


@router.get("/{entity_id}/papers")
async def get_entity_papers(
    entity_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get all papers mentioning this entity
    
    - **entity_id**: Entity ID or name
    """
    # Check entity exists
    entity = neo4j.get_entity_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    # Get papers
    skip = (page - 1) * page_size
    query = """
    MATCH (e)-[:HAS_ENTITY]-(p:Paper)
    WHERE e.id = $entity_id OR e.name = $entity_id
    RETURN p
    ORDER BY p.publication_date DESC
    SKIP $skip LIMIT $limit
    """
    result = neo4j.execute_cypher(
        query,
        {"entity_id": entity_id, "skip": skip, "limit": page_size}
    )
    
    papers = []
    for node in result["nodes"]:
        if "Paper" in node["labels"]:
            papers.append({
                "pmid": node["properties"].get("pmid"),
                "title": node["properties"].get("title"),
                "publication_date": node["properties"].get("publication_date")
            })
    
    return {
        "entity_id": entity_id,
        "entity_name": entity["name"],
        "papers": papers,
        "total": len(papers),
        "page": page,
        "page_size": page_size
    }


@router.get("/{entity_id}/relationships")
async def get_entity_relationships(
    entity_id: str,
    limit: int = Query(50, ge=1, le=200),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get all relationships involving this entity
    
    - **entity_id**: Entity ID or name
    - **limit**: Maximum number of relationships to return
    """
    # Check entity exists
    entity = neo4j.get_entity_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    # Get relationships (both incoming and outgoing)
    query = """
    MATCH (e1)-[r]->(e2)
    WHERE (e1.id = $entity_id OR e1.name = $entity_id) OR (e2.id = $entity_id OR e2.name = $entity_id)
    RETURN e1, r, e2, labels(e1) as e1_labels, labels(e2) as e2_labels, type(r) as rel_type
    LIMIT $limit
    """
    result = neo4j.execute_cypher(
        query,
        {"entity_id": entity_id, "limit": limit}
    )
    
    relationships = []
    for edge in result["edges"]:
        relationships.append({
            "type": edge["type"],
            "source": edge["source"],
            "target": edge["target"],
            "properties": edge["properties"]
        })
    
    return {
        "entity_id": entity_id,
        "entity_name": entity["name"],
        "relationships": relationships,
        "total": len(relationships)
    }


@router.get("/{entity_id}/neighbors")
async def get_entity_neighbors(
    entity_id: str,
    hops: int = Query(1, ge=1, le=3, description="Number of hops in the graph"),
    limit: int = Query(20, ge=1, le=100),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get neighboring entities in the graph (entities connected by relationships)
    
    - **entity_id**: Entity ID or name
    - **hops**: Number of hops to traverse (1-3)
    - **limit**: Maximum number of neighbors to return
    """
    # Check entity exists
    entity = neo4j.get_entity_by_id(entity_id)
    if not entity:
        raise HTTPException(status_code=404, detail=f"Entity {entity_id} not found")
    
    # Get neighbors
    query = f"""
    MATCH path = (e1)-[*1..{hops}]-(e2)
    WHERE (e1.id = $entity_id OR e1.name = $entity_id) AND e1 <> e2
    WITH e2, labels(e2) as labels, length(path) as distance
    ORDER BY distance ASC, e2.name ASC
    LIMIT $limit
    RETURN e2, labels, distance
    """
    result = neo4j.execute_cypher(
        query,
        {"entity_id": entity_id, "limit": limit}
    )
    
    neighbors = []
    for node in result["nodes"]:
        # Skip the source entity
        node_id = node["properties"].get("id", node["properties"].get("name"))
        if node_id != entity_id:
            entity_type = next((l for l in node["labels"] if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
            neighbors.append({
                "id": node_id,
                "name": node["properties"].get("name"),
                "entity_type": entity_type.upper(),
                "distance": 1  # Would need to extract from query result
            })
    
    return {
        "entity_id": entity_id,
        "entity_name": entity["name"],
        "neighbors": neighbors,
        "total": len(neighbors)
    }

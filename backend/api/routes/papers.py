"""
API Routes - Papers Endpoint
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional

from api.models.schemas import PaperResponse, PaperListResponse
from api.services.neo4j_service import Neo4jService
from knowledge_graph.config import config

router = APIRouter(prefix="/api/papers", tags=["papers"])


def get_neo4j_service() -> Neo4jService:
    """Dependency injection for Neo4j service"""
    return Neo4jService(
        uri=config.neo4j_uri,
        user=config.neo4j_user,
        password=config.neo4j_password
    )


@router.get("/", response_model=PaperListResponse)
async def list_papers(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    List all papers in the knowledge graph
    
    - **page**: Page number (starts at 1)
    - **page_size**: Number of items per page (max 100)
    """
    skip = (page - 1) * page_size
    papers, total = neo4j.get_papers(skip=skip, limit=page_size)
    
    return PaperListResponse(
        papers=papers,
        total=total,
        page=page,
        page_size=page_size
    )


@router.get("/{paper_id}", response_model=PaperResponse)
async def get_paper(
    paper_id: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get a specific paper by PMID
    
    - **paper_id**: PubMed ID (PMID)
    """
    paper = neo4j.get_paper_by_id(paper_id)
    
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")
    
    return PaperResponse(**paper)


@router.get("/{paper_id}/entities")
async def get_paper_entities(
    paper_id: str,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get all entities mentioned in a paper
    
    - **paper_id**: PubMed ID (PMID)
    """
    # Check paper exists
    paper = neo4j.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")
    
    # Get entities
    query = """
    MATCH (p:Paper {pmid: $pmid})-[:HAS_ENTITY]->(e)
    RETURN e, labels(e) as labels
    ORDER BY e.name
    """
    result = neo4j.execute_cypher(query, {"pmid": paper_id})
    
    entities = []
    for node in result["nodes"]:
        if "Paper" not in node["labels"]:
            entity_type = next((l for l in node["labels"] if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
            entities.append({
                "id": node["properties"].get("id", node["properties"].get("name")),
                "name": node["properties"].get("name"),
                "entity_type": entity_type.upper(),
                "normalized_name": node["properties"].get("normalized_name")
            })
    
    return {
        "paper_id": paper_id,
        "entities": entities,
        "total": len(entities)
    }


@router.get("/{paper_id}/related")
async def get_related_papers(
    paper_id: str,
    limit: int = Query(10, ge=1, le=50, description="Number of related papers"),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get papers related to this paper (based on shared entities)
    
    - **paper_id**: PubMed ID (PMID)
    - **limit**: Maximum number of related papers to return
    """
    # Check paper exists
    paper = neo4j.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")
    
    # Find related papers
    query = """
    MATCH (p1:Paper {pmid: $pmid})-[:HAS_ENTITY]->(e)<-[:HAS_ENTITY]-(p2:Paper)
    WHERE p1 <> p2
    WITH p2, count(DISTINCT e) as shared_entities
    ORDER BY shared_entities DESC
    LIMIT $limit
    RETURN p2, shared_entities
    """
    result = neo4j.execute_cypher(query, {"pmid": paper_id, "limit": limit})
    
    related = []
    for node in result["nodes"]:
        if "Paper" in node["labels"]:
            related.append({
                "pmid": node["properties"].get("pmid"),
                "title": node["properties"].get("title"),
                "shared_entities": 0  # Would need to calculate from query
            })
    
    return {
        "paper_id": paper_id,
        "related_papers": related,
        "total": len(related)
    }

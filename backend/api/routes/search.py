"""
API Routes - Search Endpoint
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
from datetime import datetime

from api.models.schemas import SearchRequest, SearchResponse, SearchResult, EntityType
from api.services.neo4j_service import Neo4jService
from knowledge_graph.config import config

router = APIRouter(prefix="/api/search", tags=["search"])


def get_neo4j_service() -> Neo4jService:
    """Dependency injection for Neo4j service"""
    return Neo4jService(
        uri=config.neo4j_uri,
        user=config.neo4j_user,
        password=config.neo4j_password
    )


@router.post("/", response_model=SearchResponse)
async def search(
    request: SearchRequest,
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Search across papers, entities, and relationships
    
    - **query**: Search query string
    - **entity_types**: Optional filter by entity types
    - **page**: Page number
    - **page_size**: Items per page
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    start_time = datetime.now()
    results = []
    
    # Search papers (title and abstract)
    paper_query = """
    MATCH (p:Paper)
    WHERE toLower(p.title) CONTAINS toLower($query)
       OR toLower(p.abstract) CONTAINS toLower($query)
    RETURN p, 'paper' as type,
           CASE
             WHEN toLower(p.title) CONTAINS toLower($query) THEN 1.0
             ELSE 0.5
           END as score
    ORDER BY score DESC
    LIMIT $limit
    """
    
    paper_result = neo4j.execute_cypher(
        paper_query,
        {"query": request.query, "limit": request.page_size}
    )
    
    for node in paper_result["nodes"]:
        if "Paper" in node["labels"]:
            results.append(SearchResult(
                type="paper",
                id=node["properties"].get("pmid"),
                title=node["properties"].get("title", ""),
                description=node["properties"].get("abstract", "")[:200] + "...",
                score=1.0,
                metadata={
                    "authors": node["properties"].get("authors", []),
                    "journal": node["properties"].get("journal"),
                    "publication_date": node["properties"].get("publication_date")
                }
            ))
    
    # Search entities (name and synonyms)
    if not request.entity_types:
        entity_labels = "Gene|Protein|Disease|Chemical|Stressor|Phenotype|Organism|CellType|Intervention"
    else:
        entity_labels = "|".join([t.value.capitalize() for t in request.entity_types])
    
    entity_query = f"""
    MATCH (e)
    WHERE any(label IN labels(e) WHERE label =~ '{entity_labels}')
      AND (toLower(e.name) CONTAINS toLower($query)
           OR any(syn IN e.synonyms WHERE toLower(syn) CONTAINS toLower($query)))
    OPTIONAL MATCH (p:Paper)-[:HAS_ENTITY]->(e)
    WITH e, labels(e) as labels, count(DISTINCT p) as paper_count,
         CASE
           WHEN toLower(e.name) = toLower($query) THEN 1.0
           WHEN toLower(e.name) CONTAINS toLower($query) THEN 0.8
           ELSE 0.5
         END as score
    RETURN e, labels, paper_count, score
    ORDER BY score DESC, paper_count DESC
    LIMIT $limit
    """
    
    entity_result = neo4j.execute_cypher(
        entity_query,
        {"query": request.query, "limit": request.page_size}
    )
    
    for node in entity_result["nodes"]:
        entity_type = next((l for l in node["labels"] if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
        results.append(SearchResult(
            type="entity",
            id=node["properties"].get("id", node["properties"].get("name")),
            title=node["properties"].get("name", ""),
            description=node["properties"].get("description", "") or f"{entity_type} entity",
            score=0.8,
            metadata={
                "entity_type": entity_type,
                "normalized_name": node["properties"].get("normalized_name"),
                "paper_count": 0  # Would be extracted from query result
            }
        ))
    
    # Sort by score
    results.sort(key=lambda x: x.score, reverse=True)
    
    # Paginate
    start_idx = (request.page - 1) * request.page_size
    end_idx = start_idx + request.page_size
    paginated_results = results[start_idx:end_idx]
    
    end_time = datetime.now()
    query_time_ms = (end_time - start_time).total_seconds() * 1000
    
    return SearchResponse(
        results=paginated_results,
        total=len(results),
        page=request.page,
        page_size=request.page_size,
        query_time_ms=query_time_ms
    )


@router.get("/papers")
async def search_papers(
    q: str = Query(..., min_length=1, description="Search query"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Search papers by title, abstract, or keywords
    
    - **q**: Search query
    - **page**: Page number
    - **page_size**: Items per page
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    skip = (page - 1) * page_size
    
    query = """
    MATCH (p:Paper)
    WHERE toLower(p.title) CONTAINS toLower($query)
       OR toLower(p.abstract) CONTAINS toLower($query)
       OR any(kw IN p.keywords WHERE toLower(kw) CONTAINS toLower($query))
    RETURN p
    ORDER BY p.publication_date DESC
    SKIP $skip LIMIT $limit
    """
    
    result = neo4j.execute_cypher(
        query,
        {"query": q, "skip": skip, "limit": page_size}
    )
    
    papers = []
    for node in result["nodes"]:
        if "Paper" in node["labels"]:
            papers.append({
                "pmid": node["properties"].get("pmid"),
                "title": node["properties"].get("title"),
                "abstract": node["properties"].get("abstract", "")[:200] + "...",
                "publication_date": node["properties"].get("publication_date")
            })
    
    return {
        "query": q,
        "papers": papers,
        "total": len(papers),
        "page": page,
        "page_size": page_size
    }


@router.get("/entities")
async def search_entities(
    q: str = Query(..., min_length=1, description="Search query"),
    entity_type: Optional[EntityType] = Query(None, description="Filter by entity type"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Search entities by name or synonyms
    
    - **q**: Search query
    - **entity_type**: Optional entity type filter
    - **page**: Page number
    - **page_size**: Items per page
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    skip = (page - 1) * page_size
    
    # Build query based on entity type filter
    if entity_type:
        label = entity_type.value.capitalize()
        match_clause = f"MATCH (e:{label})"
    else:
        match_clause = "MATCH (e) WHERE any(label IN labels(e) WHERE label IN ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention'])"
    
    query = f"""
    {match_clause}
    WHERE toLower(e.name) CONTAINS toLower($query)
       OR any(syn IN e.synonyms WHERE toLower(syn) CONTAINS toLower($query))
    RETURN e, labels(e) as labels
    ORDER BY e.name
    SKIP $skip LIMIT $limit
    """
    
    result = neo4j.execute_cypher(
        query,
        {"query": q, "skip": skip, "limit": page_size}
    )
    
    entities = []
    for node in result["nodes"]:
        entity_type_str = next((l for l in node["labels"] if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
        entities.append({
            "id": node["properties"].get("id", node["properties"].get("name")),
            "name": node["properties"].get("name"),
            "entity_type": entity_type_str.upper(),
            "normalized_name": node["properties"].get("normalized_name")
        })
    
    return {
        "query": q,
        "entity_type": entity_type.value if entity_type else "all",
        "entities": entities,
        "total": len(entities),
        "page": page,
        "page_size": page_size
    }


@router.get("/autocomplete")
async def autocomplete(
    q: str = Query(..., min_length=1, description="Partial search query"),
    limit: int = Query(10, ge=1, le=50),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Autocomplete suggestions for entity names
    
    - **q**: Partial query string
    - **limit**: Maximum number of suggestions
    """
    if not neo4j.is_connected():
        return {"suggestions": []}
    
    query = """
    MATCH (e)
    WHERE any(label IN labels(e) WHERE label IN ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention'])
      AND toLower(e.name) STARTS WITH toLower($query)
    RETURN DISTINCT e.name as name, labels(e) as labels
    ORDER BY e.name
    LIMIT $limit
    """
    
    result = neo4j.execute_cypher(query, {"query": q, "limit": limit})
    
    suggestions = []
    for node in result["nodes"]:
        entity_type = next((l for l in node["labels"] if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
        suggestions.append({
            "name": node["properties"].get("name"),
            "type": entity_type.upper()
        })
    
    return {"suggestions": suggestions}

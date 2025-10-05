"""
API Routes - Analytics and Statistics Endpoint
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import datetime

from api.models.schemas import StatsResponse, NetworkStats, EntityStats, EntityType
from api.services.neo4j_service import Neo4jService
from knowledge_graph.config import config

router = APIRouter(prefix="/api/analytics", tags=["analytics"])


def get_neo4j_service() -> Neo4jService:
    """Dependency injection for Neo4j service"""
    return Neo4jService(
        uri=config.neo4j_uri,
        user=config.neo4j_user,
        password=config.neo4j_password
    )


@router.get("/stats", response_model=StatsResponse)
async def get_statistics(
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get overall knowledge graph statistics
    
    Returns:
    - Total counts for papers, entities, relationships, topics
    - Network statistics (density, avg degree, etc.)
    - Entity type breakdown
    """
    stats = neo4j.get_statistics()
    
    # Build entity stats
    entity_stats = []
    for entity_type_str in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']:
        count = stats["network_stats"]["node_types"].get(entity_type_str, 0)
        if count > 0:
            entity_stats.append(EntityStats(
                entity_type=EntityType[entity_type_str.upper()],
                count=count,
                top_entities=[]
            ))
    
    return StatsResponse(
        papers=stats["papers"],
        entities=stats["entities"],
        relationships=stats["relationships"],
        topics=stats["topics"],
        network_stats=NetworkStats(**stats["network_stats"]),
        entity_stats=entity_stats,
        last_updated=stats["last_updated"]
    )


@router.get("/top-entities")
async def get_top_entities(
    entity_type: Optional[EntityType] = Query(None, description="Filter by entity type"),
    metric: str = Query("paper_count", description="Ranking metric: paper_count, degree"),
    limit: int = Query(20, ge=1, le=100),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get top entities ranked by various metrics
    
    - **entity_type**: Optional entity type filter
    - **metric**: Ranking metric (paper_count, degree)
    - **limit**: Number of top entities to return
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    # Build query based on entity type
    if entity_type:
        label = entity_type.value.capitalize()
        match_clause = f"MATCH (e:{label})"
    else:
        match_clause = "MATCH (e) WHERE any(label IN labels(e) WHERE label IN ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention'])"
    
    if metric == "paper_count":
        query = f"""
        {match_clause}
        OPTIONAL MATCH (p:Paper)-[:HAS_ENTITY]->(e)
        WITH e, labels(e) as labels, count(DISTINCT p) as paper_count
        RETURN e, labels, paper_count
        ORDER BY paper_count DESC
        LIMIT $limit
        """
    elif metric == "degree":
        query = f"""
        {match_clause}
        OPTIONAL MATCH (e)-[r]-(other)
        WITH e, labels(e) as labels, count(DISTINCT r) as degree
        RETURN e, labels, degree as paper_count
        ORDER BY degree DESC
        LIMIT $limit
        """
    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unknown metric: {metric}. Use 'paper_count' or 'degree'"
        )
    
    result = neo4j.execute_cypher(query, {"limit": limit})
    
    top_entities = []
    for node in result["nodes"]:
        entity_type_str = next((l for l in node["labels"] if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
        top_entities.append({
            "id": node["properties"].get("id", node["properties"].get("name")),
            "name": node["properties"].get("name"),
            "entity_type": entity_type_str.upper(),
            metric: 0  # Would be extracted from query result
        })
    
    return {
        "metric": metric,
        "entity_type": entity_type.value if entity_type else "all",
        "entities": top_entities,
        "total": len(top_entities)
    }


@router.get("/co-occurrence")
async def get_co_occurrence(
    entity_id: str,
    limit: int = Query(20, ge=1, le=100),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get entities that frequently co-occur with the given entity in papers
    
    - **entity_id**: Entity ID or name
    - **limit**: Number of co-occurring entities to return
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    query = """
    MATCH (e1)-[:HAS_ENTITY]-(p:Paper)-[:HAS_ENTITY]-(e2)
    WHERE (e1.id = $entity_id OR e1.name = $entity_id) AND e1 <> e2
    WITH e2, labels(e2) as labels, count(DISTINCT p) as co_occurrence_count
    ORDER BY co_occurrence_count DESC
    LIMIT $limit
    RETURN e2, labels, co_occurrence_count
    """
    
    result = neo4j.execute_cypher(query, {"entity_id": entity_id, "limit": limit})
    
    co_occurring = []
    for node in result["nodes"]:
        entity_type = next((l for l in node["labels"] if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
        co_occurring.append({
            "id": node["properties"].get("id", node["properties"].get("name")),
            "name": node["properties"].get("name"),
            "entity_type": entity_type.upper(),
            "co_occurrence_count": 0  # Would be extracted from query
        })
    
    return {
        "entity_id": entity_id,
        "co_occurring_entities": co_occurring,
        "total": len(co_occurring)
    }


@router.get("/publication-trends")
async def get_publication_trends(
    start_year: int = Query(2000, ge=1970, le=2025),
    end_year: int = Query(2025, ge=1970, le=2025),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get publication trends over time
    
    - **start_year**: Start year (default: 2000)
    - **end_year**: End year (default: 2025)
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    query = """
    MATCH (p:Paper)
    WHERE p.publication_date >= $start_year AND p.publication_date <= $end_year
    WITH substring(p.publication_date, 0, 4) as year, count(p) as paper_count
    RETURN year, paper_count
    ORDER BY year
    """
    
    result = neo4j.execute_cypher(
        query,
        {"start_year": str(start_year), "end_year": str(end_year)}
    )
    
    trends = []
    for node in result["nodes"]:
        props = node["properties"]
        if "year" in props and "paper_count" in props:
            trends.append({
                "year": int(props["year"]),
                "paper_count": props["paper_count"]
            })
    
    return {
        "start_year": start_year,
        "end_year": end_year,
        "trends": trends
    }


@router.get("/entity-type-distribution")
async def get_entity_type_distribution(
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get distribution of entity types in the knowledge graph
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    stats = neo4j.get_statistics()
    
    distribution = []
    for entity_type in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']:
        count = stats["network_stats"]["node_types"].get(entity_type, 0)
        if count > 0:
            distribution.append({
                "entity_type": entity_type.upper(),
                "count": count,
                "percentage": (count / stats["entities"] * 100) if stats["entities"] > 0 else 0
            })
    
    return {
        "distribution": distribution,
        "total_entities": stats["entities"]
    }


@router.get("/relationship-type-distribution")
async def get_relationship_type_distribution(
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Get distribution of relationship types in the knowledge graph
    """
    if not neo4j.is_connected():
        raise HTTPException(
            status_code=503,
            detail="Neo4j database is not connected"
        )
    
    stats = neo4j.get_statistics()
    
    distribution = []
    for rel_type in ['UPREGULATES', 'DOWNREGULATES', 'CAUSES', 'TREATS', 'INTERACTS_WITH', 'PART_OF', 'ASSOCIATED_WITH']:
        count = stats["network_stats"]["edge_types"].get(rel_type, 0)
        if count > 0:
            distribution.append({
                "relationship_type": rel_type,
                "count": count,
                "percentage": (count / stats["relationships"] * 100) if stats["relationships"] > 0 else 0
            })
    
    return {
        "distribution": distribution,
        "total_relationships": stats["relationships"]
    }

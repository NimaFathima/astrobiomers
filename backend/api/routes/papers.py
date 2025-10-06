"""
API Routes - Papers Endpoint
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging

from api.models.schemas import PaperResponse, PaperListResponse
from api.services.neo4j_service import Neo4jService
from knowledge_graph.config import config
from knowledge_graph.summarization import get_summarizer

logger = logging.getLogger(__name__)
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


@router.get("/{paper_id}/summary")
async def get_paper_summary(
    paper_id: str,
    model: str = Query("bart", description="Model to use: 'bart' or 'pegasus'"),
    max_length: int = Query(150, ge=50, le=500, description="Maximum summary length"),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Generate AI-powered summary of a paper using BART or PEGASUS.
    
    - **paper_id**: PubMed ID (PMID)
    - **model**: Summarization model ('bart' or 'pegasus')
    - **max_length**: Maximum length of summary in tokens
    
    Returns:
        Dict with 'summary', 'model_used', 'key_points', metadata
    """
    # Get paper
    paper = neo4j.get_paper_by_id(paper_id)
    if not paper:
        raise HTTPException(status_code=404, detail=f"Paper {paper_id} not found")
    
    abstract = paper.get('abstract', '')
    
    if not abstract or len(abstract.strip()) < 50:
        raise HTTPException(
            status_code=400,
            detail="Paper abstract too short or missing"
        )
    
    try:
        # Select model
        model_name = "facebook/bart-large-cnn" if model.lower() == "bart" else "google/pegasus-xsum"
        
        logger.info(f"Generating summary for paper {paper_id} using {model_name}")
        
        # Get summarizer
        summarizer = get_summarizer(model_name=model_name)
        
        # Generate summary
        result = summarizer.summarize_abstract(
            abstract,
            max_length=max_length,
            min_length=max(30, max_length // 3)
        )
        
        # Generate key points
        key_points = summarizer.generate_key_points(abstract, num_points=3)
        
        logger.info(f"✅ Summary generated for paper {paper_id}")
        
        return {
            "paper_id": paper_id,
            "paper_title": paper.get('title', ''),
            "summary": result['summary'],
            "key_points": key_points,
            "model_used": result['model_used'],
            "original_length": result.get('original_length', len(abstract)),
            "summary_length": result.get('summary_length', len(result['summary'])),
            "compression_ratio": result.get('length_ratio', 0),
            "parameters": {
                "model": model,
                "max_length": max_length
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Summarization failed for paper {paper_id}: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate summary: {str(e)}"
        )


@router.post("/{paper_id}/summarize/batch")
async def batch_summarize(
    paper_ids: list[str],
    model: str = Query("bart", description="Model to use"),
    neo4j: Neo4jService = Depends(get_neo4j_service)
):
    """
    Generate summaries for multiple papers at once.
    
    - **paper_ids**: List of paper PMIDs
    - **model**: Summarization model ('bart' or 'pegasus')
    
    Returns:
        List of summaries with metadata
    """
    if len(paper_ids) > 50:
        raise HTTPException(
            status_code=400,
            detail="Maximum 50 papers per batch request"
        )
    
    summaries = []
    errors = []
    
    for paper_id in paper_ids:
        try:
            summary = await get_paper_summary(paper_id, model=model, neo4j=neo4j)
            summaries.append(summary)
        except Exception as e:
            errors.append({
                "paper_id": paper_id,
                "error": str(e)
            })
    
    return {
        "summaries": summaries,
        "errors": errors,
        "total_requested": len(paper_ids),
        "successful": len(summaries),
        "failed": len(errors)
    }

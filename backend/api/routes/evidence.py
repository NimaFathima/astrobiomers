"""
Evidence API Routes
Provides endpoints for relationship evidence and citations
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

# Add backend to path
BACKEND_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_PATH))

from api.services.evidence_service import EvidenceService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/evidence", tags=["evidence"])

# Initialize service
evidence_service = None


def get_evidence_service():
    """Get or initialize evidence service"""
    global evidence_service
    if evidence_service is None:
        evidence_service = EvidenceService()
    return evidence_service


# Pydantic models
class Paper(BaseModel):
    id: str
    title: str
    year: Optional[int]
    authors: Optional[str]
    abstract: Optional[str]
    pmid: Optional[str]
    doi: Optional[str]


class EdgeEvidenceRequest(BaseModel):
    source_id: str
    target_id: str
    relationship_type: Optional[str] = None


class EdgeEvidenceResponse(BaseModel):
    found: bool
    source: Optional[str]
    target: Optional[str]
    relationship_type: Optional[str]
    relationship_properties: Optional[dict]
    evidence_count: int
    papers: List[Paper]
    confidence: str
    message: Optional[str] = None


class EdgeWithEvidence(BaseModel):
    source_id: str
    source_name: str
    target_id: str
    target_name: str
    relationship_type: str
    evidence_count: int
    confidence: str


@router.post("/edge", response_model=EdgeEvidenceResponse)
async def get_edge_evidence(request: EdgeEvidenceRequest):
    """
    Get papers that provide evidence for a specific edge/relationship
    
    Example:
    ```
    POST /api/evidence/edge
    {
        "source_id": "4:abc123",
        "target_id": "4:def456",
        "relationship_type": "CAUSES"
    }
    ```
    """
    try:
        service = get_evidence_service()
        evidence = service.get_edge_evidence(
            source_id=request.source_id,
            target_id=request.target_id,
            relationship_type=request.relationship_type
        )
        
        if not evidence["found"]:
            return EdgeEvidenceResponse(
                found=False,
                evidence_count=0,
                papers=[],
                confidence="unverified",
                message=evidence.get("message", "No evidence found")
            )
        
        return EdgeEvidenceResponse(
            found=True,
            source=evidence["source"],
            target=evidence["target"],
            relationship_type=evidence["relationship_type"],
            relationship_properties=evidence["relationship_properties"],
            evidence_count=evidence["evidence_count"],
            papers=[Paper(**paper) for paper in evidence["papers"]],
            confidence=evidence["confidence"]
        )
        
    except Exception as e:
        logger.error(f"Error getting edge evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/all-edges", response_model=List[EdgeWithEvidence])
async def get_all_edges_evidence(limit: int = Query(100, ge=1, le=500)):
    """
    Get evidence counts for all edges in the graph
    
    Returns list of edges sorted by evidence count
    """
    try:
        service = get_evidence_service()
        edges = service.get_all_edge_evidence(limit=limit)
        return [EdgeWithEvidence(**edge) for edge in edges]
        
    except Exception as e:
        logger.error(f"Error getting all edges evidence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


class EntitySearchRequest(BaseModel):
    entities: List[str]


@router.post("/papers-by-entities", response_model=List[Paper])
async def search_papers_by_entities(request: EntitySearchRequest):
    """
    Find papers that mention multiple entities
    
    Example:
    ```
    POST /api/evidence/papers-by-entities
    {
        "entities": ["Microgravity", "Bone Loss", "Osteoporosis"]
    }
    ```
    """
    try:
        service = get_evidence_service()
        papers = service.search_papers_by_entities(entity_names=request.entities)
        return [Paper(**paper) for paper in papers]
        
    except Exception as e:
        logger.error(f"Error searching papers by entities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def evidence_health():
    """Check evidence service health"""
    try:
        service = get_evidence_service()
        return {
            "status": "ok",
            "service": "evidence",
            "message": "Evidence service is operational"
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "evidence",
            "message": str(e)
        }

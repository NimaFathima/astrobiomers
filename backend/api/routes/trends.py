"""
Trends API Routes
Provides endpoints for trend analysis, collaborations, and temporal patterns
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from pydantic import BaseModel
import sys
from pathlib import Path

# Add backend to path
BACKEND_PATH = Path(__file__).parent.parent.parent
sys.path.insert(0, str(BACKEND_PATH))

from api.services.trend_analysis import TrendAnalysisService
import logging

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/trends", tags=["trends"])

# Initialize service
trend_service = None


def get_trend_service():
    """Get or initialize trend analysis service"""
    global trend_service
    if trend_service is None:
        trend_service = TrendAnalysisService()
    return trend_service


# Pydantic models
class TimelinePoint(BaseModel):
    year: int
    count: int


class TopicTimeline(BaseModel):
    topic: str
    start_year: int
    end_year: int
    timeline: List[TimelinePoint]
    total_papers: int


class EmergingTopic(BaseModel):
    topic: str
    type: str
    recent_papers: int
    historical_papers: int
    growth_rate: float
    status: str


class CollaborationNode(BaseModel):
    id: str
    name: str


class CollaborationEdge(BaseModel):
    source: str
    target: str
    weight: int


class CollaborationNetwork(BaseModel):
    focus_author: Optional[str]
    nodes: List[CollaborationNode]
    edges: List[CollaborationEdge]
    total_authors: int
    total_collaborations: int


class TopAuthor(BaseModel):
    rank: int
    name: str
    paper_count: int
    first_year: Optional[int]
    last_year: Optional[int]
    years_active: int
    papers_per_year: float


class TopicCoOccurrence(BaseModel):
    topic1: str
    type1: str
    topic2: str
    type2: str
    co_occurrence_count: int
    strength: str


@router.get("/timeline", response_model=TopicTimeline)
async def get_timeline(
    topic: Optional[str] = Query(None, description="Specific topic to analyze (None for all)"),
    start_year: int = Query(2000, ge=1900, le=2025),
    end_year: int = Query(2025, ge=1900, le=2025)
):
    """
    Get publication timeline for a topic or all topics
    
    Example:
    - GET /api/trends/timeline?topic=microgravity&start_year=2010&end_year=2024
    - GET /api/trends/timeline (all topics)
    """
    try:
        service = get_trend_service()
        timeline_data = service.get_topic_timeline(
            topic=topic,
            start_year=start_year,
            end_year=end_year
        )
        return TopicTimeline(**timeline_data)
        
    except Exception as e:
        logger.error(f"Error getting timeline: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/emerging", response_model=List[EmergingTopic])
async def get_emerging_topics(
    timeframe_years: int = Query(5, ge=1, le=20, description="Years to analyze"),
    min_papers: int = Query(3, ge=1, description="Minimum papers required")
):
    """
    Identify topics with increasing publication rates
    
    Returns topics sorted by growth rate
    """
    try:
        service = get_trend_service()
        emerging = service.get_emerging_topics(
            timeframe_years=timeframe_years,
            min_papers=min_papers
        )
        return [EmergingTopic(**topic) for topic in emerging]
        
    except Exception as e:
        logger.error(f"Error getting emerging topics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/collaborations", response_model=CollaborationNetwork)
async def get_collaborations(
    author: Optional[str] = Query(None, description="Author name to analyze"),
    depth: int = Query(2, ge=1, le=3, description="Degrees of separation")
):
    """
    Get author collaboration network
    
    Example:
    - GET /api/trends/collaborations?author=Smith (network for specific author)
    - GET /api/trends/collaborations (top collaboration pairs)
    """
    try:
        service = get_trend_service()
        network = service.get_collaboration_network(
            author_name=author,
            depth=depth
        )
        return CollaborationNetwork(**network)
        
    except Exception as e:
        logger.error(f"Error getting collaboration network: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-authors", response_model=List[TopAuthor])
async def get_top_authors(
    topic: Optional[str] = Query(None, description="Filter by topic"),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Get top authors by publication count
    
    Example:
    - GET /api/trends/top-authors?topic=bone+loss&limit=10
    - GET /api/trends/top-authors (all topics)
    """
    try:
        service = get_trend_service()
        authors = service.get_top_authors(topic=topic, limit=limit)
        return [TopAuthor(**author) for author in authors]
        
    except Exception as e:
        logger.error(f"Error getting top authors: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/co-occurrence", response_model=List[TopicCoOccurrence])
async def get_topic_co_occurrence(
    min_papers: int = Query(2, ge=1, description="Minimum papers for co-occurrence")
):
    """
    Find topics that frequently appear together in papers
    
    Returns pairs of topics that co-occur, sorted by frequency
    """
    try:
        service = get_trend_service()
        co_occurrences = service.get_topic_co_occurrence(min_papers=min_papers)
        return [TopicCoOccurrence(**co_occ) for co_occ in co_occurrences]
        
    except Exception as e:
        logger.error(f"Error getting topic co-occurrence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def trends_health():
    """Check trends service health"""
    try:
        service = get_trend_service()
        return {
            "status": "ok",
            "service": "trends",
            "message": "Trend analysis service is operational"
        }
    except Exception as e:
        return {
            "status": "error",
            "service": "trends",
            "message": str(e)
        }

"""
API Models - Pydantic schemas for request/response validation
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


# =============== ENUMS ===============

class EntityType(str, Enum):
    """Entity types in knowledge graph"""
    GENE = "GENE"
    PROTEIN = "PROTEIN"
    DISEASE = "DISEASE"
    CHEMICAL = "CHEMICAL"
    STRESSOR = "STRESSOR"
    PHENOTYPE = "PHENOTYPE"
    ORGANISM = "ORGANISM"
    CELL_TYPE = "CELL_TYPE"
    INTERVENTION = "INTERVENTION"


class RelationType(str, Enum):
    """Relationship types in knowledge graph"""
    UPREGULATES = "UPREGULATES"
    DOWNREGULATES = "DOWNREGULATES"
    CAUSES = "CAUSES"
    TREATS = "TREATS"
    INTERACTS_WITH = "INTERACTS_WITH"
    PART_OF = "PART_OF"
    ASSOCIATED_WITH = "ASSOCIATED_WITH"


# =============== PAPER MODELS ===============

class PaperMetadata(BaseModel):
    """Paper metadata"""
    pmid: Optional[str] = None
    pmcid: Optional[str] = None
    doi: Optional[str] = None
    title: str
    abstract: Optional[str] = None
    authors: List[str] = []
    journal: Optional[str] = None
    publication_date: Optional[str] = None
    mesh_terms: List[str] = []
    keywords: List[str] = []


class PaperResponse(BaseModel):
    """Paper details response"""
    id: str
    metadata: PaperMetadata
    entities_count: int = 0
    relationships_count: int = 0
    topics: List[str] = []
    created_at: Optional[datetime] = None


class PaperListResponse(BaseModel):
    """List of papers response"""
    papers: List[PaperResponse]
    total: int
    page: int = 1
    page_size: int = 20


# =============== ENTITY MODELS ===============

class EntityBase(BaseModel):
    """Base entity model"""
    name: str
    entity_type: EntityType
    source: Optional[str] = None


class Entity(EntityBase):
    """Entity with full details"""
    id: str
    normalized_name: Optional[str] = None
    external_ids: Dict[str, str] = {}
    ontology_terms: List[str] = []
    synonyms: List[str] = []
    description: Optional[str] = None
    paper_count: int = 0


class EntityListResponse(BaseModel):
    """List of entities response"""
    entities: List[Entity]
    total: int
    page: int = 1
    page_size: int = 20


# =============== RELATIONSHIP MODELS ===============

class Relationship(BaseModel):
    """Relationship between entities"""
    id: str
    subject: Entity
    relation: RelationType
    object: Entity
    confidence: Optional[float] = None
    evidence: List[str] = []  # PMIDs
    source_sentences: List[str] = []


class RelationshipListResponse(BaseModel):
    """List of relationships response"""
    relationships: List[Relationship]
    total: int
    page: int = 1
    page_size: int = 20


# =============== GRAPH QUERY MODELS ===============

class GraphQueryRequest(BaseModel):
    """Request for graph query"""
    query: str = Field(..., description="Cypher query or natural language query")
    query_type: str = Field("cypher", description="Query type: 'cypher' or 'natural'")
    parameters: Dict[str, Any] = {}
    limit: int = Field(100, ge=1, le=1000)


class GraphNode(BaseModel):
    """Graph node representation"""
    id: str
    labels: List[str]
    properties: Dict[str, Any]


class GraphEdge(BaseModel):
    """Graph edge representation"""
    id: str
    type: str
    source: str  # node id
    target: str  # node id
    properties: Dict[str, Any] = {}


class GraphQueryResponse(BaseModel):
    """Graph query response"""
    nodes: List[GraphNode]
    edges: List[GraphEdge]
    statistics: Dict[str, int]
    query_time_ms: float


# =============== TOPIC MODELS ===============

class Topic(BaseModel):
    """Research topic"""
    id: int
    name: str
    keywords: List[str]
    paper_count: int
    representative_papers: List[str] = []  # PMIDs


class TopicListResponse(BaseModel):
    """List of topics response"""
    topics: List[Topic]
    total: int


class TopicTrend(BaseModel):
    """Topic trend over time"""
    topic_id: int
    topic_name: str
    year: int
    paper_count: int


class TopicTrendResponse(BaseModel):
    """Topic trends response"""
    trends: List[TopicTrend]


# =============== SEARCH MODELS ===============

class SearchRequest(BaseModel):
    """Search request"""
    query: str = Field(..., min_length=1)
    entity_types: List[EntityType] = []
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)


class SearchResult(BaseModel):
    """Search result"""
    type: str  # "paper", "entity", "relationship"
    id: str
    title: str
    description: str
    score: float
    metadata: Dict[str, Any] = {}


class SearchResponse(BaseModel):
    """Search response"""
    results: List[SearchResult]
    total: int
    page: int
    page_size: int
    query_time_ms: float


# =============== ANALYTICS MODELS ===============

class NetworkStats(BaseModel):
    """Network statistics"""
    node_count: int
    edge_count: int
    node_types: Dict[str, int]
    edge_types: Dict[str, int]
    density: float
    avg_degree: float


class EntityStats(BaseModel):
    """Entity statistics"""
    entity_type: EntityType
    count: int
    top_entities: List[Dict[str, Any]] = []


class StatsResponse(BaseModel):
    """Overall statistics response"""
    papers: int
    entities: int
    relationships: int
    topics: int
    network_stats: NetworkStats
    entity_stats: List[EntityStats]
    last_updated: datetime


# =============== PIPELINE MODELS ===============

class PipelineStatus(BaseModel):
    """Pipeline execution status"""
    status: str  # "running", "completed", "failed"
    stage: str
    progress: float  # 0-100
    message: str
    started_at: datetime
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class PipelineRequest(BaseModel):
    """Request to run pipeline"""
    papers: int = Field(10, ge=1, le=1000, description="Number of papers to process")
    use_curated: bool = Field(True, description="Use NASA curated publications")
    use_pubmed: bool = Field(False, description="Fetch from PubMed")
    use_genelab: bool = Field(False, description="Fetch from GeneLab")
    load_neo4j: bool = Field(True, description="Load into Neo4j")
    output_dir: Optional[str] = None


class PipelineResponse(BaseModel):
    """Pipeline execution response"""
    task_id: str
    status: str
    message: str
    estimated_time_minutes: int


# =============== HEALTH CHECK ===============

class HealthCheck(BaseModel):
    """Health check response"""
    status: str
    version: str
    database_connected: bool
    services: Dict[str, bool]

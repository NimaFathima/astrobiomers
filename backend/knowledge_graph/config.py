"""
Configuration for Knowledge Graph Construction Pipeline
"""

from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from typing import List, Optional
from pathlib import Path


class KnowledgeGraphConfig(BaseSettings):
    """Configuration settings for KG construction pipeline."""
    
    model_config = SettingsConfigDict(
        env_file=[
            str(Path(__file__).parent.parent.parent / ".env"),  # Root level
            str(Path(__file__).parent.parent / ".env"),          # Backend level
            ".env"                                                # Current directory
        ],
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # App Settings
    debug: bool = Field(True, env='DEBUG')
    
    # PubMed API
    pubmed_email: str = Field(..., env='PUBMED_EMAIL')
    pubmed_api_key: Optional[str] = Field(None, env='PUBMED_API_KEY')
    pubmed_batch_size: int = 200
    pubmed_rate_limit: float = 0.34  # seconds between requests with API key
    
    # NASA GeneLab
    genelab_api_url: str = Field(
        'https://genelab-data.ndc.nasa.gov/genelab/data',
        env='GENELAB_API_URL'
    )
    nasa_api_key: str = Field('DEMO_KEY', env='NASA_API_KEY')
    
    # NASA Open Science Data Repository (OSDR)
    osdr_api_url: str = Field(
        'https://osdr.nasa.gov/bio/repo/data',
        env='OSDR_API_URL'
    )
    
    # NASA Task Book
    taskbook_url: str = Field(
        'https://taskbook.nasaprs.com/tbp',
        env='TASKBOOK_URL'
    )
    
    # NASA Space Life Sciences Laboratory (NSLSL)
    nslsl_url: str = Field(
        'https://public.ksc.nasa.gov/nslsl',
        env='NSLSL_URL'
    )
    
    # Space Biology Publications (jgalazka GitHub)
    sb_publications_csv_url: str = Field(
        'https://raw.githubusercontent.com/jgalazka/SB_publications/main/SB_publication_PMC.csv',
        env='SB_PUBLICATIONS_URL'
    )
    
    # Neo4j
    neo4j_uri: str = Field('bolt://localhost:7687', env='NEO4J_URI')
    neo4j_user: str = Field('neo4j', env='NEO4J_USER')
    neo4j_password: str = Field(..., env='NEO4J_PASSWORD')
    neo4j_database: Optional[str] = Field('astrobiomers', env='NEO4J_DATABASE')
    
    # NLP Models
    scibert_model: str = 'allenai/scibert_scivocab_uncased'
    scispacy_model: str = 'en_ner_bc5cdr_md'
    sentence_transformer_model: str = 'pritamdeka/S-PubMedBert-MS-MARCO'
    
    # Entity Extraction
    entity_confidence_threshold: float = 0.75
    entity_batch_size: int = 32
    use_gpu: bool = True
    gpu_device: int = 0
    
    # Relationship Extraction
    relation_confidence_threshold: float = 0.70
    relation_max_distance: int = 100  # max characters between entities
    
    # Topic Modeling
    topic_min_cluster_size: int = 10
    topic_min_samples: int = 5
    topic_n_neighbors: int = 15
    topic_n_components: int = 5
    
    # Entity Resolution
    mygene_url: str = 'https://mygene.info/v3'
    uniprot_url: str = 'https://rest.uniprot.org/uniprotkb'
    ebi_ols_url: str = 'https://www.ebi.ac.uk/ols4/api'
    
    # Pipeline
    pipeline_batch_size: int = 100
    max_papers_per_run: int = 10000
    save_intermediate_results: bool = True
    intermediate_results_dir: str = './data/intermediate'
    
    # Search Query
    space_biology_stressors: List[str] = [
        "space biology",
        "spaceflight",
        "microgravity",
        "space radiation",
        "cosmic radiation",
        "hypergravity",
        "International Space Station",
        "ISS",
        "space mission",
        "astronaut",
        "ground analog",
        "bed rest",
        "hindlimb unloading"
    ]
    
    biological_terms: List[str] = [
        "gene expression",
        "protein",
        "pathway",
        "phenotype",
        "transcriptomics",
        "proteomics",
        "metabolomics",
        "bone loss",
        "muscle atrophy",
        "immune system",
        "cardiovascular",
        "neurovestibular"
    ]
    
    # Date Range
    start_date: str = "1974/01/01"
    end_date: str = "2025/12/31"

    @property
    def PUBMED_EUTILS_BASE(self) -> str:
        return "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"

    @property
    def SPACE_BIOLOGY_SEARCH_TERMS(self) -> List[str]:
        return self.space_biology_stressors

    @property
    def NASA_CURATED_PUBLICATIONS_URL(self) -> str:
        return self.sb_publications_csv_url


# Global config instance
config = KnowledgeGraphConfig()


class Config(KnowledgeGraphConfig):
    """Backward compatible alias exposing legacy attribute names."""

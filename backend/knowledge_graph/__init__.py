"""
Knowledge Graph Construction Module

This module contains all components for building the Space Biology Knowledge Graph:
- Data acquisition from PubMed, PMC, NASA GeneLab
- Text preprocessing and NLP pipeline
- Entity and relationship extraction using SciBERT
- Topic modeling with BERTopic
- Entity resolution and ontology alignment
- Neo4j graph database integration
"""

# Lazy imports to avoid loading heavy dependencies unless needed
__all__ = [
    'PubMedAcquisition',
    'GeneLabAcquisition',
    'SpaceBiologyPublications',
    'NASATaskBook',
    'NASAOSDR',
    'NASANSLSL',
    'IntegratedDataAcquisition',
    'TextPreprocessor',
    'EntityExtractor',
    'RelationExtractor',
    'TopicModeler',
    'EntityResolver',
    'OntologyAligner',
    'Neo4jLoader',
    'KnowledgeGraphPipeline'
]

__version__ = '1.0.0'


def __getattr__(name):
    """Lazy import to avoid loading heavy dependencies"""
    if name == 'PubMedAcquisition' or name == 'GeneLabAcquisition':
        from .data_acquisition import PubMedAcquisition, GeneLabAcquisition
        return PubMedAcquisition if name == 'PubMedAcquisition' else GeneLabAcquisition
    elif name in ['SpaceBiologyPublications', 'NASATaskBook', 'NASAOSDR', 'NASANSLSL', 'IntegratedDataAcquisition']:
        from .nasa_resources import (
            SpaceBiologyPublications, NASATaskBook, NASAOSDR,
            NASANSLSL, IntegratedDataAcquisition
        )
        return locals()[name]
    elif name == 'TextPreprocessor':
        from .text_preprocessing import TextPreprocessor
        return TextPreprocessor
    elif name == 'EntityExtractor':
        from .ner_extraction import EntityExtractor
        return EntityExtractor
    elif name == 'RelationExtractor':
        from .relation_extraction import RelationExtractor
        return RelationExtractor
    elif name == 'TopicModeler':
        from .topic_modeling import TopicModeler
        return TopicModeler
    elif name == 'EntityResolver':
        from .entity_resolution import EntityResolver
        return EntityResolver
    elif name == 'OntologyAligner':
        from .ontology_alignment import OntologyAligner
        return OntologyAligner
    elif name == 'Neo4jLoader':
        from .neo4j_loader import Neo4jLoader
        return Neo4jLoader
    elif name == 'KnowledgeGraphPipeline':
        from .pipeline import KnowledgeGraphPipeline
        return KnowledgeGraphPipeline
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

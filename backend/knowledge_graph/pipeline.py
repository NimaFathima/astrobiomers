"""
Main Pipeline Module for Space Biology Knowledge Graph Construction

Orchestrates the complete ETL pipeline:
1. Data Acquisition (PubMed, NASA resources)
2. Text Preprocessing (cleaning, normalization)
3. Entity Extraction (NER with SciBERT/SciSpacy)
4. Relationship Extraction (dependency parsing, patterns)
5. Topic Modeling (BERTopic)
6. Entity Resolution (MyGene, UniProt, etc.)
7. Ontology Alignment (GO, HPO, Mondo, etc.)
8. Neo4j Loading (graph construction)

Author: Space Biology KG Team
Date: October 2025
"""

import logging
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path
import time

logger = logging.getLogger(__name__)


class KnowledgeGraphPipeline:
    """
    Main pipeline for constructing the Space Biology Knowledge Graph.
    
    Coordinates all stages of the ETL process.
    """
    
    def __init__(self, config=None):
        """Initialize the pipeline with configuration."""
        from knowledge_graph.config import config as default_config
        from knowledge_graph.data_acquisition import PubMedAcquisition, GeneLabAcquisition
        from knowledge_graph.nasa_resources import IntegratedDataAcquisition
        from knowledge_graph.text_preprocessing import TextPreprocessor
        from knowledge_graph.ner_extraction import EntityExtractor
        from knowledge_graph.relation_extraction import RelationshipExtractor
        from knowledge_graph.topic_modeling import TopicModeler
        from knowledge_graph.entity_resolution import EntityResolver
        from knowledge_graph.ontology_alignment import OntologyAligner
        from knowledge_graph.neo4j_loader import Neo4jLoader
        
        self.config = config or default_config
        
        # Initialize all components
        logger.info("Initializing pipeline components...")
        
        self.pubmed = PubMedAcquisition(email=self.config.pubmed_email, api_key=self.config.pubmed_api_key)
        self.genelab = GeneLabAcquisition()
        self.nasa = IntegratedDataAcquisition()  # No config parameter
        self.preprocessor = TextPreprocessor(spacy_model="en_core_web_sm")
        self.entity_extractor = EntityExtractor(
            scibert_model="allenai/scibert_scivocab_uncased",
            use_gpu=False,  # CPU for compatibility
            confidence_threshold=0.75
        )
        self.relation_extractor = RelationshipExtractor(self.config)
        self.topic_modeler = TopicModeler(self.config)
        self.entity_resolver = EntityResolver(self.config)
        self.ontology_aligner = OntologyAligner(self.config)
        self.neo4j_loader = None  # Initialized when needed
        
        # Pipeline state
        self.pipeline_start_time = None
        self.stage_times = {}
        
        logger.info("Pipeline initialized successfully")
    
    def _convert_to_json_serializable(self, obj):
        """
        Convert numpy types to JSON-serializable Python types.
        
        Args:
            obj: Object to convert (can be dict, list, numpy type, etc.)
        
        Returns:
            JSON-serializable version of the object
        """
        import numpy as np
        
        if isinstance(obj, dict):
            return {key: self._convert_to_json_serializable(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_to_json_serializable(item) for item in obj]
        elif isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return obj
    
    def run(
        self,
        max_papers: int = 1000,
        use_curated: bool = True,
        use_pubmed: bool = True,
        use_genelab: bool = False,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        incremental: bool = False,
        load_to_neo4j: bool = True,
        output_dir: str = None
    ) -> Dict:
        """
        Run the complete knowledge graph construction pipeline.
        
        Args:
            max_papers: Maximum number of papers to process
            use_curated: Use curated space biology publications
            use_pubmed: Search PubMed for additional papers
            use_genelab: Include GeneLab datasets
            start_date: Start date for paper search (YYYY-MM-DD)
            end_date: End date for paper search (YYYY-MM-DD)
            incremental: Only process new papers
            load_to_neo4j: Load results into Neo4j
            output_dir: Directory for output files
        
        Returns:
            Dictionary with pipeline statistics and results
        """
        self.pipeline_start_time = time.time()
        logger.info("="*70)
        logger.info("Starting Knowledge Graph Construction Pipeline")
        logger.info("="*70)
        
        # Setup output directory
        if output_dir is None:
            output_dir = self.config.OUTPUT_DIR
        
        os.makedirs(output_dir, exist_ok=True)
        
        results = {
            'status': 'running',
            'start_time': datetime.now().isoformat(),
            'parameters': {
                'max_papers': max_papers,
                'use_curated': use_curated,
                'use_pubmed': use_pubmed,
                'use_genelab': use_genelab,
                'start_date': start_date,
                'end_date': end_date
            },
            'stages': {}
        }
        
        try:
            # Stage 1: Data Acquisition
            papers = self._stage_data_acquisition(
                max_papers, use_curated, use_pubmed, use_genelab,
                start_date, end_date, incremental, output_dir
            )
            results['stages']['data_acquisition'] = {
                'status': 'complete',
                'papers_acquired': len(papers),
                'duration': self.stage_times.get('data_acquisition', 0)
            }
            
            # Stage 2: Text Preprocessing
            papers = self._stage_text_preprocessing(papers, output_dir)
            results['stages']['text_preprocessing'] = {
                'status': 'complete',
                'papers_processed': len(papers),
                'duration': self.stage_times.get('text_preprocessing', 0)
            }
            
            # Stage 3: Entity Extraction
            papers = self._stage_entity_extraction(papers, output_dir)
            total_entities = sum(len(p.get('entities', [])) for p in papers)
            results['stages']['entity_extraction'] = {
                'status': 'complete',
                'total_entities': total_entities,
                'duration': self.stage_times.get('entity_extraction', 0)
            }
            
            # Stage 4: Relationship Extraction
            relationships = self._stage_relationship_extraction(papers, output_dir)
            results['stages']['relationship_extraction'] = {
                'status': 'complete',
                'total_relationships': len(relationships),
                'duration': self.stage_times.get('relationship_extraction', 0)
            }
            
            # Stage 5: Topic Modeling
            papers = self._stage_topic_modeling(papers, output_dir)
            results['stages']['topic_modeling'] = {
                'status': 'complete',
                'topics_discovered': len(set(p.get('topic_id', -1) for p in papers)) - 1,
                'duration': self.stage_times.get('topic_modeling', 0)
            }
            
            # Stage 6: Entity Resolution
            all_entities = self._collect_all_entities(papers)
            all_entities = self._stage_entity_resolution(all_entities, output_dir)
            results['stages']['entity_resolution'] = {
                'status': 'complete',
                'entities_resolved': sum(1 for e in all_entities if e.get('resolved')),
                'duration': self.stage_times.get('entity_resolution', 0)
            }
            
            # Stage 7: Ontology Alignment
            all_entities = self._stage_ontology_alignment(all_entities, output_dir)
            relationships = self._stage_relationship_enrichment(relationships)
            results['stages']['ontology_alignment'] = {
                'status': 'complete',
                'entities_aligned': sum(1 for e in all_entities if e.get('ontology_aligned')),
                'duration': self.stage_times.get('ontology_alignment', 0)
            }
            
            # Stage 8: Neo4j Loading
            if load_to_neo4j:
                graph_stats = self._stage_neo4j_loading(
                    papers, all_entities, relationships, output_dir
                )
                results['stages']['neo4j_loading'] = {
                    'status': 'complete',
                    'graph_statistics': graph_stats,
                    'duration': self.stage_times.get('neo4j_loading', 0)
                }
            
            # Pipeline complete
            results['status'] = 'complete'
            results['end_time'] = datetime.now().isoformat()
            results['total_duration'] = time.time() - self.pipeline_start_time
            
            logger.info("="*70)
            logger.info("Pipeline completed successfully!")
            logger.info(f"Total duration: {results['total_duration']:.2f} seconds")
            logger.info("="*70)
            
            # Save results
            self._save_pipeline_results(results, output_dir)
            
        except Exception as e:
            logger.error(f"Pipeline failed: {e}", exc_info=True)
            results['status'] = 'failed'
            results['error'] = str(e)
            results['end_time'] = datetime.now().isoformat()
            self._save_pipeline_results(results, output_dir)
            raise
        
        return results
    
    def _stage_data_acquisition(
        self, max_papers, use_curated, use_pubmed, use_genelab,
        start_date, end_date, incremental, output_dir
    ) -> List[Dict]:
        """Stage 1: Acquire papers from various sources."""
        logger.info("\n" + "="*70)
        logger.info("STAGE 1: Data Acquisition")
        logger.info("="*70)
        
        stage_start = time.time()
        
        # Use integrated acquisition
        results = self.nasa.acquire_all_sources(
            use_curated=use_curated,
            use_pubmed=use_pubmed,
            use_genelab=use_genelab,
            max_papers=max_papers
            # Note: start_date and end_date are not supported by acquire_all_sources
        )
        
        papers = results.get('all_papers', [])
        
        # If all_papers is empty, try curated_publications
        if not papers:
            papers = results.get('curated_publications', [])
        
        # Limit to max_papers
        papers = papers[:max_papers]
        
        logger.info(f"Acquired {len(papers)} papers")
        logger.info(f"  - Curated: {len(results.get('curated_publications', []))}")
        logger.info(f"  - PubMed: {len(results.get('pubmed_papers', []))}")
        
        # Save raw data
        output_file = os.path.join(output_dir, 'raw_papers.json')
        with open(output_file, 'w') as f:
            json.dump(papers, f, indent=2)
        
        logger.info(f"Saved to: {output_file}")
        
        self.stage_times['data_acquisition'] = time.time() - stage_start
        return papers
    
    def _stage_text_preprocessing(self, papers: List[Dict], output_dir: str) -> List[Dict]:
        """Stage 2: Preprocess text."""
        logger.info("\n" + "="*70)
        logger.info("STAGE 2: Text Preprocessing")
        logger.info("="*70)
        
        stage_start = time.time()
        
        papers = self.preprocessor.preprocess_batch(papers)
        
        logger.info(f"Preprocessed {len(papers)} papers")
        
        # Save preprocessed data
        output_file = os.path.join(output_dir, 'preprocessed_papers.json')
        with open(output_file, 'w') as f:
            json.dump(papers, f, indent=2)
        
        logger.info(f"Saved to: {output_file}")
        
        self.stage_times['text_preprocessing'] = time.time() - stage_start
        return papers
    
    def _stage_entity_extraction(self, papers: List[Dict], output_dir: str) -> List[Dict]:
        """Stage 3: Extract entities."""
        logger.info("\n" + "="*70)
        logger.info("STAGE 3: Entity Extraction")
        logger.info("="*70)
        
        stage_start = time.time()
        
        papers = self.entity_extractor.extract_from_papers_batch(papers)
        
        total_entities = sum(len(p.get('entities', [])) for p in papers)
        logger.info(f"Extracted {total_entities} entities from {len(papers)} papers")
        
        # Get basic statistics
        entity_types = {}
        for paper in papers:
            for entity in paper.get('entities', []):
                entity_type = entity.get('type', 'UNKNOWN')
                entity_types[entity_type] = entity_types.get(entity_type, 0) + 1
        logger.info(f"Entity types: {entity_types}")
        
        # Save entities
        output_file = os.path.join(output_dir, 'extracted_entities.json')
        with open(output_file, 'w') as f:
            # Convert numpy float32 to regular float for JSON serialization
            papers_serializable = []
            for paper in papers:
                paper_copy = paper.copy()
                if 'entities' in paper_copy:
                    entities_serializable = []
                    for entity in paper_copy['entities']:
                        entity_copy = entity.copy()
                        # Convert float32 to float
                        for key, value in entity_copy.items():
                            if hasattr(value, 'item'):  # numpy types have .item() method
                                entity_copy[key] = value.item()
                        entities_serializable.append(entity_copy)
                    paper_copy['entities'] = entities_serializable
                papers_serializable.append(paper_copy)
            json.dump(papers_serializable, f, indent=2)
        
        logger.info(f"Saved to: {output_file}")
        
        self.stage_times['entity_extraction'] = time.time() - stage_start
        return papers
    
    def _stage_relationship_extraction(self, papers: List[Dict], output_dir: str) -> List[Dict]:
        """Stage 4: Extract relationships."""
        logger.info("\n" + "="*70)
        logger.info("STAGE 4: Relationship Extraction")
        logger.info("="*70)
        
        stage_start = time.time()
        
        relationships = self.relation_extractor.extract_from_papers_batch(papers)
        
        logger.info(f"Extracted {len(relationships)} relationships")
        
        # Get basic statistics  
        relationship_types = {}
        confidences = []
        for rel in relationships:
            rel_type = rel.get('type', 'UNKNOWN')
            relationship_types[rel_type] = relationship_types.get(rel_type, 0) + 1
            if 'confidence' in rel:
                confidences.append(rel['confidence'])
        
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0
        logger.info(f"By type: {relationship_types}")
        logger.info(f"Average confidence: {avg_confidence:.2f}")
        
        # Aggregate relationships
        aggregated = self.relation_extractor.aggregate_relationships(relationships)
        logger.info(f"Aggregated to {len(aggregated)} unique relationships")
        
        # Save relationships
        output_file = os.path.join(output_dir, 'extracted_relationships.json')
        with open(output_file, 'w') as f:
            json.dump(list(aggregated.values()), f, indent=2)
        
        logger.info(f"Saved to: {output_file}")
        
        self.stage_times['relationship_extraction'] = time.time() - stage_start
        return list(aggregated.values())
    
    def _stage_topic_modeling(self, papers: List[Dict], output_dir: str) -> List[Dict]:
        """Stage 5: Discover topics."""
        logger.info("\n" + "="*70)
        logger.info("STAGE 5: Topic Modeling")
        logger.info("="*70)
        
        stage_start = time.time()
        
        # Only fit if we have enough papers
        if len(papers) >= 50:
            self.topic_modeler.fit_topics(papers, min_topic_size=10)
            papers = self.topic_modeler.assign_topics_to_papers(papers)
            
            # Get basic statistics
            topic_counts = {}
            papers_with_topics = 0
            for paper in papers:
                if 'topic_id' in paper and paper['topic_id'] >= 0:
                    papers_with_topics += 1
                    topic_id = paper['topic_id']
                    topic_counts[topic_id] = topic_counts.get(topic_id, 0) + 1
            
            logger.info(f"Discovered {len(topic_counts)} topics")
            logger.info(f"Papers with topics: {papers_with_topics}")
            
            # Save model
            model_path = os.path.join(output_dir, 'topic_model')
            self.topic_modeler.save_model(model_path)
            logger.info(f"Saved model to: {model_path}")
        else:
            logger.warning(f"Not enough papers ({len(papers)}) for topic modeling (need 50+)")
        
        self.stage_times['topic_modeling'] = time.time() - stage_start
        return papers
    
    def _stage_entity_resolution(self, entities: List[Dict], output_dir: str) -> List[Dict]:
        """Stage 6: Resolve entities to databases."""
        logger.info("\n" + "="*70)
        logger.info("STAGE 6: Entity Resolution")
        logger.info("="*70)
        
        stage_start = time.time()
        
        entities = self.entity_resolver.resolve_entities_batch(entities)
        
        # Get basic statistics
        total_entities = len(entities)
        resolved_entities = sum(1 for e in entities if e.get('resolved', False))
        resolution_rate = resolved_entities / total_entities if total_entities > 0 else 0
        
        logger.info(f"Resolved {resolved_entities}/{total_entities} entities")
        logger.info(f"Resolution rate: {resolution_rate:.1%}")
        
        # Save resolved entities (convert numpy types to native Python)
        output_file = os.path.join(output_dir, 'resolved_entities.json')
        with open(output_file, 'w') as f:
            json.dump(self._convert_to_json_serializable(entities), f, indent=2)
        
        logger.info(f"Saved to: {output_file}")
        
        self.stage_times['entity_resolution'] = time.time() - stage_start
        return entities
    
    def _stage_ontology_alignment(self, entities: List[Dict], output_dir: str) -> List[Dict]:
        """Stage 7: Align entities to ontologies."""
        logger.info("\n" + "="*70)
        logger.info("STAGE 7: Ontology Alignment")
        logger.info("="*70)
        
        stage_start = time.time()
        
        entities = self.ontology_aligner.align_entities(entities)
        
        # Get statistics
        stats = self.ontology_aligner.get_alignment_statistics(entities)
        logger.info(f"Aligned {stats['aligned']}/{stats['total_entities']} entities")
        logger.info(f"Alignment rate: {stats['alignment_rate']:.1%}")
        logger.info(f"By ontology: {stats['by_ontology']}")
        
        # Save aligned entities (convert numpy types to native Python)
        output_file = os.path.join(output_dir, 'aligned_entities.json')
        with open(output_file, 'w') as f:
            json.dump(self._convert_to_json_serializable(entities), f, indent=2)
        
        logger.info(f"Saved to: {output_file}")
        
        self.stage_times['ontology_alignment'] = time.time() - stage_start
        return entities
    
    def _stage_relationship_enrichment(self, relationships: List[Dict]) -> List[Dict]:
        """Enrich relationships with ontology information."""
        return self.ontology_aligner.enrich_relationships(relationships)
    
    def _stage_neo4j_loading(
        self, papers: List[Dict], entities: List[Dict],
        relationships: List[Dict], output_dir: str
    ) -> Dict:
        """Stage 8: Load into Neo4j."""
        logger.info("\n" + "="*70)
        logger.info("STAGE 8: Neo4j Loading")
        logger.info("="*70)
        
        stage_start = time.time()
        
        # Initialize Neo4j loader
        from knowledge_graph.neo4j_loader import Neo4jLoader
        self.neo4j_loader = Neo4jLoader(self.config)
        
        # Initialize schema
        self.neo4j_loader.initialize_schema()
        
        # Load data
        self.neo4j_loader.load_papers(papers)
        self.neo4j_loader.load_entities(entities)
        self.neo4j_loader.load_relationships(relationships)
        self.neo4j_loader.create_paper_entity_links(papers)
        self.neo4j_loader.create_paper_topic_links(papers)
        
        # Get statistics
        stats = self.neo4j_loader.get_graph_statistics()
        logger.info(f"Graph loaded successfully!")
        logger.info(f"  Nodes: {stats['total_nodes']}")
        logger.info(f"  Relationships: {stats['total_relationships']}")
        
        self.neo4j_loader.close()
        
        self.stage_times['neo4j_loading'] = time.time() - stage_start
        return stats
    
    def _collect_all_entities(self, papers: List[Dict]) -> List[Dict]:
        """Collect all unique entities from papers."""
        entity_map = {}
        
        for paper in papers:
            for entity in paper.get('entities', []):
                key = (entity['text'].lower(), entity['type'])
                if key not in entity_map:
                    entity_map[key] = entity
        
        return list(entity_map.values())
    
    def _save_pipeline_results(self, results: Dict, output_dir: str):
        """Save pipeline results summary."""
        output_file = os.path.join(output_dir, 'pipeline_results.json')
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"\nPipeline results saved to: {output_file}")


if __name__ == '__main__':
    # Test pipeline
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Create pipeline
    pipeline = KnowledgeGraphPipeline()
    
    # Run with small test dataset
    results = pipeline.run(
        max_papers=10,
        use_curated=True,
        use_pubmed=False,
        load_to_neo4j=False,  # Set to True if Neo4j is running
        output_dir='data/pipeline_test'
    )
    
    print("\n" + "="*70)
    print("Pipeline Test Results:")
    print("="*70)
    print(f"Status: {results['status']}")
    print(f"Duration: {results.get('total_duration', 0):.2f} seconds")
    print("\nStage Summary:")
    for stage, info in results.get('stages', {}).items():
        print(f"  {stage}: {info['status']} ({info.get('duration', 0):.2f}s)")

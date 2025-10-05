"""
Ontology Alignment Module for Space Biology Knowledge Graph

Maps extracted entities and relationships to standard biomedical ontologies:
- Gene Ontology (GO): Molecular functions, biological processes, cellular components
- Mondo Disease Ontology: Disease standardization
- Human Phenotype Ontology (HPO): Phenotype descriptions
- UBERON: Anatomical structures
- Cell Ontology (CL): Cell types
- ChEBI: Chemical entities
- Environment Ontology (ENVO): Environmental conditions

Author: Space Biology KG Team
Date: October 2025
"""

import logging
import requests
from typing import List, Dict, Set, Optional, Tuple
from collections import defaultdict
import json

logger = logging.getLogger(__name__)


class OntologyAligner:
    """
    Align entities and relationships to biomedical ontologies.
    
    Provides semantic enrichment and standardization.
    """
    
    def __init__(self, config=None):
        """Initialize ontology aligner."""
        from knowledge_graph.config import config as default_config
        
        self.config = config or default_config
        
        # BioPortal API for ontology access
        self.bioportal_url = "https://data.bioontology.org"
        self.bioportal_api_key = None  # User should provide
        
        # OLS (Ontology Lookup Service) API
        self.ols_url = "https://www.ebi.ac.uk/ols/api"
        
        # Cache
        self.go_cache = {}
        self.hpo_cache = {}
        self.mondo_cache = {}
        
        # Load space biology ontology mappings
        self._initialize_mappings()
        
        logger.info("OntologyAligner initialized")
    
    def _initialize_mappings(self):
        """Initialize predefined ontology mappings for space biology."""
        
        # Space biology stressors -> ENVO terms
        self.stressor_mappings = {
            'microgravity': {
                'envo_id': 'ENVO:01001004',
                'label': 'microgravity environment',
                'definition': 'An environment with very low gravity'
            },
            'radiation': {
                'envo_id': 'ENVO:01001023',
                'label': 'radiation exposure',
                'definition': 'Exposure to ionizing or non-ionizing radiation'
            },
            'cosmic radiation': {
                'envo_id': 'ENVO:01001024',
                'label': 'cosmic ray exposure',
                'definition': 'Exposure to high-energy particles from outer space'
            },
            'spaceflight': {
                'envo_id': 'ENVO:01001000',
                'label': 'space environment',
                'definition': 'Environment outside Earth\'s atmosphere'
            },
            'hypergravity': {
                'envo_id': 'ENVO:01001005',
                'label': 'hypergravity environment',
                'definition': 'Environment with increased gravitational force'
            }
        }
        
        # Phenotypes -> HPO terms
        self.phenotype_mappings = {
            'muscle atrophy': {
                'hpo_id': 'HP:0003202',
                'label': 'Skeletal muscle atrophy',
                'definition': 'Atrophy (wasting) of skeletal muscle'
            },
            'bone loss': {
                'hpo_id': 'HP:0000939',
                'label': 'Osteoporosis',
                'definition': 'Reduction in bone mineral density'
            },
            'immune dysfunction': {
                'hpo_id': 'HP:0002721',
                'label': 'Immunodeficiency',
                'definition': 'Decreased immune system function'
            },
            'cardiovascular deconditioning': {
                'hpo_id': 'HP:0001637',
                'label': 'Abnormal cardiac function',
                'definition': 'Abnormality of the function of the heart'
            },
            'vision changes': {
                'hpo_id': 'HP:0000505',
                'label': 'Visual impairment',
                'definition': 'Impairment of vision'
            }
        }
        
        # Common GO terms for space biology
        self.go_mappings = {
            'muscle contraction': {
                'go_id': 'GO:0006936',
                'aspect': 'biological_process',
                'label': 'muscle contraction'
            },
            'bone remodeling': {
                'go_id': 'GO:0046849',
                'aspect': 'biological_process',
                'label': 'bone remodeling'
            },
            'protein degradation': {
                'go_id': 'GO:0030163',
                'aspect': 'biological_process',
                'label': 'protein catabolic process'
            },
            'immune response': {
                'go_id': 'GO:0006955',
                'aspect': 'biological_process',
                'label': 'immune response'
            },
            'oxidative stress': {
                'go_id': 'GO:0006979',
                'aspect': 'biological_process',
                'label': 'response to oxidative stress'
            },
            'dna damage': {
                'go_id': 'GO:0006974',
                'aspect': 'biological_process',
                'label': 'cellular response to DNA damage stimulus'
            }
        }
    
    def align_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Align entities to relevant ontologies.
        
        Args:
            entities: List of entities with 'text', 'type'
        
        Returns:
            Entities with ontology annotations
        """
        logger.info(f"Aligning {len(entities)} entities to ontologies...")
        
        for entity in entities:
            entity_type = entity.get('type')
            entity_text = entity['text'].lower()
            
            # Align based on entity type
            if entity_type == 'STRESSOR':
                self._align_stressor(entity)
            elif entity_type == 'PHENOTYPE':
                self._align_phenotype(entity)
            elif entity_type in ['GENE', 'PROTEIN']:
                self._align_gene(entity)
            elif entity_type == 'DISEASE':
                self._align_disease(entity)
            elif entity_type == 'CELL_TYPE':
                self._align_cell_type(entity)
            elif entity_type == 'ANATOMICAL':
                self._align_anatomy(entity)
        
        logger.info("Ontology alignment complete")
        return entities
    
    def _align_stressor(self, entity: Dict):
        """Align stressor to ENVO ontology."""
        text = entity['text'].lower()
        
        # Check predefined mappings
        if text in self.stressor_mappings:
            mapping = self.stressor_mappings[text]
            entity['envo_id'] = mapping['envo_id']
            entity['envo_label'] = mapping['label']
            entity['envo_definition'] = mapping['definition']
            entity['ontology_aligned'] = True
        else:
            # Try partial matching
            for key, value in self.stressor_mappings.items():
                if key in text or text in key:
                    entity['envo_id'] = value['envo_id']
                    entity['envo_label'] = value['label']
                    entity['envo_definition'] = value['definition']
                    entity['ontology_aligned'] = True
                    return
            
            entity['ontology_aligned'] = False
    
    def _align_phenotype(self, entity: Dict):
        """Align phenotype to HPO ontology."""
        text = entity['text'].lower()
        
        # Check cache
        if text in self.hpo_cache:
            entity.update(self.hpo_cache[text])
            entity['ontology_aligned'] = True
            return
        
        # Check predefined mappings
        if text in self.phenotype_mappings:
            mapping = self.phenotype_mappings[text]
            entity['hpo_id'] = mapping['hpo_id']
            entity['hpo_label'] = mapping['label']
            entity['hpo_definition'] = mapping['definition']
            entity['ontology_aligned'] = True
            
            # Cache result
            self.hpo_cache[text] = {
                'hpo_id': mapping['hpo_id'],
                'hpo_label': mapping['label'],
                'hpo_definition': mapping['definition']
            }
        else:
            # Try OLS API search
            try:
                hpo_info = self._search_ols('hp', text)
                if hpo_info:
                    entity['hpo_id'] = hpo_info['id']
                    entity['hpo_label'] = hpo_info['label']
                    entity['hpo_definition'] = hpo_info.get('definition', '')
                    entity['ontology_aligned'] = True
                    
                    # Cache result
                    self.hpo_cache[text] = {
                        'hpo_id': hpo_info['id'],
                        'hpo_label': hpo_info['label'],
                        'hpo_definition': hpo_info.get('definition', '')
                    }
                else:
                    entity['ontology_aligned'] = False
            except Exception as e:
                logger.debug(f"Could not align phenotype {text}: {e}")
                entity['ontology_aligned'] = False
    
    def _align_gene(self, entity: Dict):
        """Align gene to GO terms."""
        text = entity['text'].lower()
        
        # Check cache
        if text in self.go_cache:
            entity['go_terms'] = self.go_cache[text]
            entity['ontology_aligned'] = True
            return
        
        # Use resolved gene info if available
        entrez_id = entity.get('entrez_id')
        
        if entrez_id:
            try:
                # Query MyGene.info for GO terms
                response = requests.get(
                    f"https://mygene.info/v3/gene/{entrez_id}",
                    params={'fields': 'go'},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    go_info = data.get('go', {})
                    
                    go_terms = []
                    
                    # Extract BP, MF, CC terms
                    for aspect in ['BP', 'MF', 'CC']:
                        if aspect in go_info:
                            for term in go_info[aspect]:
                                go_terms.append({
                                    'go_id': term['id'],
                                    'term': term['term'],
                                    'aspect': aspect,
                                    'evidence': term.get('evidence', '')
                                })
                    
                    if go_terms:
                        entity['go_terms'] = go_terms
                        entity['ontology_aligned'] = True
                        
                        # Cache result
                        self.go_cache[text] = go_terms
                    else:
                        entity['ontology_aligned'] = False
                else:
                    entity['ontology_aligned'] = False
                    
            except Exception as e:
                logger.debug(f"Could not get GO terms for {text}: {e}")
                entity['ontology_aligned'] = False
        else:
            entity['ontology_aligned'] = False
    
    def _align_disease(self, entity: Dict):
        """Align disease to Mondo ontology."""
        text = entity['text'].lower()
        
        # Check cache
        if text in self.mondo_cache:
            entity.update(self.mondo_cache[text])
            entity['ontology_aligned'] = True
            return
        
        # Use resolved disease info if available
        if entity.get('mondo_id'):
            entity['ontology_aligned'] = True
            return
        
        # Try OLS API search
        try:
            mondo_info = self._search_ols('mondo', text)
            if mondo_info:
                entity['mondo_id'] = mondo_info['id']
                entity['mondo_label'] = mondo_info['label']
                entity['mondo_definition'] = mondo_info.get('definition', '')
                entity['ontology_aligned'] = True
                
                # Cache result
                self.mondo_cache[text] = {
                    'mondo_id': mondo_info['id'],
                    'mondo_label': mondo_info['label'],
                    'mondo_definition': mondo_info.get('definition', '')
                }
            else:
                entity['ontology_aligned'] = False
        except Exception as e:
            logger.debug(f"Could not align disease {text}: {e}")
            entity['ontology_aligned'] = False
    
    def _align_cell_type(self, entity: Dict):
        """Align cell type to Cell Ontology."""
        # Use resolved CL ID if available
        if entity.get('cl_id'):
            entity['ontology_aligned'] = True
            return
        
        # Try OLS API search
        try:
            cl_info = self._search_ols('cl', entity['text'])
            if cl_info:
                entity['cl_id'] = cl_info['id']
                entity['cl_label'] = cl_info['label']
                entity['cl_definition'] = cl_info.get('definition', '')
                entity['ontology_aligned'] = True
            else:
                entity['ontology_aligned'] = False
        except Exception as e:
            logger.debug(f"Could not align cell type {entity['text']}: {e}")
            entity['ontology_aligned'] = False
    
    def _align_anatomy(self, entity: Dict):
        """Align anatomical term to UBERON."""
        try:
            uberon_info = self._search_ols('uberon', entity['text'])
            if uberon_info:
                entity['uberon_id'] = uberon_info['id']
                entity['uberon_label'] = uberon_info['label']
                entity['uberon_definition'] = uberon_info.get('definition', '')
                entity['ontology_aligned'] = True
            else:
                entity['ontology_aligned'] = False
        except Exception as e:
            logger.debug(f"Could not align anatomy {entity['text']}: {e}")
            entity['ontology_aligned'] = False
    
    def _search_ols(self, ontology: str, query: str) -> Optional[Dict]:
        """
        Search OLS (Ontology Lookup Service) for term.
        
        Args:
            ontology: Ontology abbreviation (hp, mondo, go, cl, uberon)
            query: Search term
        
        Returns:
            Dict with id, label, definition or None
        """
        try:
            response = requests.get(
                f"{self.ols_url}/search",
                params={
                    'q': query,
                    'ontology': ontology,
                    'exact': 'true',
                    'rows': 1
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                docs = data.get('response', {}).get('docs', [])
                
                if docs:
                    doc = docs[0]
                    return {
                        'id': doc.get('obo_id', doc.get('short_form')),
                        'label': doc.get('label'),
                        'definition': doc.get('description', [''])[0] if doc.get('description') else ''
                    }
            
            return None
            
        except Exception as e:
            logger.debug(f"OLS search error: {e}")
            return None
    
    def enrich_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """
        Enrich relationships with ontology information.
        
        Adds semantic context from ontologies.
        """
        logger.info(f"Enriching {len(relationships)} relationships...")
        
        for rel in relationships:
            rel_type = rel['relation_type']
            
            # Map to standard relation ontology terms
            if rel_type in ['UPREGULATES', 'DOWNREGULATES']:
                rel['ro_id'] = 'RO:0002213'  # Regulates
                rel['ro_label'] = 'regulates'
            elif rel_type == 'CAUSES':
                rel['ro_id'] = 'RO:0002410'  # Causally related to
                rel['ro_label'] = 'causally related to'
            elif rel_type == 'INTERACTS_WITH':
                rel['ro_id'] = 'RO:0002434'  # Interacts with
                rel['ro_label'] = 'interacts with'
            elif rel_type == 'PART_OF':
                rel['ro_id'] = 'RO:0002102'  # Part of
                rel['ro_label'] = 'part of'
            elif rel_type == 'TREATS':
                rel['ro_id'] = 'RO:0002606'  # Treats
                rel['ro_label'] = 'treats'
        
        return relationships
    
    def get_alignment_statistics(self, entities: List[Dict]) -> Dict:
        """Get statistics about ontology alignment."""
        stats = {
            'total_entities': len(entities),
            'aligned': 0,
            'not_aligned': 0,
            'by_ontology': defaultdict(int),
            'by_type': defaultdict(lambda: {'total': 0, 'aligned': 0})
        }
        
        for entity in entities:
            entity_type = entity.get('type', 'UNKNOWN')
            is_aligned = entity.get('ontology_aligned', False)
            
            stats['by_type'][entity_type]['total'] += 1
            
            if is_aligned:
                stats['aligned'] += 1
                stats['by_type'][entity_type]['aligned'] += 1
                
                # Count by ontology
                if entity.get('go_terms'):
                    stats['by_ontology']['GO'] += 1
                if entity.get('hpo_id'):
                    stats['by_ontology']['HPO'] += 1
                if entity.get('mondo_id'):
                    stats['by_ontology']['Mondo'] += 1
                if entity.get('envo_id'):
                    stats['by_ontology']['ENVO'] += 1
                if entity.get('cl_id'):
                    stats['by_ontology']['CL'] += 1
                if entity.get('uberon_id'):
                    stats['by_ontology']['UBERON'] += 1
            else:
                stats['not_aligned'] += 1
        
        # Calculate alignment rate
        if stats['total_entities'] > 0:
            stats['alignment_rate'] = stats['aligned'] / stats['total_entities']
        else:
            stats['alignment_rate'] = 0.0
        
        # Convert defaultdicts
        stats['by_ontology'] = dict(stats['by_ontology'])
        stats['by_type'] = dict(stats['by_type'])
        
        return stats


if __name__ == '__main__':
    # Test ontology alignment
    logging.basicConfig(level=logging.INFO)
    
    aligner = OntologyAligner()
    
    # Test entities
    test_entities = [
        {'text': 'microgravity', 'type': 'STRESSOR'},
        {'text': 'muscle atrophy', 'type': 'PHENOTYPE'},
        {'text': 'bone loss', 'type': 'PHENOTYPE'},
        {'text': 'radiation', 'type': 'STRESSOR'},
        {'text': 'IGF-1', 'type': 'GENE', 'entrez_id': '3479'},
        {'text': 'skeletal muscle', 'type': 'CELL_TYPE', 'cl_id': 'CL:0000188'}
    ]
    
    # Align
    aligned = aligner.align_entities(test_entities)
    
    print("\nAligned Entities:")
    for entity in aligned:
        print(f"\n{entity['text']} ({entity['type']})")
        print(f"  Aligned: {entity.get('ontology_aligned', False)}")
        
        if entity.get('envo_id'):
            print(f"  ENVO: {entity['envo_id']} - {entity['envo_label']}")
        if entity.get('hpo_id'):
            print(f"  HPO: {entity['hpo_id']} - {entity['hpo_label']}")
        if entity.get('go_terms'):
            print(f"  GO terms: {len(entity['go_terms'])} found")
            for term in entity['go_terms'][:3]:
                print(f"    - {term['go_id']}: {term['term']} ({term['aspect']})")
    
    # Get statistics
    stats = aligner.get_alignment_statistics(aligned)
    print(f"\n\nAlignment Statistics:")
    print(f"  Total: {stats['total_entities']}")
    print(f"  Aligned: {stats['aligned']}")
    print(f"  Alignment rate: {stats['alignment_rate']:.1%}")
    print(f"  By ontology: {stats['by_ontology']}")

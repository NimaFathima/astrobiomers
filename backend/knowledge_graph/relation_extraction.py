"""
Relationship Extraction Module for Space Biology Knowledge Graph

Extracts relationships between biomedical entities using:
1. Dependency parsing patterns
2. Co-occurrence analysis
3. Rule-based patterns for space biology
4. Distant supervision with ontologies

Author: Space Biology KG Team
Date: October 2025
"""

import re
import logging
from typing import List, Dict, Tuple, Set, Optional, TYPE_CHECKING
from collections import defaultdict

try:  # pragma: no cover - optional dependency
    import spacy  # type: ignore
except Exception:  # pragma: no cover
    spacy = None  # type: ignore

if TYPE_CHECKING:  # pragma: no cover - typing hints only
    from spacy.tokens import Doc, Span, Token  # type: ignore
else:
    Doc = Span = Token = None  # type: ignore

logger = logging.getLogger(__name__)


class RelationshipExtractor:
    """
    Extract relationships between entities using multiple methods.
    
    Relationship Types:
    - UPREGULATES/DOWNREGULATES: Gene expression changes
    - CAUSES: Stressor -> Phenotype
    - TREATS/PREVENTS: Intervention -> Phenotype
    - INTERACTS_WITH: Protein-protein interactions
    - PART_OF: Anatomical relationships
    - ASSOCIATED_WITH: General associations
    - STUDIED_IN: Entity -> Organism
    - MEASURED_IN: Entity -> Assay/Study
    """
    
    def __init__(self, config=None):
        """Initialize relationship extractor."""
        from knowledge_graph.config import config as default_config
        
        self.config = config or default_config
        
        # Load spaCy model with dependency parser
        logger.info("Loading spaCy model for dependency parsing...")
        self.nlp = spacy.load("en_core_web_sm")
        
        # Define relationship patterns
        self._initialize_patterns()
        
        logger.info("RelationshipExtractor initialized")
    
    def _initialize_patterns(self):
        """Initialize dependency patterns and trigger words for each relation type."""
        
        # UPREGULATES patterns
        self.upregulation_triggers = {
            'increase', 'increases', 'increased', 'increasing', 'upregulate', 'upregulates',
            'upregulated', 'upregulation', 'enhance', 'enhances', 'enhanced', 'activate',
            'activates', 'activated', 'activation', 'induce', 'induces', 'induced', 'induction',
            'stimulate', 'stimulates', 'stimulated', 'stimulation', 'promote', 'promotes',
            'promoted', 'elevation', 'elevated', 'overexpress', 'overexpressed', 'overexpression'
        }
        
        # DOWNREGULATES patterns
        self.downregulation_triggers = {
            'decrease', 'decreases', 'decreased', 'decreasing', 'downregulate', 'downregulates',
            'downregulated', 'downregulation', 'inhibit', 'inhibits', 'inhibited', 'inhibition',
            'suppress', 'suppresses', 'suppressed', 'suppression', 'reduce', 'reduces', 'reduced',
            'reduction', 'repress', 'represses', 'repressed', 'repression', 'attenuate',
            'attenuates', 'attenuated', 'attenuation', 'diminish', 'diminished'
        }
        
        # CAUSES patterns
        self.causation_triggers = {
            'cause', 'causes', 'caused', 'causing', 'lead', 'leads', 'led', 'leading',
            'result', 'results', 'resulted', 'resulting', 'induce', 'induces', 'induced',
            'produce', 'produces', 'produced', 'trigger', 'triggers', 'triggered'
        }
        
        # TREATS/PREVENTS patterns
        self.treatment_triggers = {
            'treat', 'treats', 'treated', 'treatment', 'prevent', 'prevents', 'prevented',
            'prevention', 'ameliorate', 'ameliorates', 'ameliorated', 'amelioration',
            'alleviate', 'alleviates', 'alleviated', 'alleviation', 'rescue', 'rescues',
            'rescued', 'protect', 'protects', 'protected', 'protection', 'countermeasure'
        }
        
        # INTERACTS_WITH patterns
        self.interaction_triggers = {
            'interact', 'interacts', 'interacted', 'interaction', 'bind', 'binds', 'bound',
            'binding', 'associate', 'associates', 'associated', 'association', 'complex',
            'partner', 'colocalize', 'colocalizes', 'colocalized'
        }
        
        # PART_OF patterns
        self.partof_triggers = {
            'part', 'component', 'member', 'element', 'region', 'domain', 'subunit',
            'contained', 'within', 'localized', 'located'
        }
        
        # Negation patterns
        self.negation_words = {
            'not', 'no', 'neither', 'nor', 'never', 'none', 'without', 'lack', 'absent',
            'unlikely', 'fail', 'failed', 'unable', 'cannot', 'did not', "didn't", 'unaffected'
        }
        
        # Space biology specific patterns
        self.spaceflight_patterns = [
            # Microgravity effects
            (r'(microgravity|spaceflight)\s+(?:induce[sd]?|cause[sd]?|lead[sd]? to)\s+(.+?)\s+(loss|atrophy|dysfunction)',
             'CAUSES', 'stressor', 'phenotype'),
            
            # Radiation effects
            (r'(radiation|cosmic rays)\s+(?:induce[sd]?|cause[sd]?)\s+(.+?)\s+(damage|mutation|apoptosis)',
             'CAUSES', 'stressor', 'phenotype'),
            
            # Gene expression changes
            (r'(.+?)\s+(?:gene|protein|mRNA)\s+(?:expression\s+)?(?:was|were)\s+(increased|decreased|upregulated|downregulated)',
             'REGULATES', 'entity', 'entity'),
            
            # Intervention effects
            (r'(.+?)\s+(?:exercise|training|diet|drug)\s+(?:prevent[sd]?|ameliorate[sd]?|reduce[sd]?)\s+(.+?)',
             'TREATS', 'intervention', 'phenotype'),
        ]
    
    def extract_relationships(self, text: str, entities: List[Dict]) -> List[Dict]:
        """
        Extract relationships from text given a list of entities.
        
        Args:
            text: Input text
            entities: List of entities with 'text', 'type', 'start', 'end'
        
        Returns:
            List of relationships with source, target, type, evidence
        """
        if not entities:
            return []
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Extract relationships using multiple methods
        relationships = []
        
        # Method 1: Dependency parsing
        dep_relations = self._extract_dependency_relations(doc, entities)
        relationships.extend(dep_relations)
        
        # Method 2: Pattern matching
        pattern_relations = self._extract_pattern_relations(text, entities)
        relationships.extend(pattern_relations)
        
        # Method 3: Co-occurrence (for weak associations)
        cooccur_relations = self._extract_cooccurrence_relations(text, entities)
        relationships.extend(cooccur_relations)
        
        # Deduplicate and filter
        relationships = self._deduplicate_relationships(relationships)
        relationships = self._filter_negated_relationships(doc, relationships)
        
        return relationships
    
    def _extract_dependency_relations(self, doc: Doc, entities: List[Dict]) -> List[Dict]:
        """Extract relationships using dependency parsing."""
        relationships = []
        
        # Create entity lookup by token indices
        entity_map = self._map_entities_to_tokens(doc, entities)
        
        for token in doc:
            # Check if token is a relation trigger
            lemma = token.lemma_.lower()
            
            # Find subject and object entities
            subject = self._find_entity_in_subtree(token, entity_map, dep_type='nsubj')
            obj = self._find_entity_in_subtree(token, entity_map, dep_type='dobj')
            
            if not subject or not obj:
                continue
            
            # Determine relationship type
            rel_type = None
            confidence = 0.0
            
            if lemma in self.upregulation_triggers:
                rel_type = 'UPREGULATES'
                confidence = 0.85
            elif lemma in self.downregulation_triggers:
                rel_type = 'DOWNREGULATES'
                confidence = 0.85
            elif lemma in self.causation_triggers:
                rel_type = 'CAUSES'
                confidence = 0.80
            elif lemma in self.treatment_triggers:
                rel_type = 'TREATS'
                confidence = 0.80
            elif lemma in self.interaction_triggers:
                rel_type = 'INTERACTS_WITH'
                confidence = 0.75
            elif lemma in self.partof_triggers:
                rel_type = 'PART_OF'
                confidence = 0.70
            
            if rel_type:
                # Extract context (sentence)
                sentence = token.sent.text
                
                relationships.append({
                    'source': subject['text'],
                    'source_type': subject['type'],
                    'target': obj['text'],
                    'target_type': obj['type'],
                    'relation_type': rel_type,
                    'confidence': confidence,
                    'evidence': sentence,
                    'trigger_word': token.text,
                    'extraction_method': 'dependency_parsing'
                })
        
        return relationships
    
    def _extract_pattern_relations(self, text: str, entities: List[Dict]) -> List[Dict]:
        """Extract relationships using regex patterns."""
        relationships = []
        
        for pattern, rel_type, source_type, target_type in self.spaceflight_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Extract matched groups
                groups = match.groups()
                if len(groups) >= 2:
                    source_text = groups[0].strip()
                    target_text = groups[1].strip() if len(groups) > 1 else groups[0].strip()
                    
                    # Find matching entities
                    source_entity = self._find_matching_entity(source_text, entities)
                    target_entity = self._find_matching_entity(target_text, entities)
                    
                    if source_entity and target_entity:
                        # Extract context
                        context_start = max(0, match.start() - 100)
                        context_end = min(len(text), match.end() + 100)
                        evidence = text[context_start:context_end]
                        
                        relationships.append({
                            'source': source_entity['text'],
                            'source_type': source_entity['type'],
                            'target': target_entity['text'],
                            'target_type': target_entity['type'],
                            'relation_type': rel_type,
                            'confidence': 0.75,
                            'evidence': evidence,
                            'trigger_word': match.group(0),
                            'extraction_method': 'pattern_matching'
                        })
        
        return relationships
    
    def _extract_cooccurrence_relations(self, text: str, entities: List[Dict]) -> List[Dict]:
        """
        Extract weak associations based on entity co-occurrence in sentences.
        Only for entities that appear together without explicit relation.
        """
        relationships = []
        
        # Process with spaCy to get sentences
        doc = self.nlp(text)
        
        for sent in doc.sents:
            # Find entities in this sentence
            sent_entities = [
                e for e in entities
                if e['start'] >= sent.start_char and e['end'] <= sent.end_char
            ]
            
            # Create co-occurrence relationships for entities in same sentence
            for i, entity1 in enumerate(sent_entities):
                for entity2 in sent_entities[i+1:]:
                    # Only create ASSOCIATED_WITH for different entity types
                    if entity1['type'] != entity2['type']:
                        relationships.append({
                            'source': entity1['text'],
                            'source_type': entity1['type'],
                            'target': entity2['text'],
                            'target_type': entity2['type'],
                            'relation_type': 'ASSOCIATED_WITH',
                            'confidence': 0.50,  # Low confidence for co-occurrence
                            'evidence': sent.text,
                            'trigger_word': 'co-occurrence',
                            'extraction_method': 'co-occurrence'
                        })
        
        return relationships
    
    def _map_entities_to_tokens(self, doc: Doc, entities: List[Dict]) -> Dict[int, Dict]:
        """Map entities to their token indices."""
        entity_map = {}
        
        for entity in entities:
            # Find tokens that overlap with entity span
            for token in doc:
                if (token.idx >= entity['start'] and 
                    token.idx < entity['end']):
                    entity_map[token.i] = entity
        
        return entity_map
    
    def _find_entity_in_subtree(self, token: Token, entity_map: Dict, dep_type: str) -> Dict:
        """Find entity in token's dependency subtree."""
        # Check direct children
        for child in token.children:
            if child.dep_ == dep_type and child.i in entity_map:
                return entity_map[child.i]
            
            # Check grandchildren
            for grandchild in child.children:
                if grandchild.i in entity_map:
                    return entity_map[grandchild.i]
        
        return None
    
    def _find_matching_entity(self, text: str, entities: List[Dict]) -> Dict:
        """Find entity that matches or contains the text."""
        text_lower = text.lower()
        
        for entity in entities:
            entity_text_lower = entity['text'].lower()
            
            # Exact match
            if entity_text_lower == text_lower:
                return entity
            
            # Containment match
            if text_lower in entity_text_lower or entity_text_lower in text_lower:
                return entity
        
        return None
    
    def _deduplicate_relationships(self, relationships: List[Dict]) -> List[Dict]:
        """Remove duplicate relationships, keeping highest confidence."""
        unique_rels = {}
        
        for rel in relationships:
            # Create key from source, target, and type
            key = (
                rel['source'].lower(),
                rel['target'].lower(),
                rel['relation_type']
            )
            
            # Keep highest confidence version
            if key not in unique_rels or rel['confidence'] > unique_rels[key]['confidence']:
                unique_rels[key] = rel
        
        return list(unique_rels.values())
    
    def _filter_negated_relationships(self, doc: Doc, relationships: List[Dict]) -> List[Dict]:
        """Filter out relationships that appear in negated context."""
        filtered = []
        
        for rel in relationships:
            # Check if trigger word appears with negation
            is_negated = False
            
            for token in doc:
                if token.text.lower() == rel['trigger_word'].lower():
                    # Check for negation in dependencies
                    for child in token.children:
                        if child.dep_ == 'neg':
                            is_negated = True
                            break
                    
                    # Check for negation words nearby
                    for i in range(max(0, token.i - 3), min(len(doc), token.i + 3)):
                        if doc[i].text.lower() in self.negation_words:
                            is_negated = True
                            break
                    
                    break
            
            if not is_negated:
                filtered.append(rel)
            else:
                logger.debug(f"Filtered negated relationship: {rel['source']} -> {rel['target']}")
        
        return filtered
    
    def extract_from_papers_batch(self, papers: List[Dict]) -> List[Dict]:
        """
        Extract relationships from a batch of papers.
        
        Args:
            papers: List of papers with 'pmid', 'title', 'abstract', 'entities'
        
        Returns:
            List of relationships with paper metadata
        """
        all_relationships = []
        
        for i, paper in enumerate(papers):
            if (i + 1) % 100 == 0:
                logger.info(f"Extracting relationships from paper {i+1}/{len(papers)}")
            
            try:
                # Extract from title and abstract
                text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
                entities = paper.get('entities', [])
                
                if not entities:
                    continue
                
                # Extract relationships
                relationships = self.extract_relationships(text, entities)
                
                # Add paper metadata
                for rel in relationships:
                    rel['pmid'] = paper.get('pmid')
                    rel['doi'] = paper.get('doi')
                    rel['publication_year'] = paper.get('publication_year')
                    rel['paper_title'] = paper.get('title')
                
                all_relationships.extend(relationships)
                
            except Exception as e:
                logger.error(f"Error extracting relationships from paper {paper.get('pmid')}: {e}")
                continue
        
        logger.info(f"Extracted {len(all_relationships)} relationships from {len(papers)} papers")
        return all_relationships
    
    def aggregate_relationships(self, relationships: List[Dict]) -> Dict[Tuple, Dict]:
        """
        Aggregate relationships across multiple papers.
        
        Returns:
            Dictionary mapping (source, target, type) -> aggregated info
        """
        aggregated = defaultdict(lambda: {
            'count': 0,
            'confidence_scores': [],
            'pmids': set(),
            'evidence_sentences': [],
            'extraction_methods': set()
        })
        
        for rel in relationships:
            key = (
                rel['source'].lower(),
                rel['target'].lower(),
                rel['relation_type']
            )
            
            agg = aggregated[key]
            agg['count'] += 1
            agg['confidence_scores'].append(rel['confidence'])
            agg['pmids'].add(rel.get('pmid'))
            agg['evidence_sentences'].append(rel['evidence'])
            agg['extraction_methods'].add(rel['extraction_method'])
            
            # Keep first instance details
            if agg['count'] == 1:
                agg['source'] = rel['source']
                agg['source_type'] = rel['source_type']
                agg['target'] = rel['target']
                agg['target_type'] = rel['target_type']
                agg['relation_type'] = rel['relation_type']
        
        # Calculate aggregate confidence
        for key, agg in aggregated.items():
            agg['pmids'] = list(agg['pmids'])
            agg['extraction_methods'] = list(agg['extraction_methods'])
            agg['avg_confidence'] = sum(agg['confidence_scores']) / len(agg['confidence_scores'])
            
            # Boost confidence based on multiple papers
            paper_boost = min(0.2, agg['count'] * 0.02)  # Max +0.2 for 10+ papers
            agg['final_confidence'] = min(0.99, agg['avg_confidence'] + paper_boost)
            
            # Keep only top 5 evidence sentences
            agg['evidence_sentences'] = agg['evidence_sentences'][:5]
        
        return dict(aggregated)
    
    def get_relationship_statistics(self, relationships: List[Dict]) -> Dict:
        """Get statistics about extracted relationships."""
        stats = {
            'total_relationships': len(relationships),
            'by_type': defaultdict(int),
            'by_method': defaultdict(int),
            'by_confidence': {'high': 0, 'medium': 0, 'low': 0},
            'avg_confidence': 0.0
        }
        
        confidence_sum = 0.0
        
        for rel in relationships:
            stats['by_type'][rel['relation_type']] += 1
            stats['by_method'][rel['extraction_method']] += 1
            
            conf = rel['confidence']
            confidence_sum += conf
            
            if conf >= 0.80:
                stats['by_confidence']['high'] += 1
            elif conf >= 0.60:
                stats['by_confidence']['medium'] += 1
            else:
                stats['by_confidence']['low'] += 1
        
        if relationships:
            stats['avg_confidence'] = confidence_sum / len(relationships)
        
        # Convert defaultdicts to regular dicts
        stats['by_type'] = dict(stats['by_type'])
        stats['by_method'] = dict(stats['by_method'])
        
        return stats


if __name__ == '__main__':
    # Test relationship extraction
    logging.basicConfig(level=logging.INFO)
    
    extractor = RelationshipExtractor()
    
    # Test text
    text = """
    Spaceflight induces muscle atrophy in astronauts. Microgravity causes upregulation of
    atrogin-1 gene expression, leading to increased protein degradation. Exercise countermeasures
    can prevent bone loss and muscle atrophy during long-duration missions. The IGF-1 protein
    interacts with PI3K to activate the mTOR pathway, which regulates muscle protein synthesis.
    """
    
    # Test entities
    entities = [
        {'text': 'Spaceflight', 'type': 'STRESSOR', 'start': 0, 'end': 11},
        {'text': 'muscle atrophy', 'type': 'PHENOTYPE', 'start': 20, 'end': 34},
        {'text': 'Microgravity', 'type': 'STRESSOR', 'start': 50, 'end': 62},
        {'text': 'atrogin-1', 'type': 'GENE', 'start': 92, 'end': 101},
        {'text': 'Exercise', 'type': 'INTERVENTION', 'start': 168, 'end': 176},
        {'text': 'bone loss', 'type': 'PHENOTYPE', 'start': 207, 'end': 216},
        {'text': 'IGF-1', 'type': 'GENE', 'start': 263, 'end': 268},
        {'text': 'PI3K', 'type': 'GENE', 'start': 290, 'end': 294},
        {'text': 'mTOR', 'type': 'GENE', 'start': 310, 'end': 314}
    ]
    
    # Extract relationships
    relationships = extractor.extract_relationships(text, entities)
    
    print(f"\nExtracted {len(relationships)} relationships:")
    for rel in relationships:
        print(f"  {rel['source']} --[{rel['relation_type']}]--> {rel['target']}")
        print(f"    Confidence: {rel['confidence']:.2f}, Method: {rel['extraction_method']}")
        print(f"    Evidence: {rel['evidence'][:100]}...")
        print()
    
    # Get statistics
    stats = extractor.get_relationship_statistics(relationships)
    print("\nRelationship Statistics:")
    print(f"  Total: {stats['total_relationships']}")
    print(f"  By type: {stats['by_type']}")
    print(f"  By method: {stats['by_method']}")
# Pillar 1: Knowledge Foundation - Detailed Design

## Overview

The Knowledge Foundation is the semantic backbone of the Space Biology Knowledge Engine. It transforms unstructured scientific literature into a structured, queryable knowledge graph that captures entities (genes, proteins, organisms, stressors) and their complex relationships.

## 1. Knowledge Graph Schema

### 1.1 Entity Types (Nodes)

#### Gene
```cypher
CREATE (g:Gene {
  id: String,              // HGNC ID (primary)
  symbol: String,          // e.g., "MYOD1"
  name: String,            // Full name
  aliases: [String],       // Alternative symbols
  ncbi_gene_id: String,    // NCBI Gene ID
  organism_id: String,     // FK to Organism
  chromosome: String,      // Chromosomal location
  description: String,
  created_at: DateTime,
  updated_at: DateTime
})
CREATE INDEX FOR (g:Gene) ON (g.id)
CREATE INDEX FOR (g:Gene) ON (g.symbol)
CREATE INDEX FOR (g:Gene) ON (g.organism_id)
```

#### Protein
```cypher
CREATE (p:Protein {
  id: String,              // UniProt ID (primary)
  name: String,
  gene_id: String,         // FK to Gene
  sequence: String,        // Amino acid sequence
  mass: Float,             // Molecular weight
  function: String,
  subcellular_location: [String],
  created_at: DateTime,
  updated_at: DateTime
})
CREATE INDEX FOR (p:Protein) ON (p.id)
CREATE INDEX FOR (p:Protein) ON (p.gene_id)
```

#### Organism
```cypher
CREATE (o:Organism {
  id: String,              // NCBI Taxon ID (primary)
  scientific_name: String, // e.g., "Mus musculus"
  common_name: String,     // e.g., "mouse"
  taxonomy: {              // Hierarchical classification
    kingdom: String,
    phylum: String,
    class: String,
    order: String,
    family: String,
    genus: String,
    species: String
  },
  model_organism: Boolean,
  created_at: DateTime
})
CREATE INDEX FOR (o:Organism) ON (o.id)
CREATE INDEX FOR (o:Organism) ON (o.scientific_name)
```

#### Stressor
```cypher
CREATE (s:Stressor {
  id: String,              // Custom ID
  type: String,            // ENUM: microgravity, radiation, isolation, etc.
  name: String,            // e.g., "Simulated microgravity"
  description: String,
  parameters: {            // Type-specific parameters
    duration: String,
    intensity: String,
    // For microgravity: clinostat speed, RPM
    // For radiation: dose, particle type
  },
  ground_analog: Boolean,  // True if ground-based simulation
  created_at: DateTime
})
CREATE INDEX FOR (s:Stressor) ON (s.id)
CREATE INDEX FOR (s:Stressor) ON (s.type)
```

#### BiologicalProcess (GO Term)
```cypher
CREATE (bp:BiologicalProcess {
  id: String,              // GO ID (e.g., "GO:0008150")
  name: String,
  definition: String,
  synonyms: [String],
  is_obsolete: Boolean,
  created_at: DateTime
})
CREATE INDEX FOR (bp:BiologicalProcess) ON (bp.id)
```

#### CellularComponent (GO Term)
```cypher
CREATE (cc:CellularComponent {
  id: String,              // GO ID (e.g., "GO:0005575")
  name: String,
  definition: String,
  synonyms: [String],
  is_obsolete: Boolean,
  created_at: DateTime
})
CREATE INDEX FOR (cc:CellularComponent) ON (cc.id)
```

#### MolecularFunction (GO Term)
```cypher
CREATE (mf:MolecularFunction {
  id: String,              // GO ID (e.g., "GO:0003674")
  name: String,
  definition: String,
  synonyms: [String],
  is_obsolete: Boolean,
  created_at: DateTime
})
CREATE INDEX FOR (mf:MolecularFunction) ON (mf.id)
```

#### Phenotype
```cypher
CREATE (ph:Phenotype {
  id: String,              // HPO ID (e.g., "HP:0000118")
  name: String,            // e.g., "Muscle atrophy"
  definition: String,
  synonyms: [String],
  affected_system: String, // e.g., "musculoskeletal"
  created_at: DateTime
})
CREATE INDEX FOR (ph:Phenotype) ON (ph.id)
```

#### Experiment
```cypher
CREATE (e:Experiment {
  id: String,              // Custom ID
  name: String,
  platform: String,        // ISS, Shuttle, ground-based
  module: String,          // e.g., "Columbus", "Destiny"
  mission: String,         // e.g., "ISS Expedition 45"
  start_date: Date,
  end_date: Date,
  duration_days: Integer,
  sample_type: [String],   // tissue, cell culture, etc.
  experimental_conditions: {
    temperature: String,
    co2_level: String,
    humidity: String,
    custom: Map
  },
  genelab_id: String,      // Link to NASA GeneLab
  osdr_id: String,         // Link to OSDR
  created_at: DateTime
})
CREATE INDEX FOR (e:Experiment) ON (e.id)
CREATE INDEX FOR (e:Experiment) ON (e.genelab_id)
```

#### Publication
```cypher
CREATE (pub:Publication {
  id: String,              // PMID or DOI
  pmid: String,
  doi: String,
  title: String,
  abstract: String,
  authors: [String],
  journal: String,
  publication_date: Date,
  keywords: [String],
  mesh_terms: [String],
  full_text_available: Boolean,
  open_access: Boolean,
  citation_count: Integer,
  embedding_vector: [Float], // Stored in vector DB, reference here
  created_at: DateTime,
  last_processed: DateTime
})
CREATE INDEX FOR (pub:Publication) ON (pub.id)
CREATE INDEX FOR (pub:Publication) ON (pub.pmid)
CREATE INDEX FOR (pub:Publication) ON (pub.doi)
CREATE FULLTEXT INDEX publicationFulltext FOR (pub:Publication) ON (pub.title, pub.abstract)
```

### 1.2 Relationship Types (Edges)

#### EXPRESSES
```cypher
CREATE (organism:Organism)-[:EXPRESSES {
  tissue: String,          // Where expression occurs
  developmental_stage: String,
  baseline_expression: Float,
  evidence: String,        // EBI Expression Atlas, etc.
  confidence: Float,       // 0-1
  source_id: String        // FK to Publication
}]->(gene:Gene)
```

#### CODES_FOR
```cypher
CREATE (gene:Gene)-[:CODES_FOR {
  transcript_variant: String,
  evidence: String,
  confidence: Float,
  source_id: String
}]->(protein:Protein)
```

#### PARTICIPATES_IN
```cypher
CREATE (protein:Protein)-[:PARTICIPATES_IN {
  role: String,            // e.g., "catalyst", "regulator"
  evidence_code: String,   // GO evidence codes (IDA, IMP, etc.)
  evidence: String,
  confidence: Float,
  source_id: String
}]->(process:BiologicalProcess)
```

#### LOCATED_IN
```cypher
CREATE (protein:Protein)-[:LOCATED_IN {
  evidence_code: String,
  evidence: String,
  confidence: Float,
  source_id: String
}]->(component:CellularComponent)
```

#### HAS_FUNCTION
```cypher
CREATE (protein:Protein)-[:HAS_FUNCTION {
  evidence_code: String,
  evidence: String,
  confidence: Float,
  source_id: String
}]->(function:MolecularFunction)
```

#### AFFECTED_BY
```cypher
CREATE (entity)-[:AFFECTED_BY {
  effect_type: String,     // ENUM: upregulation, downregulation, activation, inhibition
  magnitude: Float,        // Fold change or effect size
  p_value: Float,
  timepoint: String,       // When effect was measured
  tissue: String,          // Where effect was observed
  experimental_conditions: Map,
  evidence: String,
  confidence: Float,
  source_id: String
}]->(stressor:Stressor)
```

#### CAUSES
```cypher
CREATE (stressor:Stressor)-[:CAUSES {
  mechanism: String,       // Biological mechanism if known
  severity: String,        // mild, moderate, severe
  onset_time: String,      // How quickly phenotype appears
  reversibility: Boolean,
  evidence: String,
  confidence: Float,
  source_id: String
}]->(phenotype:Phenotype)
```

#### INTERACTS_WITH
```cypher
CREATE (protein1:Protein)-[:INTERACTS_WITH {
  interaction_type: String, // physical, genetic, regulatory
  detection_method: String, // e.g., "yeast two-hybrid"
  interaction_score: Float, // e.g., STRING score
  evidence: String,
  confidence: Float,
  source_id: String
}]->(protein2:Protein)
```

#### STUDIED_IN
```cypher
CREATE (entity)-[:STUDIED_IN {
  primary_focus: Boolean,  // Is this entity the main subject?
  outcome_measured: [String],
  created_at: DateTime
}]->(experiment:Experiment)
```

#### REPORTED_IN
```cypher
CREATE (entity)-[:REPORTED_IN {
  context: String,         // Context in which entity appears
  sentence: String,        // Exact sentence from publication
  section: String,         // abstract, methods, results, etc.
  extraction_method: String, // NER model used
  extraction_confidence: Float,
  created_at: DateTime
}]->(publication:Publication)
```

#### CITES
```cypher
CREATE (pub1:Publication)-[:CITES]->(pub2:Publication)
```

## 2. Data Ingestion Pipeline

### 2.1 Architecture

```
┌──────────────────────────────────────────────────────────────┐
│                     DATA SOURCES                              │
├──────────────────────────────────────────────────────────────┤
│  PubMed  │  PMC  │  NASA GeneLab  │  OSDR  │  Custom PDFs   │
└────┬──────────────────────────────────────────────────────┬───┘
     │                                                       │
     ▼                                                       ▼
┌─────────────────┐                              ┌──────────────────┐
│  Acquisition    │                              │  Manual Upload   │
│  Scheduler      │                              │  Interface       │
│  (Airflow DAG)  │                              └──────────────────┘
└────┬────────────┘                                        │
     │                                                     │
     └──────────────────┬──────────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │  Raw Data Store  │
              │  (S3/Blob)       │
              └────┬─────────────┘
                   │
                   ▼
              ┌──────────────────┐
              │  Preprocessing   │
              │  - PDF to text   │
              │  - Metadata norm │
              │  - Deduplication │
              └────┬─────────────┘
                   │
                   ▼
              ┌──────────────────┐
              │  NLP Pipeline    │
              │  - Sentence seg  │
              │  - Tokenization  │
              │  - NER           │
              │  - Relation Ext  │
              └────┬─────────────┘
                   │
                   ▼
              ┌──────────────────┐
              │  Entity          │
              │  Resolution      │
              │  - Linking       │
              │  - Deduplication │
              │  - Validation    │
              └────┬─────────────┘
                   │
                   ├──────────────────┐
                   │                  │
                   ▼                  ▼
          ┌──────────────┐   ┌──────────────┐
          │  Neo4j KG    │   │  Vector DB   │
          │  Update      │   │  (Embeddings)│
          └──────────────┘   └──────────────┘
                   │
                   ▼
          ┌──────────────┐
          │ Elasticsearch│
          │  Index       │
          └──────────────┘
```

### 2.2 PubMed Ingestion

```python
# scripts/ingest_pubmed.py

from Bio import Entrez
from datetime import datetime, timedelta
import time

class PubMedIngester:
    def __init__(self, email: str, api_key: str):
        Entrez.email = email
        Entrez.api_key = api_key
        
    def fetch_space_biology_papers(self, start_date: str, end_date: str):
        """
        Fetch papers related to space biology from PubMed.
        """
        query = (
            '("space biology"[Title/Abstract] OR '
            '"spaceflight"[Title/Abstract] OR '
            '"microgravity"[Title/Abstract] OR '
            '"space radiation"[Title/Abstract] OR '
            '"International Space Station"[Title/Abstract]) '
            f'AND ("{start_date}"[Date - Publication] : "{end_date}"[Date - Publication])'
        )
        
        # Search for papers
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=10000,
            sort="pub_date"
        )
        record = Entrez.read(handle)
        pmids = record["IdList"]
        
        # Fetch details in batches
        papers = []
        batch_size = 200
        for i in range(0, len(pmids), batch_size):
            batch_pmids = pmids[i:i+batch_size]
            papers.extend(self._fetch_paper_details(batch_pmids))
            time.sleep(0.5)  # Rate limiting
            
        return papers
    
    def _fetch_paper_details(self, pmids: list):
        """Fetch full details for a list of PMIDs."""
        handle = Entrez.efetch(
            db="pubmed",
            id=",".join(pmids),
            rettype="xml"
        )
        records = Entrez.read(handle)
        
        papers = []
        for article in records['PubmedArticle']:
            paper = self._parse_pubmed_article(article)
            papers.append(paper)
        
        return papers
    
    def _parse_pubmed_article(self, article):
        """Extract relevant fields from PubMed article."""
        medline = article['MedlineCitation']
        article_data = medline['Article']
        
        # Extract authors
        authors = []
        if 'AuthorList' in article_data:
            for author in article_data['AuthorList']:
                if 'LastName' in author and 'ForeName' in author:
                    authors.append(f"{author['ForeName']} {author['LastName']}")
        
        # Extract abstract
        abstract = ""
        if 'Abstract' in article_data and 'AbstractText' in article_data['Abstract']:
            abstract = " ".join([str(text) for text in article_data['Abstract']['AbstractText']])
        
        # Extract MeSH terms
        mesh_terms = []
        if 'MeshHeadingList' in medline:
            mesh_terms = [mesh['DescriptorName'].title() for mesh in medline['MeshHeadingList']]
        
        paper = {
            'pmid': str(medline['PMID']),
            'title': article_data.get('ArticleTitle', ''),
            'abstract': abstract,
            'authors': authors,
            'journal': article_data.get('Journal', {}).get('Title', ''),
            'publication_date': self._extract_publication_date(article_data),
            'mesh_terms': mesh_terms,
            'keywords': self._extract_keywords(medline)
        }
        
        return paper
    
    def _extract_publication_date(self, article_data):
        """Extract and format publication date."""
        if 'ArticleDate' in article_data and len(article_data['ArticleDate']) > 0:
            date = article_data['ArticleDate'][0]
            return f"{date['Year']}-{date['Month'].zfill(2)}-{date['Day'].zfill(2)}"
        elif 'Journal' in article_data and 'JournalIssue' in article_data['Journal']:
            pub_date = article_data['Journal']['JournalIssue'].get('PubDate', {})
            year = pub_date.get('Year', '2000')
            month = pub_date.get('Month', '01')
            return f"{year}-{month}-01"
        return None
    
    def _extract_keywords(self, medline):
        """Extract author keywords."""
        keywords = []
        if 'KeywordList' in medline:
            for keyword_list in medline['KeywordList']:
                keywords.extend([str(k) for k in keyword_list])
        return keywords
```

### 2.3 Named Entity Recognition (NER)

```python
# backend/knowledge_graph/ner.py

import spacy
from transformers import AutoTokenizer, AutoModelForTokenClassification, pipeline
from typing import List, Dict

class BiomedicalNER:
    def __init__(self):
        # Load SciBERT fine-tuned on BC5CDR for disease/chemical NER
        self.bc5cdr_model = pipeline(
            "ner",
            model="dmis-lab/biobert-v1.1",
            tokenizer="dmis-lab/biobert-v1.1",
            aggregation_strategy="simple"
        )
        
        # Load SciSpacy for additional entity types
        self.scispacy_model = spacy.load("en_ner_bc5cdr_md")
        
        # Custom model for space biology specific entities (train this)
        # self.space_bio_model = load_custom_space_biology_model()
        
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract biomedical entities from text.
        Returns list of entity dictionaries with type, text, start, end, confidence.
        """
        entities = []
        
        # Extract genes/proteins with BioBERT
        biobert_entities = self._extract_biobert(text)
        entities.extend(biobert_entities)
        
        # Extract additional entities with SciSpacy
        scispacy_entities = self._extract_scispacy(text)
        entities.extend(scispacy_entities)
        
        # Deduplicate entities (keep highest confidence for overlaps)
        entities = self._deduplicate_entities(entities)
        
        return entities
    
    def _extract_biobert(self, text: str) -> List[Dict]:
        """Extract entities using BioBERT."""
        results = self.bc5cdr_model(text)
        
        entities = []
        for entity in results:
            entities.append({
                'type': self._map_biobert_label(entity['entity_group']),
                'text': entity['word'],
                'start': entity['start'],
                'end': entity['end'],
                'confidence': entity['score']
            })
        
        return entities
    
    def _extract_scispacy(self, text: str) -> List[Dict]:
        """Extract entities using SciSpacy."""
        doc = self.scispacy_model(text)
        
        entities = []
        for ent in doc.ents:
            entities.append({
                'type': ent.label_,
                'text': ent.text,
                'start': ent.start_char,
                'end': ent.end_char,
                'confidence': 0.85  # SciSpacy doesn't provide confidence scores
            })
        
        return entities
    
    def _map_biobert_label(self, label: str) -> str:
        """Map BioBERT labels to our schema."""
        mapping = {
            'GENE': 'Gene',
            'PROTEIN': 'Protein',
            'DISEASE': 'Phenotype',
            'CHEMICAL': 'Chemical',
            'CELL_LINE': 'CellLine',
            'CELL_TYPE': 'CellType',
            'SPECIES': 'Organism'
        }
        return mapping.get(label, label)
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Remove overlapping entities, keeping the one with highest confidence.
        """
        # Sort by start position and confidence
        entities = sorted(entities, key=lambda x: (x['start'], -x['confidence']))
        
        deduplicated = []
        last_end = -1
        
        for entity in entities:
            # If entity doesn't overlap with previous, keep it
            if entity['start'] >= last_end:
                deduplicated.append(entity)
                last_end = entity['end']
        
        return deduplicated

# Example usage
ner = BiomedicalNER()
text = """Exposure to microgravity resulted in significant upregulation of ATROGIN-1 
(FBXO32) and MuRF1 (TRIM63) in skeletal muscle tissue of mice."""

entities = ner.extract_entities(text)
# Output:
# [
#   {'type': 'Gene', 'text': 'ATROGIN-1', 'start': 65, 'end': 74, 'confidence': 0.95},
#   {'type': 'Gene', 'text': 'FBXO32', 'start': 76, 'end': 82, 'confidence': 0.93},
#   {'type': 'Gene', 'text': 'MuRF1', 'start': 88, 'end': 93, 'confidence': 0.94},
#   {'type': 'Gene', 'text': 'TRIM63', 'start': 95, 'end': 101, 'confidence': 0.92},
#   {'type': 'Organism', 'text': 'mice', 'start': 133, 'end': 137, 'confidence': 0.98}
# ]
```

### 2.4 Relation Extraction

```python
# backend/knowledge_graph/relation_extraction.py

import spacy
from typing import List, Dict, Tuple
import re

class RelationExtractor:
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        
        # Define relation patterns
        self.relation_patterns = {
            'UPREGULATES': [
                r'upregulat\w*',
                r'increas\w*',
                r'activat\w*',
                r'induc\w*',
                r'stimulat\w*'
            ],
            'DOWNREGULATES': [
                r'downregulat\w*',
                r'decreas\w*',
                r'inhibit\w*',
                r'suppress\w*',
                r'reduc\w*'
            ],
            'INTERACTS_WITH': [
                r'interact\w*',
                r'bind\w*',
                r'associate\w*',
                r'complex\w*'
            ],
            'CAUSES': [
                r'caus\w*',
                r'result\w* in',
                r'lead\w* to',
                r'induc\w*'
            ]
        }
        
    def extract_relations(self, text: str, entities: List[Dict]) -> List[Dict]:
        """
        Extract relationships between entities in text.
        """
        doc = self.nlp(text)
        relations = []
        
        # Create entity index
        entity_index = self._index_entities(entities, doc)
        
        # Extract relations using dependency parsing
        dependency_relations = self._extract_dependency_relations(doc, entity_index)
        relations.extend(dependency_relations)
        
        # Extract relations using pattern matching
        pattern_relations = self._extract_pattern_relations(doc, entity_index)
        relations.extend(pattern_relations)
        
        return relations
    
    def _index_entities(self, entities: List[Dict], doc) -> Dict:
        """Create an index of entities by token position."""
        entity_index = {}
        for entity in entities:
            # Find token span for entity
            for token in doc:
                if token.idx >= entity['start'] and token.idx < entity['end']:
                    entity_index[token.i] = entity
        return entity_index
    
    def _extract_dependency_relations(self, doc, entity_index: Dict) -> List[Dict]:
        """Extract relations using dependency parse trees."""
        relations = []
        
        for token in doc:
            # Check if token is a relation trigger word
            relation_type = self._identify_relation_type(token.lemma_)
            
            if relation_type:
                # Find subject and object entities
                subject = self._find_subject(token, entity_index)
                obj = self._find_object(token, entity_index)
                
                if subject and obj:
                    relations.append({
                        'type': relation_type,
                        'subject': subject,
                        'object': obj,
                        'trigger': token.text,
                        'confidence': 0.75,  # Rule-based confidence
                        'sentence': token.sent.text
                    })
        
        return relations
    
    def _identify_relation_type(self, lemma: str) -> str:
        """Identify relation type from trigger word."""
        for rel_type, patterns in self.relation_patterns.items():
            for pattern in patterns:
                if re.match(pattern, lemma, re.IGNORECASE):
                    return rel_type
        return None
    
    def _find_subject(self, token, entity_index: Dict):
        """Find subject entity for a relation trigger."""
        # Look for nominal subject
        for child in token.children:
            if child.dep_ in ['nsubj', 'nsubjpass']:
                # Check if child or its children are entities
                for t in [child] + list(child.subtree):
                    if t.i in entity_index:
                        return entity_index[t.i]
        return None
    
    def _find_object(self, token, entity_index: Dict):
        """Find object entity for a relation trigger."""
        # Look for direct object or prepositional object
        for child in token.children:
            if child.dep_ in ['dobj', 'pobj', 'attr']:
                for t in [child] + list(child.subtree):
                    if t.i in entity_index:
                        return entity_index[t.i]
        return None
    
    def _extract_pattern_relations(self, doc, entity_index: Dict) -> List[Dict]:
        """Extract relations using regex patterns."""
        relations = []
        text = doc.text
        
        # Pattern: Entity1 TRIGGER Entity2
        # Example: "MYOD1 upregulates FBXO32"
        
        # Get sorted list of entities
        entities = sorted(entity_index.values(), key=lambda x: x['start'])
        
        # Check each pair of entities
        for i, ent1 in enumerate(entities):
            for ent2 in entities[i+1:]:
                # Get text between entities
                between_start = ent1['end']
                between_end = ent2['start']
                
                if between_end - between_start > 50:  # Skip if too far apart
                    continue
                
                between_text = text[between_start:between_end]
                
                # Check for relation trigger words
                relation_type = None
                for rel_type, patterns in self.relation_patterns.items():
                    for pattern in patterns:
                        if re.search(pattern, between_text, re.IGNORECASE):
                            relation_type = rel_type
                            break
                    if relation_type:
                        break
                
                if relation_type:
                    relations.append({
                        'type': relation_type,
                        'subject': ent1,
                        'object': ent2,
                        'confidence': 0.70,
                        'sentence': between_text
                    })
        
        return relations
```

### 2.5 Entity Resolution & Linking

```python
# backend/knowledge_graph/entity_resolution.py

from typing import List, Dict, Optional
import requests

class EntityResolver:
    """
    Resolve extracted entity mentions to canonical database identifiers.
    """
    
    def __init__(self):
        self.gene_cache = {}
        self.protein_cache = {}
        
    def resolve_gene(self, gene_text: str, organism: str = "human") -> Optional[Dict]:
        """
        Resolve gene mention to HGNC/NCBI Gene ID.
        """
        cache_key = f"{gene_text}_{organism}"
        if cache_key in self.gene_cache:
            return self.gene_cache[cache_key]
        
        # Query MyGene.info API
        url = "https://mygene.info/v3/query"
        params = {
            'q': gene_text,
            'species': organism,
            'fields': 'symbol,name,HGNC,entrezgene,ensembl.gene',
            'size': 1
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('hits') and len(data['hits']) > 0:
                hit = data['hits'][0]
                resolved = {
                    'id': str(hit.get('entrezgene', '')),
                    'symbol': hit.get('symbol', ''),
                    'name': hit.get('name', ''),
                    'hgnc_id': hit.get('HGNC', ''),
                    'confidence': hit.get('_score', 0) / 100.0
                }
                self.gene_cache[cache_key] = resolved
                return resolved
        
        return None
    
    def resolve_protein(self, protein_text: str) -> Optional[Dict]:
        """
        Resolve protein mention to UniProt ID.
        """
        if protein_text in self.protein_cache:
            return self.protein_cache[protein_text]
        
        # Query UniProt API
        url = "https://rest.uniprot.org/uniprotkb/search"
        params = {
            'query': protein_text,
            'format': 'json',
            'size': 1
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('results') and len(data['results']) > 0:
                result = data['results'][0]
                resolved = {
                    'id': result.get('primaryAccession', ''),
                    'name': result.get('proteinDescription', {}).get('recommendedName', {}).get('fullName', {}).get('value', ''),
                    'gene': result.get('genes', [{}])[0].get('geneName', {}).get('value', ''),
                    'organism': result.get('organism', {}).get('scientificName', '')
                }
                self.protein_cache[protein_text] = resolved
                return resolved
        
        return None
    
    def resolve_organism(self, organism_text: str) -> Optional[Dict]:
        """
        Resolve organism mention to NCBI Taxonomy ID.
        """
        # Query NCBI Taxonomy API
        url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
        params = {
            'db': 'taxonomy',
            'term': organism_text,
            'retmode': 'json'
        }
        
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            if data.get('esearchresult', {}).get('idlist'):
                tax_id = data['esearchresult']['idlist'][0]
                
                # Fetch details
                detail_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"
                detail_params = {
                    'db': 'taxonomy',
                    'id': tax_id,
                    'retmode': 'xml'
                }
                
                # Parse XML response (simplified)
                return {
                    'id': tax_id,
                    'scientific_name': organism_text
                }
        
        return None
```

## 3. Knowledge Graph Construction

### 3.1 Graph Builder

```python
# backend/knowledge_graph/graph_builder.py

from neo4j import GraphDatabase
from typing import List, Dict
import logging

class KnowledgeGraphBuilder:
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.logger = logging.getLogger(__name__)
    
    def close(self):
        self.driver.close()
    
    def create_publication_node(self, publication: Dict):
        """Create or update publication node."""
        with self.driver.session() as session:
            session.write_transaction(
                self._create_publication, publication
            )
    
    @staticmethod
    def _create_publication(tx, pub: Dict):
        query = """
        MERGE (p:Publication {id: $id})
        SET p.pmid = $pmid,
            p.doi = $doi,
            p.title = $title,
            p.abstract = $abstract,
            p.authors = $authors,
            p.journal = $journal,
            p.publication_date = date($publication_date),
            p.keywords = $keywords,
            p.mesh_terms = $mesh_terms,
            p.updated_at = datetime()
        """
        tx.run(query, **pub)
    
    def create_entity_node(self, entity: Dict):
        """Create or update entity node."""
        with self.driver.session() as session:
            session.write_transaction(
                self._create_entity, entity
            )
    
    @staticmethod
    def _create_entity(tx, entity: Dict):
        entity_type = entity['type']
        query = f"""
        MERGE (e:{entity_type} {{id: $id}})
        SET e += $properties,
            e.updated_at = datetime()
        """
        tx.run(query, id=entity['id'], properties=entity.get('properties', {}))
    
    def create_relationship(self, rel: Dict):
        """Create relationship between entities."""
        with self.driver.session() as session:
            session.write_transaction(
                self._create_relationship, rel
            )
    
    @staticmethod
    def _create_relationship(tx, rel: Dict):
        rel_type = rel['type']
        query = f"""
        MATCH (a {{id: $from_id}})
        MATCH (b {{id: $to_id}})
        MERGE (a)-[r:{rel_type}]->(b)
        SET r += $properties,
            r.updated_at = datetime()
        """
        tx.run(
            query,
            from_id=rel['from_id'],
            to_id=rel['to_id'],
            properties=rel.get('properties', {})
        )
    
    def link_entities_to_publication(self, pub_id: str, entity_ids: List[str]):
        """Create REPORTED_IN relationships."""
        with self.driver.session() as session:
            session.write_transaction(
                self._link_to_publication, pub_id, entity_ids
            )
    
    @staticmethod
    def _link_to_publication(tx, pub_id: str, entity_ids: List[str]):
        query = """
        MATCH (p:Publication {id: $pub_id})
        MATCH (e) WHERE e.id IN $entity_ids
        MERGE (e)-[r:REPORTED_IN]->(p)
        SET r.created_at = datetime()
        """
        tx.run(query, pub_id=pub_id, entity_ids=entity_ids)
```

### 3.2 Airflow DAG for Pipeline Orchestration

```python
# data_pipeline/dags/space_biology_ingestion.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
import sys
sys.path.append('/opt/airflow/scripts')

from ingest_pubmed import PubMedIngester
from ner import BiomedicalNER
from relation_extraction import RelationExtractor
from entity_resolution import EntityResolver
from graph_builder import KnowledgeGraphBuilder

default_args = {
    'owner': 'astrobiomers',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'space_biology_ingestion',
    default_args=default_args,
    description='Ingest and process space biology publications',
    schedule_interval=timedelta(days=1),  # Run daily
)

def fetch_new_publications(**context):
    """Fetch new publications from PubMed."""
    ingester = PubMedIngester(
        email=context['params']['email'],
        api_key=context['params']['api_key']
    )
    
    # Fetch papers from last 7 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    
    papers = ingester.fetch_space_biology_papers(
        start_date=start_date.strftime('%Y/%m/%d'),
        end_date=end_date.strftime('%Y/%m/%d')
    )
    
    # Save to XCom for next task
    context['task_instance'].xcom_push(key='papers', value=papers)
    return len(papers)

def extract_entities(**context):
    """Extract entities from fetched papers."""
    papers = context['task_instance'].xcom_pull(
        task_ids='fetch_publications',
        key='papers'
    )
    
    ner = BiomedicalNER()
    
    for paper in papers:
        # Extract from title and abstract
        text = f"{paper['title']} {paper['abstract']}"
        paper['entities'] = ner.extract_entities(text)
    
    context['task_instance'].xcom_push(key='papers_with_entities', value=papers)
    return len(papers)

def extract_relations(**context):
    """Extract relationships between entities."""
    papers = context['task_instance'].xcom_pull(
        task_ids='extract_entities',
        key='papers_with_entities'
    )
    
    rel_extractor = RelationExtractor()
    
    for paper in papers:
        text = f"{paper['title']} {paper['abstract']}"
        paper['relations'] = rel_extractor.extract_relations(
            text,
            paper['entities']
        )
    
    context['task_instance'].xcom_push(key='papers_with_relations', value=papers)
    return len(papers)

def resolve_entities(**context):
    """Resolve entities to canonical identifiers."""
    papers = context['task_instance'].xcom_pull(
        task_ids='extract_relations',
        key='papers_with_relations'
    )
    
    resolver = EntityResolver()
    
    for paper in papers:
        for entity in paper['entities']:
            if entity['type'] == 'Gene':
                resolved = resolver.resolve_gene(entity['text'])
                if resolved:
                    entity['resolved'] = resolved
            elif entity['type'] == 'Protein':
                resolved = resolver.resolve_protein(entity['text'])
                if resolved:
                    entity['resolved'] = resolved
    
    context['task_instance'].xcom_push(key='papers_resolved', value=papers)
    return len(papers)

def build_knowledge_graph(**context):
    """Add data to Neo4j knowledge graph."""
    papers = context['task_instance'].xcom_pull(
        task_ids='resolve_entities',
        key='papers_resolved'
    )
    
    kg_builder = KnowledgeGraphBuilder(
        uri=context['params']['neo4j_uri'],
        user=context['params']['neo4j_user'],
        password=context['params']['neo4j_password']
    )
    
    try:
        for paper in papers:
            # Create publication node
            kg_builder.create_publication_node(paper)
            
            # Create entity nodes
            entity_ids = []
            for entity in paper['entities']:
                if 'resolved' in entity:
                    kg_builder.create_entity_node(entity['resolved'])
                    entity_ids.append(entity['resolved']['id'])
            
            # Link entities to publication
            kg_builder.link_entities_to_publication(paper['pmid'], entity_ids)
            
            # Create relationship edges
            for relation in paper['relations']:
                if 'resolved' in relation['subject'] and 'resolved' in relation['object']:
                    kg_builder.create_relationship({
                        'type': relation['type'],
                        'from_id': relation['subject']['resolved']['id'],
                        'to_id': relation['object']['resolved']['id'],
                        'properties': {
                            'confidence': relation['confidence'],
                            'source_id': paper['pmid'],
                            'sentence': relation['sentence']
                        }
                    })
    finally:
        kg_builder.close()
    
    return len(papers)

# Define tasks
t1 = PythonOperator(
    task_id='fetch_publications',
    python_callable=fetch_new_publications,
    params={
        'email': '{{ var.value.pubmed_email }}',
        'api_key': '{{ var.value.pubmed_api_key }}'
    },
    dag=dag,
)

t2 = PythonOperator(
    task_id='extract_entities',
    python_callable=extract_entities,
    dag=dag,
)

t3 = PythonOperator(
    task_id='extract_relations',
    python_callable=extract_relations,
    dag=dag,
)

t4 = PythonOperator(
    task_id='resolve_entities',
    python_callable=resolve_entities,
    dag=dag,
)

t5 = PythonOperator(
    task_id='build_knowledge_graph',
    python_callable=build_knowledge_graph,
    params={
        'neo4j_uri': '{{ var.value.neo4j_uri }}',
        'neo4j_user': '{{ var.value.neo4j_user }}',
        'neo4j_password': '{{ var.value.neo4j_password }}'
    },
    dag=dag,
)

# Define task dependencies
t1 >> t2 >> t3 >> t4 >> t5
```

## 4. Query Examples

### 4.1 Cypher Queries

```cypher
-- Find all genes upregulated by microgravity in mice
MATCH (g:Gene)<-[r:AFFECTED_BY]-(s:Stressor {type: 'microgravity'}),
      (g)-[:EXPRESSES]-(o:Organism {common_name: 'mouse'})
WHERE r.effect_type = 'upregulation'
RETURN g.symbol, g.name, r.magnitude, r.source_id
ORDER BY r.magnitude DESC
LIMIT 20;

-- Find proteins that interact with MYOD1
MATCH (p1:Protein {name: 'MYOD1'})-[r:INTERACTS_WITH]-(p2:Protein)
RETURN p2.name, r.interaction_type, r.confidence
ORDER BY r.confidence DESC;

-- Find pathways affected by space radiation
MATCH (s:Stressor {type: 'radiation'})-[:CAUSES]->(ph:Phenotype),
      (p:Protein)-[:AFFECTED_BY]->(s),
      (p)-[:PARTICIPATES_IN]->(bp:BiologicalProcess)
RETURN DISTINCT bp.name, count(p) as affected_proteins
ORDER BY affected_proteins DESC
LIMIT 10;

-- Find most-studied entities
MATCH (e)-[r:REPORTED_IN]->(pub:Publication)
RETURN labels(e)[0] as entity_type, e.name, count(pub) as publication_count
ORDER BY publication_count DESC
LIMIT 50;

-- Find knowledge gaps (entities with few publications)
MATCH (e:Gene)
OPTIONAL MATCH (e)-[:REPORTED_IN]->(pub:Publication)
WITH e, count(pub) as pub_count
WHERE pub_count < 3
RETURN e.symbol, e.name, pub_count
ORDER BY pub_count ASC;
```

---

## Summary

Pillar 1 establishes the **Knowledge Foundation** through:
1. **Structured Schema**: Comprehensive entity and relationship types
2. **Automated Ingestion**: Scalable pipeline for continuous data acquisition
3. **NLP Processing**: State-of-art models for entity and relation extraction
4. **Entity Resolution**: Linking to canonical databases
5. **Graph Construction**: Neo4j-based knowledge graph with rich metadata

This foundation enables the subsequent pillars to provide intelligent querying, visualization, and collaborative features.

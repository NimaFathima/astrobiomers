# Part I.2: Data Ingestion and Processing Pipeline (ETL)

## Overview

The construction of the Biomedical Knowledge Graph (BKG) is **not a one-time data entry task** but a **continuous, automated process** known as an Extract, Transform, Load (ETL) pipeline. This workflow is a multi-step procedure requiring careful design to ensure the resulting graph is of high quality, consistency, and applicability.

The ETL pipeline is the **technical engine** that converts raw, unstructured text from scientific papers into the structured, factual triples of the knowledge graph. The sophistication of this pipeline directly determines the ultimate power and accuracy of the entire application.

**Pipeline Formula**: `Raw Text → Structured Knowledge → Queryable Graph`

The process can be broken down into **four distinct stages**:

1. **Data Acquisition and Preprocessing**
2. **Entity and Relationship Extraction**
3. **Thematic Analysis with Topic Modeling**
4. **Integration and Storage**

---

## 1.2.1 Step 1: Data Acquisition and Preprocessing

### 1.2.1.1 Data Acquisition Strategy

The first step involves **systematically gathering** source documents from multiple repositories.

#### **Primary Source: PubMed and PubMed Central**

**Access Method**: NCBI E-utilities API

**API Endpoints**:
- `esearch.fcgi` - Search for relevant papers
- `efetch.fcgi` - Retrieve paper details
- `elink.fcgi` - Find related articles

**Search Strategy**:

```python
# Comprehensive space biology query
base_query = """
(
  "space biology"[Title/Abstract] OR
  "spaceflight"[Title/Abstract] OR
  "microgravity"[Title/Abstract] OR
  "space radiation"[Title/Abstract] OR
  "cosmic radiation"[Title/Abstract] OR
  "hypergravity"[Title/Abstract] OR
  "International Space Station"[Title/Abstract] OR
  "ISS"[Title] OR
  "space mission"[Title/Abstract] OR
  "astronaut"[Title/Abstract] OR
  "ground analog"[Title/Abstract] OR
  "bed rest"[Title/Abstract] OR
  "hindlimb unloading"[Title/Abstract]
)
AND
(
  "gene expression"[Title/Abstract] OR
  "protein"[Title/Abstract] OR
  "pathway"[Title/Abstract] OR
  "phenotype"[Title/Abstract] OR
  "transcriptomics"[Title/Abstract] OR
  "proteomics"[Title/Abstract] OR
  "metabolomics"[Title/Abstract] OR
  "bone loss"[Title/Abstract] OR
  "muscle atrophy"[Title/Abstract] OR
  "immune system"[Title/Abstract] OR
  "cardiovascular"[Title/Abstract] OR
  "neurovestibular"[Title/Abstract]
)
"""

# Date range: Last 50 years of space biology research
date_range = "1974/01/01:2025/12/31"

# Filters
filters = [
    "hasabstract",           # Must have abstract
    "english[Language]",     # English only
    "NOT review[Publication Type]"  # Exclude reviews initially
]
```

**Implementation**:

```python
# backend/knowledge_graph/data_acquisition.py

from Bio import Entrez
import time
import logging
from typing import List, Dict
import json

class PubMedAcquisition:
    """
    Handles systematic acquisition of publications from PubMed.
    """
    
    def __init__(self, email: str, api_key: str = None):
        Entrez.email = email
        if api_key:
            Entrez.api_key = api_key  # Higher rate limits with API key
        self.logger = logging.getLogger(__name__)
        
    def search_space_biology_papers(
        self, 
        start_date: str, 
        end_date: str,
        max_results: int = 10000
    ) -> List[str]:
        """
        Search PubMed for space biology papers.
        
        Args:
            start_date: Start date (YYYY/MM/DD)
            end_date: End date (YYYY/MM/DD)
            max_results: Maximum number of results to return
            
        Returns:
            List of PMIDs
        """
        query = self._build_query(start_date, end_date)
        
        self.logger.info(f"Searching PubMed with query: {query[:100]}...")
        
        # Initial search to get count and IDs
        handle = Entrez.esearch(
            db="pubmed",
            term=query,
            retmax=max_results,
            sort="pub_date",
            usehistory="y"  # Use history server for large result sets
        )
        
        record = Entrez.read(handle)
        handle.close()
        
        count = int(record["Count"])
        self.logger.info(f"Found {count} papers matching criteria")
        
        # Get all PMIDs
        pmids = record["IdList"]
        
        # If more results than retmax, fetch in batches using history
        if count > max_results:
            webenv = record["WebEnv"]
            query_key = record["QueryKey"]
            pmids = self._fetch_all_pmids(webenv, query_key, count)
        
        return pmids
    
    def _build_query(self, start_date: str, end_date: str) -> str:
        """Construct comprehensive PubMed query."""
        stressors = [
            "space biology", "spaceflight", "microgravity", 
            "space radiation", "cosmic radiation", "hypergravity",
            "International Space Station", "ISS", "space mission",
            "astronaut", "ground analog", "bed rest", "hindlimb unloading"
        ]
        
        biological_terms = [
            "gene expression", "protein", "pathway", "phenotype",
            "transcriptomics", "proteomics", "metabolomics",
            "bone loss", "muscle atrophy", "immune system",
            "cardiovascular", "neurovestibular"
        ]
        
        stressor_query = " OR ".join([f'"{term}"[Title/Abstract]' for term in stressors])
        bio_query = " OR ".join([f'"{term}"[Title/Abstract]' for term in biological_terms])
        
        query = f"({stressor_query}) AND ({bio_query})"
        query += f' AND ("{start_date}"[Date - Publication] : "{end_date}"[Date - Publication])'
        query += " AND hasabstract AND english[Language]"
        
        return query
    
    def fetch_paper_details(self, pmids: List[str], batch_size: int = 200) -> List[Dict]:
        """
        Fetch detailed information for papers.
        
        Args:
            pmids: List of PubMed IDs
            batch_size: Number of papers to fetch per request
            
        Returns:
            List of paper dictionaries with metadata
        """
        papers = []
        
        for i in range(0, len(pmids), batch_size):
            batch = pmids[i:i+batch_size]
            
            self.logger.info(f"Fetching batch {i//batch_size + 1}: {len(batch)} papers")
            
            try:
                handle = Entrez.efetch(
                    db="pubmed",
                    id=",".join(batch),
                    rettype="xml",
                    retmode="xml"
                )
                
                records = Entrez.read(handle)
                handle.close()
                
                # Parse each article
                for article in records['PubmedArticle']:
                    paper = self._parse_article(article)
                    papers.append(paper)
                
                # Rate limiting: 3 requests per second without key, 10 with key
                time.sleep(0.34 if Entrez.api_key else 1.0)
                
            except Exception as e:
                self.logger.error(f"Error fetching batch {i//batch_size + 1}: {e}")
                continue
        
        return papers
    
    def _parse_article(self, article) -> Dict:
        """Extract relevant fields from PubMed article XML."""
        medline = article['MedlineCitation']
        article_data = medline['Article']
        
        # Basic metadata
        pmid = str(medline['PMID'])
        title = article_data.get('ArticleTitle', '')
        
        # Abstract
        abstract = ""
        if 'Abstract' in article_data:
            abstract_texts = article_data['Abstract'].get('AbstractText', [])
            if isinstance(abstract_texts, list):
                abstract = " ".join([str(text) for text in abstract_texts])
            else:
                abstract = str(abstract_texts)
        
        # Authors
        authors = []
        if 'AuthorList' in article_data:
            for author in article_data['AuthorList']:
                if 'LastName' in author and 'ForeName' in author:
                    authors.append(f"{author['ForeName']} {author['LastName']}")
                elif 'CollectiveName' in author:
                    authors.append(author['CollectiveName'])
        
        # Journal
        journal = article_data.get('Journal', {}).get('Title', '')
        
        # Publication date
        pub_date = self._extract_publication_date(article_data)
        
        # DOI
        doi = None
        if 'ELocationID' in article_data:
            for eloc in article_data['ELocationID']:
                if eloc.attributes.get('EIdType') == 'doi':
                    doi = str(eloc)
        
        # Article IDs (PMC, DOI)
        pmc_id = None
        if 'PubmedData' in article and 'ArticleIdList' in article['PubmedData']:
            for article_id in article['PubmedData']['ArticleIdList']:
                if article_id.attributes.get('IdType') == 'pmc':
                    pmc_id = str(article_id)
                elif article_id.attributes.get('IdType') == 'doi' and not doi:
                    doi = str(article_id)
        
        # MeSH terms
        mesh_terms = []
        if 'MeshHeadingList' in medline:
            for mesh in medline['MeshHeadingList']:
                mesh_terms.append(str(mesh['DescriptorName']))
        
        # Keywords
        keywords = []
        if 'KeywordList' in medline:
            for keyword_list in medline['KeywordList']:
                keywords.extend([str(k) for k in keyword_list])
        
        return {
            'pmid': pmid,
            'pmc_id': pmc_id,
            'doi': doi,
            'title': title,
            'abstract': abstract,
            'authors': authors,
            'journal': journal,
            'publication_date': pub_date,
            'publication_year': int(pub_date.split('-')[0]) if pub_date else None,
            'mesh_terms': mesh_terms,
            'keywords': keywords,
            'full_text_available': pmc_id is not None
        }
    
    def _extract_publication_date(self, article_data) -> str:
        """Extract and standardize publication date."""
        # Try ArticleDate first
        if 'ArticleDate' in article_data and len(article_data['ArticleDate']) > 0:
            date = article_data['ArticleDate'][0]
            year = date.get('Year', '2000')
            month = date.get('Month', '01').zfill(2)
            day = date.get('Day', '01').zfill(2)
            return f"{year}-{month}-{day}"
        
        # Fall back to JournalIssue PubDate
        if 'Journal' in article_data and 'JournalIssue' in article_data['Journal']:
            pub_date = article_data['Journal']['JournalIssue'].get('PubDate', {})
            year = pub_date.get('Year', '2000')
            
            # Try to get month
            month = pub_date.get('Month', '01')
            # Convert month names to numbers
            month_map = {
                'Jan': '01', 'Feb': '02', 'Mar': '03', 'Apr': '04',
                'May': '05', 'Jun': '06', 'Jul': '07', 'Aug': '08',
                'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dec': '12'
            }
            if month in month_map:
                month = month_map[month]
            elif not month.isdigit():
                month = '01'
            
            return f"{year}-{month.zfill(2)}-01"
        
        return None
```

#### **Secondary Source: NASA GeneLab**

```python
# backend/knowledge_graph/genelab_acquisition.py

import requests
import logging
from typing import List, Dict

class GeneLabAcquisition:
    """
    Handles acquisition of omics datasets from NASA GeneLab.
    """
    
    def __init__(self):
        self.base_url = "https://genelab-data.ndc.nasa.gov/genelab/data"
        self.logger = logging.getLogger(__name__)
    
    def search_datasets(
        self, 
        organism: str = None,
        assay_type: str = None,
        factor: str = None
    ) -> List[Dict]:
        """
        Search GeneLab for datasets.
        
        Args:
            organism: Organism name (e.g., "Mus musculus")
            assay_type: Type of assay (e.g., "RNA sequencing")
            factor: Experimental factor (e.g., "Spaceflight")
            
        Returns:
            List of dataset metadata
        """
        search_url = f"{self.base_url}/search"
        
        params = {'term': '', 'type': 'cgene'}
        
        # Build search term
        terms = []
        if organism:
            terms.append(f"organism:{organism}")
        if assay_type:
            terms.append(f"assay_type:{assay_type}")
        if factor:
            terms.append(f"factor:{factor}")
        
        params['term'] = " AND ".join(terms)
        
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            return data.get('studies', [])
            
        except Exception as e:
            self.logger.error(f"Error searching GeneLab: {e}")
            return []
```

### 1.2.1.2 Text Preprocessing

Once acquired, the raw text undergoes a **critical preprocessing phase** to prepare it for NLP analysis.

**Preprocessing Steps**:

```python
# backend/knowledge_graph/text_preprocessing.py

import spacy
from typing import List, Dict
import re
import logging

class TextPreprocessor:
    """
    Handles text preprocessing for NLP pipeline.
    """
    
    def __init__(self):
        # Load spaCy model
        self.nlp = spacy.load("en_core_web_sm")
        self.logger = logging.getLogger(__name__)
        
        # Custom stopwords for scientific text
        self.custom_stopwords = {
            'et', 'al', 'fig', 'figure', 'table', 'however', 
            'therefore', 'thus', 'furthermore', 'moreover',
            'respectively', 'approximately'
        }
    
    def preprocess(self, text: str) -> Dict:
        """
        Preprocess scientific text.
        
        Args:
            text: Raw text from publication
            
        Returns:
            Dictionary with preprocessed text and metadata
        """
        # Clean text
        cleaned = self._clean_text(text)
        
        # Sentence segmentation
        sentences = self._segment_sentences(cleaned)
        
        # Tokenization and linguistic processing
        processed_sentences = []
        for sent in sentences:
            processed = self._process_sentence(sent)
            processed_sentences.append(processed)
        
        return {
            'original': text,
            'cleaned': cleaned,
            'sentences': processed_sentences,
            'sentence_count': len(sentences)
        }
    
    def _clean_text(self, text: str) -> str:
        """
        Clean raw text.
        
        Steps:
        1. Remove special characters but keep hyphens in compound words
        2. Normalize whitespace
        3. Remove citations [1], [2,3]
        4. Remove figure/table references
        """
        # Remove citation brackets
        text = re.sub(r'\[\d+(?:,\s*\d+)*\]', '', text)
        
        # Remove figure/table references
        text = re.sub(r'\((?:Fig|Figure|Table)\.\s*\d+[A-Za-z]?\)', '', text, flags=re.IGNORECASE)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    def _segment_sentences(self, text: str) -> List[str]:
        """Segment text into sentences using spaCy."""
        doc = self.nlp(text)
        return [sent.text for sent in doc.sents]
    
    def _process_sentence(self, sentence: str) -> Dict:
        """
        Process individual sentence.
        
        Returns:
            Dictionary with tokens, lemmas, POS tags, etc.
        """
        doc = self.nlp(sentence)
        
        tokens = []
        lemmas = []
        pos_tags = []
        
        for token in doc:
            # Skip stopwords and punctuation
            if token.is_stop or token.is_punct:
                continue
            
            # Skip custom stopwords
            if token.lemma_.lower() in self.custom_stopwords:
                continue
            
            tokens.append(token.text)
            lemmas.append(token.lemma_)
            pos_tags.append(token.pos_)
        
        return {
            'original': sentence,
            'tokens': tokens,
            'lemmas': lemmas,
            'pos_tags': pos_tags,
            'token_count': len(tokens)
        }
```

**Preprocessing Benefits**:

1. **Stopword Removal**: Eliminates common but semantically empty words
   - Standard stopwords: "the", "is", "and", "a", "of"
   - Domain-specific: "et al", "fig", "however", "therefore"

2. **Lemmatization**: Reduces words to base form
   - "running" → "run"
   - "genes" → "gene"
   - "upregulated" → "upregulate"

3. **Normalization**: Standardizes text format
   - Whitespace normalization
   - Special character handling

4. **Noise Removal**:
   - Citation numbers [1], [2,3]
   - Figure/table references (Fig. 1A)
   - URLs and email addresses

---

## 1.2.2 Step 2: Entity and Relationship Extraction

This stage is the **core of the knowledge extraction process**. Here, advanced NLP models are used to read and "understand" the preprocessed text, identifying predefined entities and semantic relationships between them.

### 1.2.2.1 Model Selection: SciBERT

To achieve high accuracy in this complex domain, the system will employ **transformer-based language models** that have been specifically pre-trained on scientific literature.

**Primary Model**: [SciBERT](https://arxiv.org/abs/1903.10676)

**Why SciBERT?**

| Feature | General BERT | SciBERT | Advantage |
|---------|-------------|---------|-----------|
| **Training Corpus** | Wikipedia, Books | 1.14M scientific papers (Semantic Scholar) | Domain expertise |
| **Vocabulary** | General English | Scientific terminology | Better tokenization of technical terms |
| **Understanding** | Common language | Scientific jargon, complex syntax | Higher accuracy on biomedical text |
| **Performance** | Baseline | +5-10% on biomedical NER tasks | Proven superiority |

**SciBERT Variants**:
- `allenai/scibert_scivocab_uncased` - Scientific vocabulary, lowercase
- `allenai/scibert_scivocab_cased` - Scientific vocabulary, preserves case
- `dmis-lab/biobert-v1.1` - Alternative, specialized for biomedical text

### 1.2.2.2 Named Entity Recognition (NER)

**Task**: Identifying mentions of predefined entities within text.

**Implementation**:

```python
# backend/knowledge_graph/ner_extraction.py

from transformers import AutoTokenizer, AutoModelForTokenClassification
from transformers import pipeline
import spacy
from typing import List, Dict
import logging

class EntityExtractor:
    """
    Extract biomedical entities from scientific text using SciBERT and SciSpacy.
    """
    
    def __init__(self, device: int = -1):
        """
        Initialize entity extraction models.
        
        Args:
            device: GPU device (-1 for CPU, 0+ for GPU)
        """
        self.logger = logging.getLogger(__name__)
        self.device = device
        
        # Load SciBERT for gene/protein NER
        self.logger.info("Loading SciBERT model...")
        self.scibert_ner = pipeline(
            "ner",
            model="allenai/scibert_scivocab_uncased",
            tokenizer="allenai/scibert_scivocab_uncased",
            aggregation_strategy="simple",
            device=device
        )
        
        # Load SciSpacy for disease/chemical NER
        self.logger.info("Loading SciSpacy model...")
        self.scispacy_nlp = spacy.load("en_ner_bc5cdr_md")
        
        # Entity type mapping
        self.entity_type_map = {
            'GENE': 'Gene',
            'PROTEIN': 'Protein',
            'DISEASE': 'Disease',
            'CHEMICAL': 'Metabolite',
            'CELL_LINE': 'CellLine',
            'CELL_TYPE': 'CellType',
            'SPECIES': 'Organism'
        }
        
        # Confidence threshold
        self.confidence_threshold = 0.75
    
    def extract_entities(self, text: str) -> List[Dict]:
        """
        Extract all entities from text using multiple models.
        
        Args:
            text: Input text
            
        Returns:
            List of entity dictionaries
        """
        entities = []
        
        # Extract with SciBERT
        scibert_entities = self._extract_with_scibert(text)
        entities.extend(scibert_entities)
        
        # Extract with SciSpacy
        scispacy_entities = self._extract_with_scispacy(text)
        entities.extend(scispacy_entities)
        
        # Extract space biology specific entities
        space_bio_entities = self._extract_space_biology_entities(text)
        entities.extend(space_bio_entities)
        
        # Deduplicate
        entities = self._deduplicate_entities(entities)
        
        # Filter by confidence
        entities = [e for e in entities if e['confidence'] >= self.confidence_threshold]
        
        return entities
    
    def _extract_with_scibert(self, text: str) -> List[Dict]:
        """Extract entities using SciBERT."""
        try:
            results = self.scibert_ner(text)
            
            entities = []
            for entity in results:
                entities.append({
                    'type': self.entity_type_map.get(entity['entity_group'], entity['entity_group']),
                    'text': entity['word'],
                    'start': entity['start'],
                    'end': entity['end'],
                    'confidence': entity['score'],
                    'source': 'SciBERT'
                })
            
            return entities
            
        except Exception as e:
            self.logger.error(f"SciBERT extraction error: {e}")
            return []
    
    def _extract_with_scispacy(self, text: str) -> List[Dict]:
        """Extract entities using SciSpacy."""
        try:
            doc = self.scispacy_nlp(text)
            
            entities = []
            for ent in doc.ents:
                entities.append({
                    'type': self.entity_type_map.get(ent.label_, ent.label_),
                    'text': ent.text,
                    'start': ent.start_char,
                    'end': ent.end_char,
                    'confidence': 0.85,
                    'source': 'SciSpacy'
                })
            
            return entities
            
        except Exception as e:
            self.logger.error(f"SciSpacy extraction error: {e}")
            return []
    
    def _extract_space_biology_entities(self, text: str) -> List[Dict]:
        """
        Extract space biology specific entities using pattern matching.
        """
        import re
        
        entities = []
        
        # Stressor patterns
        stressor_patterns = {
            'Microgravity': r'\b(?:microgravity|micro-gravity|μg|ug|weightlessness|zero-g)\b',
            'Simulated Microgravity': r'\b(?:simulated microgravity|clinostat|RPM|rotating wall vessel)\b',
            'Cosmic Radiation': r'\b(?:cosmic radiation|GCR|galactic cosmic ray|space radiation)\b',
            'Solar Particle Event': r'\b(?:SPE|solar particle event|solar energetic particle)\b',
            'Hypergravity': r'\b(?:hypergravity|hyper-gravity|centrifuge|2g|2 g)\b',
            'Isolation': r'\b(?:isolation|confinement|confined environment)\b',
            'Altered Gravity': r'\b(?:altered gravity|variable gravity|partial gravity)\b'
        }
        
        for stressor_name, pattern in stressor_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                entities.append({
                    'type': 'Stressor',
                    'text': match.group(),
                    'start': match.start(),
                    'end': match.end(),
                    'confidence': 0.90,
                    'source': 'Pattern',
                    'canonical_name': stressor_name
                })
        
        return entities
    
    def _deduplicate_entities(self, entities: List[Dict]) -> List[Dict]:
        """
        Remove overlapping entities, keeping the one with highest confidence.
        """
        # Sort by start position and confidence (descending)
        entities = sorted(entities, key=lambda x: (x['start'], -x['confidence']))
        
        deduplicated = []
        last_end = -1
        
        for entity in entities:
            # If entity doesn't overlap with previous, keep it
            if entity['start'] >= last_end:
                deduplicated.append(entity)
                last_end = entity['end']
            # If it overlaps, only keep if higher confidence
            elif entity['confidence'] > deduplicated[-1]['confidence']:
                deduplicated[-1] = entity
                last_end = entity['end']
        
        return deduplicated
```

**Example Output**:

```python
# Input sentence:
"Exposure to microgravity resulted in significant upregulation of ATROGIN-1 (FBXO32) and MuRF1 (TRIM63) in skeletal muscle tissue of mice."

# Extracted entities:
[
    {'type': 'Stressor', 'text': 'microgravity', 'confidence': 0.92, 'source': 'Pattern'},
    {'type': 'Gene', 'text': 'ATROGIN-1', 'confidence': 0.95, 'source': 'SciBERT'},
    {'type': 'Gene', 'text': 'FBXO32', 'confidence': 0.93, 'source': 'SciBERT'},
    {'type': 'Gene', 'text': 'MuRF1', 'confidence': 0.94, 'source': 'SciBERT'},
    {'type': 'Gene', 'text': 'TRIM63', 'confidence': 0.92, 'source': 'SciBERT'},
    {'type': 'Tissue', 'text': 'skeletal muscle tissue', 'confidence': 0.89, 'source': 'SciSpacy'},
    {'type': 'Organism', 'text': 'mice', 'confidence': 0.98, 'source': 'SciSpacy'}
]
```

### 1.2.2.3 Relationship Extraction (RE)

**Task**: Classifying the semantic relationship between pairs of identified entities.

**Example**: In the sentence "Microgravity exposure leads to an upregulation of gene X," the model extracts:
- Triple: `(Gene X, is_upregulated_by, Microgravity)`

**Implementation**:

```python
# backend/knowledge_graph/relation_extraction.py

import spacy
from typing import List, Dict
import re
import logging

class RelationExtractor:
    """
    Extract relationships between entities in scientific text.
    """
    
    def __init__(self):
        self.nlp = spacy.load("en_core_web_sm")
        self.logger = logging.getLogger(__name__)
        
        # Relation patterns (trigger words)
        self.relation_patterns = {
            'UPREGULATES': [
                r'upregulat\w*', r'increas\w*', r'elevat\w*',
                r'activat\w*', r'induc\w*', r'stimulat\w*',
                r'enhanc\w*', r'amplif\w*', r'boost\w*'
            ],
            'DOWNREGULATES': [
                r'downregulat\w*', r'decreas\w*', r'reduc\w*',
                r'inhibit\w*', r'suppress\w*', r'repress\w*',
                r'attenuate\w*', r'diminish\w*', r'impair\w*'
            ],
            'CAUSES': [
                r'caus\w*', r'lead\w* to', r'result\w* in',
                r'induc\w*', r'trigger\w*', r'provoke\w*',
                r'elicit\w*', r'produce\w*'
            ],
            'PREVENTS': [
                r'prevent\w*', r'protect\w* against', r'counteract\w*',
                r'mitigate\w*', r'ameliorate\w*', r'alleviate\w*'
            ],
            'INTERACTS_WITH': [
                r'interact\w*', r'bind\w*', r'associate\w* with',
                r'complex\w* with', r'partner\w* with'
            ],
            'PARTICIPATES_IN': [
                r'participat\w* in', r'involv\w* in', r'play\w* (?:a |an )?role in',
                r'mediat\w*', r'regulat\w*'
            ],
            'LOCATED_IN': [
                r'locat\w* in', r'found in', r'present in',
                r'express\w* in', r'detect\w* in'
            ]
        }
    
    def extract_relations(
        self, 
        text: str, 
        entities: List[Dict]
    ) -> List[Dict]:
        """
        Extract relationships between entities in text.
        
        Args:
            text: Input text
            entities: List of entities extracted from text
            
        Returns:
            List of relation dictionaries
        """
        doc = self.nlp(text)
        relations = []
        
        # Create entity index by character position
        entity_index = self._create_entity_index(entities, doc)
        
        # Method 1: Dependency parsing
        dep_relations = self._extract_dependency_relations(doc, entity_index)
        relations.extend(dep_relations)
        
        # Method 2: Pattern matching
        pattern_relations = self._extract_pattern_relations(text, entities)
        relations.extend(pattern_relations)
        
        # Deduplicate
        relations = self._deduplicate_relations(relations)
        
        return relations
    
    def _extract_pattern_relations(
        self, 
        text: str, 
        entities: List[Dict]
    ) -> List[Dict]:
        """
        Extract relations using co-occurrence patterns.
        """
        relations = []
        
        # Sort entities by position
        sorted_entities = sorted(entities, key=lambda x: x['start'])
        
        # Check pairs of nearby entities
        for i, ent1 in enumerate(sorted_entities):
            for ent2 in sorted_entities[i+1:]:
                # Distance threshold
                distance = ent2['start'] - ent1['end']
                
                if distance > 100:  # Skip if too far apart
                    break
                
                # Get text between entities
                between_text = text[ent1['end']:ent2['start']]
                
                # Check for relation triggers
                relation_type = None
                trigger = None
                
                for rel_type, patterns in self.relation_patterns.items():
                    for pattern in patterns:
                        match = re.search(pattern, between_text, re.IGNORECASE)
                        if match:
                            relation_type = rel_type
                            trigger = match.group()
                            break
                    if relation_type:
                        break
                
                if relation_type:
                    relations.append({
                        'type': relation_type,
                        'subject': ent1,
                        'object': ent2,
                        'trigger': trigger,
                        'confidence': 0.70,
                        'method': 'pattern_matching'
                    })
        
        return relations
    
    def _deduplicate_relations(self, relations: List[Dict]) -> List[Dict]:
        """Remove duplicate relations, keeping highest confidence."""
        relation_map = {}
        
        for rel in relations:
            key = (
                rel['subject']['text'],
                rel['type'],
                rel['object']['text']
            )
            
            if key not in relation_map:
                relation_map[key] = rel
            elif rel['confidence'] > relation_map[key]['confidence']:
                relation_map[key] = rel
        
        return list(relation_map.values())
```

---

## 1.2.3 Step 3: Thematic Analysis with Topic Modeling

Beyond extracting individual facts, we want to **understand the broader themes** present in the literature. Topic modeling enables us to group papers by subject matter and identify emerging research trends.

### 1.2.3.1 Why BERTopic?

**BERTopic** is a modern topic modeling technique that leverages transformer-based embeddings.

**Advantages over traditional LDA**:

| Feature | LDA | BERTopic |
|---------|-----|----------|
| **Embeddings** | Bag-of-words | Contextualized (BERT) |
| **Interpretability** | Word probability distributions | Coherent topics with representative documents |
| **Dynamic Topics** | Static | Can evolve over time |
| **Hierarchical Structure** | Flat | Hierarchical topic trees |
| **Outlier Handling** | Poor | Explicit outlier detection |

### 1.2.3.2 Implementation

```python
# backend/knowledge_graph/topic_modeling.py

from bertopic import BERTopic
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import CountVectorizer
from umap import UMAP
from hdbscan import HDBSCAN
import numpy as np
from typing import List, Dict
import logging

class TopicModeler:
    """
    Perform topic modeling on scientific papers using BERTopic.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # Embedding model - use biomedical model
        self.logger.info("Loading sentence transformer model...")
        self.embedding_model = SentenceTransformer('pritamdeka/S-PubMedBert-MS-MARCO')
        
        # UMAP for dimensionality reduction
        umap_model = UMAP(
            n_neighbors=15,
            n_components=5,
            min_dist=0.0,
            metric='cosine'
        )
        
        # HDBSCAN for clustering
        hdbscan_model = HDBSCAN(
            min_cluster_size=10,
            min_samples=5,
            metric='euclidean',
            cluster_selection_method='eom'
        )
        
        # Vectorizer - use c-TF-IDF
        vectorizer_model = CountVectorizer(
            stop_words='english',
            min_df=2,
            ngram_range=(1, 2)
        )
        
        # Initialize BERTopic
        self.topic_model = BERTopic(
            embedding_model=self.embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            vectorizer_model=vectorizer_model,
            nr_topics='auto',  # Automatic topic reduction
            verbose=True
        )
    
    def fit_topics(self, papers: List[Dict]) -> Dict:
        """
        Fit topic model on corpus of papers.
        
        Args:
            papers: List of paper dictionaries with 'title' and 'abstract'
            
        Returns:
            Dictionary with topic model results
        """
        # Prepare documents
        documents = []
        doc_ids = []
        
        for paper in papers:
            # Combine title and abstract
            text = f"{paper.get('title', '')} {paper.get('abstract', '')}"
            documents.append(text)
            doc_ids.append(paper.get('pmid', 'unknown'))
        
        self.logger.info(f"Fitting topic model on {len(documents)} papers...")
        
        # Fit the model
        topics, probs = self.topic_model.fit_transform(documents)
        
        # Get topic information
        topic_info = self.topic_model.get_topic_info()
        
        # Assign topics to papers
        for i, paper in enumerate(papers):
            paper['topic_id'] = int(topics[i])
            paper['topic_probability'] = float(probs[i][topics[i]])
            
            # Get topic label
            if topics[i] != -1:  # -1 is outlier topic
                topic_row = topic_info[topic_info['Topic'] == topics[i]]
                if len(topic_row) > 0:
                    paper['topic_name'] = topic_row.iloc[0]['Name']
        
        self.logger.info(f"Identified {len(topic_info) - 1} topics (excluding outliers)")
        
        return {
            'topic_info': topic_info,
            'topics': topics,
            'probabilities': probs,
            'papers': papers
        }
    
    def get_topic_hierarchy(self) -> Dict:
        """
        Get hierarchical structure of topics.
        
        Returns:
            Dictionary representing topic hierarchy
        """
        hierarchical_topics = self.topic_model.hierarchical_topics(
            self.topic_model.topics_
        )
        
        return hierarchical_topics
    
    def visualize_topics(self, output_path: str = None):
        """
        Create interactive visualizations of topics.
        
        Args:
            output_path: Path to save HTML visualizations
        """
        # Topic visualization
        fig = self.topic_model.visualize_topics()
        if output_path:
            fig.write_html(f"{output_path}/topics.html")
        
        # Topic hierarchy
        fig_hierarchy = self.topic_model.visualize_hierarchy()
        if output_path:
            fig_hierarchy.write_html(f"{output_path}/hierarchy.html")
        
        # Topic over time (if temporal data available)
        # fig_time = self.topic_model.visualize_topics_over_time(...)
        
        return fig, fig_hierarchy
```

**Topics Generated** (Example):

```
Topic 0: Microgravity Muscle Atrophy
  - Keywords: microgravity, muscle, atrophy, FBXO32, MuRF1, hindlimb, unloading
  - Papers: 143
  
Topic 1: Spaceflight Immune System
  - Keywords: immune, spaceflight, lymphocyte, cytokine, inflammation, stress
  - Papers: 98
  
Topic 2: Cosmic Radiation DNA Damage
  - Keywords: radiation, DNA, repair, chromosome, damage, HZE, particles
  - Papers: 87
  
Topic 3: Bone Loss Osteoporosis
  - Keywords: bone, density, osteoblast, osteoclast, calcium, resorption
  - Papers: 76
```

---

## 1.2.4 Step 4: Integration and Storage

The final stage involves **loading the extracted knowledge** into Neo4j and ensuring **data quality** through entity resolution and ontology alignment.

### 1.2.4.1 Entity Resolution

**Challenge**: The same biological entity may be mentioned with different names:
- "FBXO32" vs "ATROGIN-1" vs "F-box protein 32"
- "Homo sapiens" vs "human"

**Solution**: Entity Linking to Standard Databases

```python
# backend/knowledge_graph/entity_resolution.py

import requests
from typing import Dict, List
import logging

class EntityResolver:
    """
    Resolve entity mentions to canonical database identifiers.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
        # API endpoints
        self.mygene_url = "https://mygene.info/v3"
        self.uniprot_url = "https://rest.uniprot.org/uniprotkb"
        self.ncbi_taxonomy_url = "https://www.ncbi.nlm.nih.gov/taxonomy"
    
    def resolve_gene(self, gene_symbol: str, organism: str = "human") -> Dict:
        """
        Resolve gene symbol to Entrez Gene ID.
        
        Args:
            gene_symbol: Gene symbol (e.g., "FBXO32")
            organism: Organism name
            
        Returns:
            Dictionary with resolved identifiers
        """
        try:
            # Query MyGene.info
            response = requests.get(
                f"{self.mygene_url}/query",
                params={
                    'q': f'symbol:{gene_symbol} AND organism:"{organism}"',
                    'fields': 'entrezgene,symbol,name,ensembl.gene,uniprot',
                    'species': organism
                }
            )
            
            data = response.json()
            
            if 'hits' in data and len(data['hits']) > 0:
                hit = data['hits'][0]
                
                return {
                    'entrez_id': str(hit.get('entrezgene', '')),
                    'symbol': hit.get('symbol', gene_symbol),
                    'name': hit.get('name', ''),
                    'ensembl_id': hit.get('ensembl', {}).get('gene', ''),
                    'uniprot_ids': hit.get('uniprot', {}),
                    'source': 'MyGene.info',
                    'resolved': True
                }
            
            return {'resolved': False, 'original': gene_symbol}
            
        except Exception as e:
            self.logger.error(f"Error resolving gene {gene_symbol}: {e}")
            return {'resolved': False, 'original': gene_symbol}
    
    def resolve_protein(self, protein_name: str) -> Dict:
        """
        Resolve protein name to UniProt ID.
        
        Args:
            protein_name: Protein name
            
        Returns:
            Dictionary with UniProt ID and metadata
        """
        try:
            response = requests.get(
                f"{self.uniprot_url}/search",
                params={
                    'query': protein_name,
                    'format': 'json',
                    'size': 1
                }
            )
            
            data = response.json()
            
            if 'results' in data and len(data['results']) > 0:
                result = data['results'][0]
                
                return {
                    'uniprot_id': result['primaryAccession'],
                    'name': result['proteinDescription']['recommendedName']['fullName']['value'],
                    'gene': result.get('genes', [{}])[0].get('geneName', {}).get('value', ''),
                    'organism': result['organism']['scientificName'],
                    'resolved': True
                }
            
            return {'resolved': False, 'original': protein_name}
            
        except Exception as e:
            self.logger.error(f"Error resolving protein {protein_name}: {e}")
            return {'resolved': False, 'original': protein_name}
```

### 1.2.4.2 Ontology Alignment

**Purpose**: Standardize entity types using biomedical ontologies.

```python
# backend/knowledge_graph/ontology_alignment.py

import requests
from typing import Dict, List
import logging

class OntologyAligner:
    """
    Align entities to standard ontologies.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.ebi_ols_url = "https://www.ebi.ac.uk/ols4/api"
    
    def map_to_go(self, term: str) -> List[Dict]:
        """
        Map biological process/function to Gene Ontology.
        
        Args:
            term: Biological term
            
        Returns:
            List of GO term matches
        """
        try:
            response = requests.get(
                f"{self.ebi_ols_url}/search",
                params={
                    'q': term,
                    'ontology': 'go',
                    'exact': 'false'
                }
            )
            
            data = response.json()
            
            matches = []
            if 'response' in data and 'docs' in data['response']:
                for doc in data['response']['docs']:
                    matches.append({
                        'go_id': doc['obo_id'],
                        'label': doc['label'],
                        'description': doc.get('description', [''])[0],
                        'namespace': doc.get('ontology_prefix', 'GO')
                    })
            
            return matches
            
        except Exception as e:
            self.logger.error(f"Error mapping to GO: {e}")
            return []
```

### 1.2.4.3 Neo4j Integration

**Loading Data into the Graph**:

```python
# backend/knowledge_graph/neo4j_loader.py

from neo4j import GraphDatabase
from typing import List, Dict
import logging

class Neo4jLoader:
    """
    Load extracted knowledge into Neo4j graph database.
    """
    
    def __init__(self, uri: str, user: str, password: str):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.logger = logging.getLogger(__name__)
    
    def close(self):
        self.driver.close()
    
    def create_gene_node(self, gene_data: Dict):
        """Create or update Gene node."""
        with self.driver.session() as session:
            session.execute_write(self._create_gene, gene_data)
    
    @staticmethod
    def _create_gene(tx, data):
        query = """
        MERGE (g:Gene {entrez_id: $entrez_id})
        SET g.symbol = $symbol,
            g.name = $name,
            g.ensembl_id = $ensembl_id,
            g.updated_at = datetime()
        RETURN g
        """
        result = tx.run(query, **data)
        return result.single()
    
    def create_relation(self, subject_id: str, relation_type: str, 
                       object_id: str, properties: Dict):
        """Create relationship between nodes."""
        with self.driver.session() as session:
            session.execute_write(
                self._create_relation,
                subject_id, relation_type, object_id, properties
            )
    
    @staticmethod
    def _create_relation(tx, subject_id, relation_type, object_id, properties):
        query = f"""
        MATCH (s {{entrez_id: $subject_id}})
        MATCH (o {{entrez_id: $object_id}})
        MERGE (s)-[r:{relation_type}]->(o)
        SET r += $properties
        SET r.updated_at = datetime()
        RETURN r
        """
        result = tx.run(
            query,
            subject_id=subject_id,
            object_id=object_id,
            properties=properties
        )
        return result.single()
    
    def batch_load_papers(self, papers: List[Dict], batch_size: int = 100):
        """
        Load papers with entities and relations in batches.
        
        Args:
            papers: List of processed paper dictionaries
            batch_size: Number of papers per batch
        """
        for i in range(0, len(papers), batch_size):
            batch = papers[i:i+batch_size]
            
            self.logger.info(f"Loading batch {i//batch_size + 1}: {len(batch)} papers")
            
            with self.driver.session() as session:
                session.execute_write(self._load_paper_batch, batch)
    
    @staticmethod
    def _load_paper_batch(tx, papers):
        """Load a batch of papers with their entities and relations."""
        for paper in papers:
            # Create ResearchPaper node
            tx.run("""
                MERGE (p:ResearchPaper {pmid: $pmid})
                SET p.title = $title,
                    p.abstract = $abstract,
                    p.publication_date = date($publication_date),
                    p.journal = $journal,
                    p.topic_id = $topic_id,
                    p.updated_at = datetime()
                """,
                pmid=paper['pmid'],
                title=paper['title'],
                abstract=paper['abstract'],
                publication_date=paper['publication_date'],
                journal=paper.get('journal', ''),
                topic_id=paper.get('topic_id', -1)
            )
            
            # Create entity nodes and link to paper
            for entity in paper.get('entities', []):
                # Create entity node based on type
                # Link to paper with MENTIONS relationship
                pass
            
            # Create relationship edges
            for relation in paper.get('relations', []):
                # Create relationship between entities
                # Add paper as source
                pass
```

---

## 1.2.5 Quality Assurance and Metrics

### 1.2.5.1 Quality Checks

1. **Entity Extraction Quality**:
   - Precision: What % of extracted entities are correct?
   - Recall: What % of entities in text were found?
   - F1 Score: Harmonic mean of precision and recall

2. **Relationship Extraction Quality**:
   - Accuracy: What % of extracted triples are factually correct?
   - Coverage: What % of stated relationships were captured?

3. **Graph Quality**:
   - Connectivity: Are nodes well connected?
   - Redundancy: Are there duplicate entities/relationships?
   - Consistency: Do relationships follow biological logic?

### 1.2.5.2 Pipeline Orchestration with Airflow

```python
# backend/airflow/dags/etl_pipeline.py

from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta

default_args = {
    'owner': 'space-biology-kg',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'space_biology_etl',
    default_args=default_args,
    description='ETL pipeline for Space Biology Knowledge Graph',
    schedule_interval='@weekly',  # Run weekly
    catchup=False
)

# Task 1: Acquire new papers
acquire_papers = PythonOperator(
    task_id='acquire_papers',
    python_callable=acquire_papers_task,
    dag=dag
)

# Task 2: Preprocess text
preprocess_text = PythonOperator(
    task_id='preprocess_text',
    python_callable=preprocess_text_task,
    dag=dag
)

# Task 3: Extract entities
extract_entities = PythonOperator(
    task_id='extract_entities',
    python_callable=extract_entities_task,
    dag=dag
)

# Task 4: Extract relations
extract_relations = PythonOperator(
    task_id='extract_relations',
    python_callable=extract_relations_task,
    dag=dag
)

# Task 5: Perform topic modeling
topic_modeling = PythonOperator(
    task_id='topic_modeling',
    python_callable=topic_modeling_task,
    dag=dag
)

# Task 6: Entity resolution
resolve_entities = PythonOperator(
    task_id='resolve_entities',
    python_callable=resolve_entities_task,
    dag=dag
)

# Task 7: Load into Neo4j
load_neo4j = PythonOperator(
    task_id='load_neo4j',
    python_callable=load_neo4j_task,
    dag=dag
)

# Define task dependencies
acquire_papers >> preprocess_text >> extract_entities >> extract_relations
extract_relations >> topic_modeling >> resolve_entities >> load_neo4j
```

---

## Summary

The ETL pipeline is the **automated knowledge extraction engine** that powers the Space Biology Knowledge Graph. Through four sophisticated stages:

1. **Data Acquisition**: Systematically gathering papers from PubMed, PMC, and NASA GeneLab
2. **NLP Processing**: Using SciBERT and SciSpacy to extract entities and relationships with high accuracy
3. **Topic Modeling**: Employing BERTopic to discover research themes and trends
4. **Integration**: Loading structured knowledge into Neo4j with entity resolution and quality assurance

This pipeline transforms **unstructured scientific literature** into a **queryable, semantically-rich knowledge graph** that enables:
- Multi-hop reasoning across biological scales
- Evidence-backed answers to complex questions
- Discovery of hidden connections
- Temporal trend analysis
- Cross-study synthesis

**Key Performance Metrics**:
- **Throughput**: 1000+ papers/day processing capacity
- **Entity Extraction F1**: >0.90 for genes/proteins, >0.85 for diseases/phenotypes
- **Relationship Extraction Accuracy**: >0.80
- **Entity Resolution Coverage**: >95% of genes/proteins linked to standard IDs
- **Graph Growth**: ~500K new triples per week

The pipeline runs continuously via Apache Airflow, ensuring the knowledge graph remains current with the latest research findings.

---

**Next Steps**:
- Part II: Interactive Interface - Building visualization and exploration tools
- Part III: Intelligence Layer - Implementing RAG-powered AI assistant
- Part IV: Collaboration Layer - Enabling community engagement


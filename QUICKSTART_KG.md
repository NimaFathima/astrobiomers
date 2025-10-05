# Quick Start Guide: Building the Space Biology Knowledge Graph

## Overview

This guide will help you start constructing the Space Biology Knowledge Graph from scientific literature.

## Prerequisites

✅ **Already Set Up:**
- Docker and Docker Compose installed
- Python 3.10+ installed
- Git repository initialized

## Step-by-Step Setup

### 1. Configure Environment Variables

First, create your `.env` file with your API credentials:

```powershell
# Copy the example file
cp .env.example .env
```

**Required API Keys:**
- `PUBMED_EMAIL`: Your email (required by NCBI)
- `PUBMED_API_KEY`: NCBI API key (optional but recommended for higher rate limits)
  - Get one at: https://www.ncbi.nlm.nih.gov/account/
- `NEO4J_PASSWORD`: Password for Neo4j database
- `OPENAI_API_KEY`: For AI features (optional for initial KG construction)

### 2. Install Python Dependencies

Run the automated setup script:

```powershell
cd backend
python setup_kg.py
```

This will:
- ✓ Install all Python packages
- ✓ Download spaCy models
- ✓ Download SciSpacy models (biomedical NER)
- ✓ Download SciBERT transformer models
- ✓ Download sentence transformers for topic modeling
- ✓ Create data directories

**Or install manually:**

```powershell
# Install requirements
pip install -r requirements.txt

# Install spaCy models
python -m spacy download en_core_web_sm
python -m spacy download en_core_web_md

# Install SciSpacy model
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_ner_bc5cdr_md-0.5.3.tar.gz
```

### 3. Start Docker Services

Start Neo4j, PostgreSQL, Redis, Elasticsearch, and other services:

```powershell
# From project root
docker-compose up -d
```

**Verify services are running:**

```powershell
docker-compose ps
```

**Access Neo4j Browser:**
- URL: http://localhost:7474
- Username: `neo4j`
- Password: (from your `.env` file)

### 4. Initialize Neo4j Database Schema

Create the database schema with constraints and indexes:

```powershell
cd backend
python -m knowledge_graph.cli init-db
```

This creates:
- Node constraints (unique IDs)
- Indexes for fast lookups
- Full-text search indexes

### 5. Build the Knowledge Graph

Now you're ready to start constructing the knowledge graph!

#### Option A: Quick Test Run (100 papers)

```powershell
python -m knowledge_graph.cli build --papers 100
```

#### Option B: Small Dataset (1000 papers)

```powershell
python -m knowledge_graph.cli build --papers 1000
```

#### Option C: Full Dataset (10,000+ papers)

```powershell
python -m knowledge_graph.cli build --papers 10000
```

#### Option D: Incremental Updates

```powershell
python -m knowledge_graph.cli build --incremental
```

### 6. Monitor Progress

The pipeline will show progress through 7 stages:

```
[1/7] Initializing pipeline...
[2/7] Acquiring papers from PubMed...
[3/7] Preprocessing text...
[4/7] Extracting entities (NER)...
[5/7] Extracting relationships (RE)...
[6/7] Topic modeling...
[7/7] Loading into Neo4j...
```

**Check logs:**

```powershell
# View real-time logs
tail -f data/logs/kg_construction.log

# Or on Windows PowerShell
Get-Content data/logs/kg_construction.log -Wait
```

### 7. Check Knowledge Graph Status

```powershell
# Check connection and data directories
python -m knowledge_graph.cli status

# View statistics
python -m knowledge_graph.cli stats
```

**Expected output:**

```
Knowledge Graph Statistics
======================================================================

Node Counts:
  ResearchPaper                         1,000
  Gene                                  5,234
  Protein                               3,456
  Disease                                 234
  Stressor                                 45
  Phenotype                                12
  TOTAL                                 9,981

Relationship Counts:
  UPREGULATES                           2,345
  DOWNREGULATES                         1,876
  CAUSES                                  543
  INTERACTS_WITH                          876
  TOTAL                                 5,640
```

### 8. Explore the Knowledge Graph

**Neo4j Browser (http://localhost:7474):**

```cypher
// View sample data
MATCH (n) RETURN n LIMIT 25

// Find papers about microgravity and muscle atrophy
MATCH (p:ResearchPaper)-[:MENTIONS]->(s:Stressor {canonical_name: 'Microgravity'})
MATCH (p)-[:MENTIONS]->(ph:Phenotype {canonical_name: 'Muscle Atrophy'})
RETURN p, s, ph
LIMIT 10

// Find genes upregulated by microgravity
MATCH (g:Gene)<-[:UPREGULATES]-(s:Stressor {canonical_name: 'Microgravity'})
RETURN g.symbol, g.name, count(*) as paper_count
ORDER BY paper_count DESC
LIMIT 20

// Explore relationship between genes and pathways
MATCH (g:Gene)-[r:PARTICIPATES_IN]->(p:Pathway)
RETURN g, r, p
LIMIT 50
```

## Pipeline Architecture

The ETL pipeline follows this flow:

```
┌─────────────────────────────────────────────────────────────┐
│                    1. Data Acquisition                      │
│  PubMed E-utilities → Download papers matching query        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   2. Text Preprocessing                     │
│  Clean text → Remove citations/figures → Lemmatization      │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  3. Entity Extraction (NER)                 │
│  SciBERT → Genes/Proteins   SciSpacy → Diseases/Chemicals  │
│  Pattern Matching → Stressors/Phenotypes                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│               4. Relationship Extraction (RE)               │
│  Dependency Parsing → Trigger Words → Extract Relations     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                    5. Topic Modeling                        │
│  BERTopic → Contextual Embeddings → Cluster Documents       │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   6. Entity Resolution                      │
│  MyGene.info → Map to Entrez IDs   UniProt → Protein IDs   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                  7. Neo4j Integration                       │
│  Create Nodes → Create Relationships → Add Properties       │
└─────────────────────────────────────────────────────────────┘
```

## Performance Expectations

### Processing Speed
- **Papers/hour**: ~500-1,000 (depends on GPU availability)
- **With GPU**: 3-5x faster entity/relation extraction
- **PubMed API**: Rate limited to 3-10 requests/sec

### Resource Usage
- **CPU**: 50-80% during processing
- **RAM**: 4-8 GB for models
- **GPU VRAM**: 2-4 GB (if using GPU)
- **Disk**: ~1 GB per 1,000 papers

### Accuracy Metrics
- **Entity Extraction F1**: 0.90+ for genes/proteins
- **Relation Extraction Accuracy**: 0.80+
- **Entity Resolution Coverage**: 95%+ for genes

## Troubleshooting

### Issue: Models not downloading

```powershell
# Manually download models
python -m spacy download en_core_web_sm
pip install https://s3-us-west-2.amazonaws.com/ai2-s2-scispacy/releases/v0.5.3/en_ner_bc5cdr_md-0.5.3.tar.gz
```

### Issue: Neo4j connection failed

```powershell
# Check if Neo4j is running
docker-compose ps

# Restart Neo4j
docker-compose restart neo4j

# Check logs
docker-compose logs neo4j
```

### Issue: Out of memory

```powershell
# Reduce batch size in config.py
pipeline_batch_size = 50  # Default is 100

# Or process fewer papers at once
python -m knowledge_graph.cli build --papers 500
```

### Issue: PubMed API rate limiting

Get an API key from NCBI to increase limits:
- Without key: 3 requests/second
- With key: 10 requests/second
- Add to `.env`: `PUBMED_API_KEY=your_key_here`

## Next Steps

After building the initial knowledge graph:

1. **Explore the Graph**: Use Neo4j Browser to run Cypher queries
2. **Start the Backend API**: `uvicorn backend.main:app --reload`
3. **Start the Frontend**: `cd frontend && npm start`
4. **Set Up Incremental Updates**: Schedule regular pipeline runs
5. **Enable AI Assistant**: Configure OpenAI API key for RAG queries

## Advanced Usage

### Custom Date Range

```powershell
python -m knowledge_graph.cli build --start-date 2020/01/01 --end-date 2023/12/31
```

### Acquire Specific Papers

```powershell
python -m knowledge_graph.cli acquire --pmids "12345678,23456789,34567890" --output data/raw/custom_papers.json
```

### Monitor with Airflow (Optional)

```powershell
# Start Airflow
docker-compose up airflow-webserver airflow-scheduler

# Access at http://localhost:8080
# Enable the "space_biology_etl" DAG
```

## Support & Documentation

- **Full Documentation**: `/docs/architecture/`
- **ETL Pipeline Details**: `/docs/architecture/PART_I_ETL_PIPELINE_DETAILED.md`
- **Knowledge Foundation**: `/docs/architecture/PART_I_KNOWLEDGE_FOUNDATION_DETAILED.md`
- **System Architecture**: `/docs/architecture/SYSTEM_ARCHITECTURE.md`

## Questions?

Check the logs for detailed error messages:
```powershell
Get-Content data/logs/kg_construction.log -Tail 50
```

Happy Knowledge Graph Building! 🚀🧬

# NASA Space Biology Data Sources Integration

## Overview

The Space Biology Knowledge Graph now integrates **6 major NASA and space biology data sources** to provide the most comprehensive collection of spaceflight and space-relevant research data.

## Integrated Data Sources

### 1. 🎯 Curated Space Biology Publications (jgalazka)

**Source**: https://github.com/jgalazka/SB_publications

**Description**: Curated collection of 608+ open access space biology publications since 2010

**Key Features**:
- ✅ Full text available in PubMed Central
- ✅ Manually curated for relevance
- ✅ Quality-controlled dataset
- ✅ Direct PMC links for download

**Data Format**: CSV with title and PMC URL

**Usage**:
```python
from knowledge_graph.nasa_resources import SpaceBiologyPublications

sb_pubs = SpaceBiologyPublications()
publications = sb_pubs.fetch_curated_publications()
# Returns: 608+ publications with PMC IDs and links
```

**CLI Command**:
```powershell
python -m knowledge_graph.cli acquire-curated
```

**Priority**: ⭐⭐⭐⭐⭐ (Highest - pre-validated space biology papers)

---

### 2. 🧬 NASA GeneLab

**Source**: https://genelab-data.ndc.nasa.gov

**Description**: Omics datasets from spaceflight and ground-based analog experiments

**Key Features**:
- RNA-sequencing (transcriptomics)
- Proteomics
- Metabolomics
- Epigenomics
- Multiple model organisms (mouse, rat, human, plants, microbes)
- Flight and ground control data

**API Access**: Yes (REST API available)

**Usage**:
```python
from knowledge_graph.data_acquisition import GeneLabAcquisition

genelab = GeneLabAcquisition()
datasets = genelab.search_datasets(
    organism="Mus musculus",
    assay_type="RNA sequencing",
    factor="Spaceflight"
)
```

**Data Types**:
- GLDS datasets (GeneLab Data System)
- Associated publications (PMIDs)
- Processed gene expression data
- Experimental metadata

**Priority**: ⭐⭐⭐⭐⭐ (Highest - experimental data)

---

### 3. 🔬 NASA Open Science Data Repository (OSDR)

**Source**: https://www.nasa.gov/osdr/

**Description**: Comprehensive repository for spaceflight and space-relevant research data

**Key Features**:
- Multi-omics data (genomics, transcriptomics, proteomics, metabolomics)
- Imaging data
- Physiological data
- Environmental data
- Mission metadata
- Unified data portal

**API Access**: Yes

**Usage**:
```python
from knowledge_graph.nasa_resources import NASAOSDR

osdr = NASAOSDR()
datasets = osdr.search_datasets(
    query="microgravity",
    data_type="transcriptomics",
    organism="Homo sapiens"
)
```

**Integration Points**:
- Links to publications (PMIDs)
- Cross-references with GeneLab
- Mission and experiment context

**Priority**: ⭐⭐⭐⭐⭐ (Highest - comprehensive data)

---

### 4. 📚 NASA Task Book

**Source**: https://taskbook.nasaprs.com/tbp/

**Description**: Database of NASA-funded research projects and grants

**Key Features**:
- Research project descriptions
- Principal investigators
- Funding information
- Project objectives and methods
- Expected results and outcomes
- Associated publications

**API Access**: Limited (may require authentication)

**Usage**:
```python
from knowledge_graph.nasa_resources import NASATaskBook

taskbook = NASATaskBook()
projects = taskbook.search_projects(
    keyword="muscle atrophy",
    division="Space Biology",
    status="Active"
)
```

**Data Types**:
- Task/Project metadata
- Publication links
- Research objectives
- Timeline information

**Status**: ⚠️ Partial integration (authentication may be required)

**Priority**: ⭐⭐⭐ (Medium - metadata/context)

---

### 5. 🚀 NASA Space Life Sciences Laboratory (NSLSL)

**Source**: https://public.ksc.nasa.gov/nslsl/

**Description**: Kennedy Space Center facility for space biology research

**Key Features**:
- Ground-based research capabilities
- Pre-flight hardware testing
- Cell culture facilities
- Molecular biology labs
- Microbiology facilities
- Plant biology research

**API Access**: Limited

**Usage**:
```python
from knowledge_graph.nasa_resources import NASANSLSL

nslsl = NASANSLSL()
facility_info = nslsl.get_facility_info()
experiments = nslsl.search_experiments(keyword="plant biology")
```

**Status**: ⚠️ Partial integration (web scraping may be required)

**Priority**: ⭐⭐ (Low - facility information)

---

### 6. 📖 PubMed/PubMed Central

**Source**: https://pubmed.ncbi.nlm.nih.gov

**Description**: Comprehensive biomedical literature database

**Key Features**:
- 35+ million citations
- Full text via PubMed Central
- NCBI E-utilities API
- MeSH term indexing
- Citation network

**API Access**: Yes (E-utilities)

**Usage**:
```python
from knowledge_graph.data_acquisition import PubMedAcquisition

pubmed = PubMedAcquisition()
pmids = pubmed.search_space_biology_papers(max_results=1000)
papers = pubmed.fetch_paper_details(pmids)
```

**Priority**: ⭐⭐⭐⭐⭐ (Highest - literature foundation)

---

## Integrated Data Acquisition

### Using All Sources Together

```python
from knowledge_graph.nasa_resources import IntegratedDataAcquisition

# Initialize integrated client
integrated = IntegratedDataAcquisition()

# Acquire from all sources
results = integrated.acquire_all_sources(
    use_curated=True,      # jgalazka/SB_publications
    use_pubmed=True,       # PubMed/PMC
    use_genelab=True,      # NASA GeneLab
    use_osdr=True,         # NASA OSDR
    max_papers=1000
)

print(f"Curated publications: {len(results['curated_publications'])}")
print(f"PubMed papers: {len(results['pubmed_papers'])}")
print(f"GeneLab datasets: {len(results['genelab_datasets'])}")
print(f"OSDR datasets: {len(results['osdr_datasets'])}")
print(f"Total: {results['total_publications']} publications")
```

### Priority-Based Acquisition

Get the most valuable papers first:

```python
# Get top 100 priority papers
papers = integrated.get_priority_papers(limit=100)

# Priority order:
# 1. Curated Space Biology publications (validated)
# 2. Recent high-impact PubMed papers
# 3. Papers linked to GeneLab/OSDR datasets
```

## CLI Commands

### List Available Sources

```powershell
python -m knowledge_graph.cli list-nasa-sources
```

**Output**:
```
======================================================================
NASA Space Biology Data Sources
======================================================================

✓ Integrated Curated Space Biology Publications
   URL: https://github.com/jgalazka/SB_publications
   Type: Publications
   Description: 608+ open access papers since 2010

✓ Integrated NASA GeneLab
   URL: https://genelab-data.ndc.nasa.gov
   Type: Omics Data
   Description: Omics datasets from spaceflight experiments

✓ Integrated NASA OSDR
   URL: https://www.nasa.gov/osdr/
   Type: Multi-omics, Imaging
   Description: Open Science Data Repository

⚠ Partial NASA Task Book
   URL: https://taskbook.nasaprs.com
   Type: Project Info
   Description: Research project metadata

⚠ Partial NASA NSLSL
   URL: https://public.ksc.nasa.gov/nslsl
   Type: Experiments
   Description: Space Life Sciences Laboratory

✓ Integrated PubMed/PMC
   URL: https://pubmed.ncbi.nlm.nih.gov
   Type: Publications
   Description: Biomedical literature database
```

### Acquire Curated Publications

```powershell
python -m knowledge_graph.cli acquire-curated --output data/raw/curated.json
```

**Output**: 608+ curated space biology papers with PMC links

### Acquire from All Sources

```powershell
python -m knowledge_graph.cli acquire-all --max-papers 1000 --output data/raw/all_sources.json
```

**Output**: JSON file with data from all sources:
```json
{
  "curated_publications": [...],
  "pubmed_papers": [...],
  "genelab_datasets": [...],
  "osdr_datasets": [...],
  "total_publications": 1608,
  "acquisition_timestamp": "2025-10-01T12:00:00"
}
```

## Data Flow Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Acquisition Layer                    │
└─────────────────────────────────────────────────────────────┘
                            ↓
    ┌───────────────────────┼───────────────────────┐
    ↓                       ↓                       ↓
┌─────────┐         ┌─────────────┐         ┌─────────────┐
│ Curated │         │   PubMed    │         │   GeneLab   │
│ SB Pubs │────────▶│     API     │────────▶│   Datasets  │
│ (GitHub)│         │ (E-utils)   │         │ (Omics)     │
└─────────┘         └─────────────┘         └─────────────┘
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            ↓
    ┌───────────────────────┼───────────────────────┐
    ↓                       ↓                       ↓
┌─────────┐         ┌─────────────┐         ┌─────────────┐
│  OSDR   │         │ Task Book   │         │    NSLSL    │
│ (NASA)  │         │   (NASA)    │         │   (KSC)     │
└─────────┘         └─────────────┘         └─────────────┘
    │                       │                       │
    └───────────────────────┼───────────────────────┘
                            ↓
                ┌───────────────────────┐
                │ Integrated Collection │
                │  (All Sources Merged) │
                └───────────────────────┘
                            ↓
                ┌───────────────────────┐
                │   ETL Pipeline        │
                │ (Text Processing)     │
                └───────────────────────┘
                            ↓
                ┌───────────────────────┐
                │  Knowledge Graph      │
                │     (Neo4j)           │
                └───────────────────────┘
```

## Benefits of Integration

### 1. **Comprehensive Coverage**
- 608+ curated papers (high quality)
- 10,000+ PubMed papers (broad coverage)
- 200+ GeneLab datasets (experimental data)
- 100+ OSDR datasets (multi-omics)

### 2. **Data Triangulation**
- Cross-validate findings across sources
- Link publications → datasets → experiments
- Trace data provenance

### 3. **Context Enrichment**
- Mission metadata from OSDR
- Project context from Task Book
- Experimental details from GeneLab

### 4. **Quality Assurance**
- Curated publications = pre-validated
- GeneLab datasets = peer-reviewed
- Multiple sources = higher confidence

## Implementation Status

| Source | Status | API Access | Data Available | Priority |
|--------|--------|-----------|----------------|----------|
| **Curated SB Pubs** | ✅ Complete | ✅ Yes (GitHub) | 608+ papers | ⭐⭐⭐⭐⭐ |
| **PubMed/PMC** | ✅ Complete | ✅ Yes (E-utils) | 35M+ papers | ⭐⭐⭐⭐⭐ |
| **GeneLab** | ✅ Complete | ✅ Yes (REST) | 200+ datasets | ⭐⭐⭐⭐⭐ |
| **OSDR** | ✅ Complete | ✅ Yes (REST) | 100+ datasets | ⭐⭐⭐⭐⭐ |
| **Task Book** | ⚠️ Partial | ⚠️ Limited | Project metadata | ⭐⭐⭐ |
| **NSLSL** | ⚠️ Partial | ⚠️ Limited | Facility info | ⭐⭐ |

## Next Steps

1. **Test Integration**:
   ```powershell
   python -m knowledge_graph.cli acquire-curated
   python -m knowledge_graph.cli list-nasa-sources
   ```

2. **Build Knowledge Graph**:
   ```powershell
   python -m knowledge_graph.cli build --papers 1000
   ```

3. **Explore Data**:
   - Check `data/raw/curated.json` for curated papers
   - View `data/raw/all_sources.json` for integrated data

## References

- **Curated Publications**: https://github.com/jgalazka/SB_publications
- **NASA OSDR**: https://www.nasa.gov/osdr/
- **NASA GeneLab**: https://genelab-data.ndc.nasa.gov
- **NASA Task Book**: https://taskbook.nasaprs.com
- **NSLSL**: https://public.ksc.nasa.gov/nslsl/
- **PubMed**: https://pubmed.ncbi.nlm.nih.gov

## Questions?

For issues or questions about data acquisition:
1. Check logs: `data/logs/kg_construction.log`
2. Test individual sources with CLI commands
3. Review source-specific documentation

---

**Updated**: October 1, 2025
**Integration**: Complete for primary sources (Curated, PubMed, GeneLab, OSDR)

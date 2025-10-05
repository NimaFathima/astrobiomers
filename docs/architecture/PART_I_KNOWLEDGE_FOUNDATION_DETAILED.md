# Part I: The Knowledge Foundation - Space Biology Knowledge Graph

## Overview

The Knowledge Foundation is the **bedrock** of the Space Biology Knowledge Engine. All advanced features—from interactive visualizations to AI-powered querying—depend on the quality, accuracy, and comprehensiveness of this foundational layer. This is achieved through a **Biomedical Knowledge Graph (BKG)**, a powerful paradigm for integrating heterogeneous data and enabling inference in complex domains like space biology.

## 1.1 A Semantic Model for Space Biology: Defining the Schema

### Formal Definition

A Biomedical Knowledge Graph is formally defined as a structured framework:

**G = (E, R, T)**

Where:
- **E** = Set of entities (nodes) representing biological concepts
- **R** = Set of relations (edge types) defining semantic connections
- **T** = Set of factual triples (head_entity, relation, tail_entity)

This graph-based data model provides a flexible and powerful alternative to traditional relational databases, enabling:
- **Multi-hop reasoning**: Traverse complex relationship paths
- **Semantic querying**: Query by meaning, not just keywords
- **Knowledge inference**: Derive new facts from existing relationships
- **Heterogeneous integration**: Combine diverse data types seamlessly

### 1.1.1 Entity Types: The Nodes of Knowledge

The selection of entity types dictates the analytical capabilities of the entire system. A robust ontology for space biology must capture the **multi-scale nature** of the domain, from molecular components to whole-organism physiology and experimental context.

#### **Category 1: Biological Entities**

This category forms the core of biological knowledge, spanning from molecular to organismal scales.

##### **1.1.1.1 Molecular Entities**

```cypher
// Gene Node
CREATE (:Gene {
  id: String,                    // HGNC ID or NCBI Gene ID
  symbol: String,                // e.g., "TP53"
  name: String,                  // Full gene name
  aliases: [String],             // Alternative symbols
  ncbi_gene_id: String,
  ensembl_id: String,
  chromosome: String,            // Chromosomal location
  organism_id: String,           // FK to Organism
  description: Text,
  GO_annotations: [String],      // GO term IDs
  created_at: DateTime,
  updated_at: DateTime
})

// Protein Node
CREATE (:Protein {
  id: String,                    // UniProt ID
  name: String,
  uniprot_id: String,
  gene_id: String,               // FK to Gene
  sequence: Text,                // Amino acid sequence
  molecular_weight: Float,       // kDa
  isoelectric_point: Float,
  function: Text,
  subcellular_location: [String],
  post_translational_modifications: [String],
  domains: [String],             // Protein domains
  pfam_ids: [String],
  created_at: DateTime
})

// Metabolite Node
CREATE (:Metabolite {
  id: String,                    // HMDB ID, ChEBI ID, or PubChem CID
  name: String,
  hmdb_id: String,
  chebi_id: String,
  pubchem_cid: String,
  formula: String,               // Chemical formula
  molecular_weight: Float,
  inchi: String,                 // InChI identifier
  smiles: String,                // SMILES structure
  pathways: [String],            // KEGG pathway IDs
  biological_role: Text,
  created_at: DateTime
})

// RNA Transcript Node
CREATE (:RNATranscript {
  id: String,                    // Ensembl transcript ID
  type: String,                  // mRNA, miRNA, lncRNA, etc.
  gene_id: String,               // FK to Gene
  ensembl_transcript_id: String,
  sequence: Text,
  length: Integer,               // Nucleotides
  biotype: String,
  created_at: DateTime
})
```

##### **1.1.1.2 Functional Entities**

```cypher
// Biological Pathway Node
CREATE (:BiologicalPathway {
  id: String,                    // KEGG ID, Reactome ID, or WikiPathways ID
  name: String,                  // e.g., "PI3K-Akt Signaling Pathway"
  kegg_id: String,
  reactome_id: String,
  wikipathways_id: String,
  description: Text,
  category: String,              // e.g., "Signal Transduction", "Metabolism"
  organism_specific: Boolean,
  organism_id: String,
  components: [String],          // Gene/protein IDs
  created_at: DateTime
})

// Molecular Function Node (GO Term)
CREATE (:MolecularFunction {
  id: String,                    // GO ID (e.g., "GO:0003674")
  go_id: String,
  name: String,                  // e.g., "kinase activity"
  definition: Text,
  synonyms: [String],
  namespace: String,             // "molecular_function"
  parent_terms: [String],        // Parent GO term IDs
  child_terms: [String],         // Child GO term IDs
  is_obsolete: Boolean,
  created_at: DateTime
})

// Biological Process Node (GO Term)
CREATE (:BiologicalProcess {
  id: String,                    // GO ID (e.g., "GO:0008150")
  go_id: String,
  name: String,                  // e.g., "cell proliferation"
  definition: Text,
  synonyms: [String],
  namespace: String,             // "biological_process"
  parent_terms: [String],
  child_terms: [String],
  is_obsolete: Boolean,
  created_at: DateTime
})

// Cellular Component Node (GO Term)
CREATE (:CellularComponent {
  id: String,                    // GO ID (e.g., "GO:0005575")
  go_id: String,
  name: String,                  // e.g., "mitochondrion"
  definition: Text,
  synonyms: [String],
  namespace: String,             // "cellular_component"
  parent_terms: [String],
  child_terms: [String],
  is_obsolete: Boolean,
  created_at: DateTime
})
```

##### **1.1.1.3 Anatomical Entities**

```cypher
// Cell Type Node
CREATE (:CellType {
  id: String,                    // Cell Ontology (CL) ID
  cl_id: String,                 // e.g., "CL:0000057" (fibroblast)
  name: String,                  // e.g., "Osteoblast"
  synonyms: [String],
  definition: Text,
  tissue_id: String,             // FK to Tissue
  characteristic_markers: [String], // Gene/protein markers
  functions: [Text],
  parent_cell_types: [String],
  created_at: DateTime
})

// Tissue Node
CREATE (:Tissue {
  id: String,                    // UBERON ID
  uberon_id: String,             // e.g., "UBERON:0002481" (bone tissue)
  name: String,                  // e.g., "Skeletal Muscle"
  synonyms: [String],
  definition: Text,
  organ_id: String,              // FK to Organ
  cell_types: [String],          // Cell type IDs
  functions: [Text],
  created_at: DateTime
})

// Organ Node
CREATE (:Organ {
  id: String,                    // UBERON ID
  uberon_id: String,
  name: String,                  // e.g., "Heart"
  synonyms: [String],
  definition: Text,
  system_id: String,             // FK to PhysiologicalSystem
  tissues: [String],             // Tissue IDs
  functions: [Text],
  created_at: DateTime
})

// Physiological System Node
CREATE (:PhysiologicalSystem {
  id: String,                    // Custom or UBERON ID
  name: String,                  // e.g., "Cardiovascular System"
  uberon_id: String,
  synonyms: [String],
  definition: Text,
  organs: [String],              // Organ IDs
  primary_functions: [Text],
  regulatory_mechanisms: [Text],
  created_at: DateTime
})
```

##### **1.1.1.4 Phenotypic Entities**

```cypher
// Disease Node
CREATE (:Disease {
  id: String,                    // Mondo Disease Ontology ID or ICD-10
  mondo_id: String,              // e.g., "MONDO:0005015" (diabetes)
  icd10_code: String,
  name: String,                  // e.g., "Osteoporosis"
  synonyms: [String],
  definition: Text,
  category: String,              // e.g., "Metabolic", "Musculoskeletal"
  affected_systems: [String],    // PhysiologicalSystem IDs
  symptoms: [String],            // Phenotype IDs
  known_causes: [Text],
  treatments: [String],          // Countermeasure IDs
  created_at: DateTime
})

// Phenotype Node
CREATE (:Phenotype {
  id: String,                    // HPO (Human Phenotype Ontology) ID
  hpo_id: String,                // e.g., "HP:0000939" (osteoporosis)
  name: String,                  // e.g., "Bone Density Loss"
  synonyms: [String],
  definition: Text,
  affected_system: String,       // e.g., "Musculoskeletal"
  severity_scale: String,        // e.g., "Mild/Moderate/Severe"
  measurable: Boolean,           // Can it be quantified?
  measurement_units: String,     // e.g., "g/cm²" for bone density
  parent_phenotypes: [String],   // Parent HPO term IDs
  associated_genes: [String],    // Gene IDs
  created_at: DateTime
})
```

#### **Category 2: Organism Entities**

This category provides taxonomic and genetic context for experimental findings.

```cypher
// Species/Organism Node
CREATE (:Organism {
  id: String,                    // NCBI Taxonomy ID
  ncbi_taxon_id: String,         // e.g., "9606" for Homo sapiens
  scientific_name: String,       // e.g., "Mus musculus"
  common_name: String,           // e.g., "Mouse"
  taxonomy: {
    kingdom: String,             // "Animalia"
    phylum: String,              // "Chordata"
    class: String,               // "Mammalia"
    order: String,               // "Rodentia"
    family: String,              // "Muridae"
    genus: String,               // "Mus"
    species: String              // "musculus"
  },
  model_organism: Boolean,       // Commonly used in research?
  genome_size: Integer,          // Base pairs
  chromosome_count: Integer,
  genome_assembly: String,       // e.g., "GRCh38" for human
  space_research_relevance: Text,
  created_at: DateTime
})

// Strain/Genotype Node
CREATE (:Strain {
  id: String,                    // Custom or MGI ID for mice
  name: String,                  // e.g., "C57BL/6J"
  organism_id: String,           // FK to Organism
  genetic_background: String,
  notable_mutations: [String],   // Gene IDs with mutations
  phenotypic_characteristics: [String], // Phenotype IDs
  commonly_used_for: [Text],     // Research applications
  source: String,                // e.g., "Jackson Laboratory"
  created_at: DateTime
})
```

#### **Category 3: Environmental & Experimental Entities**

This category captures the unique aspects of space biology research.

##### **1.1.1.5 Stressor Entities**

```cypher
// Stressor Node
CREATE (:Stressor {
  id: String,                    // Custom ID
  type: String,                  // ENUM: "Microgravity", "Radiation", "Isolation", etc.
  name: String,                  // e.g., "Simulated Microgravity"
  description: Text,
  category: String,              // "Physical", "Environmental", "Psychological"
  
  // Type-specific parameters (stored as JSON)
  parameters: {
    // For Microgravity:
    gravity_level: Float,        // G-force (0 for true microgravity)
    simulation_method: String,   // "Clinostat", "RPM", "Parabolic Flight", "ISS"
    rpm: Integer,                // For rotating devices
    
    // For Radiation:
    radiation_type: String,      // "GCR", "SPE", "X-ray", "Gamma"
    particle_type: String,       // "Proton", "Heavy Ion", "Electron"
    dose: Float,                 // Gray (Gy)
    dose_rate: Float,            // Gy/day
    energy: Float,               // MeV
    
    // For Environmental:
    duration: String,            // e.g., "30 days"
    intensity: String,           // "Low", "Moderate", "High"
    exposure_pattern: String     // "Acute", "Chronic", "Intermittent"
  },
  
  ground_analog: Boolean,        // Is this a ground-based simulation?
  flight_analog: Boolean,        // Parabolic flight, drop tower?
  space_environment: Boolean,    // True spaceflight condition?
  
  biological_effects_summary: Text,
  affected_systems: [String],    // PhysiologicalSystem IDs
  
  created_at: DateTime
})
```

##### **1.1.1.6 Countermeasure Entities**

```cypher
// Countermeasure Node
CREATE (:Countermeasure {
  id: String,                    // Custom ID
  type: String,                  // "Exercise", "Pharmacological", "Nutritional", "Behavioral"
  name: String,                  // e.g., "Resistive Exercise Protocol"
  description: Text,
  
  // Type-specific parameters
  parameters: {
    // For Exercise:
    exercise_type: String,       // "Aerobic", "Resistive", "Combined"
    intensity: String,           // "Low", "Moderate", "High"
    duration_minutes: Integer,
    frequency_per_week: Integer,
    equipment: String,           // e.g., "ARED", "Treadmill", "Cycle Ergometer"
    
    // For Pharmacological:
    drug_name: String,
    drug_class: String,
    dosage: String,
    administration_route: String, // "Oral", "IV", "IM", etc.
    
    // For Nutritional:
    supplement_name: String,
    nutrient_type: String,       // "Vitamin", "Mineral", "Protein", etc.
    daily_dose: String
  },
  
  target_stressors: [String],    // Stressor IDs it aims to counteract
  target_phenotypes: [String],   // Phenotype IDs it aims to prevent/treat
  efficacy_evidence: String,     // "Strong", "Moderate", "Weak", "Inconclusive"
  side_effects: [Text],
  
  nasa_approved: Boolean,        // Approved for ISS use?
  operational_constraints: Text, // Space-specific limitations
  
  created_at: DateTime
})
```

##### **1.1.1.7 Experimental Context Entities**

```cypher
// Space Mission Node
CREATE (:SpaceMission {
  id: String,                    // Custom ID
  name: String,                  // e.g., "ISS Expedition 68"
  mission_type: String,          // "ISS", "Shuttle", "Artemis", "Commercial"
  launch_date: Date,
  return_date: Date,
  duration_days: Integer,
  
  vehicle: String,               // "ISS", "Space Shuttle", "SpaceX Dragon", etc.
  module: String,                // For ISS: "Columbus", "Destiny", "Kibo"
  
  crew_size: Integer,
  crew_members: [String],        // Names or IDs
  
  research_focus: [Text],        // Primary research areas
  biological_experiments: [String], // Experiment IDs
  
  microgravity_exposure: Float,  // Average G-level
  radiation_exposure_msv: Float, // Total mission dose
  
  mission_url: String,           // NASA mission page
  created_at: DateTime
})

// Ground Analog Study Node
CREATE (:GroundAnalog {
  id: String,                    // Custom ID
  name: String,                  // e.g., "60-Day Bed Rest Study"
  analog_type: String,           // "Bed Rest", "Hindlimb Unloading", "Dry Immersion", "HERA", "Antarctic", "Cave"
  description: Text,
  
  simulated_stressor: String,    // Stressor ID (e.g., microgravity effects)
  fidelity: String,              // "High", "Moderate", "Low" - how well it simulates space
  
  location: String,              // Where conducted
  facility: String,              // e.g., "DLR :envihab", "MEDES Clinic"
  
  start_date: Date,
  end_date: Date,
  duration_days: Integer,
  
  participant_count: Integer,
  participant_demographics: {
    age_range: String,
    sex_distribution: String,
    health_status: String
  },
  
  experimental_protocol: Text,
  countermeasures_tested: [String], // Countermeasure IDs
  
  created_at: DateTime
})

// Research Payload Node
CREATE (:ResearchPayload {
  id: String,                    // NASA payload ID
  name: String,                  // e.g., "Rodent Research-1"
  payload_type: String,          // "Biology", "Biotechnology", "Human Research"
  
  mission_id: String,            // FK to SpaceMission
  launch_date: Date,
  return_date: Date,
  
  hardware: String,              // e.g., "Rodent Habitat"
  organisms_studied: [String],   // Organism IDs
  sample_types: [String],        // "Tissue", "Blood", "Cells", etc.
  
  research_objectives: [Text],
  principal_investigator: String,
  institution: String,
  
  genelab_accession: String,     // Link to GeneLab dataset
  osdr_accession: String,        // Link to OSDR
  
  data_types: [String],          // "RNA-seq", "Proteomics", "Metabolomics", "Imaging"
  
  created_at: DateTime
})

// Dataset Node
CREATE (:Dataset {
  id: String,                    // GeneLab accession number or OSDR ID
  genelab_id: String,            // e.g., "GLDS-242"
  osdr_id: String,               // OSDR identifier
  title: String,
  description: Text,
  
  data_type: String,             // "Transcriptomics", "Proteomics", "Metabolomics", "Imaging"
  assay_type: String,            // "RNA-seq", "Microarray", "Mass Spec", etc.
  
  organism_id: String,           // FK to Organism
  tissue_types: [String],        // Tissue IDs
  
  experiment_id: String,         // FK to SpaceMission or GroundAnalog
  stressors: [String],           // Stressor IDs
  
  sample_count: Integer,
  control_count: Integer,
  treatment_count: Integer,
  
  publication_ids: [String],     // FK to ResearchPaper (PMIDs)
  
  data_repository_url: String,
  download_url: String,
  file_formats: [String],
  total_size_gb: Float,
  
  processed: Boolean,            // Has it been processed by our pipeline?
  processed_date: DateTime,
  
  created_at: DateTime
})
```

#### **Category 4: Bibliographic Entities**

This category links knowledge back to its source.

```cypher
// Research Paper Node
CREATE (:ResearchPaper {
  id: String,                    // PMID (primary) or DOI
  pmid: String,                  // PubMed ID
  doi: String,                   // Digital Object Identifier
  pmc_id: String,                // PubMed Central ID
  
  title: String,
  abstract: Text,
  full_text: Text,               // If available from PMC
  
  authors: [String],             // Author names
  author_affiliations: [{
    author: String,
    institution: String,
    country: String
  }],
  
  corresponding_author: String,
  corresponding_email: String,
  
  journal: String,
  journal_issn: String,
  volume: String,
  issue: String,
  pages: String,
  
  publication_date: Date,
  publication_year: Integer,
  
  keywords: [String],            // Author keywords
  mesh_terms: [String],          // MeSH subject headings
  
  publication_type: [String],    // "Research Article", "Review", "Case Study"
  
  citation_count: Integer,       // From external sources
  cited_by: [String],            // PMIDs of citing papers
  references: [String],          // PMIDs of referenced papers
  
  funding_sources: [Text],       // e.g., "NASA Grant NNX15AL12G"
  nasa_funded: Boolean,
  
  open_access: Boolean,
  full_text_available: Boolean,
  pdf_url: String,
  
  datasets: [String],            // Dataset IDs mentioned/used
  genelab_datasets: [String],    // GeneLab accessions
  
  // NLP Processing metadata
  entities_extracted: Boolean,
  relationships_extracted: Boolean,
  extraction_date: DateTime,
  extraction_confidence: Float,
  
  embedding_vector_id: String,   // Reference to vector in vector DB
  
  created_at: DateTime,
  last_updated: DateTime
})
```

---

## 1.2 Defining Relationships: The Edges of Understanding

The **edges** in the knowledge graph encode the active knowledge, transforming a list of entities into a web of interconnected facts. Relationships must be semantically precise to enable meaningful queries and reasoning.

### 1.2.1 Molecular Relationships

```cypher
// Gene-Protein Relationships
CREATE (gene:Gene)-[:CODES_FOR {
  transcript_id: String,         // Ensembl transcript ID
  evidence_code: String,         // e.g., "IDA" (Inferred from Direct Assay)
  confidence: Float,             // 0-1
  source: String                 // Database source
}]->(protein:Protein)

// Gene-Function Relationships
CREATE (gene:Gene)-[:HAS_MOLECULAR_FUNCTION {
  go_evidence_code: String,      // GO evidence codes
  evidence: Text,
  confidence: Float,
  source_publication: String     // PMID
}]->(function:MolecularFunction)

// Protein-Pathway Relationships
CREATE (protein:Protein)-[:PARTICIPATES_IN {
  role: String,                  // "catalyst", "regulator", "substrate"
  evidence: Text,
  kegg_pathway_id: String,
  confidence: Float,
  source_publication: String
}]->(pathway:BiologicalPathway)

// Protein-Protein Interactions
CREATE (protein1:Protein)-[:INTERACTS_WITH {
  interaction_type: String,      // "physical", "genetic", "regulatory"
  detection_method: String,      // "yeast two-hybrid", "co-IP", "predicted"
  interaction_score: Float,      // e.g., STRING score
  binding_site: String,          // If known
  evidence: Text,
  confidence: Float,
  source_database: String,       // "STRING", "BioGRID", "IntAct"
  source_publication: String
}]->(protein2:Protein)

// Gene Homology
CREATE (gene1:Gene)-[:IS_HOMOLOG_OF {
  homology_type: String,         // "ortholog", "paralog"
  sequence_identity: Float,      // Percentage
  e_value: Float,                // BLAST e-value
  source_database: String        // "HomoloGene", "OrthoDB"
}]->(gene2:Gene)
```

### 1.2.2 Expression & Regulation Relationships

```cypher
// Gene/Protein Expression in Tissue
CREATE (gene:Gene)-[:EXPRESSED_IN {
  tissue_id: String,
  expression_level: String,      // "High", "Medium", "Low"
  tpm_value: Float,              // Transcripts Per Million
  developmental_stage: String,   // "Adult", "Embryonic", etc.
  conditions: String,            // "Baseline", "Stressed"
  evidence: String,
  source_database: String,       // "GTEx", "ENCODE"
  source_publication: String
}]->(tissue:Tissue)

// Stressor Effects on Gene/Protein
CREATE (stressor:Stressor)-[:AFFECTS {
  effect_type: String,           // "upregulation", "downregulation", "no_change"
  magnitude: Float,              // Fold change
  log2_fold_change: Float,
  p_value: Float,
  adjusted_p_value: Float,
  statistical_method: String,    // "DESeq2", "edgeR", "t-test"
  
  organism_id: String,           // What organism was studied
  tissue_id: String,             // What tissue was examined
  cell_type_id: String,          // If cell-type specific
  
  timepoint: String,             // "6h", "7d", "30d" post-exposure
  duration: String,              // Duration of exposure
  
  experimental_conditions: {
    sample_size: Integer,
    control_group: String,
    treatment_group: String,
    additional_factors: Text
  },
  
  evidence: Text,
  confidence: Float,             // 0-1, based on statistical significance
  source_dataset: String,        // Dataset ID if from omics data
  source_publication: String     // PMID
}]->(target:Gene|Protein|Pathway)

// Regulatory Relationships
CREATE (regulator:Gene|Protein)-[:REGULATES {
  regulation_type: String,       // "activates", "inhibits", "modulates"
  mechanism: String,             // "transcriptional", "post-translational", "epigenetic"
  evidence: Text,
  confidence: Float,
  source_publication: String
}]->(target:Gene|Protein|BiologicalProcess)
```

### 1.2.3 Phenotypic & Disease Relationships

```cypher
// Stressor-Phenotype Associations
CREATE (stressor:Stressor)-[:CAUSES {
  phenotype_id: String,
  mechanism: Text,               // Biological mechanism if known
  severity: String,              // "Mild", "Moderate", "Severe"
  onset_time: String,            // How quickly phenotype appears
  reversibility: Boolean,        // Can it be reversed?
  organism_id: String,           // What organism exhibits this
  incidence_rate: Float,         // Percentage affected
  
  evidence: Text,
  confidence: Float,
  source_publication: String
}]->(phenotype:Phenotype)

// Phenotype-Gene Associations
CREATE (phenotype:Phenotype)-[:ASSOCIATED_WITH_GENE {
  association_type: String,      // "causative", "modifier", "correlated"
  penetrance: Float,             // 0-1, how often gene causes phenotype
  evidence: Text,
  confidence: Float,
  source_database: String,       // "ClinVar", "OMIM", "GWAS Catalog"
  source_publication: String
}]->(gene:Gene)

// Disease-Phenotype Relationships
CREATE (disease:Disease)-[:HAS_PHENOTYPE {
  frequency: String,             // "Obligate", "Very common", "Occasional"
  onset_age: String,             // When it typically appears
  severity: String,
  evidence: Text,
  source: String                 // "HPO", "Orphanet"
}]->(phenotype:Phenotype)

// Countermeasure Effectiveness
CREATE (countermeasure:Countermeasure)-[:TREATS {
  target_phenotype_id: String,
  efficacy: String,              // "High", "Moderate", "Low"
  response_time: String,         // How quickly it works
  duration_of_effect: String,
  
  study_type: String,            // "RCT", "Observational", "Preclinical"
  sample_size: Integer,
  statistical_significance: Float, // p-value
  
  side_effects: [Text],
  contraindications: [Text],
  
  evidence: Text,
  confidence: Float,
  source_publication: String
}]->(phenotype:Phenotype)
```

### 1.2.4 Experimental Context Relationships

```cypher
// Paper-Entity Relationships
CREATE (paper:ResearchPaper)-[:INVESTIGATES {
  primary_focus: Boolean,        // Is this entity the main subject?
  context: Text,                 // Context in which entity appears
  sentence: Text,                // Exact sentence mentioning entity
  section: String,               // "Abstract", "Methods", "Results", "Discussion"
  extraction_method: String,     // "NER_BioBERT", "Manual"
  extraction_confidence: Float,
  page_number: Integer,
  created_at: DateTime
}]->(entity:Gene|Protein|Phenotype|Stressor)

// Entity-Experiment Relationships
CREATE (entity)-[:STUDIED_IN {
  primary_focus: Boolean,
  outcome_measured: [String],    // What was measured
  sample_type: String,           // "Tissue", "Blood", "Cells"
  methodology: String,           // Experimental technique
  findings_summary: Text,
  statistical_significance: Float,
  created_at: DateTime
}]->(experiment:SpaceMission|GroundAnalog|ResearchPayload)

// Dataset-Entity Relationships
CREATE (dataset:Dataset)-[:CONTAINS_DATA_ON {
  data_type: String,             // "Expression", "Abundance", "Activity"
  measurement_type: String,      // "RNA-seq", "Proteomics"
  number_of_samples: Integer,
  differential_expression: Boolean, // Was DE analysis performed?
  created_at: DateTime
}]->(entity:Gene|Protein|Metabolite)

// Paper Citations
CREATE (paper1:ResearchPaper)-[:CITES]->(paper2:ResearchPaper)

// Funding Relationships
CREATE (paper:ResearchPaper)-[:FUNDED_BY {
  grant_number: String,
  program: String,
  amount: String
}]->(:FundingAgency {name: "NASA"})
```

### 1.2.5 Anatomical & Hierarchical Relationships

```cypher
// Hierarchical relationships
CREATE (child:CellType)-[:PART_OF]->(parent:Tissue)
CREATE (tissue:Tissue)-[:PART_OF]->(organ:Organ)
CREATE (organ:Organ)-[:PART_OF]->(system:PhysiologicalSystem)

// GO Term hierarchies
CREATE (child:MolecularFunction)-[:IS_A]->(parent:MolecularFunction)
CREATE (child:BiologicalProcess)-[:IS_A]->(parent:BiologicalProcess)

// Taxonomic hierarchies
CREATE (strain:Strain)-[:IS_VARIANT_OF]->(organism:Organism)
```

---

## 1.3 Data Sources: Building a Comprehensive Knowledge Base

The BKG will be populated by integrating information from diverse authoritative sources. This integration is a key strength of the knowledge graph approach.

### 1.3.1 Primary Literature

**Source**: PubMed and PubMed Central

**Coverage**: 35+ million citations for biomedical literature

**Integration Strategy**:
```python
# Query for space biology papers
query = """
(space biology[Title/Abstract] OR 
 spaceflight[Title/Abstract] OR 
 microgravity[Title/Abstract] OR 
 space radiation[Title/Abstract] OR 
 International Space Station[Title/Abstract])
AND (gene OR protein OR pathway OR phenotype)
"""

# Fetch papers from last 50 years
date_range = "1974/01/01:2025/12/31"
```

**Extraction Pipeline**:
1. Fetch metadata (title, abstract, authors, MeSH terms)
2. Download full text from PMC when available
3. Extract entities using BioBERT/SciBERT
4. Extract relationships using dependency parsing + ML models
5. Link to existing KG entities (entity resolution)
6. Generate embeddings for semantic search

### 1.3.2 Omics Databases

**Source**: NASA GeneLab

**Website**: https://genelab.nasa.gov/

**Content**: Multi-omics datasets from spaceflight and ground analog studies
- Genomics
- Transcriptomics (RNA-seq, microarray)
- Proteomics
- Metabolomics
- Epigenomics

**Integration Strategy**:
- Query GeneLab API for datasets
- Download processed data (gene expression matrices, DEG lists)
- Create `Dataset` nodes
- Link datasets to:
  - Missions (`SpaceMission` nodes)
  - Organisms studied
  - Genes/proteins with differential expression
  - Publications describing the data

**Example**:
```python
# GLDS-242: Mouse liver gene expression after 29 days on ISS
dataset = {
  "genelab_id": "GLDS-242",
  "organism": "Mus musculus",
  "tissue": "Liver",
  "stressor": "Microgravity",
  "mission": "SpaceX-12",
  "duration_days": 29,
  "deg_count": 547  # Differentially expressed genes
}
```

### 1.3.3 Project Databases

**Source**: NASA Task Book

**Website**: https://taskbook.nasaprs.com/

**Content**: Information about funded research projects
- Project objectives
- Principal Investigators
- Institutions
- Timeline
- Findings

**Integration Strategy**:
- Scrape or API access to Task Book entries
- Create project nodes
- Link projects to:
  - Publications (outputs)
  - Datasets generated
  - Investigators
  - Research topics

### 1.3.4 Public Ontologies

To ensure **semantic consistency** and **interoperability**, the BKG leverages established biomedical vocabularies:

| Ontology | Purpose | Examples | Integration |
|----------|---------|----------|-------------|
| **Gene Ontology (GO)** | Gene functions, biological processes, cellular components | GO:0008150 (biological_process) | Annotate genes/proteins with GO terms |
| **Mondo Disease Ontology** | Diseases and disorders | MONDO:0005015 (diabetes mellitus) | Standardize disease names |
| **Human Phenotype Ontology (HPO)** | Phenotypic abnormalities | HP:0000939 (osteoporosis) | Describe spaceflight-induced phenotypes |
| **UBERON** | Anatomical structures | UBERON:0002481 (bone tissue) | Standardize tissue/organ names |
| **Cell Ontology (CL)** | Cell types | CL:0000057 (fibroblast) | Annotate cell types |
| **NCBI Taxonomy** | Organisms | 9606 (Homo sapiens) | Standardize organism names |
| **SNOMED CT** | Clinical terminology | Comprehensive medical terms | Clinical phenotypes |
| **KEGG** | Pathways and reactions | hsa04151 (PI3K-Akt pathway) | Biological pathways |
| **Reactome** | Biological pathways | R-HSA-1640170 (Cell Cycle) | Detailed pathway maps |
| **ChEBI** | Chemical entities | CHEBI:16541 (protein) | Metabolites, drugs |

**Integration Approach**:
1. **Direct Mapping**: Use ontology IDs as primary identifiers
2. **Term Alignment**: Map extracted entities to ontology terms
3. **Hierarchy Import**: Import parent-child relationships from ontologies
4. **Synonym Expansion**: Use ontology synonyms for entity resolution

### 1.3.5 Additional Specialized Databases

| Database | Content | Use Case |
|----------|---------|----------|
| **UniProt** | Protein sequences and functions | Protein annotation |
| **HGNC** | Human gene nomenclature | Gene name standardization |
| **MGI** | Mouse genome informatics | Mouse gene/phenotype data |
| **STRING** | Protein-protein interactions | Interaction networks |
| **BioGRID** | Genetic and protein interactions | Comprehensive interactions |
| **GTEx** | Gene expression across tissues | Baseline expression data |
| **ClinVar** | Clinical variants | Gene-disease associations |
| **HMDB** | Human metabolome | Metabolite information |
| **PubChem** | Chemical structures | Chemical entity data |

---

## 1.4 Knowledge Graph Construction Pipeline

### Phase 1: Data Acquisition
```
PubMed API → Fetch papers → Store in S3
GeneLab API → Download datasets → Store metadata
Ontology Downloads → OBO format → Import to Neo4j
```

### Phase 2: NLP Processing
```
PDF/Text → Preprocessing → Sentence segmentation
→ BioBERT NER → Entity extraction
→ Dependency parsing → Relationship extraction
→ Entity resolution → Link to ontologies
```

### Phase 3: Graph Population
```
Entities → Create/Update nodes in Neo4j
Relationships → Create edges with properties
Publications → Link everything to sources
Embeddings → Generate and store in vector DB
```

### Phase 4: Quality Assurance
```
Validation rules → Check for inconsistencies
Confidence scoring → Assess reliability
Manual curation → Review low-confidence entries
Feedback loop → Improve extraction models
```

---

## 1.5 Knowledge Graph Statistics (Target)

| Metric | Target |
|--------|--------|
| **Publications** | 10,000+ |
| **Genes** | 20,000+ |
| **Proteins** | 15,000+ |
| **Phenotypes** | 500+ |
| **Stressors** | 50+ |
| **Datasets** | 200+ (from GeneLab) |
| **Relationships** | 500,000+ |
| **Average Confidence** | >0.85 |

---

**Next**: Part II will detail the Interactive Interface layer for visualizing and exploring this knowledge graph.

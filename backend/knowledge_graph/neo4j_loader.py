"""
Neo4j Loader Module for Space Biology Knowledge Graph

Loads processed data into Neo4j graph database:
- Creates schema (constraints, indexes)
- Loads nodes (papers, entities, topics)
- Creates relationships
- Batch processing for efficiency

Author: Space Biology KG Team
Date: October 2025
"""

import logging
from typing import List, Dict, Optional, Set
from collections import defaultdict
import time

from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, ClientError

logger = logging.getLogger(__name__)


class Neo4jLoader:
    """
    Load knowledge graph data into Neo4j database.
    
    Node Types:
    - Paper: Scientific publications
    - Gene: Genes and proteins
    - Disease: Diseases and phenotypes
    - Stressor: Space biology stressors
    - Organism: Model organisms
    - CellType: Cell types
    - Topic: Research topics
    - Intervention: Countermeasures
    
    Relationship Types:
    - MENTIONS: Paper -> Entity
    - UPREGULATES/DOWNREGULATES: Gene -> Gene
    - CAUSES: Stressor -> Phenotype
    - TREATS: Intervention -> Disease
    - INTERACTS_WITH: Gene -> Gene
    - PART_OF: Entity -> Entity
    - HAS_TOPIC: Paper -> Topic
    - STUDIED_IN: Entity -> Organism
    """
    
    def __init__(self, config=None, uri: str = None, user: str = None, password: str = None, database: str = None):
        """
        Initialize Neo4j loader.
        
        Args:
            config: Configuration object
            uri: Neo4j connection URI
            user: Neo4j username
            password: Neo4j password
            database: Neo4j database name
        """
        from knowledge_graph.config import config as default_config
        
        self.config = config or default_config
        
        # Connection parameters
        self.uri = uri or self.config.neo4j_uri
        self.user = user or self.config.neo4j_user
        self.password = password or self.config.neo4j_password
        self.database = database or getattr(self.config, 'neo4j_database', None)
        
        self.driver = None
        self._connect()
        
        logger.info(f"Neo4jLoader initialized (database: {self.database or 'default'})")
    
    def _connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            
            # Test connection
            with self.driver.session(database=self.database) as session:
                result = session.run("RETURN 1 as test")
                result.single()
            
            logger.info(f"Connected to Neo4j at {self.uri}")
            
        except ServiceUnavailable as e:
            logger.error(f"Could not connect to Neo4j: {e}")
            raise
    
    def close(self):
        """Close Neo4j connection."""
        if self.driver:
            self.driver.close()
            logger.info("Neo4j connection closed")
    
    def initialize_schema(self):
        """
        Create database schema: constraints and indexes.
        """
        logger.info("Initializing Neo4j schema...")
        
        with self.driver.session(database=self.database) as session:
            # Constraints (ensure uniqueness)
            constraints = [
                "CREATE CONSTRAINT paper_pmid IF NOT EXISTS FOR (p:Paper) REQUIRE p.pmid IS UNIQUE",
                "CREATE CONSTRAINT gene_symbol IF NOT EXISTS FOR (g:Gene) REQUIRE g.symbol IS UNIQUE",
                "CREATE CONSTRAINT disease_name IF NOT EXISTS FOR (d:Disease) REQUIRE d.name IS UNIQUE",
                "CREATE CONSTRAINT stressor_name IF NOT EXISTS FOR (s:Stressor) REQUIRE s.name IS UNIQUE",
                "CREATE CONSTRAINT phenotype_name IF NOT EXISTS FOR (p:Phenotype) REQUIRE p.name IS UNIQUE",
                "CREATE CONSTRAINT organism_taxid IF NOT EXISTS FOR (o:Organism) REQUIRE o.taxid IS UNIQUE",
                "CREATE CONSTRAINT celltype_id IF NOT EXISTS FOR (c:CellType) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT topic_id IF NOT EXISTS FOR (t:Topic) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT intervention_name IF NOT EXISTS FOR (i:Intervention) REQUIRE i.name IS UNIQUE"
            ]
            
            for constraint in constraints:
                try:
                    session.run(constraint)
                    logger.info(f"Created constraint: {constraint.split()[2]}")
                except ClientError as e:
                    if "EquivalentSchemaRuleAlreadyExists" in str(e):
                        logger.debug(f"Constraint already exists: {constraint.split()[2]}")
                    else:
                        logger.error(f"Error creating constraint: {e}")
            
            # Indexes (improve query performance)
            indexes = [
                "CREATE INDEX paper_doi IF NOT EXISTS FOR (p:Paper) ON (p.doi)",
                "CREATE INDEX paper_year IF NOT EXISTS FOR (p:Paper) ON (p.publication_year)",
                "CREATE INDEX gene_entrez IF NOT EXISTS FOR (g:Gene) ON (g.entrez_id)",
                "CREATE INDEX gene_name IF NOT EXISTS FOR (g:Gene) ON (g.name)",
                "CREATE INDEX disease_mondo IF NOT EXISTS FOR (d:Disease) ON (d.mondo_id)",
                "CREATE INDEX stressor_envo IF NOT EXISTS FOR (s:Stressor) ON (s.envo_id)",
                "CREATE INDEX phenotype_hpo IF NOT EXISTS FOR (p:Phenotype) ON (p.hpo_id)",
                "CREATE INDEX topic_label IF NOT EXISTS FOR (t:Topic) ON (t.label)"
            ]
            
            for index in indexes:
                try:
                    session.run(index)
                    logger.info(f"Created index: {index.split()[2]}")
                except ClientError as e:
                    if "EquivalentSchemaRuleAlreadyExists" in str(e):
                        logger.debug(f"Index already exists: {index.split()[2]}")
                    else:
                        logger.error(f"Error creating index: {e}")
        
        logger.info("Schema initialization complete")
    
    def load_papers(self, papers: List[Dict], batch_size: int = 100):
        """
        Load papers as nodes in Neo4j.
        
        Args:
            papers: List of paper dictionaries
            batch_size: Number of papers per batch
        """
        logger.info(f"Loading {len(papers)} papers...")
        
        cypher = """
        UNWIND $batch as paper
        MERGE (p:Paper {
            id: COALESCE(paper.pmid, paper.pmc_id, paper.doi, paper.title)
        })
        SET p.pmid = paper.pmid,
            p.title = paper.title,
            p.abstract = paper.abstract,
            p.doi = paper.doi,
            p.pmc_id = paper.pmc_id,
            p.publication_year = paper.publication_year,
            p.journal = paper.journal,
            p.authors = paper.authors,
            p.mesh_terms = paper.mesh_terms,
            p.source = paper.source,
            p.curated = paper.curated
        RETURN count(p) as created
        """
        
        loaded = 0
        
        with self.driver.session(database=self.database) as session:
            for i in range(0, len(papers), batch_size):
                batch = papers[i:i + batch_size]
                
                # Prepare batch data
                batch_data = []
                for paper in batch:
                    # Create unique ID using PMID, PMC ID, DOI, or title
                    paper_id = (paper.get('pmid') or 
                              paper.get('pmc_id') or 
                              paper.get('doi') or 
                              paper.get('title', 'unknown'))
                    
                    batch_data.append({
                        'id': paper_id,
                        'pmid': paper.get('pmid'),
                        'title': paper.get('title', ''),
                        'abstract': paper.get('abstract', ''),
                        'doi': paper.get('doi'),
                        'pmc_id': paper.get('pmc_id'),
                        'publication_year': paper.get('publication_year'),
                        'journal': paper.get('journal', ''),
                        'authors': paper.get('authors', []),
                        'mesh_terms': paper.get('mesh_terms', []),
                        'source': paper.get('source', 'pubmed'),
                        'curated': paper.get('curated', False)
                    })
                
                result = session.run(cypher, batch=batch_data)
                count = result.single()['created']
                loaded += count
                
                if (i + batch_size) % 1000 == 0:
                    logger.info(f"Loaded {loaded}/{len(papers)} papers")
        
        logger.info(f"Loaded {loaded} papers total")
    
    def load_entities(self, entities: List[Dict], batch_size: int = 500):
        """
        Load entities as nodes in Neo4j.
        
        Args:
            entities: List of entity dictionaries
            batch_size: Number of entities per batch
        """
        logger.info(f"Loading {len(entities)} entities...")
        
        # Group entities by type
        by_type = defaultdict(list)
        for entity in entities:
            by_type[entity['type']].append(entity)
        
        # Load each type
        for entity_type, type_entities in by_type.items():
            logger.info(f"Loading {len(type_entities)} {entity_type} entities...")
            
            if entity_type in ['GENE', 'PROTEIN']:
                self._load_genes(type_entities, batch_size)
            elif entity_type == 'DISEASE':
                self._load_diseases(type_entities, batch_size)
            elif entity_type == 'STRESSOR':
                self._load_stressors(type_entities, batch_size)
            elif entity_type == 'PHENOTYPE':
                self._load_phenotypes(type_entities, batch_size)
            elif entity_type == 'ORGANISM':
                self._load_organisms(type_entities, batch_size)
            elif entity_type == 'CELL_TYPE':
                self._load_cell_types(type_entities, batch_size)
            elif entity_type == 'INTERVENTION':
                self._load_interventions(type_entities, batch_size)
            else:
                logger.warning(f"Unknown entity type: {entity_type}")
        
        logger.info("Entity loading complete")
    
    def _load_genes(self, genes: List[Dict], batch_size: int):
        """Load gene entities."""
        cypher = """
        UNWIND $batch as gene
        MERGE (g:Gene {symbol: gene.symbol})
        SET g.name = gene.name,
            g.entrez_id = gene.entrez_id,
            g.uniprot_id = gene.uniprot_id,
            g.ensembl_id = gene.ensembl_id,
            g.summary = gene.summary,
            g.go_terms = gene.go_terms
        RETURN count(g) as created
        """
        
        self._batch_load(genes, cypher, batch_size, 'symbol')
    
    def _load_diseases(self, diseases: List[Dict], batch_size: int):
        """Load disease entities."""
        cypher = """
        UNWIND $batch as disease
        MERGE (d:Disease {name: disease.name})
        SET d.mondo_id = disease.mondo_id,
            d.doid = disease.doid,
            d.hpo_id = disease.hpo_id,
            d.definition = disease.definition
        RETURN count(d) as created
        """
        
        self._batch_load(diseases, cypher, batch_size, 'name')
    
    def _load_stressors(self, stressors: List[Dict], batch_size: int):
        """Load stressor entities."""
        cypher = """
        UNWIND $batch as stressor
        MERGE (s:Stressor {name: stressor.name})
        SET s.envo_id = stressor.envo_id,
            s.category = stressor.category,
            s.definition = stressor.definition
        RETURN count(s) as created
        """
        
        self._batch_load(stressors, cypher, batch_size, 'name')
    
    def _load_phenotypes(self, phenotypes: List[Dict], batch_size: int):
        """Load phenotype entities."""
        cypher = """
        UNWIND $batch as phenotype
        MERGE (p:Phenotype {name: phenotype.name})
        SET p.hpo_id = phenotype.hpo_id,
            p.category = phenotype.category,
            p.definition = phenotype.definition
        RETURN count(p) as created
        """
        
        self._batch_load(phenotypes, cypher, batch_size, 'name')
    
    def _load_organisms(self, organisms: List[Dict], batch_size: int):
        """Load organism entities."""
        cypher = """
        UNWIND $batch as organism
        MERGE (o:Organism {taxid: organism.taxid})
        SET o.scientific_name = organism.scientific_name,
            o.common_name = organism.common_name
        RETURN count(o) as created
        """
        
        self._batch_load(organisms, cypher, batch_size, 'taxid')
    
    def _load_cell_types(self, cell_types: List[Dict], batch_size: int):
        """Load cell type entities."""
        cypher = """
        UNWIND $batch as cell
        MERGE (c:CellType {id: cell.id})
        SET c.name = cell.name,
            c.cl_id = cell.cl_id,
            c.definition = cell.definition
        RETURN count(c) as created
        """
        
        self._batch_load(cell_types, cypher, batch_size, 'id')
    
    def _load_interventions(self, interventions: List[Dict], batch_size: int):
        """Load intervention entities."""
        cypher = """
        UNWIND $batch as intervention
        MERGE (i:Intervention {name: intervention.name})
        SET i.type = intervention.type,
            i.description = intervention.description
        RETURN count(i) as created
        """
        
        self._batch_load(interventions, cypher, batch_size, 'name')
    
    def _batch_load(self, items: List[Dict], cypher: str, batch_size: int, key_field: str):
        """Generic batch loading helper."""
        loaded = 0
        
        with self.driver.session(database=self.database) as session:
            for i in range(0, len(items), batch_size):
                batch = items[i:i + batch_size]
                
                # Prepare batch with normalized keys
                batch_data = []
                for item in batch:
                    # Ensure key field exists - prefer canonical_name, then text, then key_field
                    if key_field not in item or not item[key_field]:
                        item[key_field] = item.get('canonical_name') or item.get('text', f'unknown_{i}')
                    
                    batch_data.append(item)
                
                result = session.run(cypher, batch=batch_data)
                count = result.single()['created']
                loaded += count
        
        logger.info(f"Loaded {loaded} items")
    
    def load_relationships(self, relationships: List[Dict], batch_size: int = 500):
        """
        Load relationships between entities.
        
        Args:
            relationships: List of relationship dictionaries
            batch_size: Number of relationships per batch
        """
        logger.info(f"Loading {len(relationships)} relationships...")
        
        cypher = """
        UNWIND $batch as rel
        MATCH (source {name: rel.source})
        MATCH (target {name: rel.target})
        CALL apoc.create.relationship(source, rel.type, {
            confidence: rel.confidence,
            evidence: rel.evidence,
            pmid: rel.pmid,
            extraction_method: rel.method
        }, target) YIELD rel as r
        RETURN count(r) as created
        """
        
        # Alternative without APOC
        cypher_simple = """
        UNWIND $batch as rel
        MATCH (source)
        WHERE source.name = rel.source OR source.symbol = rel.source
        MATCH (target)
        WHERE target.name = rel.target OR target.symbol = rel.target
        MERGE (source)-[r:RELATED {type: rel.type}]->(target)
        SET r.confidence = rel.confidence,
            r.evidence = rel.evidence,
            r.pmids = rel.pmids,
            r.extraction_method = rel.method
        RETURN count(r) as created
        """
        
        loaded = 0
        
        with self.driver.session(database=self.database) as session:
            for i in range(0, len(relationships), batch_size):
                batch = relationships[i:i + batch_size]
                
                # Prepare batch data
                batch_data = []
                for rel in batch:
                    batch_data.append({
                        'source': rel.get('source'),
                        'target': rel.get('target'),
                        'type': rel.get('relation_type', 'RELATED'),
                        'confidence': rel.get('confidence', 0.5),
                        'evidence': rel.get('evidence', ''),
                        'pmids': rel.get('pmids', []),
                        'method': rel.get('extraction_method', 'unknown')
                    })
                
                try:
                    result = session.run(cypher_simple, batch=batch_data)
                    count = result.single()['created']
                    loaded += count
                except Exception as e:
                    logger.error(f"Error loading relationship batch: {e}")
                
                if (i + batch_size) % 5000 == 0:
                    logger.info(f"Loaded {loaded}/{len(relationships)} relationships")
        
        logger.info(f"Loaded {loaded} relationships total")
    
    def load_topics(self, topics: List[Dict], batch_size: int = 100):
        """
        Load research topics.
        
        Args:
            topics: List of topic dictionaries
            batch_size: Number of topics per batch
        """
        logger.info(f"Loading {len(topics)} topics...")
        
        cypher = """
        UNWIND $batch as topic
        MERGE (t:Topic {id: topic.id})
        SET t.label = topic.label,
            t.words = topic.words,
            t.size = topic.size,
            t.trend = topic.trend
        RETURN count(t) as created
        """
        
        loaded = 0
        
        with self.driver.session(database=self.database) as session:
            for i in range(0, len(topics), batch_size):
                batch = topics[i:i + batch_size]
                
                result = session.run(cypher, batch=batch)
                count = result.single()['created']
                loaded += count
        
        logger.info(f"Loaded {loaded} topics")
    
    def create_paper_entity_links(self, papers: List[Dict], batch_size: int = 100):
        """
        Create MENTIONS relationships between papers and entities.
        
        Args:
            papers: List of papers with 'entities' field
            batch_size: Number of papers per batch
        """
        logger.info("Creating paper-entity links...")
        
        cypher = """
        UNWIND $batch as item
        MATCH (p:Paper {id: item.paper_id})
        UNWIND item.entities as entity
        CALL {
            WITH entity
            OPTIONAL MATCH (e:Gene) WHERE e.symbol = entity.text OR e.name = entity.text
            RETURN e AS matched
            UNION
            WITH entity
            OPTIONAL MATCH (e:Disease) WHERE e.name = entity.text
            RETURN e AS matched
            UNION
            WITH entity
            OPTIONAL MATCH (e:Stressor) WHERE e.name = entity.text OR e.name = entity.canonical_name
            RETURN e AS matched
            UNION
            WITH entity
            OPTIONAL MATCH (e:Phenotype) WHERE e.name = entity.text OR e.name = entity.canonical_name
            RETURN e AS matched
        }
        WITH p, matched, entity
        WHERE matched IS NOT NULL
        MERGE (p)-[m:MENTIONS]->(matched)
        SET m.count = COALESCE(entity.count, 1),
            m.confidence = entity.confidence
        RETURN count(m) as created
        """
        
        loaded = 0
        
        with self.driver.session(database=self.database) as session:
            for i in range(0, len(papers), batch_size):
                batch = papers[i:i + batch_size]
                
                # Prepare batch data
                batch_data = []
                for paper in batch:
                    if paper.get('entities'):
                        # Create unique ID same way as in load_papers
                        paper_id = (paper.get('pmid') or 
                                  paper.get('pmc_id') or 
                                  paper.get('doi') or 
                                  paper.get('title', 'unknown'))
                        
                        batch_data.append({
                            'paper_id': paper_id,
                            'entities': paper['entities']
                        })
                
                if batch_data:
                    result = session.run(cypher, batch=batch_data)
                    count = result.single()['created']
                    loaded += count
        
        logger.info(f"Created {loaded} paper-entity links")
    
    def create_paper_topic_links(self, papers: List[Dict], batch_size: int = 100):
        """
        Create HAS_TOPIC relationships between papers and topics.
        
        Args:
            papers: List of papers with 'topic_id' field
            batch_size: Number of papers per batch
        """
        logger.info("Creating paper-topic links...")
        
        cypher = """
        UNWIND $batch as item
        MATCH (p:Paper {id: item.paper_id})
        MATCH (t:Topic {id: item.topic_id})
        MERGE (p)-[h:HAS_TOPIC]->(t)
        SET h.probability = item.probability
        RETURN count(h) as created
        """
        
        loaded = 0
        
        with self.driver.session(database=self.database) as session:
            for i in range(0, len(papers), batch_size):
                batch = papers[i:i + batch_size]
                
                # Prepare batch data
                batch_data = []
                for paper in batch:
                    if paper.get('topic_id') is not None:
                        # Create unique ID same way as in load_papers
                        paper_id = (paper.get('pmid') or 
                                  paper.get('pmc_id') or 
                                  paper.get('doi') or 
                                  paper.get('title', 'unknown'))
                        
                        batch_data.append({
                            'paper_id': paper_id,
                            'topic_id': paper['topic_id'],
                            'probability': paper.get('topic_probability', 0.0)
                        })
                
                if batch_data:
                    result = session.run(cypher, batch=batch_data)
                    count = result.single()['created']
                    loaded += count
        
        logger.info(f"Created {loaded} paper-topic links")
    
    def get_graph_statistics(self) -> Dict:
        """Get statistics about the knowledge graph."""
        with self.driver.session(database=self.database) as session:
            stats = {}
            
            # Node counts
            result = session.run("""
                MATCH (n)
                RETURN labels(n)[0] as label, count(n) as count
            """)
            
            node_counts = {record['label']: record['count'] for record in result}
            stats['nodes'] = node_counts
            stats['total_nodes'] = sum(node_counts.values())
            
            # Relationship counts
            result = session.run("""
                MATCH ()-[r]->()
                RETURN type(r) as type, count(r) as count
            """)
            
            rel_counts = {record['type']: record['count'] for record in result}
            stats['relationships'] = rel_counts
            stats['total_relationships'] = sum(rel_counts.values())
            
            return stats


if __name__ == '__main__':
    # Test Neo4j loader
    logging.basicConfig(level=logging.INFO)
    
    loader = Neo4jLoader(
        uri="bolt://localhost:7687",
        user="neo4j",
        password="password"
    )
    
    # Initialize schema
    loader.initialize_schema()
    
    # Test with sample data
    sample_papers = [
        {
            'pmid': '12345678',
            'title': 'Test Paper',
            'abstract': 'Test abstract',
            'publication_year': 2023
        }
    ]
    
    loader.load_papers(sample_papers)
    
    # Get statistics
    stats = loader.get_graph_statistics()
    print(f"\nGraph Statistics:")
    print(f"  Total nodes: {stats['total_nodes']}")
    print(f"  By type: {stats['nodes']}")
    print(f"  Total relationships: {stats['total_relationships']}")
    print(f"  By type: {stats['relationships']}")
    
    loader.close()
    
    print("\nNeo4jLoader test complete!")


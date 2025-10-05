"""
Neo4j Service - Database interaction layer
"""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

try:
    from neo4j import GraphDatabase, basic_auth
    NEO4J_AVAILABLE = True
except ImportError:
    NEO4J_AVAILABLE = False

from api.models.schemas import (
    EntityType, RelationType, GraphNode, GraphEdge,
    NetworkStats, Entity, Relationship
)

logger = logging.getLogger(__name__)


class Neo4jService:
    """Service for Neo4j database operations"""
    
    def __init__(self, uri: str, user: str, password: str):
        """Initialize Neo4j connection"""
        if not NEO4J_AVAILABLE:
            logger.warning("Neo4j driver not installed. Database features disabled.")
            self.driver = None
            return
        
        try:
            self.driver = GraphDatabase.driver(
                uri,
                auth=basic_auth(user, password)
            )
            # Test connection
            with self.driver.session() as session:
                session.run("RETURN 1")
            logger.info(f"Connected to Neo4j at {uri}")
        except Exception as e:
            logger.error(f"Failed to connect to Neo4j: {e}")
            self.driver = None
    
    def __del__(self):
        """Close driver on cleanup"""
        if self.driver:
            self.driver.close()
    
    def is_connected(self) -> bool:
        """Check if connected to Neo4j"""
        if not self.driver:
            return False
        try:
            with self.driver.session() as session:
                session.run("RETURN 1")
            return True
        except:
            return False
    
    # =============== PAPERS ===============
    
    def get_papers(self, skip: int = 0, limit: int = 20) -> Tuple[List[Dict], int]:
        """Get paginated papers"""
        if not self.driver:
            return [], 0
        
        with self.driver.session() as session:
            # Get total count
            count_query = "MATCH (p:Paper) RETURN count(p) as total"
            result = session.run(count_query)
            total = result.single()["total"]
            
            # Get papers
            query = """
            MATCH (p:Paper)
            OPTIONAL MATCH (p)-[:HAS_ENTITY]->(e)
            OPTIONAL MATCH (p)-[:HAS_TOPIC]->(t:Topic)
            WITH p, count(DISTINCT e) as entity_count, collect(DISTINCT t.name) as topics
            RETURN p, entity_count, topics
            ORDER BY p.publication_date DESC
            SKIP $skip LIMIT $limit
            """
            result = session.run(query, skip=skip, limit=limit)
            
            papers = []
            for record in result:
                paper_node = record["p"]
                papers.append({
                    "id": paper_node["pmid"],
                    "metadata": {
                        "pmid": paper_node.get("pmid"),
                        "pmcid": paper_node.get("pmcid"),
                        "doi": paper_node.get("doi"),
                        "title": paper_node.get("title"),
                        "abstract": paper_node.get("abstract"),
                        "authors": paper_node.get("authors", []),
                        "journal": paper_node.get("journal"),
                        "publication_date": paper_node.get("publication_date"),
                        "mesh_terms": paper_node.get("mesh_terms", []),
                        "keywords": paper_node.get("keywords", [])
                    },
                    "entities_count": record["entity_count"],
                    "relationships_count": 0,  # TODO: calculate
                    "topics": record["topics"],
                    "created_at": None
                })
            
            return papers, total
    
    def get_paper_by_id(self, paper_id: str) -> Optional[Dict]:
        """Get paper by PMID"""
        if not self.driver:
            return None
        
        with self.driver.session() as session:
            query = """
            MATCH (p:Paper {pmid: $pmid})
            OPTIONAL MATCH (p)-[:HAS_ENTITY]->(e)
            OPTIONAL MATCH (p)-[:HAS_TOPIC]->(t:Topic)
            RETURN p, collect(DISTINCT e) as entities, collect(DISTINCT t.name) as topics
            """
            result = session.run(query, pmid=paper_id)
            record = result.single()
            
            if not record:
                return None
            
            paper_node = record["p"]
            return {
                "id": paper_node["pmid"],
                "metadata": {
                    "pmid": paper_node.get("pmid"),
                    "pmcid": paper_node.get("pmcid"),
                    "doi": paper_node.get("doi"),
                    "title": paper_node.get("title"),
                    "abstract": paper_node.get("abstract"),
                    "authors": paper_node.get("authors", []),
                    "journal": paper_node.get("journal"),
                    "publication_date": paper_node.get("publication_date"),
                    "mesh_terms": paper_node.get("mesh_terms", []),
                    "keywords": paper_node.get("keywords", [])
                },
                "entities_count": len(record["entities"]),
                "relationships_count": 0,
                "topics": record["topics"],
                "created_at": None
            }
    
    # =============== ENTITIES ===============
    
    def get_entities(
        self, 
        entity_type: Optional[EntityType] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict], int]:
        """Get paginated entities"""
        if not self.driver:
            return [], 0
        
        with self.driver.session() as session:
            # Build query based on entity type
            if entity_type:
                label = entity_type.value.capitalize()
                count_query = f"MATCH (e:{label}) RETURN count(e) as total"
                match_clause = f"MATCH (e:{label})"
            else:
                count_query = "MATCH (e) WHERE any(label IN labels(e) WHERE label IN ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']) RETURN count(e) as total"
                match_clause = "MATCH (e) WHERE any(label IN labels(e) WHERE label IN ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention'])"
            
            # Get total
            result = session.run(count_query)
            total = result.single()["total"]
            
            # Get entities
            query = f"""
            {match_clause}
            OPTIONAL MATCH (p:Paper)-[:HAS_ENTITY]->(e)
            WITH e, count(DISTINCT p) as paper_count
            RETURN e, labels(e) as labels, paper_count
            ORDER BY paper_count DESC
            SKIP $skip LIMIT $limit
            """
            result = session.run(query, skip=skip, limit=limit)
            
            entities = []
            for record in result:
                node = record["e"]
                labels = record["labels"]
                entity_type_str = next((l for l in labels if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
                
                entities.append({
                    "id": node.get("id", node.get("name")),
                    "name": node.get("name"),
                    "entity_type": entity_type_str.upper(),
                    "normalized_name": node.get("normalized_name"),
                    "external_ids": node.get("external_ids", {}),
                    "ontology_terms": node.get("ontology_terms", []),
                    "synonyms": node.get("synonyms", []),
                    "description": node.get("description"),
                    "paper_count": record["paper_count"],
                    "source": None
                })
            
            return entities, total
    
    def get_entity_by_id(self, entity_id: str) -> Optional[Dict]:
        """Get entity by ID"""
        if not self.driver:
            return None
        
        with self.driver.session() as session:
            query = """
            MATCH (e)
            WHERE e.id = $entity_id OR e.name = $entity_id
            OPTIONAL MATCH (p:Paper)-[:HAS_ENTITY]->(e)
            RETURN e, labels(e) as labels, count(DISTINCT p) as paper_count
            """
            result = session.run(query, entity_id=entity_id)
            record = result.single()
            
            if not record:
                return None
            
            node = record["e"]
            labels = record["labels"]
            entity_type_str = next((l for l in labels if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
            
            return {
                "id": node.get("id", node.get("name")),
                "name": node.get("name"),
                "entity_type": entity_type_str.upper(),
                "normalized_name": node.get("normalized_name"),
                "external_ids": node.get("external_ids", {}),
                "ontology_terms": node.get("ontology_terms", []),
                "synonyms": node.get("synonyms", []),
                "description": node.get("description"),
                "paper_count": record["paper_count"],
                "source": None
            }
    
    # =============== RELATIONSHIPS ===============
    
    def get_relationships(
        self,
        relation_type: Optional[RelationType] = None,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[Dict], int]:
        """Get paginated relationships"""
        if not self.driver:
            return [], 0
        
        with self.driver.session() as session:
            # Build query
            if relation_type:
                rel_filter = f"[r:{relation_type.value}]"
            else:
                rel_filter = "[r]"
            
            count_query = f"""
            MATCH (s)-{rel_filter}->(o)
            WHERE type(r) IN ['UPREGULATES', 'DOWNREGULATES', 'CAUSES', 'TREATS', 'INTERACTS_WITH', 'PART_OF', 'ASSOCIATED_WITH']
            RETURN count(r) as total
            """
            result = session.run(count_query)
            total = result.single()["total"]
            
            query = f"""
            MATCH (s)-{rel_filter}->(o)
            WHERE type(r) IN ['UPREGULATES', 'DOWNREGULATES', 'CAUSES', 'TREATS', 'INTERACTS_WITH', 'PART_OF', 'ASSOCIATED_WITH']
            RETURN s, r, o, labels(s) as s_labels, labels(o) as o_labels, type(r) as rel_type
            ORDER BY r.confidence DESC
            SKIP $skip LIMIT $limit
            """
            result = session.run(query, skip=skip, limit=limit)
            
            relationships = []
            for record in result:
                s_node = record["s"]
                o_node = record["o"]
                rel = record["r"]
                
                relationships.append({
                    "id": f"{s_node.get('id', s_node.get('name'))}_{record['rel_type']}_{o_node.get('id', o_node.get('name'))}",
                    "subject": self._node_to_entity(s_node, record["s_labels"]),
                    "relation": record["rel_type"],
                    "object": self._node_to_entity(o_node, record["o_labels"]),
                    "confidence": rel.get("confidence"),
                    "evidence": rel.get("evidence", []),
                    "source_sentences": rel.get("source_sentences", [])
                })
            
            return relationships, total
    
    def _node_to_entity(self, node: Any, labels: List[str]) -> Dict:
        """Convert Neo4j node to entity dict"""
        entity_type_str = next((l for l in labels if l in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']), 'Unknown')
        
        return {
            "id": node.get("id", node.get("name")),
            "name": node.get("name"),
            "entity_type": entity_type_str.upper(),
            "normalized_name": node.get("normalized_name"),
            "external_ids": node.get("external_ids", {}),
            "ontology_terms": node.get("ontology_terms", []),
            "synonyms": node.get("synonyms", []),
            "description": node.get("description"),
            "paper_count": 0,
            "source": None
        }
    
    # =============== GRAPH QUERIES ===============
    
    def execute_cypher(
        self,
        query: str,
        parameters: Dict[str, Any] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Execute Cypher query"""
        if not self.driver:
            return {"nodes": [], "edges": [], "statistics": {}, "query_time_ms": 0}
        
        start_time = datetime.now()
        
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            records = list(result)
            
            # Extract nodes and relationships
            nodes = []
            edges = []
            node_ids = set()
            
            for record in records:
                for value in record.values():
                    if hasattr(value, 'labels'):  # It's a node
                        node_id = str(value.id)
                        if node_id not in node_ids:
                            nodes.append({
                                "id": node_id,
                                "labels": list(value.labels),
                                "properties": dict(value)
                            })
                            node_ids.add(node_id)
                    elif hasattr(value, 'type'):  # It's a relationship
                        edges.append({
                            "id": str(value.id),
                            "type": value.type,
                            "source": str(value.start_node.id),
                            "target": str(value.end_node.id),
                            "properties": dict(value)
                        })
            
            end_time = datetime.now()
            query_time_ms = (end_time - start_time).total_seconds() * 1000
            
            return {
                "nodes": nodes[:limit],
                "edges": edges[:limit],
                "statistics": {
                    "nodes": len(nodes),
                    "edges": len(edges),
                    "records": len(records)
                },
                "query_time_ms": query_time_ms
            }
    
    # =============== STATISTICS ===============
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get overall graph statistics"""
        if not self.driver:
            return self._empty_stats()
        
        with self.driver.session() as session:
            # Node counts by type
            node_query = """
            MATCH (n)
            RETURN labels(n) as labels, count(n) as count
            """
            result = session.run(node_query)
            node_counts = {}
            total_nodes = 0
            for record in result:
                labels = record["labels"]
                count = record["count"]
                for label in labels:
                    node_counts[label] = node_counts.get(label, 0) + count
                total_nodes += count
            
            # Edge counts by type
            edge_query = """
            MATCH ()-[r]->()
            RETURN type(r) as type, count(r) as count
            """
            result = session.run(edge_query)
            edge_counts = {}
            total_edges = 0
            for record in result:
                edge_counts[record["type"]] = record["count"]
                total_edges += record["count"]
            
            # Calculate density and avg degree
            density = 0
            avg_degree = 0
            if total_nodes > 1:
                max_edges = total_nodes * (total_nodes - 1)
                density = total_edges / max_edges if max_edges > 0 else 0
                avg_degree = (2 * total_edges) / total_nodes if total_nodes > 0 else 0
            
            return {
                "papers": node_counts.get("Paper", 0),
                "entities": sum(node_counts.get(t, 0) for t in ['Gene', 'Protein', 'Disease', 'Chemical', 'Stressor', 'Phenotype', 'Organism', 'CellType', 'Intervention']),
                "relationships": sum(edge_counts.get(t, 0) for t in ['UPREGULATES', 'DOWNREGULATES', 'CAUSES', 'TREATS', 'INTERACTS_WITH', 'PART_OF', 'ASSOCIATED_WITH']),
                "topics": node_counts.get("Topic", 0),
                "network_stats": {
                    "node_count": total_nodes,
                    "edge_count": total_edges,
                    "node_types": node_counts,
                    "edge_types": edge_counts,
                    "density": density,
                    "avg_degree": avg_degree
                },
                "last_updated": datetime.now()
            }
    
    def _empty_stats(self) -> Dict[str, Any]:
        """Return empty stats when database not connected"""
        return {
            "papers": 0,
            "entities": 0,
            "relationships": 0,
            "topics": 0,
            "network_stats": {
                "node_count": 0,
                "edge_count": 0,
                "node_types": {},
                "edge_types": {},
                "density": 0,
                "avg_degree": 0
            },
            "last_updated": datetime.now()
        }

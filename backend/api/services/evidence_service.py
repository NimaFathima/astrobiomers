"""
Evidence Service for Knowledge Graph
Provides evidence and citation tracking for relationships
"""

from typing import List, Dict, Any, Optional
from knowledge_graph.query_engine import QueryEngine
import logging

logger = logging.getLogger(__name__)


class EvidenceService:
    """Service for retrieving evidence supporting knowledge graph relationships"""
    
    def __init__(self):
        """Initialize the evidence service"""
        self.query_engine = QueryEngine()
        logger.info("🔬 Evidence Service initialized")
    
    def get_edge_evidence(self, source_id: str, target_id: str, relationship_type: Optional[str] = None) -> Dict[str, Any]:
        """
        Get papers that provide evidence for a specific edge/relationship
        
        Args:
            source_id: Element ID of source node
            target_id: Element ID of target node
            relationship_type: Optional specific relationship type
            
        Returns:
            Dictionary with papers, relationship info, and metadata
        """
        try:
            # Query to find the relationship and supporting papers
            if relationship_type:
                query = """
                MATCH (source)
                WHERE elementId(source) = $source_id
                MATCH (target)
                WHERE elementId(target) = $target_id
                MATCH (source)-[r]->(target)
                WHERE type(r) = $rel_type
                OPTIONAL MATCH (p:Paper)-[:MENTIONS|:STUDIES|:REPORTS]->(source)
                OPTIONAL MATCH (p)-[:MENTIONS|:STUDIES|:REPORTS]->(target)
                WITH DISTINCT r, source, target, collect(DISTINCT p) as papers
                RETURN 
                    source.name as source_name,
                    target.name as target_name,
                    type(r) as relationship_type,
                    properties(r) as relationship_props,
                    [paper IN papers | {
                        id: elementId(paper),
                        title: paper.title,
                        year: paper.year,
                        authors: paper.authors,
                        abstract: paper.abstract,
                        pmid: paper.pmid,
                        doi: paper.doi
                    }] as evidence_papers
                """
                params = {
                    "source_id": source_id,
                    "target_id": target_id,
                    "rel_type": relationship_type
                }
            else:
                # Find any relationship between nodes
                query = """
                MATCH (source)
                WHERE elementId(source) = $source_id
                MATCH (target)
                WHERE elementId(target) = $target_id
                MATCH (source)-[r]->(target)
                OPTIONAL MATCH (p:Paper)-[:MENTIONS|:STUDIES|:REPORTS]->(source)
                OPTIONAL MATCH (p)-[:MENTIONS|:STUDIES|:REPORTS]->(target)
                WITH DISTINCT r, source, target, collect(DISTINCT p) as papers
                RETURN 
                    source.name as source_name,
                    target.name as target_name,
                    type(r) as relationship_type,
                    properties(r) as relationship_props,
                    [paper IN papers | {
                        id: elementId(paper),
                        title: paper.title,
                        year: paper.year,
                        authors: paper.authors,
                        abstract: paper.abstract,
                        pmid: paper.pmid,
                        doi: paper.doi
                    }] as evidence_papers
                LIMIT 1
                """
                params = {
                    "source_id": source_id,
                    "target_id": target_id
                }
            
            results = self.query_engine.execute_query(query, params)
            
            if not results:
                logger.warning(f"No relationship found between {source_id} and {target_id}")
                return {
                    "found": False,
                    "message": "No relationship found between specified nodes"
                }
            
            result = results[0]
            evidence_papers = [p for p in result["evidence_papers"] if p is not None]
            
            logger.info(f"📚 Found {len(evidence_papers)} papers supporting relationship")
            
            return {
                "found": True,
                "source": result["source_name"],
                "target": result["target_name"],
                "relationship_type": result["relationship_type"],
                "relationship_properties": result["relationship_props"],
                "evidence_count": len(evidence_papers),
                "papers": evidence_papers,
                "confidence": self._calculate_confidence(len(evidence_papers))
            }
            
        except Exception as e:
            logger.error(f"Error getting edge evidence: {e}")
            raise
    
    def get_all_edge_evidence(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get evidence counts for all edges in the graph
        
        Args:
            limit: Maximum number of edges to return
            
        Returns:
            List of edges with their evidence counts
        """
        try:
            query = """
            MATCH (source)-[r]->(target)
            OPTIONAL MATCH (p:Paper)-[:MENTIONS|:STUDIES|:REPORTS]->(source)
            OPTIONAL MATCH (p)-[:MENTIONS|:STUDIES|:REPORTS]->(target)
            WITH DISTINCT r, source, target, count(DISTINCT p) as paper_count
            RETURN 
                elementId(source) as source_id,
                source.name as source_name,
                elementId(target) as target_id,
                target.name as target_name,
                type(r) as relationship_type,
                paper_count
            ORDER BY paper_count DESC
            LIMIT $limit
            """
            
            results = self.query_engine.execute_query(query, {"limit": limit})
            
            edges_with_evidence = []
            for result in results:
                edges_with_evidence.append({
                    "source_id": result["source_id"],
                    "source_name": result["source_name"],
                    "target_id": result["target_id"],
                    "target_name": result["target_name"],
                    "relationship_type": result["relationship_type"],
                    "evidence_count": result["paper_count"],
                    "confidence": self._calculate_confidence(result["paper_count"])
                })
            
            logger.info(f"📊 Retrieved evidence for {len(edges_with_evidence)} edges")
            return edges_with_evidence
            
        except Exception as e:
            logger.error(f"Error getting all edge evidence: {e}")
            raise
    
    def _calculate_confidence(self, paper_count: int) -> str:
        """
        Calculate confidence level based on number of supporting papers
        
        Args:
            paper_count: Number of papers supporting the relationship
            
        Returns:
            Confidence level: "high", "medium", "low", or "unverified"
        """
        if paper_count >= 5:
            return "high"
        elif paper_count >= 3:
            return "medium"
        elif paper_count >= 1:
            return "low"
        else:
            return "unverified"
    
    def search_papers_by_entities(self, entity_names: List[str]) -> List[Dict[str, Any]]:
        """
        Find papers that mention multiple entities
        
        Args:
            entity_names: List of entity names to search for
            
        Returns:
            List of papers mentioning the entities
        """
        try:
            query = """
            MATCH (e)
            WHERE e.name IN $entity_names
            MATCH (p:Paper)-[:MENTIONS|:STUDIES|:REPORTS]->(e)
            WITH p, count(DISTINCT e) as entity_count
            WHERE entity_count >= 2
            RETURN DISTINCT
                elementId(p) as id,
                p.title as title,
                p.year as year,
                p.authors as authors,
                p.abstract as abstract,
                p.pmid as pmid,
                p.doi as doi,
                entity_count
            ORDER BY entity_count DESC, p.year DESC
            LIMIT 20
            """
            
            results = self.query_engine.execute_query(query, {"entity_names": entity_names})
            
            papers = []
            for result in results:
                papers.append({
                    "id": result["id"],
                    "title": result["title"],
                    "year": result["year"],
                    "authors": result["authors"],
                    "abstract": result["abstract"],
                    "pmid": result["pmid"],
                    "doi": result["doi"],
                    "matching_entities": result["entity_count"]
                })
            
            logger.info(f"📄 Found {len(papers)} papers mentioning entities: {entity_names}")
            return papers
            
        except Exception as e:
            logger.error(f"Error searching papers by entities: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.query_engine:
            self.query_engine.close()

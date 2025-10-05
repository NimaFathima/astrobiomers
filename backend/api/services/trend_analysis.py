"""
Trend Analysis Service
Analyzes research trends, collaborations, and temporal patterns
"""

from typing import List, Dict, Any, Optional
from knowledge_graph.query_engine import QueryEngine
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class TrendAnalysisService:
    """Service for analyzing research trends over time"""
    
    def __init__(self):
        """Initialize the trend analysis service"""
        self.query_engine = QueryEngine()
        logger.info("📈 Trend Analysis Service initialized")
    
    def get_topic_timeline(self, topic: Optional[str] = None, start_year: int = 2000, end_year: int = 2025) -> Dict[str, Any]:
        """
        Get publication timeline for a topic or all topics
        
        Args:
            topic: Specific topic to analyze (None for all)
            start_year: Start year for timeline
            end_year: End year for timeline
            
        Returns:
            Timeline data with yearly publication counts
        """
        try:
            if topic:
                # Timeline for specific topic
                query = """
                MATCH (p:Paper)
                WHERE p.year >= $start_year AND p.year <= $end_year
                MATCH (p)-[:MENTIONS|:STUDIES|:REPORTS]->(e)
                WHERE toLower(e.name) CONTAINS toLower($topic)
                WITH p.year as year, count(DISTINCT p) as paper_count
                ORDER BY year
                RETURN year, paper_count
                """
                params = {"topic": topic, "start_year": start_year, "end_year": end_year}
            else:
                # Overall timeline
                query = """
                MATCH (p:Paper)
                WHERE p.year >= $start_year AND p.year <= $end_year
                WITH p.year as year, count(p) as paper_count
                ORDER BY year
                RETURN year, paper_count
                """
                params = {"start_year": start_year, "end_year": end_year}
            
            results = self.query_engine.execute_query(query, params)
            
            # Fill in missing years with zero counts
            year_counts = {result["year"]: result["paper_count"] for result in results}
            timeline = []
            for year in range(start_year, end_year + 1):
                timeline.append({
                    "year": year,
                    "count": year_counts.get(year, 0)
                })
            
            logger.info(f"📊 Generated timeline for topic: {topic or 'all topics'}")
            
            return {
                "topic": topic or "all topics",
                "start_year": start_year,
                "end_year": end_year,
                "timeline": timeline,
                "total_papers": sum(year_counts.values())
            }
            
        except Exception as e:
            logger.error(f"Error getting topic timeline: {e}")
            raise
    
    def get_emerging_topics(self, timeframe_years: int = 5, min_papers: int = 3) -> List[Dict[str, Any]]:
        """
        Identify topics with increasing publication rates
        
        Args:
            timeframe_years: Number of recent years to analyze
            min_papers: Minimum papers required to be considered
            
        Returns:
            List of emerging topics with growth metrics
        """
        try:
            query = """
            MATCH (p:Paper)
            WHERE p.year IS NOT NULL
            WITH max(p.year) as latest_year
            MATCH (recent:Paper)
            WHERE recent.year >= latest_year - $timeframe
            MATCH (recent)-[:MENTIONS|:STUDIES|:REPORTS]->(e)
            WITH e, 
                 count(DISTINCT recent) as recent_count,
                 latest_year - $timeframe as cutoff_year
            WHERE recent_count >= $min_papers
            MATCH (older:Paper)
            WHERE older.year < cutoff_year
            OPTIONAL MATCH (older)-[:MENTIONS|:STUDIES|:REPORTS]->(e)
            WITH e, 
                 recent_count,
                 count(DISTINCT older) as older_count,
                 cutoff_year
            WITH e,
                 recent_count,
                 older_count,
                 CASE 
                     WHEN older_count = 0 THEN 999.0
                     ELSE toFloat(recent_count) / toFloat(older_count)
                 END as growth_rate
            WHERE growth_rate > 1.5
            RETURN 
                e.name as topic,
                labels(e)[0] as type,
                recent_count,
                older_count,
                growth_rate
            ORDER BY growth_rate DESC
            LIMIT 20
            """
            
            params = {
                "timeframe": timeframe_years,
                "min_papers": min_papers
            }
            
            results = self.query_engine.execute_query(query, params)
            
            emerging_topics = []
            for result in results:
                emerging_topics.append({
                    "topic": result["topic"],
                    "type": result["type"],
                    "recent_papers": result["recent_count"],
                    "historical_papers": result["older_count"],
                    "growth_rate": round(result["growth_rate"], 2),
                    "status": "rapid growth" if result["growth_rate"] > 5 else "growing"
                })
            
            logger.info(f"🚀 Found {len(emerging_topics)} emerging topics")
            return emerging_topics
            
        except Exception as e:
            logger.error(f"Error getting emerging topics: {e}")
            raise
    
    def get_collaboration_network(self, author_name: Optional[str] = None, depth: int = 2) -> Dict[str, Any]:
        """
        Get author collaboration network
        
        Args:
            author_name: Specific author to analyze (None for top authors)
            depth: Degrees of separation to include
            
        Returns:
            Collaboration network with nodes and edges
        """
        try:
            if author_name:
                # Network for specific author
                query = """
                MATCH (a:Author)
                WHERE toLower(a.name) CONTAINS toLower($author)
                MATCH (a)-[:AUTHORED]->(p:Paper)<-[:AUTHORED]-(coauthor:Author)
                WHERE a <> coauthor
                WITH a, coauthor, count(p) as collaborations
                RETURN 
                    a.name as author,
                    coauthor.name as collaborator,
                    collaborations
                ORDER BY collaborations DESC
                LIMIT 50
                """
                params = {"author": author_name}
            else:
                # Top collaboration pairs
                query = """
                MATCH (a1:Author)-[:AUTHORED]->(p:Paper)<-[:AUTHORED]-(a2:Author)
                WHERE id(a1) < id(a2)
                WITH a1, a2, count(p) as collaborations
                WHERE collaborations >= 2
                RETURN 
                    a1.name as author1,
                    a2.name as author2,
                    collaborations
                ORDER BY collaborations DESC
                LIMIT 50
                """
                params = {}
            
            results = self.query_engine.execute_query(query, params)
            
            # Build network graph
            nodes = set()
            edges = []
            
            for result in results:
                if author_name:
                    author = result["author"]
                    collaborator = result["collaborator"]
                    nodes.add(author)
                    nodes.add(collaborator)
                    edges.append({
                        "source": author,
                        "target": collaborator,
                        "weight": result["collaborations"]
                    })
                else:
                    author1 = result["author1"]
                    author2 = result["author2"]
                    nodes.add(author1)
                    nodes.add(author2)
                    edges.append({
                        "source": author1,
                        "target": author2,
                        "weight": result["collaborations"]
                    })
            
            logger.info(f"🤝 Generated collaboration network: {len(nodes)} authors, {len(edges)} collaborations")
            
            return {
                "focus_author": author_name,
                "nodes": [{"id": node, "name": node} for node in nodes],
                "edges": edges,
                "total_authors": len(nodes),
                "total_collaborations": len(edges)
            }
            
        except Exception as e:
            logger.error(f"Error getting collaboration network: {e}")
            raise
    
    def get_top_authors(self, topic: Optional[str] = None, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get top authors by publication count
        
        Args:
            topic: Filter by specific topic (None for all)
            limit: Maximum number of authors to return
            
        Returns:
            List of top authors with metrics
        """
        try:
            if topic:
                query = """
                MATCH (a:Author)-[:AUTHORED]->(p:Paper)
                MATCH (p)-[:MENTIONS|:STUDIES|:REPORTS]->(e)
                WHERE toLower(e.name) CONTAINS toLower($topic)
                WITH a, 
                     count(DISTINCT p) as paper_count,
                     collect(DISTINCT p.year) as years
                RETURN 
                    a.name as name,
                    paper_count,
                    min(years) as first_year,
                    max(years) as last_year
                ORDER BY paper_count DESC
                LIMIT $limit
                """
                params = {"topic": topic, "limit": limit}
            else:
                query = """
                MATCH (a:Author)-[:AUTHORED]->(p:Paper)
                WITH a,
                     count(p) as paper_count,
                     collect(p.year) as years
                RETURN 
                    a.name as name,
                    paper_count,
                    min(years) as first_year,
                    max(years) as last_year
                ORDER BY paper_count DESC
                LIMIT $limit
                """
                params = {"limit": limit}
            
            results = self.query_engine.execute_query(query, params)
            
            top_authors = []
            for i, result in enumerate(results, 1):
                years_active = result["last_year"] - result["first_year"] + 1 if result["last_year"] and result["first_year"] else 0
                top_authors.append({
                    "rank": i,
                    "name": result["name"],
                    "paper_count": result["paper_count"],
                    "first_year": result["first_year"],
                    "last_year": result["last_year"],
                    "years_active": years_active,
                    "papers_per_year": round(result["paper_count"] / years_active, 2) if years_active > 0 else 0
                })
            
            logger.info(f"🏆 Found top {len(top_authors)} authors for topic: {topic or 'all'}")
            return top_authors
            
        except Exception as e:
            logger.error(f"Error getting top authors: {e}")
            raise
    
    def get_topic_co_occurrence(self, min_papers: int = 2) -> List[Dict[str, Any]]:
        """
        Find topics that frequently appear together in papers
        
        Args:
            min_papers: Minimum papers required for co-occurrence
            
        Returns:
            List of topic pairs with co-occurrence counts
        """
        try:
            query = """
            MATCH (e1)<-[:MENTIONS|:STUDIES|:REPORTS]-(p:Paper)-[:MENTIONS|:STUDIES|:REPORTS]->(e2)
            WHERE id(e1) < id(e2)
            WITH e1, e2, count(p) as co_occurrence
            WHERE co_occurrence >= $min_papers
            RETURN 
                e1.name as topic1,
                labels(e1)[0] as type1,
                e2.name as topic2,
                labels(e2)[0] as type2,
                co_occurrence
            ORDER BY co_occurrence DESC
            LIMIT 50
            """
            
            results = self.query_engine.execute_query(query, {"min_papers": min_papers})
            
            co_occurrences = []
            for result in results:
                co_occurrences.append({
                    "topic1": result["topic1"],
                    "type1": result["type1"],
                    "topic2": result["topic2"],
                    "type2": result["type2"],
                    "co_occurrence_count": result["co_occurrence"],
                    "strength": "strong" if result["co_occurrence"] >= 10 else "moderate" if result["co_occurrence"] >= 5 else "weak"
                })
            
            logger.info(f"🔗 Found {len(co_occurrences)} topic co-occurrences")
            return co_occurrences
            
        except Exception as e:
            logger.error(f"Error getting topic co-occurrence: {e}")
            raise
    
    def close(self):
        """Close database connection"""
        if self.query_engine:
            self.query_engine.close()

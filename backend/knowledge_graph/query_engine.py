"""
Query Engine for Neo4j Knowledge Graph
Provides a simple interface for executing Cypher queries
"""

from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env files
# Try multiple locations
env_paths = [
    Path(__file__).parent.parent.parent / ".env",  # Root level
    Path(__file__).parent.parent / ".env",          # Backend level
]
for env_path in env_paths:
    if env_path.exists():
        load_dotenv(env_path)
        break

logger = logging.getLogger(__name__)


class QueryEngine:
    """Simple query engine for Neo4j"""
    
    def __init__(self):
        """Initialize connection to Neo4j"""
        self.uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        self.user = os.getenv("NEO4J_USER", "neo4j")
        self.password = os.getenv("NEO4J_PASSWORD", "spacebiology123")
        self.database = os.getenv("NEO4J_DATABASE", "astrobiomers")
        
        try:
            self.driver = GraphDatabase.driver(
                self.uri,
                auth=(self.user, self.password)
            )
            # Test connection
            with self.driver.session(database=self.database) as session:
                session.run("RETURN 1")
            logger.info(f"✅ Connected to Neo4j at {self.uri}, database: {self.database}")
        except Exception as e:
            logger.error(f"❌ Failed to connect to Neo4j: {e}")
            raise
    
    def execute_query(self, query: str, parameters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a Cypher query and return results
        
        Args:
            query: Cypher query string
            parameters: Optional query parameters
            
        Returns:
            List of result records as dictionaries
        """
        try:
            with self.driver.session(database=self.database) as session:
                result = session.run(query, parameters or {})
                return [dict(record) for record in result]
        except Exception as e:
            logger.error(f"Query error: {e}")
            logger.error(f"Query: {query}")
            logger.error(f"Parameters: {parameters}")
            raise
    
    def close(self):
        """Close the database connection"""
        if self.driver:
            self.driver.close()
            logger.info("Closed Neo4j connection")
    
    def __del__(self):
        """Cleanup on deletion"""
        self.close()

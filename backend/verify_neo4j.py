"""
Neo4j Connection Verification Script
Space Biology Knowledge Engine

Tests Neo4j connectivity and validates configuration
before attempting to load the knowledge graph.

Author: Space Biology KG Team
Date: October 2025
"""

import os
import sys
from pathlib import Path
from neo4j import GraphDatabase
from dotenv import load_dotenv


class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Print formatted header."""
    print(f"\n{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{text.center(70)}{Colors.ENDC}")
    print(f"{Colors.HEADER}{Colors.BOLD}{'='*70}{Colors.ENDC}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.OKGREEN}✓ {text}{Colors.ENDC}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.WARNING}⚠ {text}{Colors.ENDC}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.FAIL}✗ {text}{Colors.ENDC}")


def print_info(text):
    """Print info message."""
    print(f"{Colors.OKCYAN}ℹ {text}{Colors.ENDC}")


def load_configuration():
    """Load Neo4j configuration from .env file."""
    # Load .env file
    env_path = Path(__file__).parent / '.env'
    
    if not env_path.exists():
        print_warning(f".env file not found at: {env_path}")
        print_info("Using default configuration...")
        return {
            'uri': 'bolt://localhost:7687',
            'user': 'neo4j',
            'password': 'spacebiology123',
            'database': 'astrobiomers'
        }
    
    load_dotenv(env_path)
    
    config = {
        'uri': os.getenv('NEO4J_URI', 'bolt://localhost:7687'),
        'user': os.getenv('NEO4J_USER', 'neo4j'),
        'password': os.getenv('NEO4J_PASSWORD', 'spacebiology123'),
        'database': os.getenv('NEO4J_DATABASE', 'astrobiomers')
    }
    
    print_success(f"Loaded configuration from: {env_path}")
    return config


def test_connection(config):
    """Test basic Neo4j connection."""
    print_info("Testing connection to Neo4j...")
    
    try:
        driver = GraphDatabase.driver(
            config['uri'],
            auth=(config['user'], config['password'])
        )
        
        # Test connection
        driver.verify_connectivity()
        
        print_success(f"Connected to Neo4j at {config['uri']}")
        return driver
    
    except Exception as e:
        print_error(f"Connection failed: {str(e)}")
        print_info("\nTroubleshooting:")
        print_info("1. Is Neo4j Desktop running?")
        print_info("2. Is your database started (green 'Active' status)?")
        print_info("3. Is the password correct in .env file?")
        print_info("4. Default should be: bolt://localhost:7687")
        return None


def test_database_access(driver, database):
    """Test database access and permissions."""
    print_info(f"Testing access to database '{database}'...")
    
    try:
        with driver.session(database=database) as session:
            result = session.run("RETURN 1 as test")
            value = result.single()['test']
            
            if value == 1:
                print_success(f"Database '{database}' is accessible")
                return True
    
    except Exception as e:
        error_msg = str(e)
        
        if "database does not exist" in error_msg.lower():
            print_warning(f"Database '{database}' not found")
            print_info("Try using 'neo4j' as database name, or create database in Neo4j Desktop")
            
            # Try default database
            print_info("Attempting to use default 'neo4j' database...")
            try:
                with driver.session(database='neo4j') as session:
                    session.run("RETURN 1")
                print_success("Default 'neo4j' database is accessible")
                print_warning(f"Update .env file: NEO4J_DATABASE=neo4j")
                return True
            except:
                pass
        
        print_error(f"Database access failed: {error_msg}")
        return False


def test_query_execution(driver, database):
    """Test Cypher query execution."""
    print_info("Testing Cypher query execution...")
    
    try:
        with driver.session(database=database) as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN count(n) as node_count")
            count = result.single()['node_count']
            
            print_success(f"Successfully executed query")
            print_info(f"Current node count: {count}")
            
            if count == 0:
                print_info("Database is empty - ready for knowledge graph loading!")
            else:
                print_info(f"Database contains {count} nodes")
            
            return True
    
    except Exception as e:
        print_error(f"Query execution failed: {str(e)}")
        return False


def test_write_permissions(driver, database):
    """Test write permissions by creating and deleting a test node."""
    print_info("Testing write permissions...")
    
    try:
        with driver.session(database=database) as session:
            # Create test node
            session.run("CREATE (t:Test {name: 'verification_test'})")
            
            # Verify it exists
            result = session.run("MATCH (t:Test {name: 'verification_test'}) RETURN count(t) as count")
            count = result.single()['count']
            
            if count == 1:
                # Delete test node
                session.run("MATCH (t:Test {name: 'verification_test'}) DELETE t")
                print_success("Write permissions confirmed")
                return True
            else:
                print_error("Test node creation failed")
                return False
    
    except Exception as e:
        print_error(f"Write test failed: {str(e)}")
        return False


def display_summary(config, all_tests_passed):
    """Display summary and next steps."""
    print_header("Verification Summary")
    
    if all_tests_passed:
        print(f"{Colors.OKGREEN}{Colors.BOLD}")
        print("🎉 All tests passed! Neo4j is ready for knowledge graph loading!")
        print(f"{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}Connection Details:{Colors.ENDC}")
        print(f"  URI:      {config['uri']}")
        print(f"  Username: {config['user']}")
        print(f"  Database: {config['database']}")
        print(f"  Browser:  http://localhost:7474")
        
        print(f"\n{Colors.BOLD}Next Steps:{Colors.ENDC}")
        print(f"{Colors.OKCYAN}1. Load your knowledge graph:{Colors.ENDC}")
        print(f"   python -m knowledge_graph.cli build --papers 50 --load-neo4j")
        
        print(f"\n{Colors.OKCYAN}2. Open Neo4j Browser:{Colors.ENDC}")
        print(f"   http://localhost:7474")
        
        print(f"\n{Colors.OKCYAN}3. Run exploration queries:{Colors.ENDC}")
        print(f"   MATCH (n) RETURN n LIMIT 25")
        print(f"   MATCH (s:Stressor)-[r]->(p:Phenotype) RETURN s, r, p")
        
    else:
        print(f"{Colors.FAIL}{Colors.BOLD}")
        print("❌ Some tests failed - please fix issues above")
        print(f"{Colors.ENDC}\n")
        
        print(f"{Colors.BOLD}Troubleshooting Steps:{Colors.ENDC}")
        print(f"{Colors.WARNING}1. Check Neo4j Desktop:{Colors.ENDC}")
        print(f"   - Is it running?")
        print(f"   - Is database status 'Active' (green)?")
        
        print(f"\n{Colors.WARNING}2. Verify credentials:{Colors.ENDC}")
        print(f"   - Check .env file in backend folder")
        print(f"   - Default password: spacebiology123")
        
        print(f"\n{Colors.WARNING}3. Check database name:{Colors.ENDC}")
        print(f"   - Expected: {config['database']}")
        print(f"   - Or try: neo4j (default database)")
        
        print(f"\n{Colors.WARNING}4. Restart Neo4j:{Colors.ENDC}")
        print(f"   - Stop database in Neo4j Desktop")
        print(f"   - Wait 5 seconds")
        print(f"   - Start database again")
        print(f"   - Run this script again")


def main():
    """Main verification function."""
    print_header("Neo4j Connection Verification")
    print_info("Space Biology Knowledge Engine")
    
    # Step 1: Load configuration
    config = load_configuration()
    
    print(f"\n{Colors.BOLD}Configuration:{Colors.ENDC}")
    print(f"  URI:      {config['uri']}")
    print(f"  Username: {config['user']}")
    print(f"  Database: {config['database']}")
    print()
    
    # Step 2: Test connection
    driver = test_connection(config)
    if not driver:
        display_summary(config, False)
        return False
    
    try:
        # Step 3: Test database access
        db_access = test_database_access(driver, config['database'])
        if not db_access:
            display_summary(config, False)
            return False
        
        # Step 4: Test query execution
        query_test = test_query_execution(driver, config['database'])
        if not query_test:
            display_summary(config, False)
            return False
        
        # Step 5: Test write permissions
        write_test = test_write_permissions(driver, config['database'])
        if not write_test:
            display_summary(config, False)
            return False
        
        # All tests passed
        display_summary(config, True)
        return True
    
    finally:
        driver.close()


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Verification cancelled by user{Colors.ENDC}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

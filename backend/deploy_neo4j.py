"""
Neo4j Deployment Automation Script
Space Biology Knowledge Engine

Provides guided setup for three Neo4j deployment options:
1. Neo4j Desktop (Local Development)
2. Neo4j AuraDB (Cloud Production)
3. Docker Container (Containerized)

Author: Space Biology KG Team
Date: October 2025
"""

import os
import sys
import subprocess
from pathlib import Path


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


def check_docker_installed():
    """Check if Docker is installed and running."""
    try:
        result = subprocess.run(
            ['docker', '--version'],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            return True
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    return False


def check_neo4j_running(uri="bolt://localhost:7687"):
    """Check if Neo4j is accessible."""
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(uri, auth=("neo4j", "spacebiology123"))
        with driver.session() as session:
            session.run("RETURN 1")
        driver.close()
        return True
    except Exception:
        return False


def create_env_file(uri, username, password, database):
    """Create .env file with Neo4j configuration."""
    env_content = f"""# Neo4j Configuration
NEO4J_URI={uri}
NEO4J_USER={username}
NEO4J_PASSWORD={password}
NEO4J_DATABASE={database}

# FastAPI Configuration
API_HOST=localhost
API_PORT=8000

# Pipeline Configuration
MAX_PAPERS=50
USE_CURATED=true
USE_PUBMED=true
USE_GENELAB=false
"""
    
    backend_dir = Path(__file__).parent
    env_path = backend_dir / '.env'
    
    with open(env_path, 'w') as f:
        f.write(env_content)
    
    print_success(f"Created .env file at: {env_path}")


def deploy_docker_neo4j():
    """Deploy Neo4j using Docker."""
    print_header("Neo4j Docker Deployment")
    
    if not check_docker_installed():
        print_error("Docker is not installed or not running!")
        print_info("Please install Docker Desktop from: https://www.docker.com/products/docker-desktop")
        return False
    
    print_info("Deploying Neo4j 5.13 Community Edition...")
    
    # Stop existing container if running
    subprocess.run(['docker', 'stop', 'neo4j-astrobiomers'], 
                   capture_output=True, timeout=10)
    subprocess.run(['docker', 'rm', 'neo4j-astrobiomers'], 
                   capture_output=True, timeout=10)
    
    # Run new container
    cmd = [
        'docker', 'run', '-d',
        '--name', 'neo4j-astrobiomers',
        '-p', '7474:7474',
        '-p', '7687:7687',
        '-e', 'NEO4J_AUTH=neo4j/spacebiology123',
        '-e', 'NEO4J_PLUGINS=["apoc","graph-data-science"]',
        '-e', 'NEO4J_dbms_memory_heap_max__size=2G',
        'neo4j:5.13-community'
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        if result.returncode == 0:
            print_success("Neo4j container started successfully!")
            print_info("Container ID: " + result.stdout.strip()[:12])
            print_warning("Waiting 15 seconds for Neo4j to initialize...")
            
            import time
            time.sleep(15)
            
            if check_neo4j_running():
                print_success("Neo4j is ready and responding!")
                print_info("Browser: http://localhost:7474")
                print_info("Bolt: bolt://localhost:7687")
                print_info("Username: neo4j")
                print_info("Password: spacebiology123")
                
                create_env_file(
                    uri="bolt://localhost:7687",
                    username="neo4j",
                    password="spacebiology123",
                    database="neo4j"
                )
                return True
            else:
                print_warning("Container started but Neo4j not responding yet")
                print_info("Give it another minute and check: http://localhost:7474")
                return True
        else:
            print_error(f"Failed to start container: {result.stderr}")
            return False
    
    except subprocess.TimeoutExpired:
        print_error("Docker command timed out")
        return False


def setup_desktop_neo4j():
    """Guide user through Neo4j Desktop setup."""
    print_header("Neo4j Desktop Setup Guide")
    
    print("""
Neo4j Desktop is the recommended option for local development.

📥 STEP 1: Download Neo4j Desktop
   Visit: https://neo4j.com/download/
   Download the installer for Windows
   
🔧 STEP 2: Install and Launch
   - Run the installer
   - Create a Neo4j account (free)
   - Launch Neo4j Desktop
   
📊 STEP 3: Create Database
   In Neo4j Desktop:
   1. Click "New Project" (or use existing)
   2. Click "Add Database" → "Create Local Database"
   3. Database Name: astrobiomers
   4. Password: spacebiology123
   5. Version: 5.x (latest)
   6. Click "Create"
   
▶️ STEP 4: Start Database
   Click "Start" button on your database
   Wait for green "Active" status
   
🌐 STEP 5: Verify Installation
   Click "Open" → "Neo4j Browser"
   In the browser, run: MATCH (n) RETURN count(n)
   (Should return 0 - empty database ready)
    """)
    
    input(f"\n{Colors.BOLD}Press Enter when you've completed these steps...{Colors.ENDC}")
    
    print_info("\nChecking Neo4j connection...")
    if check_neo4j_running():
        print_success("Neo4j Desktop is running and accessible!")
        create_env_file(
            uri="bolt://localhost:7687",
            username="neo4j",
            password="spacebiology123",
            database="astrobiomers"
        )
        return True
    else:
        print_warning("Cannot connect to Neo4j yet")
        print_info("Make sure database is started in Neo4j Desktop")
        print_info("Default connection: bolt://localhost:7687")
        
        manual = input("\nDo you want to manually configure connection? (y/n): ")
        if manual.lower() == 'y':
            uri = input("Neo4j URI [bolt://localhost:7687]: ") or "bolt://localhost:7687"
            username = input("Username [neo4j]: ") or "neo4j"
            password = input("Password: ")
            database = input("Database [astrobiomers]: ") or "astrobiomers"
            
            create_env_file(uri, username, password, database)
            return True
        
        return False


def setup_aura_neo4j():
    """Guide user through Neo4j AuraDB setup."""
    print_header("Neo4j AuraDB Cloud Setup Guide")
    
    print("""
Neo4j AuraDB is a fully-managed cloud database - perfect for production!

☁️ STEP 1: Create Free Account
   Visit: https://neo4j.com/cloud/aura/
   Sign up for AuraDB Free tier
   
📊 STEP 2: Create Database Instance
   1. Click "Create Database" 
   2. Select "AuraDB Free"
   3. Instance Name: astrobiomers-kg
   4. Region: Choose closest to you
   5. Click "Create Database"
   
🔐 STEP 3: Save Credentials
   ⚠️ IMPORTANT: Save the generated credentials!
   - Connection URI (looks like: neo4j+s://xxxxx.databases.neo4j.io)
   - Username (usually: neo4j)
   - Password (auto-generated)
   
   You can download credentials as a .txt file
   
⏳ STEP 4: Wait for Deployment
   Database creation takes 2-5 minutes
   Wait for "Running" status
   
🌐 STEP 5: Test Connection
   Click "Query" button to open Browser
   Run: MATCH (n) RETURN count(n)
    """)
    
    input(f"\n{Colors.BOLD}Press Enter when your AuraDB instance is running...{Colors.ENDC}")
    
    print_info("\nEnter your AuraDB connection details:")
    uri = input("Connection URI (neo4j+s://...): ")
    username = input("Username [neo4j]: ") or "neo4j"
    password = input("Password: ")
    database = input("Database [neo4j]: ") or "neo4j"
    
    if uri and password:
        create_env_file(uri, username, password, database)
        print_success("AuraDB configuration saved!")
        return True
    else:
        print_error("Missing required connection details")
        return False


def load_knowledge_graph():
    """Load knowledge graph into Neo4j."""
    print_header("Loading Knowledge Graph")
    
    print_info("Running pipeline with Neo4j loading enabled...")
    
    cmd = [
        sys.executable, '-m', 'knowledge_graph.cli',
        'build',
        '--papers', '50',
        '--load-neo4j'
    ]
    
    try:
        result = subprocess.run(
            cmd,
            cwd=Path(__file__).parent,
            capture_output=False,
            timeout=300
        )
        
        if result.returncode == 0:
            print_success("Knowledge graph loaded successfully!")
            return True
        else:
            print_error("Pipeline failed during Neo4j loading")
            return False
    
    except subprocess.TimeoutExpired:
        print_error("Pipeline timed out (>5 minutes)")
        return False


def main():
    """Main deployment wizard."""
    print_header("Space Biology Knowledge Engine - Neo4j Deployment")
    
    print("""
This wizard will help you deploy Neo4j for your knowledge graph.

Choose your deployment option:

1. 🐳 Docker Container (Quick & Easy - Recommended)
   - Automated setup
   - Isolated environment
   - Requires Docker Desktop

2. 💻 Neo4j Desktop (Local Development)
   - Visual interface
   - Manual setup
   - Best for learning/development

3. ☁️ Neo4j AuraDB (Cloud Production)
   - Fully managed
   - Production-ready
   - Free tier available

4. ⏭️ Skip - I'll configure manually

    """)
    
    choice = input("Enter your choice (1-4): ").strip()
    
    success = False
    
    if choice == '1':
        success = deploy_docker_neo4j()
    elif choice == '2':
        success = setup_desktop_neo4j()
    elif choice == '3':
        success = setup_aura_neo4j()
    elif choice == '4':
        print_info("Manual configuration selected")
        print_info("See NEO4J_SETUP.md for instructions")
        return
    else:
        print_error("Invalid choice")
        return
    
    if success:
        print_success("\n✓ Neo4j is configured!")
        
        load_now = input("\nLoad knowledge graph now? (y/n): ")
        if load_now.lower() == 'y':
            load_knowledge_graph()
            
            print_header("🎉 Deployment Complete!")
            print_success("Neo4j is running with your knowledge graph loaded!")
            print_info("\nNext Steps:")
            print("   1. Open Neo4j Browser: http://localhost:7474")
            print("   2. Run query: MATCH (n) RETURN count(n)")
            print("   3. Explore your knowledge graph!")
        else:
            print_info("\nTo load later, run:")
            print("   cd backend")
            print("   python -m knowledge_graph.cli build --papers 50 --load-neo4j")
    else:
        print_warning("\nSetup incomplete - see error messages above")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.WARNING}Setup cancelled by user{Colors.ENDC}")
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()

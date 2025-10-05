#!/usr/bin/env python3
"""
Neo4j Setup and Data Loading for ASTROBIOMERS Production
"""

import os
import json
import subprocess
import sys
from pathlib import Path

def check_neo4j_installation():
    """Check if Neo4j is installed and accessible"""
    print("🔍 Checking Neo4j installation...")
    
    # Try to import neo4j driver
    try:
        from neo4j import GraphDatabase
        print("  ✅ Neo4j Python driver available")
        return True
    except ImportError:
        print("  ❌ Neo4j driver not available")
        return False

def download_neo4j():
    """Download and setup Neo4j Community Edition"""
    print("📥 Setting up Neo4j Community Edition...")
    
    neo4j_dir = Path("C:/neo4j-community")
    if neo4j_dir.exists():
        print(f"  ✅ Neo4j already exists at {neo4j_dir}")
        return True
    
    print("  ℹ️  Neo4j not found. Manual installation required:")
    print("     1. Visit: https://neo4j.com/download-center/#community")
    print("     2. Download Neo4j Community Server")
    print("     3. Extract to C:/neo4j-community")
    print("     4. Run: C:/neo4j-community/bin/neo4j.bat console")
    
    return False

def start_neo4j_server():
    """Start Neo4j server if not running"""
    print("🚀 Starting Neo4j server...")
    
    # Try to connect to existing instance
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "spacebiology123")
        )
        
        with driver.session() as session:
            result = session.run("RETURN 'Connection successful' as message")
            record = result.single()
            print(f"  ✅ Neo4j is running: {record['message']}")
            driver.close()
            return True
            
    except Exception as e:
        print(f"  ❌ Neo4j not accessible: {e}")
        
        # Try to start with default password
        try:
            driver = GraphDatabase.driver(
                "bolt://localhost:7687", 
                auth=("neo4j", "neo4j")
            )
            
            with driver.session() as session:
                # Change default password
                session.run("ALTER CURRENT USER SET PASSWORD FROM 'neo4j' TO 'spacebiology123'")
                print("  ✅ Neo4j password updated")
                driver.close()
                return True
                
        except Exception as e2:
            print(f"  ❌ Could not connect with default password: {e2}")
            print("  ℹ️  Please ensure Neo4j is running on bolt://localhost:7687")
            print("     - Default user: neo4j")
            print("     - Set password to: spacebiology123")
            return False

def create_neo4j_schema():
    """Create schema constraints and indexes"""
    print("📊 Creating Neo4j schema...")
    
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "spacebiology123")
        )
        
        with driver.session() as session:
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT paper_id_unique IF NOT EXISTS FOR (p:Paper) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT entity_id_unique IF NOT EXISTS FOR (e:Entity) REQUIRE e.id IS UNIQUE",
                "CREATE CONSTRAINT author_name_unique IF NOT EXISTS FOR (a:Author) REQUIRE a.name IS UNIQUE",
                "CREATE CONSTRAINT journal_name_unique IF NOT EXISTS FOR (j:Journal) REQUIRE j.name IS UNIQUE"
            ]
            
            # Create indexes
            indexes = [
                "CREATE INDEX paper_title_index IF NOT EXISTS FOR (p:Paper) ON (p.title)",
                "CREATE INDEX entity_name_index IF NOT EXISTS FOR (e:Entity) ON (e.name)",
                "CREATE INDEX entity_type_index IF NOT EXISTS FOR (e:Entity) ON (e.type)",
                "CREATE INDEX paper_year_index IF NOT EXISTS FOR (p:Paper) ON (p.year)",
                "CREATE FULLTEXT INDEX paper_content_index IF NOT EXISTS FOR (p:Paper) ON EACH [p.title, p.abstract]"
            ]
            
            all_commands = constraints + indexes
            
            for command in all_commands:
                try:
                    session.run(command)
                    print(f"  ✅ Executed: {command.split(' ')[1:4]}")
                except Exception as e:
                    if "already exists" in str(e) or "An equivalent" in str(e):
                        print(f"  ℹ️  Already exists: {command.split(' ')[1:4]}")
                    else:
                        print(f"  ❌ Failed: {command} - {e}")
        
        driver.close()
        print("  ✅ Schema creation complete")
        return True
        
    except Exception as e:
        print(f"  ❌ Schema creation failed: {e}")
        return False

def load_pipeline_data():
    """Load existing pipeline data into Neo4j"""
    print("📤 Loading pipeline data into Neo4j...")
    
    # Check if pipeline data exists
    pipeline_dir = Path("data/pipeline_output")
    if not pipeline_dir.exists():
        print("  ❌ No pipeline data found. Run pipeline first:")
        print("     python -m knowledge_graph.cli build --papers 50 --skip-neo4j")
        return False
    
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "spacebiology123")
        )
        
        # Load papers
        papers_file = pipeline_dir / "raw_papers.json"
        if papers_file.exists():
            with open(papers_file) as f:
                papers = json.load(f)
            
            with driver.session() as session:
                for paper in papers:
                    session.run("""
                        MERGE (p:Paper {id: $id})
                        SET p.title = $title,
                            p.abstract = $abstract,
                            p.year = $year,
                            p.journal = $journal,
                            p.pmc_id = $pmc_id,
                            p.pmid = $pmid,
                            p.doi = $doi
                    """, 
                    id=paper.get('id', paper.get('pmid', 'unknown')),
                    title=paper.get('title', ''),
                    abstract=paper.get('abstract', ''),
                    year=paper.get('year'),
                    journal=paper.get('journal', ''),
                    pmc_id=paper.get('pmc_id'),
                    pmid=paper.get('pmid'),
                    doi=paper.get('doi')
                    )
            
            print(f"  ✅ Loaded {len(papers)} papers")
        
        # Load entities
        entities_file = pipeline_dir / "extracted_entities.json"
        if entities_file.exists():
            with open(entities_file) as f:
                papers_with_entities = json.load(f)
            
            entity_count = 0
            with driver.session() as session:
                for paper in papers_with_entities:
                    paper_id = paper.get('id', paper.get('pmid', 'unknown'))
                    
                    for entity in paper.get('entities', []):
                        # Create entity
                        session.run("""
                            MERGE (e:Entity {name: $name, type: $type})
                            SET e.confidence = $confidence
                        """,
                        name=entity.get('name', ''),
                        type=entity.get('type', 'UNKNOWN'),
                        confidence=entity.get('confidence', 0.0)
                        )
                        
                        # Link to paper
                        session.run("""
                            MATCH (p:Paper {id: $paper_id})
                            MATCH (e:Entity {name: $entity_name, type: $entity_type})
                            MERGE (p)-[:MENTIONS]->(e)
                        """,
                        paper_id=paper_id,
                        entity_name=entity.get('name', ''),
                        entity_type=entity.get('type', 'UNKNOWN')
                        )
                        
                        entity_count += 1
            
            print(f"  ✅ Loaded {entity_count} entities")
        
        # Load relationships
        relationships_file = pipeline_dir / "extracted_relationships.json"
        if relationships_file.exists():
            with open(relationships_file) as f:
                relationships = json.load(f)
            
            with driver.session() as session:
                for rel in relationships:
                    session.run("""
                        MATCH (e1:Entity {name: $source})
                        MATCH (e2:Entity {name: $target})
                        MERGE (e1)-[r:RELATED_TO]->(e2)
                        SET r.type = $type,
                            r.confidence = $confidence,
                            r.context = $context
                    """,
                    source=rel.get('source', ''),
                    target=rel.get('target', ''),
                    type=rel.get('type', 'UNKNOWN'),
                    confidence=rel.get('confidence', 0.0),
                    context=rel.get('context', '')
                    )
            
            print(f"  ✅ Loaded {len(relationships)} relationships")
        
        driver.close()
        return True
        
    except Exception as e:
        print(f"  ❌ Data loading failed: {e}")
        return False

def verify_neo4j_data():
    """Verify that data was loaded correctly"""
    print("🔍 Verifying Neo4j data...")
    
    try:
        from neo4j import GraphDatabase
        
        driver = GraphDatabase.driver(
            "bolt://localhost:7687", 
            auth=("neo4j", "spacebiology123")
        )
        
        with driver.session() as session:
            # Count nodes
            result = session.run("MATCH (n) RETURN labels(n) as label, count(n) as count")
            
            print("  📊 Node counts:")
            total_nodes = 0
            for record in result:
                label = record['label'][0] if record['label'] else 'Unlabeled'
                count = record['count']
                total_nodes += count
                print(f"    {label}: {count}")
            
            print(f"    Total: {total_nodes}")
            
            # Count relationships
            result = session.run("MATCH ()-[r]->() RETURN type(r) as type, count(r) as count")
            
            print("  🔗 Relationship counts:")
            total_rels = 0
            for record in result:
                rel_type = record['type']
                count = record['count']
                total_rels += count
                print(f"    {rel_type}: {count}")
            
            print(f"    Total: {total_rels}")
        
        driver.close()
        
        if total_nodes > 0:
            print("  ✅ Neo4j contains data and is ready for web application!")
            return True
        else:
            print("  ⚠️  Neo4j is empty. Load data first.")
            return False
        
    except Exception as e:
        print(f"  ❌ Verification failed: {e}")
        return False

def main():
    """Main setup function"""
    print("=" * 70)
    print("🚀 ASTROBIOMERS NEO4J SETUP FOR WEB APPLICATION")
    print("=" * 70)
    
    steps = [
        ("Check Neo4j Installation", check_neo4j_installation),
        ("Start Neo4j Server", start_neo4j_server),
        ("Create Schema", create_neo4j_schema),
        ("Load Pipeline Data", load_pipeline_data),
        ("Verify Data", verify_neo4j_data)
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}...")
        success = step_func()
        
        if not success:
            print(f"\n❌ {step_name} failed. Please resolve and try again.")
            print("\n🔧 Manual Setup Instructions:")
            print("1. Download Neo4j Desktop: https://neo4j.com/download/")
            print("2. Create database with password: spacebiology123")
            print("3. Start the database")
            print("4. Re-run this script")
            return False
    
    print("\n" + "=" * 70)
    print("🎉 NEO4J SETUP COMPLETE!")
    print("✅ Graph database ready for web application")
    print("✅ Schema created with constraints and indexes")
    print("✅ Pipeline data loaded successfully")
    print()
    print("🌐 Access Neo4j Browser: http://localhost:7474")
    print("🔗 Neo4j Bolt URI: bolt://localhost:7687")
    print("👤 Username: neo4j")
    print("🔑 Password: spacebiology123")
    print()
    print("🚀 Your web application can now use the full graph database!")
    print("=" * 70)

if __name__ == "__main__":
    main()
"""
Export Neo4j Desktop data for cloud migration
Run this to export your current database to Cypher statements
"""

from neo4j import GraphDatabase
import json

# Your current Neo4j Desktop credentials
NEO4J_URI = "bolt://localhost:7687"
NEO4J_USER = "neo4j"
NEO4J_PASSWORD = "spacebiology123"
NEO4J_DATABASE = "astrobiomers"

class Neo4jExporter:
    def __init__(self, uri, user, password, database):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.database = database
        
    def close(self):
        self.driver.close()
        
    def export_to_cypher(self, output_file="neo4j_export.cypher"):
        """Export all nodes and relationships as Cypher CREATE statements"""
        
        with self.driver.session(database=self.database) as session:
            cypher_statements = []
            
            # Export nodes
            print("Exporting nodes...")
            result = session.run("MATCH (n) RETURN n, labels(n) as labels, id(n) as id")
            
            node_map = {}
            for record in result:
                node = record["n"]
                labels = record["labels"]
                node_id = record["id"]
                
                # Create node variable
                node_map[node_id] = f"n{node_id}"
                
                # Build CREATE statement
                label_str = ":".join(labels) if labels else ""
                props = dict(node)
                props_str = ", ".join([f"{k}: {json.dumps(v)}" for k, v in props.items()])
                
                cypher = f"CREATE ({node_map[node_id]}:{label_str} {{{props_str}}})"
                cypher_statements.append(cypher)
            
            print(f"Exported {len(cypher_statements)} nodes")
            
            # Export relationships
            print("Exporting relationships...")
            result = session.run("""
                MATCH (a)-[r]->(b) 
                RETURN id(a) as start_id, id(b) as end_id, type(r) as rel_type, properties(r) as props
            """)
            
            rel_count = 0
            for record in result:
                start_id = record["start_id"]
                end_id = record["end_id"]
                rel_type = record["rel_type"]
                props = record["props"]
                
                if start_id in node_map and end_id in node_map:
                    props_str = ", ".join([f"{k}: {json.dumps(v)}" for k, v in props.items()]) if props else ""
                    props_part = f" {{{props_str}}}" if props_str else ""
                    
                    cypher = f"CREATE ({node_map[start_id]})-[:{rel_type}{props_part}]->({node_map[end_id]})"
                    cypher_statements.append(cypher)
                    rel_count += 1
            
            print(f"Exported {rel_count} relationships")
            
            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write("// Neo4j Export\n")
                f.write("// Generated for cloud migration\n\n")
                f.write("// Clear database first\n")
                f.write("MATCH (n) DETACH DELETE n;\n\n")
                f.write("// Create nodes and relationships\n")
                for stmt in cypher_statements:
                    f.write(stmt + ";\n")
            
            print(f"\nExport complete! File saved: {output_file}")
            print(f"Total statements: {len(cypher_statements)}")
            
    def export_stats(self):
        """Get database statistics"""
        with self.driver.session(database=self.database) as session:
            # Count nodes
            node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
            
            # Count relationships
            rel_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
            
            # Get labels
            labels = session.run("CALL db.labels()").values()
            
            # Get relationship types
            rel_types = session.run("CALL db.relationshipTypes()").values()
            
            print("\n" + "="*50)
            print("DATABASE STATISTICS")
            print("="*50)
            print(f"Total Nodes: {node_count}")
            print(f"Total Relationships: {rel_count}")
            print(f"\nNode Labels: {', '.join([l[0] for l in labels])}")
            print(f"\nRelationship Types: {', '.join([r[0] for r in rel_types])}")
            print("="*50 + "\n")

if __name__ == "__main__":
    print("Neo4j Desktop Data Export Tool")
    print("="*50)
    
    exporter = Neo4jExporter(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE)
    
    try:
        # Show stats
        exporter.export_stats()
        
        # Export data
        print("\nStarting export...")
        exporter.export_to_cypher("neo4j_export.cypher")
        
        print("\n✅ SUCCESS! Your data is exported to: neo4j_export.cypher")
        print("\nNext steps:")
        print("1. Create Neo4j Aura account")
        print("2. Create new database")
        print("3. Upload this export.cypher file")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        print("\nTroubleshooting:")
        print("- Make sure Neo4j Desktop is running")
        print("- Check your password in this script")
        print("- Verify database name is 'astrobiomers'")
    
    finally:
        exporter.close()

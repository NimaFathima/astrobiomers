"""
Script to inspect what's currently in Neo4j and run enrichment
"""
from knowledge_graph.query_engine import QueryEngine
import json

def inspect_current_data():
    qe = QueryEngine()
    
    print("=" * 60)
    print("NEO4J DATABASE INSPECTION")
    print("=" * 60)
    
    # Get node type breakdown
    print("\n📊 NODE TYPES:")
    node_types = qe.execute_query("""
        MATCH (n)
        RETURN labels(n)[0] as label, count(n) as count
        ORDER BY count DESC
    """)
    for row in node_types:
        print(f"  {row['label']}: {row['count']}")
    
    # Get relationship types
    print("\n🔗 RELATIONSHIP TYPES:")
    rel_types = qe.execute_query("""
        MATCH ()-[r]->()
        RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
    """)
    for row in rel_types:
        print(f"  {row['rel_type']}: {row['count']}")
    
    # Sample a few papers
    print("\n📄 SAMPLE PAPERS:")
    papers = qe.execute_query("""
        MATCH (p:Paper)
        RETURN p.pmid as pmid, p.title as title, p.publication_year as year
        LIMIT 3
    """)
    for i, paper in enumerate(papers, 1):
        print(f"  {i}. [{paper.get('pmid', 'N/A')}] {paper.get('title', 'No title')[:80]}... ({paper.get('year', 'N/A')})")
    
    # Check what other entity types exist
    print("\n🔬 CHECKING FOR ENTITIES:")
    entities = qe.execute_query("""
        MATCH (n)
        WHERE NOT n:Paper
        RETURN labels(n)[0] as entity_type, n.name as name
        LIMIT 5
    """)
    if entities:
        for ent in entities:
            print(f"  {ent['entity_type']}: {ent.get('name', 'N/A')}")
    else:
        print("  ⚠️  No non-paper entities found")
    
    qe.close()

if __name__ == "__main__":
    inspect_current_data()

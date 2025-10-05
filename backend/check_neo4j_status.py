"""
Quick script to check Neo4j database status
"""
from knowledge_graph.query_engine import QueryEngine

def check_database():
    try:
        qe = QueryEngine()
        
        # Check total nodes
        result = qe.execute_query('MATCH (n) RETURN count(n) as total')
        total_nodes = result[0]['total']
        print(f"✓ Total nodes in database: {total_nodes}")
        
        # Check papers
        papers = qe.execute_query('MATCH (p:Paper) RETURN count(p) as total')
        paper_count = papers[0]['total']
        print(f"✓ Papers: {paper_count}")
        
        # Check genes
        genes = qe.execute_query('MATCH (g:Gene) RETURN count(g) as total')
        gene_count = genes[0]['total']
        print(f"✓ Genes: {gene_count}")
        
        # Check topics
        topics = qe.execute_query('MATCH (t:Topic) RETURN count(t) as total')
        topic_count = topics[0]['total']
        print(f"✓ Topics: {topic_count}")
        
        # Check relationships
        rels = qe.execute_query('MATCH ()-[r]->() RETURN count(r) as total')
        rel_count = rels[0]['total']
        print(f"✓ Relationships: {rel_count}")
        
        qe.close()
        
        if total_nodes == 0:
            print("\n⚠️  Database is EMPTY - need to run ingestion pipeline")
            return False
        else:
            print(f"\n✅ Database has data! ({total_nodes} nodes, {rel_count} relationships)")
            return True
            
    except Exception as e:
        print(f"❌ Error checking database: {e}")
        return False

if __name__ == "__main__":
    check_database()

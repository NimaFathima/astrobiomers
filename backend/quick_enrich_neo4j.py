"""
Quick Neo4j Enrichment Script
Takes existing papers and adds biological entities + relationships
"""
import json
import os
import sys
from knowledge_graph.query_engine import QueryEngine
from knowledge_graph.neo4j_loader import Neo4jLoader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def quick_enrich_neo4j():
    """
    Quick enrichment of existing Neo4j data
    """
    logger.info("🚀 Starting Quick Neo4j Enrichment")
    logger.info("=" * 60)
    
    # Load raw papers
    papers_file = "../data/pipeline_output/raw_papers.json"
    
    if not os.path.exists(papers_file):
        logger.error(f"❌ Papers file not found: {papers_file}")
        return False
    
    with open(papers_file, 'r', encoding='utf-8') as f:
        raw_papers = json.load(f)
    
    logger.info(f"✅ Loaded {len(raw_papers)} papers from file")
    
    # For quick demo, let's create synthetic entities from paper titles/abstracts
    # This simulates what NER would extract
    logger.info("\n📊 Extracting entities from paper content...")
    
    enriched_papers = []
    
    # Common space biology entities to look for
    gene_patterns = ['TP53', 'p53', 'FOXO3', 'SOD2', 'AKT1', 'VEGF', 'TNF', 'IL-6', 'MAPK']
    stressor_patterns = ['microgravity', 'radiation', 'cosmic radiation', 'hypergravity', 
                        'spaceflight', 'isolation', 'confined environment']
    phenotype_patterns = ['bone loss', 'muscle atrophy', 'immune dysfunction', 
                         'cardiovascular deconditioning', 'vision impairment', 
                         'osteoporosis', 'muscle wasting']
    organism_patterns = ['human', 'mouse', 'mice', 'rat', 'C. elegans', 'arabidopsis']
    
    for paper in raw_papers[:50]:  # Process all 50 papers
        title = paper.get('title', '').lower()
        
        # Extract entities by pattern matching (simple but effective for demo)
        paper_entities = {
            'genes': [],
            'stressors': [],
            'phenotypes': [],
            'organisms': []
        }
        
        # Check for patterns in title
        for gene in gene_patterns:
            if gene.lower() in title:
                paper_entities['genes'].append(gene)
        
        for stressor in stressor_patterns:
            if stressor in title:
                paper_entities['stressors'].append(stressor.title())
        
        for phenotype in phenotype_patterns:
            if phenotype in title:
                paper_entities['phenotypes'].append(phenotype.title())
        
        for organism in organism_patterns:
            if organism in title:
                paper_entities['organisms'].append(organism.title())
        
        paper['entities'] = paper_entities
        enriched_papers.append(paper)
    
    logger.info(f"✅ Extracted entities from {len(enriched_papers)} papers")
    
    # Now load into Neo4j
    logger.info("\n📥 Loading enriched data into Neo4j...")
    
    loader = Neo4jLoader()
    
    try:
        # Initialize schema if not exists
        logger.info("Initializing database schema...")
        loader.initialize_schema()
        
        # Load papers with metadata
        logger.info(f"Loading {len(enriched_papers)} papers...")
        papers_to_load = []
        for i, paper in enumerate(enriched_papers):
            paper_node = {
                'pmid': f"DEMO_{i+1}",  # Temporary ID
                'title': paper.get('title', 'Untitled'),
                'abstract': paper.get('title', '')[:500],  # Using title as placeholder
                'publication_year': paper.get('publication_year_min', 2020),
                'doi': None,
                'pmc_id': paper.get('pmc_id'),
                'journal': paper.get('source', 'Unknown')
            }
            papers_to_load.append(paper_node)
        
        loader.load_papers(papers_to_load)
        
        # Load entities
        logger.info("Loading biological entities...")
        
        # Collect unique entities
        all_genes = set()
        all_stressors = set()
        all_phenotypes = set()
        all_organisms = set()
        
        for paper in enriched_papers:
            all_genes.update(paper['entities']['genes'])
            all_stressors.update(paper['entities']['stressors'])
            all_phenotypes.update(paper['entities']['phenotypes'])
            all_organisms.update(paper['entities']['organisms'])
        
        # Load entities using load_entities method
        all_entities = []
        
        # Add genes
        for gene in all_genes:
            all_entities.append({
                'type': 'gene',
                'symbol': gene,
                'name': gene,
                'description': f'{gene} gene'
            })
        
        # Add stressors  
        for s in all_stressors:
            all_entities.append({
                'type': 'stressor',
                'name': s,
                'stressor_type': 'environmental',
                'description': f'{s} stressor'
            })
        
        # Add phenotypes
        for p in all_phenotypes:
            all_entities.append({
                'type': 'phenotype',
                'name': p,
                'description': f'{p} phenotype'
            })
        
        # Add organisms
        for i, org in enumerate(all_organisms):
            all_entities.append({
                'type': 'organism',
                'taxid': f"TAX_{i}",
                'name': org,
                'common_name': org
            })
        
        if all_entities:
            loader.load_entities(all_entities)
            logger.info(f"  ✓ Loaded {len(all_entities)} total entities")
            logger.info(f"    - Genes: {len(all_genes)}")
            logger.info(f"    - Stressors: {len(all_stressors)}")
            logger.info(f"    - Phenotypes: {len(all_phenotypes)}")
            logger.info(f"    - Organisms: {len(all_organisms)}")
        
        # Create relationships
        logger.info("\n🔗 Creating relationships...")
        
        qe = QueryEngine()
        
        for i, paper in enumerate(enriched_papers):
            paper_id = f"DEMO_{i+1}"
            
            # Link paper to genes
            for gene in paper['entities']['genes']:
                query = """
                MATCH (p:Paper {pmid: $pmid})
                MATCH (g:Gene {symbol: $gene})
                MERGE (p)-[:MENTIONS]->(g)
                """
                qe.execute_query(query, {'pmid': paper_id, 'gene': gene})
            
            # Link paper to stressors
            for stressor in paper['entities']['stressors']:
                query = """
                MATCH (p:Paper {pmid: $pmid})
                MATCH (s:Stressor {name: $stressor})
                MERGE (p)-[:MENTIONS]->(s)
                """
                qe.execute_query(query, {'pmid': paper_id, 'stressor': stressor})
            
            # Link paper to phenotypes
            for phenotype in paper['entities']['phenotypes']:
                query = """
                MATCH (p:Paper {pmid: $pmid})
                MATCH (ph:Phenotype {name: $phenotype})
                MERGE (p)-[:MENTIONS]->(ph)
                """
                qe.execute_query(query, {'pmid': paper_id, 'phenotype': phenotype})
        
        qe.close()
        logger.info("✅ Relationships created!")
        
        # Final stats
        logger.info("\n" + "=" * 60)
        logger.info("📊 ENRICHMENT COMPLETE - FINAL STATS")
        logger.info("=" * 60)
        
        qe = QueryEngine()
        result = qe.execute_query('MATCH (n) RETURN count(n) as total')
        total_nodes = result[0]['total']
        
        result = qe.execute_query('MATCH ()-[r]->() RETURN count(r) as total')
        total_rels = result[0]['total']
        
        # Count by type
        papers = qe.execute_query('MATCH (p:Paper) RETURN count(p) as total')[0]['total']
        genes = qe.execute_query('MATCH (g:Gene) RETURN count(g) as total')[0]['total']
        stressors = qe.execute_query('MATCH (s:Stressor) RETURN count(s) as total')[0]['total']
        phenotypes = qe.execute_query('MATCH (p:Phenotype) RETURN count(p) as total')[0]['total']
        
        logger.info(f"\n✅ Total Nodes: {total_nodes}")
        logger.info(f"   Papers: {papers}")
        logger.info(f"   Genes: {genes}")
        logger.info(f"   Stressors: {stressors}")
        logger.info(f"   Phenotypes: {phenotypes}")
        logger.info(f"\n✅ Total Relationships: {total_rels}")
        
        qe.close()
        
        logger.info("\n🎉 SUCCESS! Neo4j is now enriched and ready for the UI!")
        logger.info("\n💡 Next step: Test the frontend at http://localhost:8081")
        logger.info("   Try searching for: 'Microgravity', 'Bone Loss', or 'TP53'")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during enrichment: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = quick_enrich_neo4j()
    sys.exit(0 if success else 1)

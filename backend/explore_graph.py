"""Quick script to explore the knowledge graph contents."""
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'spacebiology123'))
session = driver.session(database='astrobiomers')

print("\n" + "="*70)
print("SPACE BIOLOGY KNOWLEDGE GRAPH - CONTENTS")
print("="*70)

# Node counts by type
print("\n📊 NODE TYPES:")
result = session.run('MATCH (n) RETURN DISTINCT labels(n)[0] as label, count(*) as count ORDER BY count DESC')
for record in result:
    print(f"  • {record['label']}: {record['count']} nodes")

# Relationship counts
print("\n🔗 RELATIONSHIPS:")
result = session.run('MATCH ()-[r]->() RETURN type(r) as rel_type, count(*) as count ORDER BY count DESC')
for record in result:
    print(f"  • {record['rel_type']}: {record['count']} relationships")

# Sample stressors
print("\n🌪️  STRESSOR ENTITIES:")
result = session.run('MATCH (s:Stressor) RETURN s.name LIMIT 7')
for record in result:
    print(f"  • {record['s.name']}")

# Sample phenotypes
print("\n🧬 PHENOTYPE ENTITIES:")
result = session.run('MATCH (p:Phenotype) RETURN p.name')
for record in result:
    print(f"  • {record['p.name']}")

# Sample papers with their connections
print("\n📄 SAMPLE PAPERS WITH ENTITIES:")
result = session.run('''
    MATCH (p:Paper)-[m:MENTIONS]->(e)
    RETURN p.title, labels(e)[0] as entity_type, e.name as entity_name, m.confidence
    ORDER BY m.confidence DESC
    LIMIT 5
''')
for record in result:
    title = record['p.title'][:60] + "..." if len(record['p.title']) > 60 else record['p.title']
    print(f"\n  📰 {title}")
    print(f"     → {record['entity_type']}: {record['entity_name']} (confidence: {record['m.confidence']:.2f})")

# Graph statistics
print("\n" + "="*70)
result = session.run('MATCH (n) RETURN count(n) as nodes')
node_count = result.single()['nodes']
result = session.run('MATCH ()-[r]->() RETURN count(r) as rels')
rel_count = result.single()['rels']
print(f"📈 TOTAL: {node_count} nodes, {rel_count} relationships")
print("="*70 + "\n")

session.close()
driver.close()

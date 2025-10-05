"""Clear data from the default Neo4j database."""
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'spacebiology123'))

print("\n" + "="*70)
print("CLEARING DEFAULT NEO4J DATABASE")
print("="*70)

# Clear default database
session = driver.session()
print("\nCounting nodes in default database...")
result = session.run('MATCH (n) RETURN count(n) as count')
count = result.single()['count']
print(f"Found {count} nodes")

if count > 0:
    print(f"\nDeleting all {count} nodes and relationships...")
    session.run('MATCH (n) DETACH DELETE n')
    print("✓ Deleted successfully!")
else:
    print("\nDatabase is already empty.")

session.close()
driver.close()

print("\n" + "="*70)
print("DEFAULT DATABASE CLEARED - Ready for pipeline run")
print("="*70 + "\n")

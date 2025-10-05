"""Check Neo4j database status."""
from neo4j import GraphDatabase

driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'spacebiology123'))

print("\n=== NEO4J DATABASES ===")
try:
    result = driver.execute_query('SHOW DATABASES')
    for r in result.records:
        print(f"  • {r['name']}: {r['currentStatus']}")
except Exception as e:
    print(f"Error: {e}")

# Check default database
print("\n=== CHECKING DEFAULT DATABASE ===")
session = driver.session()
result = session.run('MATCH (n) RETURN count(n) as count')
count = result.single()['count']
print(f"Nodes in default database: {count}")
session.close()

# Check astrobiomers database
print("\n=== CHECKING ASTROBIOMERS DATABASE ===")
session = driver.session(database='astrobiomers')
result = session.run('MATCH (n) RETURN count(n) as count')
count = result.single()['count']
print(f"Nodes in astrobiomers database: {count}")

if count > 0:
    result = session.run('MATCH (n) RETURN DISTINCT labels(n)[0] as label, count(*) as cnt ORDER BY cnt DESC')
    print("\nNode types:")
    for r in result:
        print(f"  • {r['label']}: {r['cnt']}")

session.close()
driver.close()

# Neo4j Setup for ASTROBIOMERS Web Application

## Quick Neo4j Installation (No Docker Required)

### Option 1: Download Neo4j Desktop (Recommended for Development)
1. Visit: https://neo4j.com/download/
2. Download Neo4j Desktop (free)
3. Install and create new database:
   - Database Name: astrobiomers
   - Password: spacebiology123
   - Version: 5.x

### Option 2: Neo4j Community Server
1. Download from: https://neo4j.com/download-center/#community
2. Extract to C:\neo4j
3. Configure in neo4j.conf:
   ```
   dbms.default_database=astrobiomers
   dbms.security.auth_enabled=true
   ```

### Option 3: Use Neo4j AuraDB (Cloud - Production Ready)
1. Visit: https://neo4j.com/cloud/aura/
2. Create free instance
3. Note connection details for configuration

## Configuration for ASTROBIOMERS

Update your .env file:
```env
NEO4J_URI=bolt://localhost:7687
NEO4J_USER=neo4j  
NEO4J_PASSWORD=spacebiology123
NEO4J_DATABASE=astrobiomers
```

## Loading Your Data

Once Neo4j is running, use our pipeline:
```bash
cd c:\Users\mi\Downloads\ASTROBIOMERS\backend
python -m knowledge_graph.cli build --papers 50 --load-neo4j
```

## Verification

Access Neo4j Browser at: http://localhost:7474
Run test query: `MATCH (n) RETURN count(n)`
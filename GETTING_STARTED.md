# Getting Started with ASTROBIOMERS

This guide will help you set up and run the Space Biology Knowledge Engine on your local machine.

## Prerequisites

Before you begin, ensure you have the following installed:

- **Docker Desktop** (Windows/Mac) or **Docker Engine** (Linux)
  - Download from: https://www.docker.com/products/docker-desktop/
- **Node.js** (v18+) and npm
  - Download from: https://nodejs.org/
- **Python** (v3.10+)
  - Download from: https://www.python.org/downloads/
- **Git**
  - Download from: https://git-scm.com/downloads/

### Optional but Recommended
- **VS Code** with Python and JavaScript/React extensions
- **Postman** or **Insomnia** for API testing

## Quick Start with Docker (Recommended)

The easiest way to get started is using Docker Compose, which will spin up all services automatically.

### 1. Clone the Repository

```bash
git clone <your-repository-url>
cd ASTROBIOMERS
```

### 2. Set Up Environment Variables

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env and add your API keys:
# - OPENAI_API_KEY (required for AI features)
# - PUBMED_EMAIL and PUBMED_API_KEY (for data ingestion)
```

**Windows (PowerShell)**:
```powershell
Copy-Item .env.example .env
notepad .env
```

### 3. Start All Services

```bash
docker-compose up -d
```

This will start:
- **Neo4j** (Knowledge Graph) - http://localhost:7474
- **PostgreSQL** (User Data)
- **Redis** (Caching)
- **Elasticsearch** (Search)
- **MinIO** (S3-compatible storage) - http://localhost:9001
- **Backend API** - http://localhost:8000
- **Frontend App** - http://localhost:3000
- **Airflow** (Data Pipeline) - http://localhost:8080

### 4. Initialize the Databases

Wait for all services to be healthy (about 30-60 seconds), then run:

```bash
# Initialize PostgreSQL schema
docker-compose exec backend python scripts/init_db.py

# (Optional) Load sample data
docker-compose exec backend python scripts/load_sample_data.py
```

### 5. Access the Application

Open your browser and navigate to:
- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Neo4j Browser**: http://localhost:7474 (username: `neo4j`, password: `spacebiology123`)
- **Airflow UI**: http://localhost:8080 (username: `admin`, password: `admin`)

## Manual Setup (Without Docker)

If you prefer to run services locally without Docker:

### 1. Install and Start Databases

#### Neo4j
```bash
# Download Neo4j Desktop from: https://neo4j.com/download/
# Or use Neo4j Aura (cloud): https://neo4j.com/cloud/aura/
# Create a new database with username: neo4j, password: spacebiology123
```

#### PostgreSQL
```bash
# Install PostgreSQL 15+
# Create database:
createdb astrobiomers_db

# Run initialization script:
psql -d astrobiomers_db -f scripts/init_postgres.sql
```

#### Redis
```bash
# Install Redis from: https://redis.io/download
# Or use Docker:
docker run -d -p 6379:6379 redis:7-alpine
```

#### Elasticsearch
```bash
# Download and install from: https://www.elastic.co/downloads/elasticsearch
# Or use Docker:
docker run -d -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:8.10.0
```

### 2. Set Up Backend

```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
.\venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLP models
python -m spacy download en_core_web_sm

# Set environment variables
copy ..\.env.example .env
# Edit .env with your database credentials

# Run the backend
uvicorn main:app --reload
```

Backend will be available at: http://localhost:8000

### 3. Set Up Frontend

```bash
cd frontend

# Install dependencies
npm install

# Set environment variables
copy .env.example .env.local
# Edit .env.local

# Start development server
npm start
```

Frontend will be available at: http://localhost:3000

## Verifying the Installation

### 1. Check Backend Health

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "services": {
    "api": "operational"
  }
}
```

### 2. Check Neo4j Connection

Open http://localhost:7474 in your browser and run:
```cypher
MATCH (n) RETURN count(n) as node_count;
```

### 3. Test the Frontend

Open http://localhost:3000 - you should see the home page with the four pillars.

## Next Steps

### 1. Ingest Sample Data

```bash
# Using Docker:
docker-compose exec backend python scripts/ingest_pubmed.py --query "microgravity" --max-results 100

# Or manually:
cd backend
python scripts/ingest_pubmed.py --query "microgravity" --max-results 100
```

This will:
1. Fetch 100 publications from PubMed about microgravity
2. Extract entities (genes, proteins, organisms)
3. Build relationships
4. Populate the knowledge graph

### 2. Explore the API

Open http://localhost:8000/docs to see interactive API documentation.

Try these example requests:

**Search for publications:**
```bash
curl "http://localhost:8000/api/v1/search/publications?q=microgravity"
```

**Search for entities:**
```bash
curl "http://localhost:8000/api/v1/search/entities?q=MYOD1&type=gene"
```

### 3. Query the Knowledge Graph

In Neo4j Browser (http://localhost:7474):

```cypher
// Find all genes
MATCH (g:Gene)
RETURN g.symbol, g.name
LIMIT 10;

// Find publications
MATCH (p:Publication)
RETURN p.title, p.publication_date
ORDER BY p.publication_date DESC
LIMIT 10;

// Find entity relationships
MATCH (e1)-[r]->(e2)
RETURN labels(e1)[0] as from_type, e1.name as from_name,
       type(r) as relationship,
       labels(e2)[0] as to_type, e2.name as to_name
LIMIT 20;
```

### 4. Use the AI Assistant

Once you have data loaded and your OPENAI_API_KEY configured, you can test the AI assistant:

```bash
curl -X POST http://localhost:8000/api/v1/ai/ask \
  -H "Content-Type: application/json" \
  -d '{"question": "What genes are affected by microgravity?"}'
```

## Troubleshooting

### Docker Issues

**Problem**: Services won't start
```bash
# Check service logs
docker-compose logs backend
docker-compose logs neo4j

# Restart specific service
docker-compose restart backend

# Rebuild containers
docker-compose down
docker-compose up --build
```

**Problem**: Port already in use
```bash
# Find what's using the port (example for port 8000)
# Windows:
netstat -ano | findstr :8000
# Then kill the process using Task Manager

# Mac/Linux:
lsof -i :8000
kill -9 <PID>
```

### Backend Issues

**Problem**: Module not found
```bash
# Reinstall dependencies
pip install -r requirements.txt
```

**Problem**: Database connection errors
- Check that all database services are running
- Verify credentials in `.env` file
- Check firewall settings

### Frontend Issues

**Problem**: npm install fails
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

**Problem**: Cannot connect to backend
- Verify backend is running on port 8000
- Check REACT_APP_API_URL in `.env.local`
- Check CORS settings in backend

### Data Ingestion Issues

**Problem**: PubMed API rate limiting
- Add delays between requests
- Use PUBMED_API_KEY for higher rate limits
- Process smaller batches

**Problem**: NER models not downloading
```bash
# Manually download spaCy models
python -m spacy download en_core_web_sm

# For SciBERT models, they'll download automatically on first use
# Ensure you have sufficient disk space (~2GB)
```

## Development Workflow

### Running Tests

**Backend:**
```bash
cd backend
pytest
pytest --cov=.  # With coverage
```

**Frontend:**
```bash
cd frontend
npm test
npm test -- --coverage
```

### Code Formatting

**Backend:**
```bash
cd backend
black .
flake8 .
```

**Frontend:**
```bash
cd frontend
npm run format
npm run lint
```

### Adding New Dependencies

**Backend:**
```bash
pip install <package>
pip freeze > requirements.txt
```

**Frontend:**
```bash
npm install <package>
# package.json will be updated automatically
```

## Resources

- **Project Documentation**: `docs/`
- **API Documentation**: http://localhost:8000/docs
- **Architecture Guide**: `docs/architecture/SYSTEM_ARCHITECTURE.md`
- **Roadmap**: `docs/ROADMAP.md`

## Getting Help

- Check the `docs/` folder for detailed documentation
- Review the code comments
- Check Docker logs: `docker-compose logs <service-name>`

## What's Next?

1. **Explore the Architecture**: Read `docs/architecture/SYSTEM_ARCHITECTURE.md`
2. **Follow the Roadmap**: See `docs/ROADMAP.md` for development phases
3. **Review the Code**: Start with `backend/main.py` and `frontend/src/App.jsx`
4. **Build Features**: Follow the 4-pillar architecture to add functionality

Happy coding! 🚀

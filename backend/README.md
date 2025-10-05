# Backend - Space Biology Knowledge Engine

## Setup

```bash
# Create virtual environment
python -m venv venv

# Activate (Windows)
.\venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Running

```bash
# Development mode with auto-reload
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production mode
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

## API Documentation

Once running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Project Structure

```
backend/
├── api/                    # API routes
│   ├── __init__.py
│   ├── auth.py            # Authentication endpoints
│   ├── search.py          # Search endpoints
│   ├── graph.py           # Knowledge graph endpoints
│   ├── ai.py              # AI assistant endpoints
│   └── user.py            # User management endpoints
├── knowledge_graph/       # KG processing
│   ├── __init__.py
│   ├── ner.py             # Named entity recognition
│   ├── relation_extraction.py
│   ├── entity_resolution.py
│   └── graph_builder.py
├── ai_services/           # AI/ML services
│   ├── __init__.py
│   ├── rag.py             # RAG implementation
│   ├── query_processor.py
│   └── answer_generator.py
├── models/                # Data models
│   ├── __init__.py
│   ├── user.py
│   ├── publication.py
│   └── entity.py
├── core/                  # Core utilities
│   ├── __init__.py
│   ├── config.py          # Configuration
│   ├── security.py        # Security utilities
│   └── database.py        # Database connections
├── main.py                # FastAPI application
└── requirements.txt       # Python dependencies
```

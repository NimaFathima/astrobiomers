"""
Main FastAPI Application
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from api.routes import papers, entities, graph, search, analytics
from api.models.schemas import HealthCheck
from knowledge_graph.config import config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

logger.info("🚀 Starting Space Biology Knowledge Engine API...")
logger.info("Connecting to databases...")

# Create FastAPI app
app = FastAPI(
    title="Space Biology Knowledge Graph API",
    description="REST API for querying and exploring the Space Biology Knowledge Graph",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(papers.router)
app.include_router(entities.router)
app.include_router(graph.router)
app.include_router(search.router)
app.include_router(analytics.router)


@app.get("/", response_model=dict)
async def root():
    """Root endpoint"""
    return {
        "name": "Space Biology Knowledge Graph API",
        "version": "1.0.0",
        "description": "REST API for querying space biology research knowledge",
        "documentation": "/api/docs",
        "endpoints": {
            "papers": "/api/papers",
            "entities": "/api/entities",
            "graph": "/api/graph",
            "search": "/api/search",
            "analytics": "/api/analytics",
            "health": "/api/health"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check Neo4j connection
    try:
        from api.services.neo4j_service import Neo4jService
        neo4j = Neo4jService(
            uri=config.neo4j_uri,
            user=config.neo4j_user,
            password=config.neo4j_password
        )
        db_connected = neo4j.is_connected()
    except Exception as e:
        logger.error(f"Neo4j health check failed: {e}")
        db_connected = False
    
    return {
        "status": "healthy" if db_connected else "degraded",
        "version": "1.0.0",
        "database_connected": db_connected,
        "services": {
            "neo4j": db_connected,
            "api": True
        }
    }


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc) if config.debug else "An error occurred"
        }
    )


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down API...")


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Uvicorn server...")
    # Use import string for reload to work
    uvicorn.run(
        "api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=False,  # Disabled for direct execution
        log_level="info"
    )

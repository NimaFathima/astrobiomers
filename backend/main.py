from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

# Import API routes
from api.routes import knowledge_graph

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan events for startup and shutdown"""
    # Startup
    logger.info("🚀 Starting Space Biology Knowledge Engine API...")
    logger.info("Connecting to databases...")
    # TODO: Initialize database connections
    # TODO: Load NLP models
    # TODO: Initialize vector database
    yield
    # Shutdown
    logger.info("Shutting down API...")
    # TODO: Close database connections

app = FastAPI(
    title="Space Biology Knowledge Engine API",
    description="API for querying and reasoning over space biology research",
    version="0.1.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to the Space Biology Knowledge Engine API",
        "version": "0.1.0",
        "docs": "/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "services": {
            "api": "operational",
            # TODO: Add database health checks
            # "neo4j": "operational",
            # "postgres": "operational",
            # "redis": "operational",
        }
    }

# Include routers
app.include_router(knowledge_graph.router)

# TODO: Import and include additional routers
# from api import auth, search, graph, ai, user
# app.include_router(auth.router, prefix="/api/v1/auth", tags=["authentication"])
# app.include_router(search.router, prefix="/api/v1/search", tags=["search"])
# app.include_router(ai.router, prefix="/api/v1/ai", tags=["AI assistant"])
# app.include_router(user.router, prefix="/api/v1/user", tags=["user"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

"""
Main FastAPI Application
Ticket Classification MLOps System
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import time

from app.config import settings
from app.api.routes import router
from app.models.classifier import classifier
from app.utils.logger import logger
from app.utils.metrics import metrics_collector, model_load_time, categories_loaded


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events
    """
    # Startup
    logger.info("=" * 50)
    logger.info("Starting Ticket Classification API")
    logger.info("=" * 50)
    
    try:
        # Load model
        logger.info("Loading sentence transformer model...")
        load_time = classifier.load_model()
        model_load_time.set(load_time)
        
        # Load category embeddings
        logger.info("Loading category embeddings...")
        classifier.load_category_embeddings()
        categories_loaded.set(len(classifier.category_names))
        
        logger.info(f"✓ Model loaded: {classifier.model_name}")
        logger.info(f"✓ Categories loaded: {len(classifier.category_names)}")
        logger.info(f"✓ API ready on {settings.HOST}:{settings.PORT}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Failed to initialize application: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Shutting down Ticket Classification API")


# Create FastAPI app
app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware for request logging and metrics
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all requests and track metrics"""
    start_time = time.time()
    
    # Log request
    logger.info(f"→ {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        
        # Calculate duration
        duration = time.time() - start_time
        
        # Log response
        logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
        
        return response
        
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise


# Exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    metrics_collector.record_error("unhandled_exception")
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "message": "An unexpected error occurred",
            "detail": str(exc) if settings.LOG_LEVEL == "DEBUG" else None
        }
    )


# Include API routes
app.include_router(router, prefix="/api/v1", tags=["Ticket Classification"])


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "metrics": "/api/v1/metrics"
    }


# Additional health check at root level
@app.get("/health", tags=["Health"])
async def health():
    """Simple health check"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "backend.app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.RELOAD,
        workers=settings.WORKERS if not settings.RELOAD else 1,
        log_level=settings.LOG_LEVEL.lower()
    )

# Made with Bob

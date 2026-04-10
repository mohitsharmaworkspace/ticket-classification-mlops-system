"""
Main FastAPI Application
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
    logger.info("=" * 50)
    logger.info("Starting Ticket Classification API")
    logger.info("=" * 50)
    
    try:
        logger.info("Loading embedding model...")
        load_time = classifier.load_embedding_model()
        model_load_time.set(load_time)
        
        logger.info("Loading trained MLP classifier...")
        classifier.load_trained_model()
        categories_loaded.set(len(classifier.category_names))
        
        logger.info(f"✓ Embedding model: {classifier.model_name}")
        logger.info(f"✓ Categories: {len(classifier.category_names)}")
        logger.info(f"✓ Mode: {classifier.get_model_info()['prediction_mode']}")
        logger.info(f"✓ API ready on {settings.HOST}:{settings.PORT}")
        logger.info("=" * 50)
        
    except Exception as e:
        logger.error(f"Failed to initialize: {e}")
        raise
    
    yield
    
    logger.info("Shutting down API")


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


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    logger.info(f"→ {request.method} {request.url.path}")
    
    try:
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(f"← {request.method} {request.url.path} - {response.status_code} ({duration:.3f}s)")
        return response
    except Exception as e:
        logger.error(f"Request failed: {e}")
        raise


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
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


app.include_router(router, prefix="/api/v1", tags=["Ticket Classification"])


@app.get("/", tags=["Root"])
async def root():
    return {
        "name": settings.API_TITLE,
        "version": settings.API_VERSION,
        "description": settings.API_DESCRIPTION,
        "docs": "/docs",
        "health": "/api/v1/health",
        "metrics": "/api/v1/metrics"
    }


@app.get("/health", tags=["Health"])
async def health():
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

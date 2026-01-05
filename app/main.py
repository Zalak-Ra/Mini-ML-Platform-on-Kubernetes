"""
ML Inference Service - FastAPI application for serving ML predictions
Implements health checks, structured logging, and production-ready error handling
"""
import logging
import sys
import json
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field, validator
import uvicorn

from model import model

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


# Request/Response models
class PredictionRequest(BaseModel):
    """Request model for prediction endpoint"""
    features: List[float] = Field(
        ...,
        description="List of 4 features: [sepal_length, sepal_width, petal_length, petal_width]",
        example=[5.1, 3.5, 1.4, 0.2]
    )
    
    @validator('features')
    def validate_features(cls, v):
        if len(v) != 4:
            raise ValueError('Must provide exactly 4 features')
        if not all(isinstance(x, (int, float)) for x in v):
            raise ValueError('All features must be numeric')
        if any(x < 0 for x in v):
            raise ValueError('All features must be non-negative')
        return v


class PredictionResponse(BaseModel):
    """Response model for prediction endpoint"""
    prediction: str
    prediction_index: int
    probabilities: dict
    confidence: float


class HealthResponse(BaseModel):
    """Response model for health endpoints"""
    status: str
    model_loaded: bool


# Lifespan context manager for startup/shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    Loads the ML model on startup.
    """
    logger.info("Application startup: Loading ML model...")
    try:
        model.load_model()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to load model during startup: {e}")
        raise
    
    yield
    
    logger.info("Application shutdown")


# Initialize FastAPI app
app = FastAPI(
    title="ML Inference Service",
    description="Production-grade ML inference service for Iris classification",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": "ML Inference Service",
        "version": "1.0.0",
        "endpoints": {
            "predict": "/predict",
            "health": "/health",
            "ready": "/ready",
            "docs": "/docs"
        }
    }


@app.post("/predict", response_model=PredictionResponse, tags=["Inference"])
async def predict(request: PredictionRequest):
    """
    Make a prediction on input features.
    
    Expects 4 features for Iris classification:
    - sepal_length (cm)
    - sepal_width (cm)
    - petal_length (cm)
    - petal_width (cm)
    
    Returns the predicted class and probability scores.
    """
    try:
        logger.info(f"Received prediction request: {request.features}")
        
        result = model.predict(request.features)
        
        logger.info(f"Prediction successful: {result['prediction']}")
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"Prediction error: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during prediction"
        )


@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health():
    """
    Liveness probe endpoint.
    Returns 200 if the service is alive (even if model not loaded).
    Used by Kubernetes to restart unhealthy pods.
    """
    return {
        "status": "alive",
        "model_loaded": model.health_check()
    }


@app.get("/ready", response_model=HealthResponse, tags=["Health"])
async def ready():
    """
    Readiness probe endpoint.
    Returns 200 only if the service is ready to serve requests (model loaded).
    Used by Kubernetes to route traffic only to ready pods.
    """
    if not model.health_check():
        logger.warning("Readiness check failed: model not loaded")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Model not loaded"
        )
    
    return {
        "status": "ready",
        "model_loaded": True
    }


if __name__ == "__main__":
    # Run the application
    # In production, use gunicorn or uvicorn with multiple workers
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )

"""
ML Inference Service - Standalone Demo Version
Works without scikit-learn - uses a simple mock model for demonstration
"""
import logging
import sys
from typing import List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
import uvicorn

# Configure structured logging
logging.basicConfig(
    level=logging.INFO,
    format='{"timestamp": "%(asctime)s", "level": "%(levelname)s", "logger": "%(name)s", "message": "%(message)s"}',
    handlers=[logging.StreamHandler(sys.stdout)]
)

logger = logging.getLogger(__name__)


# Simple mock model (no ML libraries needed)
class MockIrisModel:
    """
    Mock Iris classifier for demonstration.
    Uses simple rules instead of actual ML model.
    """
    
    def __init__(self):
        self.loaded = False
        self.class_names = ['setosa', 'versicolor', 'virginica']
    
    def load_model(self):
        """Simulate model loading"""
        logger.info("Loading mock Iris classification model...")
        self.loaded = True
        logger.info("Mock model loaded successfully")
    
    def predict(self, features: List[float]) -> dict:
        """
        Make prediction using simple rules.
        Rules based on typical Iris dataset characteristics:
        - Setosa: small petal length (< 2.5)
        - Versicolor: medium petal length (2.5 - 5.0)
        - Virginica: large petal length (> 5.0)
        """
        if not self.loaded:
            raise ValueError("Model not loaded")
        
        if len(features) != 4:
            raise ValueError(f"Expected 4 features, got {len(features)}")
        
        # Extract petal length (index 2)
        petal_length = features[2]
        
        # Simple rule-based classification
        if petal_length < 2.5:
            prediction_index = 0  # setosa
            probabilities = [0.95, 0.03, 0.02]
        elif petal_length < 5.0:
            prediction_index = 1  # versicolor
            probabilities = [0.02, 0.90, 0.08]
        else:
            prediction_index = 2  # virginica
            probabilities = [0.01, 0.09, 0.90]
        
        result = {
            'prediction': self.class_names[prediction_index],
            'prediction_index': prediction_index,
            'probabilities': {
                self.class_names[i]: prob 
                for i, prob in enumerate(probabilities)
            },
            'confidence': max(probabilities)
        }
        
        logger.info(f"Prediction: {result['prediction']} (confidence: {result['confidence']:.2%})")
        return result
    
    def health_check(self) -> bool:
        """Check if model is loaded"""
        return self.loaded


# Global model instance
model = MockIrisModel()


# Request/Response models
class PredictionRequest(BaseModel):
    """Request model for prediction endpoint"""
    features: List[float] = Field(
        ...,
        description="List of 4 features: [sepal_length, sepal_width, petal_length, petal_width]",
        example=[5.1, 3.5, 1.4, 0.2]
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "features": [5.1, 3.5, 1.4, 0.2]
            }
        }


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


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Load model on startup"""
    logger.info("Application startup: Loading model...")
    try:
        model.load_model()
        logger.info("Application startup complete")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise
    
    yield
    
    logger.info("Application shutdown")


# Initialize FastAPI app
app = FastAPI(
    title="ML Inference Service (Demo)",
    description="Production-grade ML inference service for Iris classification (Mock Model)",
    version="1.0.0-demo",
    lifespan=lifespan
)


@app.get("/", tags=["Root"])
async def root():
    """Root endpoint"""
    return {
        "service": "ML Inference Service (Demo)",
        "version": "1.0.0-demo",
        "note": "Using mock model for demonstration (no ML libraries required)",
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
    
    Note: This demo version uses simple rules instead of a trained ML model.
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
    Returns 200 if the service is alive.
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
    Returns 200 only if the service is ready to serve requests.
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
    uvicorn.run(
        "main_demo:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )

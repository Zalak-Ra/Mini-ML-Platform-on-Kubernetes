"""
ML Model Module - Thread-safe model wrapper for inference
Implements a simple RandomForest classifier on the Iris dataset
"""
import pickle
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.datasets import load_iris
from typing import List, Dict
import logging

logger = logging.getLogger(__name__)


class IrisModel:
    """
    Singleton ML model wrapper for Iris classification.
    Implements lazy loading and thread-safe prediction.
    """
    
    _instance = None
    _model = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(IrisModel, cls).__new__(cls)
        return cls._instance
    
    def load_model(self):
        """
        Load and train a simple RandomForest model on Iris dataset.
        In production, this would load a pre-trained model from disk/S3.
        """
        if self._model is not None:
            logger.info("Model already loaded, skipping initialization")
            return
        
        logger.info("Loading and training Iris classification model...")
        
        # Load Iris dataset
        iris = load_iris()
        X, y = iris.data, iris.target
        
        # Train a simple RandomForest classifier
        self._model = RandomForestClassifier(
            n_estimators=100,
            max_depth=5,
            random_state=42,
            n_jobs=-1  # Use all CPU cores
        )
        self._model.fit(X, y)
        
        logger.info("Model loaded successfully")
        logger.info(f"Model classes: {iris.target_names.tolist()}")
    
    def predict(self, features: List[float]) -> Dict[str, any]:
        """
        Make prediction on input features.
        
        Args:
            features: List of 4 float values [sepal_length, sepal_width, petal_length, petal_width]
        
        Returns:
            Dictionary with prediction and probability scores
        
        Raises:
            ValueError: If model not loaded or invalid input
        """
        if self._model is None:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        if len(features) != 4:
            raise ValueError(f"Expected 4 features, got {len(features)}")
        
        # Convert to numpy array and reshape for single prediction
        X = np.array(features).reshape(1, -1)
        
        # Get prediction and probabilities
        prediction = self._model.predict(X)[0]
        probabilities = self._model.predict_proba(X)[0]
        
        # Map to class names
        class_names = ['setosa', 'versicolor', 'virginica']
        
        result = {
            'prediction': class_names[prediction],
            'prediction_index': int(prediction),
            'probabilities': {
                class_names[i]: float(prob) 
                for i, prob in enumerate(probabilities)
            },
            'confidence': float(max(probabilities))
        }
        
        logger.info(f"Prediction: {result['prediction']} (confidence: {result['confidence']:.2%})")
        
        return result
    
    def health_check(self) -> bool:
        """Check if model is loaded and ready"""
        return self._model is not None


# Global model instance
model = IrisModel()

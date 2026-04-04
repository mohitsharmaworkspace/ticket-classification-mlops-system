"""
Backend configuration
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    API_TITLE: str = "Ticket Classification API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "MLOps-based ticket classification system with multi-input support"
    
    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False
    
    # CORS Settings
    CORS_ORIGINS: list = ["http://localhost:3000", "http://frontend:3000"]
    
    # File Upload Settings
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {".csv"}
    
    # Model Settings
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    CONFIDENCE_THRESHOLD: float = 0.7
    CATEGORY_EMBEDDINGS_PATH: str = "../models/embeddings/category_embeddings.pkl"
    DEFAULT_CATEGORIES_PATH: str = "../data/raw/default_categories.csv"
    
    # Data Paths
    GROUND_TRUTH_PATH: str = "../data/ground_truth/corrected_labels.csv"
    DRIFT_BASELINE_PATH: str = "../data/drift_baseline/baseline_stats.json"
    
    # Monitoring
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "../logs/api.log"
    
    # Rate Limiting
    RATE_LIMIT_PER_MINUTE: int = 100
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()

# Made with Bob

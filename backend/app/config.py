import os
from pathlib import Path
from pydantic_settings import BaseSettings
from typing import Optional, List


def get_project_root() -> Path:
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / 'params.yaml').exists():
            return current
        current = current.parent
    return Path.cwd()


PROJECT_ROOT = get_project_root()


class Settings(BaseSettings):
    API_TITLE: str = "Ticket Classification API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "MLOps-based ticket classification system"
    
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    WORKERS: int = 4
    RELOAD: bool = False
    
    CORS_ORIGINS: List[str] = ["http://localhost:3000", "http://frontend:3000"]
    
    MAX_UPLOAD_SIZE_MB: int = 10
    ALLOWED_EXTENSIONS: set = {".csv"}
    
    MODEL_NAME: str = "all-MiniLM-L6-v2"
    CONFIDENCE_THRESHOLD: float = 0.7
    
    PROJECT_ROOT: Path = PROJECT_ROOT
    MODELS_DIR: Path = PROJECT_ROOT / "models"
    DATA_DIR: Path = PROJECT_ROOT / "data"
    LOGS_DIR: Path = PROJECT_ROOT / "logs"
    
    CATEGORY_EMBEDDINGS_PATH: Path = MODELS_DIR / "embeddings" / "category_embeddings.pkl"
    MLP_MODEL_PATH: Path = MODELS_DIR / "trained" / "mlp_classifier.pth"
    DEFAULT_CATEGORIES_PATH: Path = DATA_DIR / "raw" / "default_categories.csv"
    RAW_DATA_PATH: Path = DATA_DIR / "raw" / "customer_support_tickets.csv"
    PROCESSED_DATA_PATH: Path = DATA_DIR / "processed" / "processed_tickets.csv"
    GROUND_TRUTH_PATH: Path = DATA_DIR / "ground_truth" / "corrected_labels.csv"
    DRIFT_BASELINE_PATH: Path = DATA_DIR / "drift_baseline" / "baseline_stats.json"
    
    MLFLOW_TRACKING_URI: str = os.getenv("MLFLOW_TRACKING_URI", "http://localhost:5000")
    MLFLOW_EXPERIMENT_NAME: str = "ticket_classification"
    
    ENABLE_METRICS: bool = True
    METRICS_PORT: int = 9090
    
    LOG_LEVEL: str = "INFO"
    LOG_FILE: Path = LOGS_DIR / "api.log"
    
    RATE_LIMIT_PER_MINUTE: int = 100
    
    DVC_REMOTE: Optional[str] = None
    
    AIRFLOW_HOME: Optional[Path] = None
    AIRFLOW_DAGS_FOLDER: Optional[Path] = None
    
    PROMETHEUS_PORT: int = 9090
    GRAFANA_PORT: int = 3001
    AIRFLOW_WEBSERVER_PORT: int = 8080
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._ensure_directories()
    
    def _ensure_directories(self):
        for dir_path in [self.MODELS_DIR, self.DATA_DIR, self.LOGS_DIR]:
            dir_path.mkdir(parents=True, exist_ok=True)
        
        (self.MODELS_DIR / "trained").mkdir(exist_ok=True)
        (self.MODELS_DIR / "embeddings").mkdir(exist_ok=True)
        (self.DATA_DIR / "raw").mkdir(exist_ok=True)
        (self.DATA_DIR / "processed").mkdir(exist_ok=True)
        (self.DATA_DIR / "ground_truth").mkdir(exist_ok=True)
        (self.DATA_DIR / "drift_baseline").mkdir(exist_ok=True)


settings = Settings()

# Made with Bob

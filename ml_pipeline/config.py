import os
import yaml
from pathlib import Path
from typing import Dict, Any
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    current = Path(__file__).resolve()
    while current != current.parent:
        if (current / 'params.yaml').exists():
            return current
        current = current.parent
    return Path.cwd()


class Config:
    def __init__(self, config_path: str = "params.yaml"):
        self.project_root = get_project_root()
        self.config_path = self.project_root / config_path
        self.params = self._load_config()
        self._setup_paths()
        
    def _load_config(self) -> Dict[str, Any]:
        try:
            with open(self.config_path, 'r') as f:
                params = yaml.safe_load(f)
            logger.info(f"Configuration loaded from {self.config_path}")
            return params
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {self.config_path}")
            raise
        except yaml.YAMLError as e:
            logger.error(f"Error parsing YAML file: {e}")
            raise
            
    def _setup_paths(self):
        paths = [
            self.project_root / "data" / "processed",
            self.project_root / "data" / "ground_truth",
            self.project_root / "data" / "drift_baseline",
            self.project_root / "models" / "embeddings",
            self.project_root / "models" / "trained",
            self.project_root / "logs"
        ]
        
        for path in paths:
            path.mkdir(parents=True, exist_ok=True)
            
    def get(self, key: str, default: Any = None) -> Any:
        keys = key.split('.')
        value = self.params
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            logger.warning(f"Configuration key '{key}' not found, using default: {default}")
            return default
            
    @property
    def model_name(self) -> str:
        return self.get('model.name', 'all-MiniLM-L6-v2')
        
    @property
    def raw_data_path(self) -> Path:
        path_str = self.get('data.raw_data_path', 'data/raw/customer_support_tickets.csv')
        return self.project_root / path_str
        
    @property
    def default_categories_path(self) -> Path:
        path_str = self.get('data.default_categories_path', 'data/raw/default_categories.csv')
        return self.project_root / path_str
        
    @property
    def processed_data_path(self) -> Path:
        path_str = self.get('data.processed_data_path', 'data/processed/processed_tickets.csv')
        return self.project_root / path_str
        
    @property
    def ground_truth_path(self) -> Path:
        path_str = self.get('data.ground_truth_path', 'data/ground_truth/corrected_labels.csv')
        return self.project_root / path_str
        
    @property
    def drift_baseline_path(self) -> Path:
        path_str = self.get('data.drift_baseline_path', 'data/drift_baseline/baseline_stats.json')
        return self.project_root / path_str
    
    @property
    def mlp_model_path(self) -> Path:
        return self.project_root / "models" / "trained" / "mlp_classifier.pth"
    
    @property
    def category_embeddings_path(self) -> Path:
        return self.project_root / "models" / "embeddings" / "category_embeddings.pkl"
        
    @property
    def confidence_threshold(self) -> float:
        return self.get('model.confidence_threshold', 0.7)
        
    @property
    def correction_rate_threshold(self) -> float:
        return self.get('retraining.correction_rate_threshold', 0.15)
        
    @property
    def min_samples_for_retraining(self) -> int:
        return self.get('retraining.min_samples_for_retraining', 50)
    
    @property
    def mlflow_tracking_uri(self) -> str:
        return os.getenv('MLFLOW_TRACKING_URI', self.get('mlflow.tracking_uri', 'http://localhost:5000'))
    
    @property
    def mlflow_experiment_name(self) -> str:
        return self.get('mlflow.experiment_name', 'ticket_classification')


config = Config()

# Made with Bob

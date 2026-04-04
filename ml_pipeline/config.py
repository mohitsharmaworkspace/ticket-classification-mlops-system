"""
Configuration management for ML pipeline
"""

import os
import yaml
from pathlib import Path
from typing import Dict, Any
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class Config:
    """Configuration class to load and manage parameters"""
    
    def __init__(self, config_path: str = "params.yaml"):
        """
        Initialize configuration
        
        Args:
            config_path: Path to params.yaml file
        """
        self.config_path = config_path
        self.params = self._load_config()
        self._setup_paths()
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from YAML file"""
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
        """Setup and create necessary directories"""
        paths = [
            "data/processed",
            "data/ground_truth",
            "data/drift_baseline",
            "models/embeddings",
            "models/trained",
            "logs"
        ]
        
        for path in paths:
            Path(path).mkdir(parents=True, exist_ok=True)
            
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key
        
        Args:
            key: Configuration key (supports nested keys with dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value
        """
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
        """Get model name"""
        return self.get('model.name', 'all-MiniLM-L6-v2')
        
    @property
    def raw_data_path(self) -> str:
        """Get raw data path"""
        return self.get('data.raw_data_path', 'data/raw/customer_support_tickets.csv')
        
    @property
    def default_categories_path(self) -> str:
        """Get default categories path"""
        return self.get('data.default_categories_path', 'data/raw/default_categories.csv')
        
    @property
    def processed_data_path(self) -> str:
        """Get processed data path"""
        return self.get('data.processed_data_path', 'data/processed/processed_tickets.csv')
        
    @property
    def ground_truth_path(self) -> str:
        """Get ground truth path"""
        return self.get('data.ground_truth_path', 'data/ground_truth/corrected_labels.csv')
        
    @property
    def drift_baseline_path(self) -> str:
        """Get drift baseline path"""
        return self.get('data.drift_baseline_path', 'data/drift_baseline/baseline_stats.json')
        
    @property
    def confidence_threshold(self) -> float:
        """Get confidence threshold"""
        return self.get('model.confidence_threshold', 0.7)
        
    @property
    def correction_rate_threshold(self) -> float:
        """Get correction rate threshold for retraining"""
        return self.get('retraining.correction_rate_threshold', 0.15)
        
    @property
    def min_samples_for_retraining(self) -> int:
        """Get minimum samples required for retraining"""
        return self.get('retraining.min_samples_for_retraining', 50)


# Global config instance
config = Config()

# Made with Bob

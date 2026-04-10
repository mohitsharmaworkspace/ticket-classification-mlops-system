import pandas as pd
import numpy as np
import pickle
from typing import Dict, List, Optional
from pathlib import Path
from datetime import datetime
import time

from app.utils.logger import logger
from app.config import settings
from ml_pipeline.model_training import MLPModelTrainer
from ml_pipeline.data_preprocessing import DataPreprocessor


class TrainingService:
    def __init__(self):
        self.trainer = MLPModelTrainer()
        self.preprocessor = DataPreprocessor()
        
    def train_with_default_categories(self, tickets_df: pd.DataFrame) -> Dict:
        try:
            logger.info("Starting training with default categories")
            start_time = time.time()
            
            processed_df = self.preprocessor.preprocess(tickets_df, include_ground_truth=False)
            
            results = self.trainer.train_model(processed_df)
            
            training_time = time.time() - start_time
            
            logger.info(f"Training completed in {training_time:.2f}s")
            
            return {
                'status': 'success',
                'training_time': training_time,
                'num_tickets': len(processed_df),
                'num_categories': results['model_info']['num_classes'],
                'metrics': results.get('metrics', {})
            }
            
        except Exception as e:
            logger.error(f"Training error: {e}")
            raise
    
    def retrain_with_feedback(self) -> Dict:
        try:
            logger.info("Starting retraining with feedback")
            
            raw_df = self.preprocessor.load_raw_data()
            ground_truth_df = self.preprocessor.load_ground_truth()
            
            if ground_truth_df.empty:
                logger.warning("No ground truth data available")
                return {
                    'status': 'skipped',
                    'message': 'No feedback data available'
                }
            
            from ml_pipeline.utils import merge_ground_truth_with_raw
            merged_df = merge_ground_truth_with_raw(raw_df, ground_truth_df)
            
            result = self.train_with_default_categories(merged_df)
            result['feedback_count'] = len(ground_truth_df)
            
            return result
            
        except Exception as e:
            logger.error(f"Retraining error: {e}")
            raise
    
    def get_training_status(self) -> Dict:
        try:
            from app.config import settings
            model_path = settings.MLP_MODEL_PATH
            
            if not model_path.exists():
                return {
                    'trained': False,
                    'message': 'No trained model found'
                }
            
            import torch
            checkpoint = torch.load(str(model_path), map_location='cpu')
            
            return {
                'trained': True,
                'num_categories': checkpoint['num_classes'],
                'model_type': 'MLP',
                'last_modified': datetime.fromtimestamp(model_path.stat().st_mtime).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error getting training status: {e}")
            return {
                'trained': False,
                'error': str(e)
            }


training_service = TrainingService()

# Made with Bob

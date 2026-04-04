"""
Model training and evaluation for ticket classification
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import mlflow
import mlflow.sklearn
from datetime import datetime

from ml_pipeline.config import config
from ml_pipeline.data_preprocessing import DataPreprocessor
from ml_pipeline.feature_engineering import FeatureEngineer

logger = logging.getLogger(__name__)


class ModelTrainer:
    """Model training and MLflow integration"""
    
    def __init__(self, experiment_name: Optional[str] = None):
        """
        Initialize model trainer
        
        Args:
            experiment_name: MLflow experiment name
        """
        self.experiment_name = experiment_name or config.get('mlflow.experiment_name', 'ticket_classification')
        self.mlflow_uri = config.get('mlflow.tracking_uri', 'http://mlflow:5000')
        self.preprocessor = DataPreprocessor()
        self.feature_engineer = FeatureEngineer()
        
    def setup_mlflow(self):
        """Setup MLflow tracking"""
        try:
            mlflow.set_tracking_uri(self.mlflow_uri)
            mlflow.set_experiment(self.experiment_name)
            logger.info(f"MLflow tracking URI: {self.mlflow_uri}")
            logger.info(f"MLflow experiment: {self.experiment_name}")
        except Exception as e:
            logger.warning(f"Could not connect to MLflow server: {e}")
            logger.info("Using local MLflow tracking")
            mlflow.set_tracking_uri("file:./mlruns")
            mlflow.set_experiment(self.experiment_name)
            
    def train_model(self, tickets_df: pd.DataFrame, 
                   categories_df: pd.DataFrame) -> Dict[str, Any]:
        """
        Train the classification model
        
        Args:
            tickets_df: DataFrame with ticket data
            categories_df: DataFrame with category definitions
            
        Returns:
            Dictionary with training results
        """
        logger.info("Starting model training")
        
        # Setup MLflow
        self.setup_mlflow()
        
        with mlflow.start_run(run_name=f"training_{datetime.now().strftime('%Y%m%d_%H%M%S')}"):
            # Log parameters
            mlflow.log_param("model_name", self.feature_engineer.model_name)
            mlflow.log_param("num_categories", len(categories_df))
            mlflow.log_param("num_tickets", len(tickets_df))
            
            # Generate category embeddings
            self.feature_engineer.generate_category_embeddings(categories_df)
            self.feature_engineer.save_category_embeddings()
            
            # Process tickets
            df = self.feature_engineer.process_tickets(tickets_df)
            
            # Calculate metrics
            metrics = self.calculate_metrics(df)
            
            # Log metrics
            for metric_name, metric_value in metrics.items():
                mlflow.log_metric(metric_name, metric_value)
                
            # Log artifacts
            mlflow.log_artifact("models/embeddings/category_embeddings.pkl")
            mlflow.log_artifact(config.drift_baseline_path)
            
            # Log model info
            model_info = {
                'model_name': self.feature_engineer.model_name,
                'num_categories': len(categories_df),
                'category_names': self.feature_engineer.category_names,
                'training_date': datetime.now().isoformat(),
                'metrics': metrics
            }
            
            mlflow.log_dict(model_info, "model_info.json")
            
            logger.info("Model training completed")
            logger.info(f"Metrics: {metrics}")
            
            return {
                'metrics': metrics,
                'model_info': model_info,
                'predictions_df': df
            }
            
    def calculate_metrics(self, df: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate evaluation metrics
        
        Args:
            df: DataFrame with predictions
            
        Returns:
            Dictionary of metrics
        """
        from sklearn.metrics import accuracy_score, precision_recall_fscore_support
        
        metrics = {}
        
        # If we have ground truth labels
        if 'Ticket Type' in df.columns:
            y_true = df['Ticket Type'].values
            y_pred = df['predicted_category'].values
            
            # Calculate accuracy
            accuracy = accuracy_score(y_true, y_pred)
            metrics['accuracy'] = float(accuracy)
            
            # Calculate precision, recall, f1
            precision, recall, f1, _ = precision_recall_fscore_support(
                y_true, y_pred, average='weighted', zero_division=0
            )
            
            metrics['precision'] = float(precision)
            metrics['recall'] = float(recall)
            metrics['f1_score'] = float(f1)
            
        # Confidence statistics
        metrics['mean_confidence'] = float(df['confidence_score'].mean())
        metrics['std_confidence'] = float(df['confidence_score'].std())
        metrics['min_confidence'] = float(df['confidence_score'].min())
        metrics['max_confidence'] = float(df['confidence_score'].max())
        
        # Low confidence predictions
        threshold = config.confidence_threshold
        low_confidence_count = len(df[df['confidence_score'] < threshold])
        metrics['low_confidence_ratio'] = float(low_confidence_count / len(df))
        
        return metrics
        
    def evaluate_model(self, test_df: pd.DataFrame) -> Dict[str, float]:
        """
        Evaluate model on test data
        
        Args:
            test_df: Test DataFrame
            
        Returns:
            Dictionary of evaluation metrics
        """
        logger.info("Evaluating model")
        
        # Load category embeddings
        self.feature_engineer.load_category_embeddings()
        
        # Process test data
        df = self.feature_engineer.process_tickets(test_df)
        
        # Calculate metrics
        metrics = self.calculate_metrics(df)
        
        logger.info(f"Evaluation metrics: {metrics}")
        return metrics
        
    def run_training_pipeline(self, 
                             input_data_path: Optional[str] = None,
                             categories_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Run complete training pipeline
        
        Args:
            input_data_path: Path to input data (optional)
            categories_path: Path to categories (optional)
            
        Returns:
            Training results
        """
        logger.info("Starting training pipeline")
        
        # Load and preprocess data
        tickets_df = self.preprocessor.load_raw_data(input_data_path)
        tickets_df = self.preprocessor.preprocess(tickets_df)
        
        # Load categories
        categories_df = self.preprocessor.load_categories(categories_path)
        
        # Train model
        results = self.train_model(tickets_df, categories_df)
        
        # Save processed data with predictions
        output_path = config.processed_data_path
        results['predictions_df'].to_csv(output_path, index=False)
        logger.info(f"Predictions saved to {output_path}")
        
        return results


if __name__ == "__main__":
    # Run training pipeline
    trainer = ModelTrainer()
    results = trainer.run_training_pipeline()
    
    print("\n=== Training Results ===")
    print(f"Metrics: {results['metrics']}")
    print(f"\nModel Info: {results['model_info']}")

# Made with Bob

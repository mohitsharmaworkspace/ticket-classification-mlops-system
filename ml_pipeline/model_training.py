import pandas as pd
import numpy as np
import logging
from typing import Dict, Any, Optional
from pathlib import Path
import mlflow
from datetime import datetime
from sentence_transformers import SentenceTransformer

from ml_pipeline.config import config
from ml_pipeline.data_preprocessing import DataPreprocessor
from ml_pipeline.models.mlp_classifier import MLPClassifier
from ml_pipeline.models.trainer import ModelTrainer

logger = logging.getLogger(__name__)


class MLPModelTrainer:
    def __init__(self, experiment_name: Optional[str] = None):
        self.experiment_name = experiment_name or config.mlflow_experiment_name
        self.mlflow_uri = config.mlflow_tracking_uri
        self.preprocessor = DataPreprocessor()
        self.embedding_model = None
        
    def setup_mlflow(self):
        try:
            mlflow.set_tracking_uri(self.mlflow_uri)
            mlflow.set_experiment(self.experiment_name)
            logger.info(f"MLflow tracking URI: {self.mlflow_uri}")
        except Exception as e:
            logger.warning(f"Could not connect to MLflow server: {e}")
            mlflow.set_tracking_uri("file:./mlruns")
            mlflow.set_experiment(self.experiment_name)
    
    def load_embedding_model(self):
        if self.embedding_model is None:
            model_name = config.model_name
            logger.info(f"Loading embedding model: {model_name}")
            self.embedding_model = SentenceTransformer(model_name)
        return self.embedding_model
    
    def generate_embeddings(self, texts):
        model = self.load_embedding_model()
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = model.encode(texts, show_progress_bar=True, convert_to_numpy=True)
        return embeddings
    
    def train_model(self, tickets_df: pd.DataFrame) -> Dict[str, Any]:
        logger.info("Starting MLP model training")
        
        self.setup_mlflow()
        
        text_column = 'combined_text' if 'combined_text' in tickets_df.columns else 'Ticket Description'
        label_column = 'Ticket Type'
        
        texts = tickets_df[text_column].tolist()
        labels = tickets_df[label_column].tolist()
        
        embeddings = self.generate_embeddings(texts)
        
        num_classes = len(set(labels))
        mlp_config = {
            'hidden_dims': config.get('training.mlp.hidden_layers', [256, 128]),
            'dropout_rates': config.get('training.mlp.dropout_rate', [0.3, 0.2]),
            'learning_rate': config.get('training.learning_rate', 0.001),
            'batch_size': config.get('training.batch_size', 32),
            'early_stopping_patience': config.get('training.early_stopping_patience', 5)
        }
        
        model = MLPClassifier(
            input_dim=embeddings.shape[1],
            hidden_dims=mlp_config['hidden_dims'],
            num_classes=num_classes,
            dropout_rates=mlp_config['dropout_rates']
        )
        
        trainer = ModelTrainer(model, mlp_config)
        
        epochs = config.get('training.epochs', 50)
        val_split = config.get('data.split.test_size', 0.2)
        
        training_results = trainer.train(embeddings, labels, epochs=epochs, val_split=val_split)
        
        try:
            mlflow.log_param("model_type", "MLP")
            mlflow.log_param("num_classes", num_classes)
            mlflow.log_param("num_samples", len(texts))
            mlflow.log_param("embedding_dim", embeddings.shape[1])
            mlflow.log_params(mlp_config)
            
            mlflow.log_metric("final_train_acc", training_results['train_accs'][-1])
            mlflow.log_metric("final_val_acc", training_results['final_val_acc'])
            mlflow.log_metric("best_val_loss", training_results['best_val_loss'])
            mlflow.log_metric("training_time", training_results['training_time'])
        except:
            logger.warning("MLflow logging failed")
        
        trainer.save_model()
        
        logger.info("Model training completed")
        
        return {
            'metrics': {
                'train_accuracy': training_results['train_accs'][-1],
                'val_accuracy': training_results['final_val_acc'],
                'best_val_loss': training_results['best_val_loss']
            },
            'model_info': {
                'model_type': 'MLP',
                'num_classes': num_classes,
                'training_time': training_results['training_time']
            },
            'training_history': training_results
        }
    
    def run_training_pipeline(self, input_data_path: Optional[str] = None) -> Dict[str, Any]:
        logger.info("Starting training pipeline")
        
        tickets_df = self.preprocessor.load_raw_data(input_data_path)
        tickets_df = self.preprocessor.preprocess(tickets_df)
        
        results = self.train_model(tickets_df)
        
        output_path = config.processed_data_path
        tickets_df.to_csv(str(output_path), index=False)
        logger.info(f"Processed data saved to {str(output_path)}")
        
        return results


if __name__ == "__main__":
    trainer = MLPModelTrainer()
    results = trainer.run_training_pipeline()
    
    print("\n=== Training Results ===")
    print(f"Metrics: {results['metrics']}")
    print(f"\nModel Info: {results['model_info']}")

# Made with Bob

"""
Feature engineering for ticket classification
Handles embedding generation and category matching
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from pathlib import Path
import pickle

from sentence_transformers import SentenceTransformer

from ml_pipeline.config import config
from ml_pipeline.utils import (
    calculate_cosine_similarity,
    create_category_embeddings_dict,
    save_json,
    load_json
)

logger = logging.getLogger(__name__)


class FeatureEngineer:
    """Feature engineering for ticket classification"""
    
    def __init__(self, model_name: Optional[str] = None):
        """
        Initialize feature engineer
        
        Args:
            model_name: Name of sentence transformer model
        """
        self.model_name = model_name or config.model_name
        self.model = None
        self.category_embeddings = {}
        self.category_names = []
        
    def load_model(self):
        """Load sentence transformer model"""
        if self.model is None:
            logger.info(f"Loading model: {self.model_name}")
            self.model = SentenceTransformer(self.model_name)
            logger.info("Model loaded successfully")
            
    def generate_embeddings(self, texts: List[str], 
                          batch_size: int = 32) -> np.ndarray:
        """
        Generate embeddings for texts
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding
            
        Returns:
            Array of embeddings
        """
        self.load_model()
        
        logger.info(f"Generating embeddings for {len(texts)} texts")
        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=True,
            convert_to_numpy=True
        )
        
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        return embeddings
        
    def generate_category_embeddings(self, categories_df: pd.DataFrame) -> Dict[str, np.ndarray]:
        """
        Generate embeddings for categories
        
        Args:
            categories_df: DataFrame with category information
            
        Returns:
            Dictionary mapping category names to embeddings
        """
        # Create category descriptions for embedding
        category_texts = []
        category_names = []
        
        for _, row in categories_df.iterrows():
            # Combine category name and description for better embedding
            text = f"{row['category_name']}: {row['category_description']}"
            category_texts.append(text)
            category_names.append(row['category_name'])
            
        # Generate embeddings
        embeddings = self.generate_embeddings(category_texts)
        
        # Create dictionary
        self.category_embeddings = dict(zip(category_names, embeddings))
        self.category_names = category_names
        
        logger.info(f"Generated embeddings for {len(self.category_embeddings)} categories")
        return self.category_embeddings
        
    def save_category_embeddings(self, filepath: str = "models/embeddings/category_embeddings.pkl"):
        """
        Save category embeddings to file
        
        Args:
            filepath: Output file path
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            'embeddings': self.category_embeddings,
            'category_names': self.category_names,
            'model_name': self.model_name
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(data, f)
            
        logger.info(f"Category embeddings saved to {filepath}")
        
    def load_category_embeddings(self, filepath: str = "models/embeddings/category_embeddings.pkl"):
        """
        Load category embeddings from file
        
        Args:
            filepath: Input file path
        """
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                
            self.category_embeddings = data['embeddings']
            self.category_names = data['category_names']
            
            logger.info(f"Loaded embeddings for {len(self.category_embeddings)} categories")
        except FileNotFoundError:
            logger.warning(f"Embeddings file not found: {filepath}")
            
    def predict_category(self, text_embedding: np.ndarray) -> Tuple[str, float]:
        """
        Predict category for a single text embedding
        
        Args:
            text_embedding: Text embedding vector
            
        Returns:
            Tuple of (predicted_category, confidence_score)
        """
        if not self.category_embeddings:
            raise ValueError("Category embeddings not loaded. Call generate_category_embeddings first.")
            
        best_category = None
        best_score = -1.0
        
        # Calculate similarity with each category
        for category_name, category_embedding in self.category_embeddings.items():
            similarity = calculate_cosine_similarity(text_embedding, category_embedding)
            
            if similarity > best_score:
                best_score = similarity
                best_category = category_name
                
        return best_category, float(best_score)
        
    def predict_categories_batch(self, text_embeddings: np.ndarray) -> List[Tuple[str, float]]:
        """
        Predict categories for multiple text embeddings
        
        Args:
            text_embeddings: Array of text embeddings
            
        Returns:
            List of (predicted_category, confidence_score) tuples
        """
        predictions = []
        
        logger.info(f"Predicting categories for {len(text_embeddings)} texts")
        
        for embedding in text_embeddings:
            category, score = self.predict_category(embedding)
            predictions.append((category, score))
            
        return predictions
        
    def calculate_baseline_statistics(self, embeddings: np.ndarray) -> Dict:
        """
        Calculate baseline statistics for drift detection
        
        Args:
            embeddings: Array of embeddings
            
        Returns:
            Dictionary of statistics
        """
        from ml_pipeline.utils import calculate_statistics
        
        stats = {}
        
        # Calculate statistics for each dimension
        for dim in range(embeddings.shape[1]):
            dim_data = embeddings[:, dim]
            stats[f'dim_{dim}'] = calculate_statistics(dim_data)
            
        # Overall statistics
        stats['overall'] = {
            'mean_norm': float(np.mean(np.linalg.norm(embeddings, axis=1))),
            'std_norm': float(np.std(np.linalg.norm(embeddings, axis=1))),
            'num_samples': int(embeddings.shape[0]),
            'embedding_dim': int(embeddings.shape[1])
        }
        
        logger.info("Baseline statistics calculated")
        return stats
        
    def save_baseline_statistics(self, stats: Dict, 
                                 filepath: Optional[str] = None):
        """
        Save baseline statistics for drift detection
        
        Args:
            stats: Statistics dictionary
            filepath: Output file path
        """
        if filepath is None:
            filepath = config.drift_baseline_path
            
        save_json(stats, filepath)
        
    def process_tickets(self, df: pd.DataFrame, 
                       text_column: str = 'combined_text') -> pd.DataFrame:
        """
        Process tickets: generate embeddings and predict categories
        
        Args:
            df: DataFrame with ticket data
            text_column: Column containing text to embed
            
        Returns:
            DataFrame with predictions
        """
        df = df.copy()
        
        # Generate embeddings
        texts = df[text_column].tolist()
        embeddings = self.generate_embeddings(texts)
        
        # Predict categories
        predictions = self.predict_categories_batch(embeddings)
        
        # Add predictions to dataframe
        df['predicted_category'] = [pred[0] for pred in predictions]
        df['confidence_score'] = [pred[1] for pred in predictions]
        
        # Store embeddings (optional, for drift detection)
        df['embedding'] = list(embeddings)
        
        logger.info("Ticket processing completed")
        return df
        
    def run_feature_engineering(self, tickets_df: pd.DataFrame,
                               categories_df: pd.DataFrame,
                               save_embeddings: bool = True) -> pd.DataFrame:
        """
        Run complete feature engineering pipeline
        
        Args:
            tickets_df: DataFrame with ticket data
            categories_df: DataFrame with category definitions
            save_embeddings: Whether to save category embeddings
            
        Returns:
            DataFrame with predictions
        """
        logger.info("Starting feature engineering pipeline")
        
        # Generate category embeddings
        self.generate_category_embeddings(categories_df)
        
        if save_embeddings:
            self.save_category_embeddings()
            
        # Process tickets
        df = self.process_tickets(tickets_df)
        
        # Calculate and save baseline statistics
        embeddings_array = np.array(df['embedding'].tolist())
        baseline_stats = self.calculate_baseline_statistics(embeddings_array)
        self.save_baseline_statistics(baseline_stats)
        
        logger.info("Feature engineering pipeline completed")
        return df


if __name__ == "__main__":
    from ml_pipeline.data_preprocessing import DataPreprocessor
    
    # Load and preprocess data
    preprocessor = DataPreprocessor()
    tickets_df = preprocessor.run_pipeline()
    categories_df = preprocessor.load_categories()
    
    # Run feature engineering
    engineer = FeatureEngineer()
    df = engineer.run_feature_engineering(tickets_df, categories_df)
    
    print(f"Feature engineering complete. Processed {len(df)} tickets.")
    print(f"\nSample predictions:")
    print(df[['Ticket Description', 'predicted_category', 'confidence_score']].head())

# Made with Bob

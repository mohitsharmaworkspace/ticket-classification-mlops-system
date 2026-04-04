"""
Ticket Classification Model Wrapper
"""

import numpy as np
import pandas as pd
import pickle
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer
import time

from app.config import settings
from app.utils.logger import logger
from app.utils.preprocessing import clean_text


class TicketClassifier:
    """Wrapper class for ticket classification model"""
    
    def __init__(self):
        """Initialize classifier"""
        self.model = None
        self.category_embeddings: Dict[str, np.ndarray] = {}
        self.category_names: List[str] = []
        self.model_name = settings.MODEL_NAME
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.is_loaded = False
        
    def load_model(self):
        """Load sentence transformer model"""
        try:
            start_time = time.time()
            logger.info(f"Loading model: {self.model_name}")
            
            self.model = SentenceTransformer(self.model_name)
            
            load_time = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_time:.2f}s")
            
            return load_time
        except Exception as e:
            logger.error(f"Error loading model: {e}")
            raise
            
    def load_category_embeddings(self, filepath: Optional[str] = None):
        """
        Load pre-computed category embeddings
        
        Args:
            filepath: Path to embeddings file
        """
        if filepath is None:
            filepath = settings.CATEGORY_EMBEDDINGS_PATH
            
        try:
            with open(filepath, 'rb') as f:
                data = pickle.load(f)
                
            self.category_embeddings = data['embeddings']
            self.category_names = data['category_names']
            
            logger.info(f"Loaded {len(self.category_embeddings)} category embeddings")
            self.is_loaded = True
            
        except FileNotFoundError:
            logger.warning(f"Category embeddings not found at {filepath}")
            logger.info("Will load default categories")
            self._load_default_categories()
            
    def _load_default_categories(self):
        """Load and generate embeddings for default categories"""
        try:
            categories_df = pd.read_csv(settings.DEFAULT_CATEGORIES_PATH)
            self.generate_category_embeddings(categories_df)
            logger.info("Default categories loaded and embeddings generated")
        except Exception as e:
            logger.error(f"Error loading default categories: {e}")
            raise
            
    def generate_category_embeddings(self, categories_df: pd.DataFrame):
        """
        Generate embeddings for categories
        
        Args:
            categories_df: DataFrame with category information
        """
        if self.model is None:
            self.load_model()
            
        category_texts = []
        category_names = []
        
        for _, row in categories_df.iterrows():
            # Combine name and description for better embedding
            text = f"{row['category_name']}: {row['category_description']}"
            category_texts.append(text)
            category_names.append(row['category_name'])
            
        # Generate embeddings
        logger.info(f"Generating embeddings for {len(category_texts)} categories")
        embeddings = self.model.encode(category_texts, convert_to_numpy=True)
        
        # Create dictionary
        self.category_embeddings = dict(zip(category_names, embeddings))
        self.category_names = category_names
        self.is_loaded = True
        
        logger.info("Category embeddings generated successfully")
        
    def _calculate_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
            
        return float(dot_product / (norm1 * norm2))
        
    def predict_single(self, text: str, return_all_scores: bool = False) -> Dict:
        """
        Predict category for single text
        
        Args:
            text: Input text
            return_all_scores: Whether to return scores for all categories
            
        Returns:
            Dictionary with prediction results
        """
        if not self.is_loaded:
            raise ValueError("Model not loaded. Call load_model() and load_category_embeddings() first.")
            
        # Clean text
        cleaned_text = clean_text(text)
        
        # Generate embedding
        text_embedding = self.model.encode([cleaned_text], convert_to_numpy=True)[0]
        
        # Calculate similarities
        scores = {}
        best_category = None
        best_score = -1.0
        
        for category_name, category_embedding in self.category_embeddings.items():
            similarity = self._calculate_cosine_similarity(text_embedding, category_embedding)
            scores[category_name] = similarity
            
            if similarity > best_score:
                best_score = similarity
                best_category = category_name
                
        result = {
            'predicted_category': best_category,
            'confidence_score': best_score,
            'is_low_confidence': best_score < self.confidence_threshold
        }
        
        if return_all_scores:
            result['all_scores'] = scores
            
        return result
        
    def predict_batch(self, texts: List[str]) -> List[Dict]:
        """
        Predict categories for multiple texts
        
        Args:
            texts: List of input texts
            
        Returns:
            List of prediction dictionaries
        """
        if not self.is_loaded:
            raise ValueError("Model not loaded.")
            
        # Clean texts
        cleaned_texts = [clean_text(text) for text in texts]
        
        # Generate embeddings
        text_embeddings = self.model.encode(cleaned_texts, convert_to_numpy=True)
        
        # Predict for each
        predictions = []
        for embedding in text_embeddings:
            best_category = None
            best_score = -1.0
            
            for category_name, category_embedding in self.category_embeddings.items():
                similarity = self._calculate_cosine_similarity(embedding, category_embedding)
                
                if similarity > best_score:
                    best_score = similarity
                    best_category = category_name
                    
            predictions.append({
                'predicted_category': best_category,
                'confidence_score': best_score,
                'is_low_confidence': best_score < self.confidence_threshold
            })
            
        return predictions
        
    def get_model_info(self) -> Dict:
        """Get model information"""
        return {
            'model_name': self.model_name,
            'is_loaded': self.is_loaded,
            'num_categories': len(self.category_embeddings),
            'category_names': self.category_names,
            'confidence_threshold': self.confidence_threshold
        }


# Global classifier instance
classifier = TicketClassifier()

# Made with Bob

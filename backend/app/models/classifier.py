import numpy as np
import pandas as pd
import pickle
from typing import Dict, List, Optional
from pathlib import Path
from sentence_transformers import SentenceTransformer
import time

from app.config import settings
from app.utils.logger import logger
from app.utils.preprocessing import clean_text


class TicketClassifier:
    def __init__(self):
        self.embedding_model = None
        self.mlp_predictor = None
        self.category_embeddings: Dict[str, np.ndarray] = {}
        self.category_names: List[str] = []
        self.model_name = settings.MODEL_NAME
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self.is_loaded = False
        self.use_trained_model = True
        self.trained_model_available = False
        
    def load_embedding_model(self):
        try:
            start_time = time.time()
            logger.info(f"Loading embedding model: {self.model_name}")
            
            self.embedding_model = SentenceTransformer(self.model_name)
            
            load_time = time.time() - start_time
            logger.info(f"Embedding model loaded in {load_time:.2f}s")
            
            return load_time
        except Exception as e:
            logger.error(f"Error loading embedding model: {e}")
            raise
    
    def load_trained_model(self, filepath: Optional[str] = None):
        if filepath is None:
            filepath = str(settings.MLP_MODEL_PATH)
        
        try:
            from ml_pipeline.models.predictor import ModelPredictor
            
            self.mlp_predictor = ModelPredictor.load_from_checkpoint(filepath)
            self.category_names = list(self.mlp_predictor.label_encoder.classes_)
            
            logger.info(f"Trained MLP model loaded with {len(self.category_names)} categories")
            self.is_loaded = True
            self.trained_model_available = True
            self.use_trained_model = True
            
        except FileNotFoundError:
            logger.warning(f"Trained model not found at {filepath}")
            logger.info("Falling back to similarity mode")
            self.trained_model_available = False
            self._load_default_categories()
    
    def _load_default_categories(self):
        try:
            categories_df = pd.read_csv(str(settings.DEFAULT_CATEGORIES_PATH))
            self.generate_category_embeddings(categories_df)
            self.use_trained_model = False
            logger.info("Default categories loaded for similarity mode")
        except Exception as e:
            logger.error(f"Error loading default categories: {e}")
            raise
    
    def generate_category_embeddings(self, categories_df: pd.DataFrame):
        if self.embedding_model is None:
            self.load_embedding_model()
        
        category_texts = []
        category_names = []
        
        for _, row in categories_df.iterrows():
            text = f"{row['category_name']}: {row['category_description']}"
            category_texts.append(text)
            category_names.append(row['category_name'])
        
        logger.info(f"Generating embeddings for {len(category_texts)} categories")
        embeddings = self.embedding_model.encode(category_texts, convert_to_numpy=True)
        
        self.category_embeddings = dict(zip(category_names, embeddings))
        self.category_names = category_names
        self.is_loaded = True
        
        logger.info("Category embeddings generated")
    
    def set_prediction_mode(self, use_trained_model: bool):
        if use_trained_model and not self.trained_model_available:
            logger.warning("Trained model not available, using similarity mode")
            self.use_trained_model = False
        else:
            self.use_trained_model = use_trained_model
            mode = "trained model" if use_trained_model else "similarity"
            logger.info(f"Prediction mode: {mode}")
    
    def _calculate_cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))
    
    def predict_single(self, text: str, return_all_scores: bool = False) -> Dict:
        if not self.is_loaded:
            raise ValueError("Model not loaded")
        
        cleaned_text = clean_text(text)
        
        if self.embedding_model is None:
            self.load_embedding_model()
        
        text_embedding = self.embedding_model.encode([cleaned_text], convert_to_numpy=True)[0]
        
        if self.use_trained_model and self.mlp_predictor:
            predicted_category, confidence_score, all_scores = self.mlp_predictor.predict_with_all_scores(text_embedding)
            
            result = {
                'predicted_category': predicted_category,
                'confidence_score': float(confidence_score),
                'is_low_confidence': confidence_score < self.confidence_threshold
            }
            
            if return_all_scores:
                result['all_scores'] = all_scores
        else:
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
        if not self.is_loaded:
            raise ValueError("Model not loaded")
        
        cleaned_texts = [clean_text(text) for text in texts]
        
        if self.embedding_model is None:
            self.load_embedding_model()
        
        text_embeddings = self.embedding_model.encode(cleaned_texts, convert_to_numpy=True)
        
        predictions = []
        
        if self.use_trained_model and self.mlp_predictor:
            results = self.mlp_predictor.predict_batch(text_embeddings)
            
            for category, score in results:
                predictions.append({
                    'predicted_category': category,
                    'confidence_score': float(score),
                    'is_low_confidence': score < self.confidence_threshold
                })
        else:
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
        return {
            'model_name': self.model_name,
            'is_loaded': self.is_loaded,
            'num_categories': len(self.category_names),
            'category_names': self.category_names,
            'confidence_threshold': self.confidence_threshold,
            'trained_model_available': self.trained_model_available,
            'prediction_mode': 'trained' if self.use_trained_model else 'similarity'
        }


classifier = TicketClassifier()

# Made with Bob

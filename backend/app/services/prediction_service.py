"""
Prediction service for ticket classification
"""

import pandas as pd
import io
from typing import List, Dict
from fastapi import UploadFile
import time

from app.models.classifier import classifier
from app.utils.logger import logger
from app.utils.preprocessing import clean_text, validate_text_length


class PredictionService:
    """Handle prediction operations"""
    
    def __init__(self):
        """Initialize prediction service"""
        self.classifier = classifier
        
    async def predict_single_text(self, text: str) -> Dict:
        """
        Predict category for single text
        
        Args:
            text: Input text
            
        Returns:
            Prediction result dictionary
        """
        start_time = time.time()
        
        try:
            # Validate text
            if not validate_text_length(text):
                raise ValueError("Text length must be between 10 and 1000 characters")
                
            # Get prediction
            result = self.classifier.predict_single(text, return_all_scores=True)
            
            # Calculate processing time
            processing_time = (time.time() - start_time) * 1000  # Convert to ms
            result['processing_time_ms'] = processing_time
            
            logger.info(f"Single prediction: {result['predicted_category']} (confidence: {result['confidence_score']:.3f})")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in single prediction: {e}")
            raise
            
    async def predict_bulk_csv(self, file: UploadFile) -> Dict:
        """
        Predict categories for bulk CSV upload
        
        Args:
            file: Uploaded CSV file
            
        Returns:
            Bulk prediction results
        """
        start_time = time.time()
        
        try:
            # Read CSV
            contents = await file.read()
            df = pd.read_csv(io.BytesIO(contents))
            
            # Validate CSV structure
            if 'ticket_text' not in df.columns and 'Ticket Description' not in df.columns:
                raise ValueError("CSV must contain 'ticket_text' or 'Ticket Description' column")
                
            # Get text column
            text_column = 'ticket_text' if 'ticket_text' in df.columns else 'Ticket Description'
            texts = df[text_column].tolist()
            
            # Filter valid texts
            valid_texts = [text for text in texts if validate_text_length(str(text))]
            
            if not valid_texts:
                raise ValueError("No valid texts found in CSV")
                
            # Get predictions
            predictions = self.classifier.predict_batch(valid_texts)
            
            # Format results
            results = []
            low_confidence_count = 0
            
            for idx, (text, pred) in enumerate(zip(valid_texts, predictions)):
                results.append({
                    'row_index': idx,
                    'ticket_text': text[:100] + '...' if len(text) > 100 else text,
                    'predicted_category': pred['predicted_category'],
                    'confidence_score': pred['confidence_score']
                })
                
                if pred['is_low_confidence']:
                    low_confidence_count += 1
                    
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                'predictions': results,
                'total_processed': len(results),
                'processing_time_ms': processing_time,
                'low_confidence_count': low_confidence_count
            }
            
            logger.info(f"Bulk prediction: {len(results)} tickets processed")
            
            return result
            
        except Exception as e:
            logger.error(f"Error in bulk prediction: {e}")
            raise
            
    async def predict_with_custom_categories(self, 
                                            tickets_file: UploadFile,
                                            categories_file: UploadFile) -> Dict:
        """
        Predict with custom category definitions
        
        Args:
            tickets_file: CSV file with tickets
            categories_file: CSV file with category definitions
            
        Returns:
            Prediction results with custom categories
        """
        start_time = time.time()
        
        try:
            # Read categories CSV
            cat_contents = await categories_file.read()
            categories_df = pd.read_csv(io.BytesIO(cat_contents))
            
            # Validate categories structure
            required_cols = ['category_name', 'category_description']
            if not all(col in categories_df.columns for col in required_cols):
                raise ValueError(f"Categories CSV must contain: {required_cols}")
                
            # Generate embeddings for custom categories
            logger.info(f"Generating embeddings for {len(categories_df)} custom categories")
            self.classifier.generate_category_embeddings(categories_df)
            
            # Read tickets CSV
            tickets_contents = await tickets_file.read()
            tickets_df = pd.read_csv(io.BytesIO(tickets_contents))
            
            # Validate tickets structure
            if 'ticket_text' not in tickets_df.columns and 'Ticket Description' not in tickets_df.columns:
                raise ValueError("Tickets CSV must contain 'ticket_text' or 'Ticket Description' column")
                
            # Get text column
            text_column = 'ticket_text' if 'ticket_text' in tickets_df.columns else 'Ticket Description'
            texts = tickets_df[text_column].tolist()
            
            # Filter valid texts
            valid_texts = [text for text in texts if validate_text_length(str(text))]
            
            # Get predictions
            predictions = self.classifier.predict_batch(valid_texts)
            
            # Format results
            results = []
            low_confidence_count = 0
            
            for idx, (text, pred) in enumerate(zip(valid_texts, predictions)):
                results.append({
                    'row_index': idx,
                    'ticket_text': text[:100] + '...' if len(text) > 100 else text,
                    'predicted_category': pred['predicted_category'],
                    'confidence_score': pred['confidence_score']
                })
                
                if pred['is_low_confidence']:
                    low_confidence_count += 1
                    
            processing_time = (time.time() - start_time) * 1000
            
            result = {
                'predictions': results,
                'total_processed': len(results),
                'num_categories': len(categories_df),
                'category_names': categories_df['category_name'].tolist(),
                'processing_time_ms': processing_time,
                'low_confidence_count': low_confidence_count
            }
            
            logger.info(f"Advanced mode prediction: {len(results)} tickets with {len(categories_df)} custom categories")
            
            # Reload default categories for next requests
            self.classifier._load_default_categories()
            
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced mode prediction: {e}")
            # Reload default categories on error
            try:
                self.classifier._load_default_categories()
            except:
                pass
            raise


# Global service instance
prediction_service = PredictionService()

# Made with Bob

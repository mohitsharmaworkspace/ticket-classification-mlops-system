"""
Feedback service for handling user corrections
"""

import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import Dict
import os

from app.config import settings
from app.utils.logger import logger


class FeedbackService:
    """Handle feedback and corrections"""
    
    def __init__(self):
        """Initialize feedback service"""
        self.ground_truth_path = settings.GROUND_TRUTH_PATH
        self.correction_threshold = 0.15  # 15% correction rate triggers retraining
        
    def save_feedback(self, feedback_data: Dict) -> Dict:
        """
        Save user feedback/correction
        
        Args:
            feedback_data: Feedback information
            
        Returns:
            Result dictionary
        """
        try:
            # Prepare feedback record
            record = {
                'timestamp': feedback_data.get('timestamp', datetime.now()),
                'ticket_id': feedback_data.get('ticket_id', ''),
                'original_text': feedback_data['original_text'],
                'predicted_category': feedback_data['predicted_category'],
                'corrected_category': feedback_data['corrected_category'],
                'confidence_score': feedback_data['confidence_score'],
                'is_correction': feedback_data['predicted_category'] != feedback_data['corrected_category']
            }
            
            # Load existing feedback or create new
            if Path(self.ground_truth_path).exists():
                df = pd.read_csv(self.ground_truth_path)
            else:
                df = pd.DataFrame()
                
            # Append new record
            new_df = pd.DataFrame([record])
            df = pd.concat([df, new_df], ignore_index=True)
            
            # Save to CSV
            Path(self.ground_truth_path).parent.mkdir(parents=True, exist_ok=True)
            df.to_csv(self.ground_truth_path, index=False)
            
            # Calculate correction rate
            correction_rate = df['is_correction'].sum() / len(df) if len(df) > 0 else 0
            
            # Check if retraining should be triggered
            retraining_triggered = self._should_trigger_retraining(df)
            
            logger.info(f"Feedback saved. Total: {len(df)}, Corrections: {df['is_correction'].sum()}, Rate: {correction_rate:.2%}")
            
            if retraining_triggered:
                logger.warning("⚠️ Retraining threshold reached!")
                
            return {
                'success': True,
                'message': 'Feedback saved successfully',
                'feedback_count': len(df),
                'correction_count': int(df['is_correction'].sum()),
                'correction_rate': float(correction_rate),
                'retraining_triggered': retraining_triggered
            }
            
        except Exception as e:
            logger.error(f"Error saving feedback: {e}")
            return {
                'success': False,
                'message': f'Error saving feedback: {str(e)}',
                'feedback_count': 0,
                'retraining_triggered': False
            }
            
    def _should_trigger_retraining(self, df: pd.DataFrame) -> bool:
        """
        Determine if retraining should be triggered
        
        Args:
            df: Feedback DataFrame
            
        Returns:
            True if retraining should be triggered
        """
        if len(df) < 50:  # Minimum samples
            return False
            
        # Calculate recent correction rate (last 100 samples)
        recent_df = df.tail(100)
        correction_rate = recent_df['is_correction'].sum() / len(recent_df)
        
        return correction_rate > self.correction_threshold
        
    def get_feedback_stats(self) -> Dict:
        """
        Get feedback statistics
        
        Returns:
            Statistics dictionary
        """
        try:
            if not Path(self.ground_truth_path).exists():
                return {
                    'total_feedback': 0,
                    'total_corrections': 0,
                    'correction_rate': 0.0
                }
                
            df = pd.read_csv(self.ground_truth_path)
            
            stats = {
                'total_feedback': len(df),
                'total_corrections': int(df['is_correction'].sum()),
                'correction_rate': float(df['is_correction'].sum() / len(df)) if len(df) > 0 else 0.0,
                'recent_correction_rate': float(df.tail(100)['is_correction'].sum() / min(100, len(df))) if len(df) > 0 else 0.0
            }
            
            return stats
            
        except Exception as e:
            logger.error(f"Error getting feedback stats: {e}")
            return {
                'total_feedback': 0,
                'total_corrections': 0,
                'correction_rate': 0.0
            }


# Global service instance
feedback_service = FeedbackService()

# Made with Bob

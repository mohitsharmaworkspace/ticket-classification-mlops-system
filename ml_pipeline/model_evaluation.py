"""
Model evaluation and performance analysis
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Optional
from sklearn.metrics import (
    accuracy_score,
    precision_recall_fscore_support,
    confusion_matrix,
    classification_report
)
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

from ml_pipeline.config import config

logger = logging.getLogger(__name__)


class ModelEvaluator:
    """Evaluate model performance"""
    
    def __init__(self):
        """Initialize model evaluator"""
        self.config = config
        
    def calculate_metrics(self, y_true: np.ndarray, 
                         y_pred: np.ndarray,
                         confidence_scores: Optional[np.ndarray] = None) -> Dict:
        """
        Calculate comprehensive evaluation metrics
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            confidence_scores: Confidence scores (optional)
            
        Returns:
            Dictionary of metrics
        """
        metrics = {}
        
        # Basic metrics
        metrics['accuracy'] = float(accuracy_score(y_true, y_pred))
        
        # Precision, recall, F1
        precision, recall, f1, support = precision_recall_fscore_support(
            y_true, y_pred, average='weighted', zero_division=0
        )
        
        metrics['precision'] = float(precision)
        metrics['recall'] = float(recall)
        metrics['f1_score'] = float(f1)
        
        # Per-class metrics
        precision_per_class, recall_per_class, f1_per_class, support_per_class = \
            precision_recall_fscore_support(y_true, y_pred, average=None, zero_division=0)
            
        unique_labels = np.unique(np.concatenate([y_true, y_pred]))
        
        metrics['per_class'] = {}
        for i, label in enumerate(unique_labels):
            if i < len(precision_per_class):
                metrics['per_class'][str(label)] = {
                    'precision': float(precision_per_class[i]),
                    'recall': float(recall_per_class[i]),
                    'f1_score': float(f1_per_class[i]),
                    'support': int(support_per_class[i])
                }
        
        # Confidence statistics
        if confidence_scores is not None:
            metrics['confidence'] = {
                'mean': float(np.mean(confidence_scores)),
                'std': float(np.std(confidence_scores)),
                'min': float(np.min(confidence_scores)),
                'max': float(np.max(confidence_scores)),
                'median': float(np.median(confidence_scores))
            }
            
            # Low confidence predictions
            threshold = self.config.confidence_threshold
            low_conf_mask = confidence_scores < threshold
            if low_conf_mask.any():
                metrics['low_confidence'] = {
                    'count': int(np.sum(low_conf_mask)),
                    'ratio': float(np.mean(low_conf_mask)),
                    'accuracy': float(accuracy_score(y_true[low_conf_mask], y_pred[low_conf_mask]))
                }
        
        return metrics
        
    def generate_confusion_matrix(self, y_true: np.ndarray,
                                 y_pred: np.ndarray,
                                 labels: Optional[List[str]] = None,
                                 save_path: Optional[str] = None) -> np.ndarray:
        """
        Generate confusion matrix
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Label names (optional)
            save_path: Path to save plot (optional)
            
        Returns:
            Confusion matrix array
        """
        cm = confusion_matrix(y_true, y_pred)
        
        if save_path:
            plt.figure(figsize=(12, 10))
            sns.heatmap(cm, annot=True, fmt='d', cmap='Blues',
                       xticklabels=labels, yticklabels=labels)
            plt.title('Confusion Matrix')
            plt.ylabel('True Label')
            plt.xlabel('Predicted Label')
            plt.tight_layout()
            
            Path(save_path).parent.mkdir(parents=True, exist_ok=True)
            plt.savefig(save_path)
            plt.close()
            logger.info(f"Confusion matrix saved to {save_path}")
            
        return cm
        
    def generate_classification_report(self, y_true: np.ndarray,
                                      y_pred: np.ndarray,
                                      labels: Optional[List[str]] = None) -> str:
        """
        Generate detailed classification report
        
        Args:
            y_true: True labels
            y_pred: Predicted labels
            labels: Label names (optional)
            
        Returns:
            Classification report string
        """
        report = classification_report(y_true, y_pred, target_names=labels, zero_division=0)
        return report
        
    def analyze_errors(self, df: pd.DataFrame) -> Dict:
        """
        Analyze prediction errors
        
        Args:
            df: DataFrame with predictions and true labels
            
        Returns:
            Error analysis dictionary
        """
        if 'Ticket Type' not in df.columns or 'predicted_category' not in df.columns:
            logger.warning("Cannot analyze errors: missing required columns")
            return {}
            
        # Find misclassified samples
        errors_df = df[df['Ticket Type'] != df['predicted_category']].copy()
        
        error_analysis = {
            'total_errors': len(errors_df),
            'error_rate': len(errors_df) / len(df),
            'errors_by_true_label': {},
            'errors_by_predicted_label': {},
            'common_confusions': []
        }
        
        # Errors by true label
        for label in df['Ticket Type'].unique():
            label_errors = errors_df[errors_df['Ticket Type'] == label]
            error_analysis['errors_by_true_label'][str(label)] = {
                'count': len(label_errors),
                'rate': len(label_errors) / len(df[df['Ticket Type'] == label])
            }
            
        # Errors by predicted label
        for label in df['predicted_category'].unique():
            pred_errors = errors_df[errors_df['predicted_category'] == label]
            error_analysis['errors_by_predicted_label'][str(label)] = {
                'count': len(pred_errors)
            }
            
        # Common confusions
        confusion_counts = errors_df.groupby(['Ticket Type', 'predicted_category']).size()
        confusion_counts = confusion_counts.sort_values(ascending=False)
        
        for (true_label, pred_label), count in confusion_counts.head(10).items():
            error_analysis['common_confusions'].append({
                'true_label': str(true_label),
                'predicted_label': str(pred_label),
                'count': int(count)
            })
            
        return error_analysis
        
    def evaluate_model(self, df: pd.DataFrame,
                      save_plots: bool = True,
                      output_dir: str = "models/evaluation") -> Dict:
        """
        Comprehensive model evaluation
        
        Args:
            df: DataFrame with predictions and true labels
            save_plots: Whether to save visualization plots
            output_dir: Directory for output files
            
        Returns:
            Complete evaluation report
        """
        logger.info("Starting model evaluation")
        
        if 'Ticket Type' not in df.columns or 'predicted_category' not in df.columns:
            logger.error("Missing required columns for evaluation")
            return {'error': 'Missing required columns'}
            
        y_true = df['Ticket Type'].values
        y_pred = df['predicted_category'].values
        confidence_scores = df['confidence_score'].values if 'confidence_score' in df.columns else None
        
        # Calculate metrics
        metrics = self.calculate_metrics(y_true, y_pred, confidence_scores)
        
        # Generate confusion matrix
        labels = sorted(df['Ticket Type'].unique())
        if save_plots:
            cm_path = f"{output_dir}/confusion_matrix.png"
            self.generate_confusion_matrix(y_true, y_pred, labels, cm_path)
            
        # Generate classification report
        report = self.generate_classification_report(y_true, y_pred, labels)
        
        # Analyze errors
        error_analysis = self.analyze_errors(df)
        
        # Compile evaluation report
        evaluation_report = {
            'metrics': metrics,
            'classification_report': report,
            'error_analysis': error_analysis,
            'num_samples': len(df),
            'num_classes': len(labels),
            'class_names': labels
        }
        
        logger.info("Model evaluation completed")
        logger.info(f"Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"F1 Score: {metrics['f1_score']:.4f}")
        logger.info(f"Error Rate: {error_analysis.get('error_rate', 0):.4f}")
        
        return evaluation_report
        
    def compare_models(self, results_list: List[Dict]) -> pd.DataFrame:
        """
        Compare multiple model results
        
        Args:
            results_list: List of evaluation result dictionaries
            
        Returns:
            Comparison DataFrame
        """
        comparison_data = []
        
        for i, results in enumerate(results_list):
            metrics = results.get('metrics', {})
            row = {
                'model_id': i,
                'accuracy': metrics.get('accuracy', 0),
                'precision': metrics.get('precision', 0),
                'recall': metrics.get('recall', 0),
                'f1_score': metrics.get('f1_score', 0),
                'num_samples': results.get('num_samples', 0)
            }
            comparison_data.append(row)
            
        comparison_df = pd.DataFrame(comparison_data)
        return comparison_df


if __name__ == "__main__":
    # Example usage
    evaluator = ModelEvaluator()
    
    # Create sample data
    sample_df = pd.DataFrame({
        'Ticket Type': ['Technical Issue'] * 50 + ['Billing Inquiry'] * 50,
        'predicted_category': ['Technical Issue'] * 45 + ['Billing Inquiry'] * 5 + 
                             ['Billing Inquiry'] * 48 + ['Technical Issue'] * 2,
        'confidence_score': np.random.uniform(0.6, 0.99, 100)
    })
    
    # Evaluate
    report = evaluator.evaluate_model(sample_df, save_plots=False)
    
    print("\n=== Evaluation Report ===")
    print(f"Accuracy: {report['metrics']['accuracy']:.4f}")
    print(f"F1 Score: {report['metrics']['f1_score']:.4f}")
    print(f"\nClassification Report:\n{report['classification_report']}")

# Made with Bob

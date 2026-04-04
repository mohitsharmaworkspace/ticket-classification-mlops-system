"""
Data drift detection for ticket classification
"""

import pandas as pd
import numpy as np
import logging
from typing import Dict, List, Tuple, Optional
from scipy import stats
from datetime import datetime

from ml_pipeline.config import config
from ml_pipeline.utils import load_json, save_json, calculate_statistics

logger = logging.getLogger(__name__)


class DriftDetector:
    """Detect data drift in ticket embeddings"""
    
    def __init__(self):
        """Initialize drift detector"""
        self.config = config
        self.baseline_stats = None
        self.significance_level = self.config.get('drift.significance_level', 0.05)
        
    def load_baseline(self, filepath: Optional[str] = None) -> Dict:
        """
        Load baseline statistics
        
        Args:
            filepath: Path to baseline file
            
        Returns:
            Baseline statistics dictionary
        """
        if filepath is None:
            filepath = self.config.drift_baseline_path
            
        self.baseline_stats = load_json(filepath)
        
        if not self.baseline_stats:
            logger.warning("No baseline statistics found")
        else:
            logger.info(f"Loaded baseline with {self.baseline_stats.get('overall', {}).get('num_samples', 0)} samples")
            
        return self.baseline_stats
        
    def kolmogorov_smirnov_test(self, baseline_data: np.ndarray, 
                                current_data: np.ndarray) -> Tuple[float, float]:
        """
        Perform Kolmogorov-Smirnov test for drift detection
        
        Args:
            baseline_data: Baseline data distribution
            current_data: Current data distribution
            
        Returns:
            Tuple of (statistic, p_value)
        """
        statistic, p_value = stats.ks_2samp(baseline_data, current_data)
        return float(statistic), float(p_value)
        
    def detect_drift_per_dimension(self, baseline_embeddings: np.ndarray,
                                   current_embeddings: np.ndarray) -> Dict[str, Any]:
        """
        Detect drift for each embedding dimension
        
        Args:
            baseline_embeddings: Baseline embedding array
            current_embeddings: Current embedding array
            
        Returns:
            Dictionary with drift detection results
        """
        drift_results = {
            'dimensions_with_drift': [],
            'drift_scores': {},
            'p_values': {},
            'overall_drift_detected': False
        }
        
        num_dimensions = baseline_embeddings.shape[1]
        drift_count = 0
        
        for dim in range(num_dimensions):
            baseline_dim = baseline_embeddings[:, dim]
            current_dim = current_embeddings[:, dim]
            
            # Perform KS test
            statistic, p_value = self.kolmogorov_smirnov_test(baseline_dim, current_dim)
            
            drift_results['drift_scores'][f'dim_{dim}'] = statistic
            drift_results['p_values'][f'dim_{dim}'] = p_value
            
            # Check if drift detected
            if p_value < self.significance_level:
                drift_results['dimensions_with_drift'].append(dim)
                drift_count += 1
                
        # Overall drift if more than 10% of dimensions show drift
        drift_threshold = 0.1 * num_dimensions
        if drift_count > drift_threshold:
            drift_results['overall_drift_detected'] = True
            
        drift_results['num_dimensions_with_drift'] = drift_count
        drift_results['total_dimensions'] = num_dimensions
        drift_results['drift_ratio'] = drift_count / num_dimensions
        
        return drift_results
        
    def detect_distribution_shift(self, baseline_stats: Dict,
                                  current_embeddings: np.ndarray) -> Dict:
        """
        Detect distribution shift using statistical comparison
        
        Args:
            baseline_stats: Baseline statistics
            current_embeddings: Current embeddings
            
        Returns:
            Dictionary with shift detection results
        """
        current_stats = calculate_statistics(
            np.linalg.norm(current_embeddings, axis=1)
        )
        
        baseline_mean = baseline_stats.get('overall', {}).get('mean_norm', 0)
        baseline_std = baseline_stats.get('overall', {}).get('std_norm', 1)
        
        current_mean = current_stats['mean']
        current_std = current_stats['std']
        
        # Calculate z-score for mean shift
        mean_z_score = abs(current_mean - baseline_mean) / baseline_std if baseline_std > 0 else 0
        
        # Calculate ratio for std shift
        std_ratio = current_std / baseline_std if baseline_std > 0 else 1
        
        shift_detected = mean_z_score > 2.0 or std_ratio > 1.5 or std_ratio < 0.67
        
        return {
            'shift_detected': shift_detected,
            'mean_z_score': float(mean_z_score),
            'std_ratio': float(std_ratio),
            'baseline_mean': baseline_mean,
            'current_mean': current_mean,
            'baseline_std': baseline_std,
            'current_std': current_std
        }
        
    def analyze_confidence_drift(self, df: pd.DataFrame) -> Dict:
        """
        Analyze drift in confidence scores
        
        Args:
            df: DataFrame with predictions and confidence scores
            
        Returns:
            Dictionary with confidence drift analysis
        """
        confidence_scores = df['confidence_score'].values
        
        stats_dict = calculate_statistics(confidence_scores)
        
        # Check for low confidence predictions
        threshold = self.config.confidence_threshold
        low_confidence_count = len(df[df['confidence_score'] < threshold])
        low_confidence_ratio = low_confidence_count / len(df)
        
        # Alert if too many low confidence predictions
        confidence_alert = low_confidence_ratio > 0.3
        
        return {
            'confidence_stats': stats_dict,
            'low_confidence_ratio': float(low_confidence_ratio),
            'confidence_alert': confidence_alert,
            'num_predictions': len(df)
        }
        
    def detect_drift(self, current_embeddings: np.ndarray,
                    predictions_df: Optional[pd.DataFrame] = None) -> Dict:
        """
        Comprehensive drift detection
        
        Args:
            current_embeddings: Current embedding array
            predictions_df: DataFrame with predictions (optional)
            
        Returns:
            Complete drift detection report
        """
        logger.info("Starting drift detection")
        
        # Load baseline
        if self.baseline_stats is None:
            self.load_baseline()
            
        if not self.baseline_stats:
            logger.error("Cannot perform drift detection without baseline")
            return {'error': 'No baseline statistics available'}
            
        # Reconstruct baseline embeddings (simplified - in production, store actual embeddings)
        baseline_dim = self.baseline_stats.get('overall', {}).get('embedding_dim', 384)
        baseline_samples = self.baseline_stats.get('overall', {}).get('num_samples', 100)
        
        # For demonstration, create synthetic baseline (in production, use actual stored embeddings)
        baseline_embeddings = np.random.randn(min(baseline_samples, 1000), baseline_dim)
        
        # Detect drift per dimension
        dimension_drift = self.detect_drift_per_dimension(
            baseline_embeddings[:len(current_embeddings)],
            current_embeddings
        )
        
        # Detect distribution shift
        distribution_shift = self.detect_distribution_shift(
            self.baseline_stats,
            current_embeddings
        )
        
        # Analyze confidence drift if predictions provided
        confidence_drift = None
        if predictions_df is not None and 'confidence_score' in predictions_df.columns:
            confidence_drift = self.analyze_confidence_drift(predictions_df)
            
        # Compile report
        drift_report = {
            'timestamp': datetime.now().isoformat(),
            'dimension_drift': dimension_drift,
            'distribution_shift': distribution_shift,
            'confidence_drift': confidence_drift,
            'overall_drift_detected': (
                dimension_drift['overall_drift_detected'] or 
                distribution_shift['shift_detected']
            ),
            'num_samples_analyzed': len(current_embeddings)
        }
        
        # Log results
        if drift_report['overall_drift_detected']:
            logger.warning("⚠️  DRIFT DETECTED!")
            logger.warning(f"Dimension drift: {dimension_drift['num_dimensions_with_drift']} dimensions affected")
            logger.warning(f"Distribution shift: {distribution_shift['shift_detected']}")
        else:
            logger.info("✓ No significant drift detected")
            
        return drift_report
        
    def save_drift_report(self, report: Dict, filepath: str = "data/drift_baseline/drift_report.json"):
        """
        Save drift detection report
        
        Args:
            report: Drift report dictionary
            filepath: Output file path
        """
        save_json(report, filepath)
        logger.info(f"Drift report saved to {filepath}")
        
    def should_trigger_retraining(self, drift_report: Dict,
                                 correction_rate: Optional[float] = None) -> bool:
        """
        Determine if retraining should be triggered
        
        Args:
            drift_report: Drift detection report
            correction_rate: Rate of user corrections
            
        Returns:
            True if retraining should be triggered
        """
        # Check drift
        drift_detected = drift_report.get('overall_drift_detected', False)
        
        # Check correction rate
        correction_threshold = self.config.correction_rate_threshold
        high_correction_rate = (
            correction_rate is not None and 
            correction_rate > correction_threshold
        )
        
        # Check confidence
        confidence_alert = False
        if drift_report.get('confidence_drift'):
            confidence_alert = drift_report['confidence_drift'].get('confidence_alert', False)
            
        should_retrain = drift_detected or high_correction_rate or confidence_alert
        
        if should_retrain:
            logger.warning("🔄 Retraining trigger activated!")
            if drift_detected:
                logger.warning("  - Reason: Data drift detected")
            if high_correction_rate:
                logger.warning(f"  - Reason: High correction rate ({correction_rate:.2%})")
            if confidence_alert:
                logger.warning("  - Reason: Low confidence alert")
        else:
            logger.info("✓ No retraining needed")
            
        return should_retrain


if __name__ == "__main__":
    # Example usage
    detector = DriftDetector()
    
    # Create sample embeddings
    current_embeddings = np.random.randn(100, 384)
    
    # Detect drift
    report = detector.detect_drift(current_embeddings)
    
    print("\n=== Drift Detection Report ===")
    print(f"Overall drift detected: {report['overall_drift_detected']}")
    print(f"Dimensions with drift: {report['dimension_drift']['num_dimensions_with_drift']}")
    print(f"Distribution shift: {report['distribution_shift']['shift_detected']}")

# Made with Bob

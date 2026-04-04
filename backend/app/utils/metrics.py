"""
Prometheus metrics
"""

from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from typing import Dict
import time


# Request metrics
request_count = Counter(
    'api_requests_total',
    'Total API requests',
    ['method', 'endpoint', 'status']
)

request_latency = Histogram(
    'api_request_latency_seconds',
    'API request latency',
    ['method', 'endpoint']
)

# Prediction metrics
prediction_count = Counter(
    'predictions_total',
    'Total predictions made',
    ['mode']  # single, bulk, advanced
)

confidence_score = Histogram(
    'prediction_confidence_score',
    'Prediction confidence scores',
    buckets=[0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.99, 1.0]
)

low_confidence_predictions = Counter(
    'low_confidence_predictions_total',
    'Total low confidence predictions'
)

# Feedback metrics
feedback_count = Counter(
    'feedback_submissions_total',
    'Total feedback submissions'
)

correction_count = Counter(
    'prediction_corrections_total',
    'Total prediction corrections'
)

# Model metrics
model_load_time = Gauge(
    'model_load_time_seconds',
    'Time taken to load model'
)

categories_loaded = Gauge(
    'categories_loaded_count',
    'Number of categories loaded'
)

# Error metrics
error_count = Counter(
    'api_errors_total',
    'Total API errors',
    ['error_type']
)

# System metrics
service_uptime = Gauge(
    'service_uptime_seconds',
    'Service uptime in seconds'
)


class MetricsCollector:
    """Collect and manage application metrics"""
    
    def __init__(self):
        self.start_time = time.time()
        
    def record_request(self, method: str, endpoint: str, status: int, duration: float):
        """Record API request metrics"""
        request_count.labels(method=method, endpoint=endpoint, status=status).inc()
        request_latency.labels(method=method, endpoint=endpoint).observe(duration)
        
    def record_prediction(self, mode: str, conf_score: float, is_low_confidence: bool):
        """Record prediction metrics"""
        prediction_count.labels(mode=mode).inc()
        confidence_score.observe(conf_score)
        if is_low_confidence:
            low_confidence_predictions.inc()
            
    def record_feedback(self, is_correction: bool):
        """Record feedback metrics"""
        feedback_count.inc()
        if is_correction:
            correction_count.inc()
            
    def record_error(self, error_type: str):
        """Record error metrics"""
        error_count.labels(error_type=error_type).inc()
        
    def update_uptime(self):
        """Update service uptime"""
        uptime = time.time() - self.start_time
        service_uptime.set(uptime)
        
    def get_metrics(self) -> bytes:
        """Get Prometheus metrics"""
        self.update_uptime()
        return generate_latest()
        
    def get_metrics_summary(self) -> Dict:
        """Get metrics summary as dictionary"""
        return {
            'total_requests': request_count._value.sum(),
            'total_predictions': prediction_count._value.sum(),
            'total_feedback': feedback_count._value.sum(),
            'total_corrections': correction_count._value.sum(),
            'uptime_seconds': time.time() - self.start_time
        }


# Global metrics collector
metrics_collector = MetricsCollector()

# Made with Bob

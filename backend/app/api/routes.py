"""
API Routes for Ticket Classification
"""

from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from fastapi.responses import Response
import time

from app.api.schemas import (
    SingleTextRequest,
    PredictionResponse,
    BulkPredictionResponse,
    AdvancedModeResponse,
    FeedbackRequest,
    FeedbackResponse,
    HealthResponse,
    MetricsResponse,
    ErrorResponse
)
from app.services.prediction_service import prediction_service
from app.services.feedback_service import feedback_service
from app.services.validation_service import validation_service
from app.models.classifier import classifier
from app.utils.logger import logger
from app.utils.metrics import metrics_collector
from app.config import settings

# Prometheus content type
CONTENT_TYPE_LATEST = "text/plain; version=0.0.4; charset=utf-8"

# Create router
router = APIRouter()


@router.post("/predict-text", 
            response_model=PredictionResponse,
            summary="Predict category for single text",
            description="Classify a single ticket text into a category")
async def predict_text(request: SingleTextRequest):
    """
    Predict category for a single ticket text
    
    - **text**: The ticket text to classify (10-1000 characters)
    
    Returns prediction with confidence score
    """
    start_time = time.time()
    
    try:
        # Get prediction
        result = await prediction_service.predict_single_text(request.text)
        
        # Record metrics
        duration = time.time() - start_time
        metrics_collector.record_request("POST", "/predict-text", 200, duration)
        metrics_collector.record_prediction(
            "single",
            result['confidence_score'],
            result.get('is_low_confidence', False)
        )
        
        return PredictionResponse(**result)
        
    except ValueError as e:
        logger.error(f"Validation error: {e}")
        metrics_collector.record_error("validation_error")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        metrics_collector.record_error("prediction_error")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/upload-csv",
            response_model=BulkPredictionResponse,
            summary="Bulk prediction from CSV",
            description="Upload CSV file with tickets for bulk classification")
async def upload_csv(file: UploadFile = File(...)):
    """
    Predict categories for multiple tickets from CSV
    
    - **file**: CSV file with 'ticket_text' or 'Ticket Description' column
    
    Returns predictions for all tickets
    """
    start_time = time.time()
    
    try:
        # Validate file
        validation_result = await validation_service.validate_csv_file(
            file,
            required_columns=[]  # Will check for ticket_text or Ticket Description in service
        )
        
        if not validation_result['valid']:
            raise HTTPException(status_code=400, detail=validation_result['errors'])
            
        # Get predictions
        result = await prediction_service.predict_bulk_csv(file)
        
        # Record metrics
        duration = time.time() - start_time
        metrics_collector.record_request("POST", "/upload-csv", 200, duration)
        
        for pred in result['predictions']:
            metrics_collector.record_prediction(
                "bulk",
                pred['confidence_score'],
                pred['confidence_score'] < settings.CONFIDENCE_THRESHOLD
            )
        
        return BulkPredictionResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Bulk prediction error: {e}")
        metrics_collector.record_error("bulk_prediction_error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/upload-with-categories",
            response_model=AdvancedModeResponse,
            summary="Advanced mode with custom categories",
            description="Upload tickets and custom category definitions")
async def upload_with_categories(
    tickets_file: UploadFile = File(..., description="CSV file with tickets"),
    categories_file: UploadFile = File(..., description="CSV file with category definitions")
):
    """
    Predict with custom category definitions (Advanced Mode)
    
    - **tickets_file**: CSV with 'ticket_text' or 'Ticket Description' column
    - **categories_file**: CSV with 'category_name' and 'category_description' columns
    
    Returns predictions using custom categories
    """
    start_time = time.time()
    
    try:
        # Validate categories file
        cat_validation = await validation_service.validate_csv_file(
            categories_file,
            required_columns=['category_name', 'category_description']
        )
        
        if not cat_validation['valid']:
            raise HTTPException(status_code=400, detail=f"Categories file: {cat_validation['errors']}")
            
        # Get predictions
        result = await prediction_service.predict_with_custom_categories(
            tickets_file,
            categories_file
        )
        
        # Record metrics
        duration = time.time() - start_time
        metrics_collector.record_request("POST", "/upload-with-categories", 200, duration)
        
        for pred in result['predictions']:
            metrics_collector.record_prediction(
                "advanced",
                pred['confidence_score'],
                pred['confidence_score'] < settings.CONFIDENCE_THRESHOLD
            )
        
        return AdvancedModeResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Advanced mode error: {e}")
        metrics_collector.record_error("advanced_mode_error")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/feedback",
            response_model=FeedbackResponse,
            summary="Submit feedback/correction",
            description="Submit user correction for a prediction")
async def submit_feedback(request: FeedbackRequest):
    """
    Submit feedback or correction for a prediction
    
    - **original_text**: The original ticket text
    - **predicted_category**: Model's prediction
    - **corrected_category**: User's correction
    - **confidence_score**: Original confidence score
    
    Stores correction as ground truth for retraining
    """
    start_time = time.time()
    
    try:
        # Save feedback
        result = feedback_service.save_feedback(request.dict())
        
        # Record metrics
        duration = time.time() - start_time
        metrics_collector.record_request("POST", "/feedback", 200, duration)
        metrics_collector.record_feedback(
            is_correction=(request.predicted_category != request.corrected_category)
        )
        
        return FeedbackResponse(**result)
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        metrics_collector.record_error("feedback_error")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health",
           response_model=HealthResponse,
           summary="Health check",
           description="Check API and model health status")
async def health_check():
    """
    Health check endpoint
    
    Returns service status and model information
    """
    try:
        model_info = classifier.get_model_info()
        
        return HealthResponse(
            status="healthy",
            version=settings.API_VERSION,
            model_loaded=model_info['is_loaded'],
            categories_loaded=len(model_info['category_names']) > 0
        )
        
    except Exception as e:
        logger.error(f"Health check error: {e}")
        return HealthResponse(
            status="unhealthy",
            version=settings.API_VERSION,
            model_loaded=False,
            categories_loaded=False
        )


@router.get("/metrics",
           summary="Prometheus metrics",
           description="Get Prometheus-format metrics")
async def get_metrics():
    """
    Get Prometheus metrics
    
    Returns metrics in Prometheus exposition format
    """
    try:
        metrics = metrics_collector.get_metrics()
        return Response(content=metrics, media_type=CONTENT_TYPE_LATEST)
    except Exception as e:
        logger.error(f"Metrics error: {e}")
        raise HTTPException(status_code=500, detail="Error generating metrics")


@router.get("/metrics/summary",
           response_model=MetricsResponse,
           summary="Metrics summary",
           description="Get metrics summary as JSON")
async def get_metrics_summary():
    """
    Get metrics summary
    
    Returns key metrics as JSON
    """
    try:
        # Get basic metrics
        summary = metrics_collector.get_metrics_summary()
        
        # Get feedback stats
        feedback_stats = feedback_service.get_feedback_stats()
        
        # Combine
        result = {
            'total_requests': summary.get('total_requests', 0),
            'total_predictions': summary.get('total_predictions', 0),
            'average_confidence': 0.85,  # Placeholder - would calculate from stored data
            'low_confidence_ratio': 0.1,  # Placeholder
            'feedback_count': feedback_stats.get('total_feedback', 0),
            'correction_rate': feedback_stats.get('correction_rate', 0.0),
            'uptime_seconds': summary.get('uptime_seconds', 0)
        }
        
        return MetricsResponse(**result)
        
    except Exception as e:
        logger.error(f"Metrics summary error: {e}")
        raise HTTPException(status_code=500, detail="Error generating metrics summary")

# Made with Bob

"""
API Request/Response Schemas
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Dict, Any
from datetime import datetime


# Request Schemas

class SingleTextRequest(BaseModel):
    """Request schema for single text prediction"""
    text: str = Field(..., min_length=10, max_length=1000, description="Ticket text to classify")
    
    @validator('text')
    def validate_text(cls, v):
        if not v.strip():
            raise ValueError("Text cannot be empty")
        return v.strip()


class FeedbackRequest(BaseModel):
    """Request schema for user feedback"""
    ticket_id: Optional[str] = Field(None, description="Ticket ID (if available)")
    original_text: str = Field(..., description="Original ticket text")
    predicted_category: str = Field(..., description="Model's predicted category")
    corrected_category: str = Field(..., description="User's corrected category")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Original confidence score")
    timestamp: Optional[datetime] = Field(default_factory=datetime.now)


# Response Schemas

class PredictionResponse(BaseModel):
    """Response schema for single prediction"""
    predicted_category: str = Field(..., description="Predicted category")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    all_scores: Optional[Dict[str, float]] = Field(None, description="Scores for all categories")
    processing_time_ms: float = Field(..., description="Processing time in milliseconds")


class BulkPredictionItem(BaseModel):
    """Single item in bulk prediction response"""
    row_index: int = Field(..., description="Row index in uploaded CSV")
    ticket_text: str = Field(..., description="Ticket text")
    predicted_category: str = Field(..., description="Predicted category")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")


class BulkPredictionResponse(BaseModel):
    """Response schema for bulk predictions"""
    predictions: List[BulkPredictionItem] = Field(..., description="List of predictions")
    total_processed: int = Field(..., description="Total number of tickets processed")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    low_confidence_count: int = Field(..., description="Number of low confidence predictions")


class AdvancedModeResponse(BaseModel):
    """Response schema for advanced mode (custom categories)"""
    predictions: List[BulkPredictionItem] = Field(..., description="List of predictions")
    total_processed: int = Field(..., description="Total number of tickets processed")
    num_categories: int = Field(..., description="Number of custom categories used")
    category_names: List[str] = Field(..., description="List of category names")
    processing_time_ms: float = Field(..., description="Total processing time in milliseconds")
    low_confidence_count: int = Field(..., description="Number of low confidence predictions")


class FeedbackResponse(BaseModel):
    """Response schema for feedback submission"""
    success: bool = Field(..., description="Whether feedback was saved successfully")
    message: str = Field(..., description="Response message")
    feedback_count: int = Field(..., description="Total feedback count")
    retraining_triggered: bool = Field(default=False, description="Whether retraining was triggered")


class HealthResponse(BaseModel):
    """Response schema for health check"""
    status: str = Field(..., description="Service status")
    version: str = Field(..., description="API version")
    model_loaded: bool = Field(..., description="Whether model is loaded")
    categories_loaded: bool = Field(..., description="Whether categories are loaded")
    timestamp: datetime = Field(default_factory=datetime.now)


class MetricsResponse(BaseModel):
    """Response schema for metrics"""
    total_requests: int = Field(..., description="Total number of requests")
    total_predictions: int = Field(..., description="Total number of predictions")
    average_confidence: float = Field(..., description="Average confidence score")
    low_confidence_ratio: float = Field(..., description="Ratio of low confidence predictions")
    feedback_count: int = Field(..., description="Total feedback count")
    correction_rate: float = Field(..., description="Correction rate")
    uptime_seconds: float = Field(..., description="Service uptime in seconds")


class ErrorResponse(BaseModel):
    """Response schema for errors"""
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")
    timestamp: datetime = Field(default_factory=datetime.now)


# CSV Upload Schemas

class CSVValidationResult(BaseModel):
    """Result of CSV validation"""
    valid: bool = Field(..., description="Whether CSV is valid")
    num_rows: int = Field(..., description="Number of rows")
    columns: List[str] = Field(..., description="Column names")
    errors: List[str] = Field(default_factory=list, description="Validation errors")


class CategoryDefinition(BaseModel):
    """Category definition from CSV"""
    category_id: Optional[int] = Field(None, description="Category ID")
    category_name: str = Field(..., description="Category name")
    category_description: str = Field(..., description="Category description")

# Made with Bob

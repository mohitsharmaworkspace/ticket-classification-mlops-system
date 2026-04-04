# Ticket Classification MLOps System - Architecture

## System Overview

This is an end-to-end MLOps system for ticket classification using NLP embeddings and similarity matching.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                           │
│                    (React Frontend - Port 3000)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌────────────────────┐   │
│  │ Single Text  │  │  Bulk CSV    │  │ CSV + Categories   │   │
│  │    Input     │  │   Upload     │  │   (Dynamic Mode)   │   │
│  └──────────────┘  └──────────────┘  └────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API Gateway Layer                           │
│                   (FastAPI - Port 8000)                          │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ Endpoints:                                                │  │
│  │ • POST /predict-text                                      │  │
│  │ • POST /upload-csv                                        │  │
│  │ • POST /upload-with-categories                            │  │
│  │ • POST /feedback                                          │  │
│  │ • GET /metrics (Prometheus)                               │  │
│  │ • GET /health                                             │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Model Service Layer                         │
│                   (Embedding-based Classifier)                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ • Sentence Transformers (all-MiniLM-L6-v2)               │  │
│  │ • Dynamic Category Embedding                              │  │
│  │ • Cosine Similarity Matching                              │  │
│  │ • Confidence Score Calculation                            │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Data Pipeline Layer                         │
│                    (Airflow - Port 8080)                         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ DAGs:                                                     │  │
│  │ • data_preprocessing_dag                                  │  │
│  │ • model_training_dag                                      │  │
│  │ • model_evaluation_dag                                    │  │
│  │ • drift_detection_dag                                     │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MLOps Infrastructure                          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │   MLflow     │  │     DVC      │  │   Prometheus +       │ │
│  │  (Port 5000) │  │ (Versioning) │  │   Grafana            │ │
│  │              │  │              │  │   (Port 9090, 3001)  │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Storage Layer                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐ │
│  │  Raw Data    │  │ Processed    │  │  Ground Truth        │ │
│  │              │  │    Data      │  │  (Feedback)          │ │
│  └──────────────┘  └──────────────┘  └──────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### 1. Frontend (React)
- **Port**: 3000
- **Features**:
  - Single text input with instant prediction
  - CSV bulk upload interface
  - Advanced mode: CSV + custom categories
  - Prediction results display with confidence scores
  - Feedback correction interface

### 2. Backend API (FastAPI)
- **Port**: 8000
- **Responsibilities**:
  - Request validation and preprocessing
  - Model inference orchestration
  - Feedback collection and storage
  - Metrics exposure for Prometheus
  - Health checks

### 3. Model Service
- **Technology**: Sentence Transformers
- **Model**: all-MiniLM-L6-v2
- **Features**:
  - Dynamic category embedding
  - Cosine similarity calculation
  - Confidence score generation
  - Support for custom categories

### 4. Data Pipeline (Airflow)
- **Port**: 8080
- **DAGs**:
  - Data preprocessing and validation
  - Model training and evaluation
  - Drift detection
  - Automated retraining triggers

### 5. Experiment Tracking (MLflow)
- **Port**: 5000
- **Tracks**:
  - Model parameters
  - Training metrics
  - Model artifacts
  - Model versioning

### 6. Data Versioning (DVC)
- **Features**:
  - Dataset versioning
  - Pipeline reproducibility
  - Experiment tracking
  - CI/CD integration

### 7. Monitoring (Prometheus + Grafana)
- **Prometheus Port**: 9090
- **Grafana Port**: 3001
- **Metrics**:
  - Request count and latency
  - Error rates
  - Model performance
  - Data drift indicators

## Data Flow

### Single Text Prediction
1. User enters text → Frontend
2. Frontend sends POST to `/predict-text`
3. Backend validates and preprocesses
4. Model generates embedding and finds best match
5. Returns prediction + confidence score
6. User can provide feedback

### Bulk CSV Upload
1. User uploads CSV → Frontend
2. Frontend sends POST to `/upload-csv`
3. Backend validates CSV schema
4. Processes each row through model
5. Returns predictions for all tickets
6. Allows batch feedback

### Dynamic Categories Mode
1. User uploads tickets CSV + categories CSV
2. Frontend sends POST to `/upload-with-categories`
3. Backend validates both files
4. Model generates embeddings for custom categories
5. Matches tickets against custom categories
6. Returns predictions with confidence scores

### Feedback Loop
1. User corrects prediction
2. POST to `/feedback` endpoint
3. Store corrected label as ground truth
4. Trigger drift detection
5. If correction rate > threshold → trigger retraining

## MLOps Workflow

### Training Pipeline
1. Load data from DVC
2. Preprocess and validate
3. Generate embeddings
4. Train/fine-tune model
5. Evaluate performance
6. Log to MLflow
7. Register best model
8. Version with DVC

### Monitoring & Retraining
1. Continuous monitoring of predictions
2. Calculate data drift metrics
3. Track correction rate
4. If drift detected or performance degrades:
   - Trigger Airflow retraining DAG
   - Load updated ground truth
   - Retrain model
   - Evaluate and deploy

## Technology Stack

- **Frontend**: React, Axios, Material-UI
- **Backend**: FastAPI, Pydantic, Python 3.9+
- **ML**: Sentence Transformers, scikit-learn, NumPy
- **Orchestration**: Apache Airflow
- **Tracking**: MLflow
- **Versioning**: DVC, Git
- **Monitoring**: Prometheus, Grafana
- **Containerization**: Docker, Docker Compose
- **Testing**: pytest, unittest

## Deployment Strategy

All services run in Docker containers orchestrated by Docker Compose:
- Isolated environments
- Easy scaling
- Reproducible deployments
- Local development parity

## Security Considerations

- Input validation on all endpoints
- Rate limiting
- Error handling without exposing internals
- Logging for audit trails
- No sensitive data in logs

## Scalability

- Stateless API design
- Horizontal scaling capability
- Async processing for bulk uploads
- Caching for frequently used categories
- Batch inference optimization
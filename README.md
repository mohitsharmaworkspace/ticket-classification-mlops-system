# Ticket Classification MLOps System

A complete end-to-end MLOps system for ticket classification using NLP embeddings and similarity matching.

## 🎯 Project Overview

This system classifies customer support tickets into categories using:
- **Sentence Transformers** for embedding generation
- **Cosine Similarity** for category matching
- **Multi-input support**: Single text, Bulk CSV, CSV + Custom Categories
- **Complete MLOps pipeline** with monitoring, versioning, and automated retraining

## 🏗️ Architecture

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   React     │────▶│   FastAPI   │────▶│   Model     │
│  Frontend   │     │   Backend   │     │  Service    │
│  (Port 3000)│     │  (Port 8000)│     │             │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
        ┌──────────────────┼──────────────────┐
        │                  │                  │
   ┌────▼────┐      ┌─────▼─────┐     ┌─────▼─────┐
   │ MLflow  │      │  Airflow  │     │Prometheus │
   │(Port    │      │  (Port    │     │ Grafana   │
   │ 5000)   │      │   8080)   │     │(9090,3001)│
   └─────────┘      └───────────┘     └───────────┘
```

## ✨ Features

### Multi-Input System
1. **Single Text Input**: Instant prediction for one ticket
2. **Bulk CSV Upload**: Process multiple tickets at once
3. **Advanced Mode**: Upload tickets + custom category definitions

### MLOps Components
- ✅ Data versioning with DVC
- ✅ Experiment tracking with MLflow
- ✅ Pipeline orchestration with Airflow
- ✅ Monitoring with Prometheus + Grafana
- ✅ Automated retraining on drift detection
- ✅ Feedback loop for continuous improvement
- ✅ Docker containerization

## 📁 Project Structure

```
ticket-classification-mlops-system/
├── data/                          # Data storage
│   ├── raw/                       # Raw datasets
│   ├── processed/                 # Processed data
│   ├── ground_truth/              # User corrections
│   └── drift_baseline/            # Drift detection baselines
├── models/                        # Model artifacts
│   ├── embeddings/                # Category embeddings
│   └── trained/                   # Trained models
├── backend/                       # FastAPI backend
│   ├── app/
│   │   ├── api/                   # API routes & schemas
│   │   ├── services/              # Business logic
│   │   ├── models/                # ML model wrapper
│   │   └── utils/                 # Utilities
│   └── tests/                     # Backend tests
├── frontend/                      # React frontend
│   └── src/
│       ├── components/            # UI components
│       └── services/              # API client
├── ml_pipeline/                   # ML pipeline modules
│   ├── data_preprocessing.py      # Data cleaning
│   ├── feature_engineering.py     # Embedding generation
│   ├── model_training.py          # Training logic
│   ├── model_evaluation.py        # Evaluation metrics
│   └── drift_detection.py         # Drift detection
├── airflow/                       # Airflow DAGs
│   └── dags/                      # Pipeline definitions
├── monitoring/                    # Monitoring setup
│   ├── prometheus/                # Metrics collection
│   └── grafana/                   # Dashboards
├── docs/                          # Documentation
├── tests/                         # Integration tests
├── docker-compose.yml             # Multi-container orchestration
├── dvc.yaml                       # DVC pipeline
└── params.yaml                    # Configuration
```

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Python 3.9+
- Node.js 16+ (for frontend)
- Git

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd ticket-classification-mlops-system
```

2. **Initialize DVC**
```bash
dvc init
dvc remote add -d local /tmp/dvc-storage
```

3. **Build and start all services**
```bash
docker-compose up --build
```

4. **Access the services**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- MLflow: http://localhost:5000
- Airflow: http://localhost:8080
- Grafana: http://localhost:3001

## 📊 API Endpoints

### Prediction Endpoints

#### Single Text Prediction
```bash
POST /predict-text
Content-Type: application/json

{
  "text": "My laptop is not turning on"
}

Response:
{
  "predicted_category": "Technical Issue",
  "confidence_score": 0.92,
  "processing_time_ms": 45.2
}
```

#### Bulk CSV Upload
```bash
POST /upload-csv
Content-Type: multipart/form-data

file: tickets.csv (with columns: ticket_id, ticket_text)

Response:
{
  "predictions": [...],
  "total_processed": 100,
  "processing_time_ms": 1250.5,
  "low_confidence_count": 5
}
```

#### Advanced Mode (Custom Categories)
```bash
POST /upload-with-categories
Content-Type: multipart/form-data

tickets_file: tickets.csv
categories_file: categories.csv

Response:
{
  "predictions": [...],
  "total_processed": 100,
  "num_categories": 8,
  "category_names": ["Bug", "Feature Request", ...],
  "processing_time_ms": 1450.8
}
```

#### Submit Feedback
```bash
POST /feedback
Content-Type: application/json

{
  "original_text": "Cannot login to account",
  "predicted_category": "Technical Issue",
  "corrected_category": "Account Access",
  "confidence_score": 0.75
}

Response:
{
  "success": true,
  "message": "Feedback saved successfully",
  "feedback_count": 42,
  "retraining_triggered": false
}
```

### Monitoring Endpoints

#### Health Check
```bash
GET /health

Response:
{
  "status": "healthy",
  "version": "1.0.0",
  "model_loaded": true,
  "categories_loaded": true
}
```

#### Metrics (Prometheus format)
```bash
GET /metrics
```

## 🔄 MLOps Workflow

### 1. Data Pipeline
```
Raw Data → Validation → Cleaning → Feature Engineering → Embeddings
```

### 2. Training Pipeline
```
Load Data → Preprocess → Generate Embeddings → Train → Evaluate → Register Model
```

### 3. Inference Pipeline
```
Input → Preprocess → Generate Embedding → Similarity Match → Return Prediction
```

### 4. Feedback Loop
```
User Correction → Store Ground Truth → Check Drift → Trigger Retraining (if needed)
```

### 5. Monitoring
```
Collect Metrics → Detect Drift → Alert → Trigger Retraining
```

## 📈 Monitoring & Alerting

### Prometheus Metrics
- `api_requests_total`: Total API requests
- `prediction_latency_seconds`: Prediction latency
- `confidence_score`: Confidence score distribution
- `low_confidence_predictions`: Low confidence count
- `feedback_corrections_total`: Total corrections

### Grafana Dashboards
- API Performance Dashboard
- Model Performance Dashboard
- Data Drift Dashboard
- System Health Dashboard

### Alerts
- Error rate > 5%
- Latency > 500ms
- Data drift detected
- Low confidence ratio > 30%

## 🔧 Configuration

### params.yaml
Main configuration file for:
- Model parameters
- Data paths
- Training settings
- Drift detection thresholds
- Retraining triggers

### Environment Variables
Create `.env` file:
```bash
# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Model Settings
MODEL_NAME=all-MiniLM-L6-v2
CONFIDENCE_THRESHOLD=0.7

# MLflow
MLFLOW_TRACKING_URI=http://mlflow:5000

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3001
```

## 🧪 Testing

### Run Unit Tests
```bash
# Backend tests
cd backend
pytest tests/ -v

# ML Pipeline tests
pytest ml_pipeline/tests/ -v
```

### Run Integration Tests
```bash
pytest tests/integration/ -v
```

### Run Load Tests
```bash
pytest tests/performance/ -v
```

## 📚 Documentation

- [Architecture Documentation](ARCHITECTURE.md)
- [API Documentation](docs/API_DOCUMENTATION.md)
- [User Manual](docs/USER_MANUAL.md)
- [Deployment Guide](docs/DEPLOYMENT_GUIDE.md)
- [MLOps Workflow](docs/MLOPS_WORKFLOW.md)

## 🔐 Security

- Input validation on all endpoints
- Rate limiting (100 requests/minute)
- File size limits (10MB max)
- CORS configuration
- No sensitive data in logs

## 🎯 Performance

- **Latency**: < 200ms for single prediction
- **Throughput**: 100+ predictions/second
- **Accuracy**: > 85% (configurable threshold)
- **F1 Score**: > 0.80

## 🔄 Retraining Triggers

Automatic retraining is triggered when:
1. **Data Drift Detected**: Statistical tests show distribution shift
2. **High Correction Rate**: > 15% of predictions corrected by users
3. **Performance Degradation**: Accuracy drops > 10%
4. **Minimum Samples**: At least 50 new ground truth samples

## 📦 Dependencies

### Core ML/NLP
- sentence-transformers==2.2.2
- scikit-learn==1.3.0
- torch==2.0.1

### MLOps Tools
- mlflow==2.7.1
- dvc==3.20.0
- apache-airflow==2.7.1

### Backend
- fastapi==0.104.1
- uvicorn==0.24.0

### Monitoring
- prometheus-client==0.17.1

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📝 License

MIT License

## 👥 Authors

- Your Name

## 🙏 Acknowledgments

- Sentence Transformers library
- FastAPI framework
- MLflow project
- DVC team

## 📞 Support

For issues and questions:
- GitHub Issues: [link]
- Email: support@example.com
- Documentation: [link]

---

**Built with ❤️ using MLOps best practices**
# Setup Guide - Ticket Classification MLOps System

## Prerequisites

- Python 3.8 or higher
- Node.js 14 or higher
- Git
- 8GB RAM minimum (for ML models)

## Quick Start

### 1. Install Python Dependencies

```bash
# Create virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install all Python dependencies
pip install -r requirements.txt
```

### 2. Install Frontend Dependencies

```bash
cd frontend
npm install
cd ..
```

### 3. Initialize Data Versioning

```bash
# Initialize DVC
dvc init

# Add data files to DVC tracking
dvc add data/raw/customer_support_tickets.csv
dvc add data/raw/default_categories.csv

# Commit DVC files
git add data/.gitignore data/raw/*.dvc .dvc/config
git commit -m "Initialize DVC tracking"
```

### 4. Start the Backend Service

```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at: http://localhost:8000

API Documentation: http://localhost:8000/docs

### 5. Start the Frontend (in a new terminal)

```bash
cd frontend
npm start
```

The frontend will be available at: http://localhost:3000

## Troubleshooting

### Issue: "python: command not found"

**Solution**: Use `python3` instead of `python`

```bash
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue: "ModuleNotFoundError: No module named 'fastapi'"

**Solution**: Install dependencies in a virtual environment

```bash
# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Issue: Import errors in backend

**Solution**: Make sure you're running from the backend directory

```bash
cd backend
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Issue: "Port already in use"

**Solution**: Kill the process using the port or use a different port

```bash
# Find process using port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Issue: Model download fails

**Solution**: The first run will download the sentence-transformers model (~80MB). Ensure you have:
- Stable internet connection
- Sufficient disk space
- No firewall blocking huggingface.co

### Issue: Frontend can't connect to backend

**Solution**: Check CORS settings and backend URL

1. Verify backend is running: http://localhost:8000/health
2. Check frontend API configuration in `frontend/src/services/api.js`
3. Ensure CORS is enabled in backend (already configured)

## Running with Docker (Coming Soon)

Docker setup will be available in the next phase. For now, use the manual setup above.

## System Architecture

```
┌─────────────────┐
│  React Frontend │ (Port 3000)
│  (3 Input Modes)│
└────────┬────────┘
         │ HTTP/REST
         ▼
┌─────────────────┐
│  FastAPI Backend│ (Port 8000)
│  (7 Endpoints)  │
└────────┬────────┘
         │
    ┌────┴────┬──────────┬──────────┐
    ▼         ▼          ▼          ▼
┌────────┐ ┌──────┐ ┌────────┐ ┌──────────┐
│ Model  │ │MLflow│ │Feedback│ │Prometheus│
│Service │ │      │ │ Loop   │ │ Metrics  │
└────────┘ └──────┘ └────────┘ └──────────┘
```

## API Endpoints

1. **POST /predict-text** - Single ticket prediction
2. **POST /upload-csv** - Bulk ticket prediction
3. **POST /upload-with-categories** - Tickets + custom categories
4. **POST /feedback** - Submit user corrections
5. **GET /health** - Health check
6. **GET /metrics** - Prometheus metrics
7. **GET /categories** - List available categories

## Testing the System

### Test Single Prediction

```bash
curl -X POST "http://localhost:8000/predict-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "My laptop screen is not working"}'
```

### Test Health Check

```bash
curl http://localhost:8000/health
```

### Test Frontend

1. Open http://localhost:3000
2. Try each of the 3 input modes:
   - Single Text Input
   - Bulk CSV Upload
   - Advanced Mode (CSV + Categories)

## Next Steps

After basic setup:

1. **Configure MLflow**: Set up experiment tracking
2. **Set up Airflow**: Configure retraining pipeline
3. **Deploy Monitoring**: Set up Prometheus + Grafana
4. **Containerize**: Create Docker containers
5. **Run Tests**: Execute test suite

## Support

For issues or questions:
1. Check this troubleshooting guide
2. Review logs in `logs/` directory
3. Check API documentation at http://localhost:8000/docs
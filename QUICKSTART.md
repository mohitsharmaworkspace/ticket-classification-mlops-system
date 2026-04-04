# Quick Start Guide - Ticket Classification MLOps System

## ✅ System Status

**Backend Service**: ✅ Running on http://localhost:8000
**API Documentation**: ✅ Available at http://localhost:8000/docs
**Model**: ✅ Loaded (all-MiniLM-L6-v2)
**Categories**: ✅ Loaded from default_categories.csv

---

## 🚀 Getting Started (5 Minutes)

### Step 1: Verify Backend is Running

The backend should already be running. Check the terminal output for:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

If not running, start it:
```bash
cd backend
source ../venv/bin/activate
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Step 2: Test the API

Open your browser and visit:
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

Or use curl:
```bash
# Health check
curl http://localhost:8000/health

# Single prediction
curl -X POST "http://localhost:8000/predict-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "My laptop screen is broken and not displaying anything"}'

# Get available categories
curl http://localhost:8000/categories
```

### Step 3: Start the Frontend (Optional)

In a new terminal:
```bash
cd frontend
npm install  # First time only
npm start
```

The frontend will open at http://localhost:3000

---

## 📋 Available API Endpoints

### 1. Single Text Prediction
**POST** `/predict-text`

```bash
curl -X POST "http://localhost:8000/predict-text" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "My laptop screen is not working"
  }'
```

**Response:**
```json
{
  "ticket_id": "auto-generated-uuid",
  "predicted_category": "Hardware Issue",
  "confidence": 0.89,
  "all_scores": {
    "Hardware Issue": 0.89,
    "Software Bug": 0.45,
    "Network Problem": 0.23
  }
}
```

### 2. Bulk CSV Upload
**POST** `/upload-csv`

```bash
curl -X POST "http://localhost:8000/upload-csv" \
  -F "file=@tickets.csv"
```

**CSV Format:**
```csv
ticket_id,description
T001,My laptop won't turn on
T002,Cannot connect to WiFi
T003,Application crashes on startup
```

### 3. Advanced Mode (Custom Categories)
**POST** `/upload-with-categories`

```bash
curl -X POST "http://localhost:8000/upload-with-categories" \
  -F "tickets_file=@tickets.csv" \
  -F "categories_file=@custom_categories.csv"
```

**Categories CSV Format:**
```csv
category_name,description
Critical Bug,System crashes or data loss
Minor Bug,UI glitches or cosmetic issues
Feature Request,New functionality requests
```

### 4. Submit Feedback
**POST** `/feedback`

```bash
curl -X POST "http://localhost:8000/feedback" \
  -H "Content-Type: application/json" \
  -d '{
    "ticket_id": "T001",
    "text": "My laptop won't turn on",
    "predicted_category": "Software Bug",
    "correct_category": "Hardware Issue"
  }'
```

### 5. Get Metrics
**GET** `/metrics`

```bash
curl http://localhost:8000/metrics
```

Returns Prometheus-format metrics for monitoring.

### 6. List Categories
**GET** `/categories`

```bash
curl http://localhost:8000/categories
```

---

## 🎯 Testing the Three Input Modes

### Mode 1: Single Text Input

**Via API:**
```bash
curl -X POST "http://localhost:8000/predict-text" \
  -H "Content-Type: application/json" \
  -d '{"text": "Cannot access my email account"}'
```

**Via Frontend:**
1. Go to http://localhost:3000
2. Select "Single Text Input" tab
3. Enter ticket description
4. Click "Classify"

### Mode 2: Bulk CSV Upload

**Create a test file** (`test_tickets.csv`):
```csv
ticket_id,description
T001,My computer won't start
T002,WiFi keeps disconnecting
T003,Software crashes when I open it
T004,Need help resetting my password
T005,Printer is not working
```

**Upload via API:**
```bash
curl -X POST "http://localhost:8000/upload-csv" \
  -F "file=@test_tickets.csv"
```

**Upload via Frontend:**
1. Go to "Bulk CSV Upload" tab
2. Click "Choose File" and select your CSV
3. Click "Upload and Classify"

### Mode 3: Advanced Mode (Custom Categories)

**Create tickets file** (`tickets.csv`):
```csv
ticket_id,description
T001,System crashed and lost all data
T002,Button color is slightly off
T003,Would like dark mode feature
```

**Create categories file** (`categories.csv`):
```csv
category_name,description
Critical Bug,System crashes or data loss issues
Minor Bug,UI glitches or cosmetic issues  
Feature Request,New functionality requests
```

**Upload via API:**
```bash
curl -X POST "http://localhost:8000/upload-with-categories" \
  -F "tickets_file=@tickets.csv" \
  -F "categories_file=@categories.csv"
```

**Upload via Frontend:**
1. Go to "Advanced Mode" tab
2. Upload tickets CSV
3. Upload categories CSV
4. Click "Classify with Custom Categories"

---

## 📊 Default Categories

The system comes with these pre-configured categories:

1. **Hardware Issue** - Physical device problems
2. **Software Bug** - Application errors and crashes
3. **Network Problem** - Connectivity issues
4. **Account Access** - Login and authentication
5. **Performance Issue** - Slow or unresponsive systems
6. **Data Loss** - Missing or corrupted data
7. **Feature Request** - New functionality requests
8. **Configuration** - Settings and setup issues

---

## 🔍 Monitoring & Metrics

### View Metrics
```bash
curl http://localhost:8000/metrics
```

**Key Metrics:**
- `ticket_classification_requests_total` - Total requests
- `ticket_classification_request_duration_seconds` - Latency
- `ticket_classification_errors_total` - Error count
- `ticket_classification_confidence_score` - Prediction confidence
- `model_load_time_seconds` - Model initialization time

### Health Check
```bash
curl http://localhost:8000/health
```

Returns system status and uptime.

---

## 🐛 Troubleshooting

### Backend won't start

**Error: "ModuleNotFoundError"**
```bash
# Make sure you're in the backend directory
cd backend

# Activate virtual environment
source ../venv/bin/activate

# Run from backend directory
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8000
```

### Port already in use

```bash
# Find and kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use a different port
python3 -m uvicorn app.main:app --host 0.0.0.0 --port 8001
```

### Model download fails

The first run downloads the sentence-transformers model (~80MB). Ensure:
- Stable internet connection
- Sufficient disk space
- No firewall blocking huggingface.co

### Frontend can't connect to backend

1. Verify backend is running: http://localhost:8000/health
2. Check CORS settings (already configured)
3. Verify API URL in `frontend/src/services/api.js`

---

## 📁 Project Structure

```
ticket-classification-mlops-system/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── api/         # API routes and schemas
│   │   ├── models/      # ML model wrapper
│   │   ├── services/    # Business logic
│   │   └── utils/       # Utilities
│   └── run.sh
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/  # UI components
│   │   └── services/    # API client
│   └── package.json
├── ml_pipeline/         # ML training pipeline
├── data/               # Data storage
│   ├── raw/            # Original data
│   ├── processed/      # Processed data
│   └── ground_truth/   # Feedback data
└── models/             # Trained models
```

---

## 🎓 Next Steps

1. **Explore the API**: Visit http://localhost:8000/docs
2. **Test all three modes**: Try single, bulk, and advanced inputs
3. **Submit feedback**: Use the feedback endpoint to improve the model
4. **Monitor metrics**: Check /metrics endpoint
5. **Review logs**: Check `logs/` directory for detailed logs

---

## 📚 Additional Resources

- **API Documentation**: http://localhost:8000/docs
- **Setup Guide**: See `SETUP_GUIDE.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Development Status**: See `DEVELOPMENT_STATUS.md`

---

## 🆘 Need Help?

1. Check the logs in `logs/` directory
2. Review `SETUP_GUIDE.md` for detailed setup
3. Verify all dependencies are installed: `pip list`
4. Ensure you're using Python 3.8+

---

**System is ready! Start classifying tickets! 🎉**
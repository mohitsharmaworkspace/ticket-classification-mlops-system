# Codebase Creation Hierarchy - Build Order

This document shows the exact order in which files/folders should be created from scratch.

## Level 1: Project Root & Core Configuration

```
1. Create project directory
   └── ticket-classification-mlops-system/

2. Initialize Git
   └── .git/

3. Core configuration files (in order)
   ├── .gitignore                    # First - defines what not to track
   ├── .dvcignore                    # Second - DVC ignore patterns
   ├── README.md                     # Third - project overview
   ├── requirements.txt              # Fourth - Python dependencies
   ├── params.yaml                   # Fifth - ML pipeline parameters
   ├── .env.example                  # Sixth - environment template
   └── package-lock.json             # Seventh - if using npm
```

## Level 2: Directory Structure (Empty Folders)

```
4. Create data directories
   data/
   ├── raw/
   │   └── .gitkeep
   ├── processed/
   │   └── .gitkeep
   ├── ground_truth/
   │   └── .gitkeep
   └── drift_baseline/
       └── .gitkeep

5. Create models directories
   models/
   ├── embeddings/
   │   └── .gitkeep
   └── trained/
       └── .gitkeep

6. Create logs directory
   logs/
   └── .gitkeep

7. Create MLflow directory
   mlflow/
   └── .gitkeep

8. Create monitoring directories
   monitoring/
   ├── prometheus/
   │   └── .gitkeep
   └── grafana/
       ├── provisioning/
       │   ├── dashboards/
       │   │   └── .gitkeep
       │   └── datasources/
       │       └── .gitkeep
       └── dashboards/
           └── .gitkeep

9. Create Airflow directories
   airflow/
   ├── dags/
   │   └── .gitkeep
   ├── plugins/
   │   └── .gitkeep
   ├── config/
   │   └── .gitkeep
   └── logs/
       └── .gitkeep

10. Create test directories
    tests/
    ├── integration/
    │   └── .gitkeep
    └── performance/
        └── .gitkeep

11. Create scripts directory
    scripts/
    └── .gitkeep

12. Create notebooks directory
    notebooks/
    └── .gitkeep

13. Create docs directory
    docs/
    └── .gitkeep
```

## Level 3: ML Pipeline Core (Foundation)

```
14. ml_pipeline/ package
    ml_pipeline/
    ├── __init__.py                  # First - makes it a package
    ├── config.py                    # Second - configuration management
    ├── utils.py                     # Third - utility functions
    ├── data_preprocessing.py        # Fourth - data processing
    ├── feature_engineering.py       # Fifth - feature generation
    ├── model_evaluation.py          # Sixth - evaluation metrics
    ├── drift_detection.py           # Seventh - drift monitoring
    └── model_training.py            # Eighth - training pipeline

15. ml_pipeline/models/ subpackage
    ml_pipeline/models/
    ├── __init__.py                  # First
    ├── mlp_classifier.py            # Second - model architecture
    ├── trainer.py                   # Third - training logic
    └── predictor.py                 # Fourth - inference logic
```

## Level 4: Backend API (Service Layer)

```
16. backend/ package structure
    backend/
    ├── requirements.txt             # First - backend dependencies
    ├── .env.example                 # Second - backend env template
    ├── run.sh                       # Third - startup script
    └── tests/                       # Fourth - test directory
        └── .gitkeep

17. backend/app/ core
    backend/app/
    ├── __init__.py                  # First - package init
    ├── config.py                    # Second - backend config
    └── main.py                      # Third - FastAPI application

18. backend/app/utils/
    backend/app/utils/
    ├── __init__.py                  # First
    ├── logger.py                    # Second - logging setup
    ├── metrics.py                   # Third - Prometheus metrics
    └── preprocessing.py             # Fourth - text preprocessing

19. backend/app/models/
    backend/app/models/
    ├── __init__.py                  # First
    └── classifier.py                # Second - classifier wrapper

20. backend/app/api/
    backend/app/api/
    ├── __init__.py                  # First
    ├── schemas.py                   # Second - Pydantic models
    └── routes.py                    # Third - API endpoints

21. backend/app/services/
    backend/app/services/
    ├── __init__.py                  # First
    ├── validation_service.py        # Second - input validation
    ├── prediction_service.py        # Third - prediction logic
    ├── feedback_service.py          # Fourth - feedback handling
    └── training_service.py          # Fifth - training orchestration
```

## Level 5: Frontend Application

```
22. frontend/ React app
    frontend/
    ├── package.json                 # First - npm dependencies
    ├── package-lock.json            # Second - lock file
    └── public/
        └── index.html               # Third - HTML template

23. frontend/src/ core
    frontend/src/
    ├── index.js                     # First - entry point
    ├── index.css                    # Second - global styles
    ├── App.js                       # Third - main component
    └── App.css                      # Fourth - app styles

24. frontend/src/services/
    frontend/src/services/
    └── api.js                       # First - API client

25. frontend/src/components/
    frontend/src/components/
    ├── SingleTextInput.js           # First - single text mode
    ├── BulkCSVUpload.js            # Second - bulk upload mode
    ├── AdvancedMode.js             # Third - advanced mode
    └── PredictionResults.js        # Fourth - results display

26. frontend/src/utils/
    frontend/src/utils/
    └── .gitkeep                     # Placeholder for future utils
```

## Level 6: Data Files (Seed Data)

```
27. Add seed data
    data/raw/
    ├── customer_support_tickets.csv # First - training data
    └── default_categories.csv       # Second - category definitions
```

## Level 7: Scripts & Utilities

```
28. scripts/
    └── train_initial_model.py       # Training script
```

## Level 8: Documentation

```
29. Documentation files (in order)
    ├── ARCHITECTURE.md              # First - system architecture
    ├── PROJECT_STRUCTURE.md         # Second - project layout
    ├── SETUP_GUIDE.md              # Third - setup instructions
    ├── QUICKSTART.md               # Fourth - quick start guide
    ├── DEVELOPMENT_STATUS.md       # Fifth - development status
    ├── PROJECT_DEEP_DIVE.md        # Sixth - detailed explanation
    ├── PRIORITY1_COMPLETE.md       # Seventh - milestone tracking
    ├── MLP_TRAINING_GUIDE.md       # Eighth - training guide
    └── MLOPS_INTEGRATION_READY.md  # Ninth - integration readiness
```

## Dependency Graph (What Depends on What)

```
Level 1: Configuration
    ├── params.yaml
    ├── .env.example
    └── requirements.txt

Level 2: Core Utilities (depends on Level 1)
    ├── ml_pipeline/config.py        → params.yaml
    ├── ml_pipeline/utils.py         → config.py
    └── backend/app/config.py        → .env

Level 3: Data Processing (depends on Level 2)
    ├── ml_pipeline/data_preprocessing.py → config.py, utils.py
    └── backend/app/utils/preprocessing.py → config.py

Level 4: Models (depends on Level 3)
    ├── ml_pipeline/models/mlp_classifier.py → (standalone)
    ├── ml_pipeline/models/trainer.py        → mlp_classifier.py, config.py
    └── ml_pipeline/models/predictor.py      → mlp_classifier.py, trainer.py

Level 5: ML Pipeline (depends on Level 4)
    ├── ml_pipeline/feature_engineering.py → config.py, utils.py
    ├── ml_pipeline/model_evaluation.py    → config.py
    ├── ml_pipeline/drift_detection.py     → config.py, utils.py
    └── ml_pipeline/model_training.py      → all above

Level 6: Backend Models (depends on Level 4)
    └── backend/app/models/classifier.py → config.py, ml_pipeline/models/

Level 7: Backend Services (depends on Level 6)
    ├── backend/app/services/validation_service.py → config.py
    ├── backend/app/services/prediction_service.py → classifier.py
    ├── backend/app/services/feedback_service.py   → config.py
    └── backend/app/services/training_service.py   → ml_pipeline/model_training.py

Level 8: Backend API (depends on Level 7)
    ├── backend/app/api/schemas.py → (standalone)
    ├── backend/app/api/routes.py  → services/, schemas.py
    └── backend/app/main.py        → routes.py, config.py

Level 9: Frontend (depends on Level 8 - API)
    ├── frontend/src/services/api.js → backend API
    ├── frontend/src/components/     → api.js
    └── frontend/src/App.js          → components/

Level 10: Scripts (depends on Level 5)
    └── scripts/train_initial_model.py → ml_pipeline/model_training.py
```

## Critical Path (Minimum Viable Product)

If building from scratch, this is the minimum order:

```
1. params.yaml
2. requirements.txt
3. ml_pipeline/__init__.py
4. ml_pipeline/config.py
5. ml_pipeline/utils.py
6. ml_pipeline/data_preprocessing.py
7. ml_pipeline/models/__init__.py
8. ml_pipeline/models/mlp_classifier.py
9. ml_pipeline/models/trainer.py
10. ml_pipeline/models/predictor.py
11. ml_pipeline/model_training.py
12. backend/app/__init__.py
13. backend/app/config.py
14. backend/app/utils/logger.py
15. backend/app/models/classifier.py
16. backend/app/services/prediction_service.py
17. backend/app/api/schemas.py
18. backend/app/api/routes.py
19. backend/app/main.py
20. scripts/train_initial_model.py
```

## Build Commands (In Order)

```bash
# 1. Create project structure
mkdir -p ticket-classification-mlops-system
cd ticket-classification-mlops-system

# 2. Initialize Git
git init

# 3. Create all directories
mkdir -p data/{raw,processed,ground_truth,drift_baseline}
mkdir -p models/{embeddings,trained}
mkdir -p logs mlflow
mkdir -p monitoring/{prometheus,grafana/provisioning/{dashboards,datasources}}
mkdir -p airflow/{dags,plugins,config,logs}
mkdir -p tests/{integration,performance}
mkdir -p scripts notebooks docs

# 4. Create ML pipeline structure
mkdir -p ml_pipeline/models
touch ml_pipeline/__init__.py
touch ml_pipeline/models/__init__.py

# 5. Create backend structure
mkdir -p backend/app/{api,models,services,utils}
touch backend/app/__init__.py
touch backend/app/api/__init__.py
touch backend/app/models/__init__.py
touch backend/app/services/__init__.py
touch backend/app/utils/__init__.py

# 6. Create frontend structure
mkdir -p frontend/src/{components,services,utils}
mkdir -p frontend/public

# 7. Create configuration files
touch .gitignore .dvcignore README.md
touch requirements.txt params.yaml .env.example
touch backend/requirements.txt backend/.env.example

# 8. Install dependencies
pip install -r requirements.txt
cd backend && pip install -r requirements.txt
cd ../frontend && npm install
```

## File Creation Order Summary

**Total Files: ~60+**

1. Configuration (5 files)
2. Directory Structure (30+ folders)
3. ML Pipeline (12 files)
4. Backend (15 files)
5. Frontend (10 files)
6. Data (2 files)
7. Scripts (1 file)
8. Documentation (9 files)

This hierarchy ensures no import errors and proper dependency resolution!
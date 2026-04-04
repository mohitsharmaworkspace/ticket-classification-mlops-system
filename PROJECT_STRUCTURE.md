# Project Structure

```
ticket-classification-mlops-system/
├── README.md
├── ARCHITECTURE.md
├── PROJECT_STRUCTURE.md
├── .gitignore
├── .dvcignore
├── docker-compose.yml
├── requirements.txt
│
├── data/
│   ├── raw/
│   │   ├── customer_support_tickets.csv
│   │   └── default_categories.csv
│   ├── processed/
│   │   └── .gitkeep
│   ├── ground_truth/
│   │   └── .gitkeep
│   └── drift_baseline/
│       └── .gitkeep
│
├── models/
│   ├── embeddings/
│   │   └── .gitkeep
│   └── trained/
│       └── .gitkeep
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py
│   │   │   ├── schemas.py
│   │   │   └── dependencies.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── prediction_service.py
│   │   │   ├── feedback_service.py
│   │   │   └── validation_service.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── classifier.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── logger.py
│   │       ├── metrics.py
│   │       └── preprocessing.py
│   └── tests/
│       ├── __init__.py
│       ├── test_api.py
│       ├── test_services.py
│       └── test_models.py
│
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   ├── package-lock.json
│   ├── public/
│   │   ├── index.html
│   │   └── favicon.ico
│   └── src/
│       ├── App.js
│       ├── App.css
│       ├── index.js
│       ├── index.css
│       ├── components/
│       │   ├── SingleTextInput.js
│       │   ├── BulkCSVUpload.js
│       │   ├── AdvancedMode.js
│       │   ├── PredictionResults.js
│       │   └── FeedbackForm.js
│       ├── services/
│       │   └── api.js
│       └── utils/
│           └── helpers.js
│
├── ml_pipeline/
│   ├── __init__.py
│   ├── config.py
│   ├── data_preprocessing.py
│   ├── feature_engineering.py
│   ├── model_training.py
│   ├── model_evaluation.py
│   ├── drift_detection.py
│   └── utils.py
│
├── airflow/
│   ├── Dockerfile
│   ├── dags/
│   │   ├── __init__.py
│   │   ├── data_preprocessing_dag.py
│   │   ├── model_training_dag.py
│   │   ├── drift_detection_dag.py
│   │   └── retraining_dag.py
│   ├── plugins/
│   │   └── __init__.py
│   └── config/
│       └── airflow.cfg
│
├── mlflow/
│   ├── Dockerfile
│   └── mlruns/
│       └── .gitkeep
│
├── monitoring/
│   ├── prometheus/
│   │   ├── Dockerfile
│   │   └── prometheus.yml
│   └── grafana/
│       ├── Dockerfile
│       ├── provisioning/
│       │   ├── dashboards/
│       │   │   ├── dashboard.yml
│       │   │   └── ticket_classification_dashboard.json
│       │   └── datasources/
│       │       └── datasource.yml
│       └── grafana.ini
│
├── scripts/
│   ├── init_dvc.sh
│   ├── setup_environment.sh
│   ├── run_tests.sh
│   └── deploy.sh
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_model_experimentation.ipynb
│   └── 03_drift_analysis.ipynb
│
├── docs/
│   ├── API_DOCUMENTATION.md
│   ├── USER_MANUAL.md
│   ├── DEPLOYMENT_GUIDE.md
│   └── MLOPS_WORKFLOW.md
│
├── tests/
│   ├── integration/
│   │   ├── __init__.py
│   │   └── test_end_to_end.py
│   └── performance/
│       ├── __init__.py
│       └── test_load.py
│
├── dvc.yaml
├── dvc.lock
├── params.yaml
└── .github/
    └── workflows/
        └── ci.yml
```

## Directory Descriptions

### Root Level
- **README.md**: Project overview and setup instructions
- **ARCHITECTURE.md**: System architecture documentation
- **docker-compose.yml**: Multi-container orchestration
- **requirements.txt**: Python dependencies
- **dvc.yaml**: DVC pipeline configuration
- **params.yaml**: Hyperparameters and configuration

### data/
- **raw/**: Original datasets
- **processed/**: Cleaned and preprocessed data
- **ground_truth/**: User-corrected labels (feedback)
- **drift_baseline/**: Statistical baselines for drift detection

### models/
- **embeddings/**: Pre-computed embeddings
- **trained/**: Trained model artifacts

### backend/
- **app/**: FastAPI application
  - **api/**: API routes and schemas
  - **services/**: Business logic
  - **models/**: ML model wrapper
  - **utils/**: Helper functions
- **tests/**: Unit tests

### frontend/
- **src/**: React application source
  - **components/**: UI components for 3 input modes
  - **services/**: API client
  - **utils/**: Helper functions

### ml_pipeline/
- Data preprocessing scripts
- Feature engineering
- Model training and evaluation
- Drift detection logic

### airflow/
- **dags/**: Airflow DAG definitions
- **plugins/**: Custom operators
- **config/**: Airflow configuration

### mlflow/
- MLflow tracking server setup
- **mlruns/**: Experiment tracking data

### monitoring/
- **prometheus/**: Metrics collection
- **grafana/**: Visualization dashboards

### scripts/
- Setup and deployment scripts
- Testing scripts
- Utility scripts

### notebooks/
- Jupyter notebooks for exploration and experimentation

### docs/
- Comprehensive documentation
- API documentation
- User manuals
- Deployment guides

### tests/
- Integration tests
- Performance tests
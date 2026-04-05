# Complete Project Deep Dive: Ticket Classification MLOps System

## Table of Contents
1. [Project Structure Overview](#project-structure-overview)
2. [System Architecture & Data Flow](#system-architecture--data-flow)
3. [Detailed File-by-File Explanation](#detailed-file-by-file-explanation)

---

## Project Structure Overview

### High-Level Organization Philosophy

This project follows a **microservices-inspired architecture** with clear separation of concerns. The structure is designed around the principle that each major component (backend API, frontend UI, ML pipeline, monitoring) should be independent yet easily integrated. This makes the system modular, testable, and scalable.

### Root Directory Structure

```
ticket-classification-mlops-system/
├── backend/              # API server and business logic
├── frontend/             # User interface
├── ml_pipeline/          # Machine learning training code
├── data/                 # All data storage
├── models/               # Trained model artifacts
├── airflow/              # Workflow orchestration
├── monitoring/           # System monitoring setup
├── docs/                 # Additional documentation
├── tests/                # Test suites
├── notebooks/            # Jupyter notebooks for exploration
└── scripts/              # Utility scripts
```

### Why This Structure?

**Separation by Function**: Each top-level folder represents a distinct functional area. This makes it easy for different team members (data scientists, backend developers, frontend developers) to work independently without conflicts.

**MLOps Best Practices**: The structure follows industry standards where data, code, and models are versioned separately. This allows for reproducibility and proper experiment tracking.

**Scalability**: Each component can be containerized and deployed independently, making it easy to scale specific parts of the system based on load.

---

## Folder-by-Folder Breakdown

### 1. `/backend` - The API Server

**Purpose**: This is the heart of the application - a REST API that receives requests, processes them using the ML model, and returns predictions.

**Why FastAPI?**: FastAPI was chosen because it's modern, fast, has automatic API documentation, and supports async operations for better performance.

**Structure**:
```
backend/
├── app/
│   ├── api/          # API endpoints and request/response schemas
│   ├── models/       # ML model wrapper
│   ├── services/     # Business logic layer
│   └── utils/        # Helper functions
├── requirements.txt  # Python dependencies
└── run.sh           # Startup script
```

**Design Reasoning**: The backend follows a **layered architecture**:
- **API Layer** (`api/`): Handles HTTP requests/responses
- **Service Layer** (`services/`): Contains business logic
- **Model Layer** (`models/`): Wraps the ML model
- **Utils Layer** (`utils/`): Provides cross-cutting concerns (logging, metrics)

This separation means you can change how the API works without touching the ML model code, or swap out the ML model without changing the API endpoints.

### 2. `/frontend` - The User Interface

**Purpose**: A React-based web application that provides three different ways to interact with the classification system.

**Structure**:
```
frontend/
├── src/
│   ├── components/   # UI components for each input mode
│   ├── services/     # API communication layer
│   └── App.js        # Main application component
├── public/           # Static assets
└── package.json      # Node.js dependencies
```

**Design Reasoning**: The frontend is organized around **component-based architecture**. Each input mode (single text, bulk CSV, advanced) is a separate component, making the code reusable and maintainable. The `services/` folder abstracts away API calls, so if the backend URL changes, you only update one file.

### 3. `/ml_pipeline` - Machine Learning Training Code

**Purpose**: Contains all the code needed to train, evaluate, and improve the ML model. This is separate from the backend because training happens offline, not during API requests.

**Structure**:
```
ml_pipeline/
├── data_preprocessing.py    # Clean and prepare data
├── feature_engineering.py   # Create features from text
├── model_training.py        # Train the model
├── model_evaluation.py      # Test model performance
├── drift_detection.py       # Monitor data changes
└── config.py               # Configuration settings
```

**Design Reasoning**: Each file represents a **stage in the ML pipeline**. This modular approach means you can:
- Run just preprocessing without training
- Experiment with different feature engineering approaches
- Swap out the training algorithm easily
- Add new evaluation metrics without touching other code

The pipeline follows the **Extract-Transform-Load (ETL)** pattern common in data engineering.

### 4. `/data` - Data Storage

**Purpose**: Centralized location for all data used in the project.

**Structure**:
```
data/
├── raw/              # Original, unmodified data
├── processed/        # Cleaned and transformed data
├── ground_truth/     # User-corrected labels (feedback)
└── drift_baseline/   # Statistical baseline for monitoring
```

**Design Reasoning**: This follows the **data versioning** principle. Raw data is never modified - all transformations create new files in `processed/`. This ensures reproducibility: you can always go back to the original data and re-run the pipeline. The `ground_truth/` folder implements the **feedback loop** - when users correct predictions, that data is stored here and used to retrain the model.

### 5. `/models` - Model Artifacts

**Purpose**: Stores trained model files and embeddings.

**Structure**:
```
models/
├── trained/      # Serialized model files
└── embeddings/   # Pre-computed embeddings for categories
```

**Design Reasoning**: Models are stored separately from code because they're **binary artifacts** that change less frequently than code. This also enables **model versioning** - you can keep multiple versions of the model and roll back if needed.

### 6. `/airflow` - Workflow Orchestration

**Purpose**: Automates the retraining pipeline - when to retrain, how to validate, when to deploy.

**Structure**:
```
airflow/
├── dags/      # Workflow definitions
├── config/    # Airflow configuration
└── plugins/   # Custom operators
```

**Design Reasoning**: Airflow implements the **orchestration layer** of MLOps. It ensures that retraining happens automatically when certain conditions are met (e.g., enough new feedback data, performance degradation). This is crucial for **continuous learning** - the model improves over time without manual intervention.

### 7. `/monitoring` - System Observability

**Purpose**: Tracks system health, performance metrics, and data quality.

**Structure**:
```
monitoring/
├── prometheus/   # Metrics collection
└── grafana/      # Visualization dashboards
```

**Design Reasoning**: Following the **observability** principle, this setup allows you to:
- Track API response times
- Monitor prediction confidence scores
- Detect data drift
- Alert when something goes wrong

This is essential for **production ML systems** where you need to know if the model is degrading before users complain.

---

## System Architecture & Data Flow

### Overall System Flow

```
User Input → Frontend → Backend API → ML Model → Prediction → User
                ↓                         ↓
            Feedback                  Metrics
                ↓                         ↓
          Ground Truth              Monitoring
                ↓
          Retraining Pipeline
                ↓
          Updated Model
```

### Detailed Data Flow Explanation

#### 1. **User Interaction Flow**

**Step 1: User Submits Request**
- User enters text, uploads CSV, or provides custom categories through the React frontend
- Frontend validates the input (checks for empty fields, file format, etc.)
- Frontend sends HTTP POST request to backend API

**Step 2: Backend Receives Request**
- FastAPI router (`routes.py`) receives the request
- Request data is validated against Pydantic schemas (`schemas.py`)
- Router calls appropriate service function

**Step 3: Service Layer Processing**
- Service layer (`prediction_service.py`) extracts the text
- Calls validation service to check data quality
- Passes clean data to the model

**Step 4: Model Inference**
- Model wrapper (`classifier.py`) loads the sentence transformer
- Converts text to embeddings (numerical vectors)
- Compares ticket embedding with category embeddings
- Calculates similarity scores (cosine similarity)
- Returns category with highest score

**Step 5: Response Generation**
- Service formats the prediction with confidence score
- Metrics are recorded (Prometheus counters)
- Response is sent back through the API
- Frontend displays results to user

#### 2. **Feedback Loop Flow**

**When User Corrects a Prediction:**
- User clicks "This is wrong" and selects correct category
- Frontend sends feedback to `/feedback` endpoint
- Backend stores correction in `data/ground_truth/`
- System checks if enough corrections accumulated
- If threshold reached, triggers retraining

**Why This Matters**: This implements **active learning** - the model learns from its mistakes and gets better over time.

#### 3. **Retraining Flow**

**Triggered by Airflow DAG:**
1. **Data Collection**: Gather all feedback from ground_truth folder
2. **Data Preprocessing**: Clean and format the data
3. **Feature Engineering**: Create embeddings
4. **Model Training**: Train new model version
5. **Evaluation**: Test on validation set
6. **Comparison**: Compare with current production model
7. **Deployment**: If better, replace production model
8. **Monitoring**: Track new model's performance

**Why Automated**: Manual retraining is error-prone and slow. Automation ensures the model stays current.

#### 4. **Monitoring Flow**

**Continuous Tracking:**
- Every API request increments Prometheus counters
- Response times are recorded as histograms
- Confidence scores are tracked
- Prometheus scrapes metrics every 15 seconds
- Grafana visualizes trends
- Alerts trigger if metrics exceed thresholds

**Why Important**: You need to know if the model is degrading before it impacts users significantly.

---

## Detailed File-by-File Explanation

### Backend Files

#### `backend/app/main.py` - Application Entry Point

This file is the **heart of the backend application**. When you start the server, this is the first file that runs. It sets up the entire FastAPI application and manages the application lifecycle.

**Startup Process**: The file defines a lifespan context manager that handles what happens when the application starts and stops. During startup, it loads the machine learning model into memory. This is done at startup rather than on each request because loading a model is expensive - it can take several seconds. By loading once at startup, every subsequent request is fast. The startup also records how long the model takes to load, which is useful for monitoring. If the model fails to load, the application won't start, which is intentional - better to fail fast than serve broken predictions.

**Application Configuration**: The FastAPI app is created with metadata like title, description, and version. This metadata automatically appears in the API documentation at `/docs`. The app includes CORS (Cross-Origin Resource Sharing) middleware, which allows the frontend running on port 3000 to communicate with the backend on port 8000. Without CORS, browsers would block these requests for security reasons.

**Router Integration**: The file includes the API router from `routes.py`. This is a modular approach - instead of defining all endpoints in one file, they're organized in a separate router and then included here. This keeps the main file clean and focused on application setup.

**Logging and Metrics**: Throughout the startup process, the application logs important events. It also sets Prometheus metrics like model load time and number of categories loaded. These metrics are exposed at the `/metrics` endpoint for monitoring systems to scrape.

#### `backend/app/config.py` - Configuration Management

This file centralizes all configuration settings using Pydantic's BaseSettings. The beauty of this approach is that settings can come from environment variables, making the application **12-factor compliant** (a set of best practices for building modern applications).

**Environment-Based Configuration**: Settings like `MODEL_NAME` and `API_PORT` can be overridden by environment variables. This means you can use different settings in development, testing, and production without changing code. For example, in production you might use a different model or port.

**Type Safety**: Pydantic validates all settings at startup. If someone sets `MAX_CONFIDENCE_THRESHOLD` to a string instead of a float, the application will fail to start with a clear error message. This prevents runtime errors from bad configuration.

**Default Values**: The file provides sensible defaults for everything. This means the application works out of the box for development, but can be customized for production. For instance, the default model is "all-MiniLM-L6-v2", a good general-purpose sentence transformer, but you could swap it for a domain-specific model.

**Paths and Directories**: All file paths are defined here as Path objects. This ensures cross-platform compatibility - the same code works on Windows, Mac, and Linux. The paths are relative to the project root, making the application portable.

#### `backend/app/api/schemas.py` - Data Validation

This file defines the **contract** between the frontend and backend using Pydantic models. Every request and response must match these schemas, ensuring data integrity.

**Request Schemas**: Each input type (single text, CSV upload, advanced mode) has its own schema. For example, `SingleTextRequest` requires a text field and optionally accepts a ticket_id. Pydantic automatically validates that text is a string and not empty. If validation fails, FastAPI returns a clear error message to the user before any business logic runs.

**Response Schemas**: These define what the API returns. `PredictionResponse` includes the predicted category, confidence score, and all category scores. This structured response makes it easy for the frontend to display results consistently. The schemas also serve as documentation - developers can see exactly what data to expect.

**Nested Models**: Some schemas contain other schemas. For example, `BulkPredictionResponse` contains a list of `PredictionResponse` objects. This represents the hierarchical nature of the data - a bulk upload returns multiple predictions.

**Field Validation**: Schemas include validators like `min_length`, `max_length`, and `ge` (greater than or equal). These enforce business rules at the API boundary. For instance, confidence scores must be between 0 and 1, and text can't be longer than 10,000 characters (to prevent abuse).

#### `backend/app/api/routes.py` - API Endpoints

This file defines all the HTTP endpoints that clients can call. It's the **interface** between the outside world and your application logic.

**Endpoint Organization**: Each endpoint is a Python function decorated with `@router.post()` or `@router.get()`. The decorator specifies the HTTP method and URL path. FastAPI automatically generates OpenAPI documentation from these decorators and the type hints.

**Dependency Injection**: Endpoints use FastAPI's dependency injection system. For example, services are injected rather than imported directly. This makes testing easier - you can inject mock services during tests.

**Error Handling**: Each endpoint is wrapped in try-except blocks. If something goes wrong (invalid file, model error, etc.), the endpoint catches the exception and returns a proper HTTP error response with a clear message. This prevents the server from crashing and gives users actionable feedback.

**Request Processing Flow**: Take the `/predict-text` endpoint as an example. It receives a `SingleTextRequest`, extracts the text, calls the prediction service, records metrics (request count, latency), and returns a `PredictionResponse`. The entire flow is type-safe - if you try to return the wrong type, Python's type checker will catch it.

**File Upload Handling**: Endpoints like `/upload-csv` handle file uploads. They validate the file type, read the contents, parse the CSV, and process each row. If the CSV is malformed, they return a clear error. This is more complex than simple text input because files can be large and in various formats.

**Metrics Recording**: After each request, the endpoint records Prometheus metrics. This includes incrementing request counters, recording latency, and tracking confidence scores. These metrics are crucial for monitoring system health in production.

#### `backend/app/models/classifier.py` - ML Model Wrapper

This file wraps the sentence transformer model in a clean interface. It's the **bridge** between the ML world and the application world.

**Model Loading**: The `TicketClassifier` class loads the sentence transformer model from Hugging Face. The first time you run the application, it downloads the model (about 80MB). Subsequent runs use the cached version. The model is loaded once and reused for all predictions, which is much more efficient than loading it for each request.

**Category Management**: The classifier can work with either default categories (loaded from CSV) or custom categories provided by the user. It stores category embeddings in memory for fast comparison. When you provide custom categories, it computes their embeddings on the fly.

**Embedding Generation**: The core of the classifier is the `_get_embedding()` method. It converts text into a numerical vector (embedding) that captures the semantic meaning. Similar texts have similar embeddings. This is what makes the classification work - we compare the ticket embedding with category embeddings.

**Similarity Calculation**: The `predict()` method computes cosine similarity between the ticket embedding and each category embedding. Cosine similarity measures how similar two vectors are, ranging from -1 (opposite) to 1 (identical). The category with the highest similarity is the prediction.

**Confidence Scoring**: The raw similarity scores are normalized to create confidence scores between 0 and 1. A high confidence (>0.8) means the model is very sure, while low confidence (<0.5) suggests the ticket might not fit any category well. This helps users know when to trust the prediction.

**Thread Safety**: The classifier uses locks to ensure thread-safe access to the model. This is important because FastAPI can handle multiple requests concurrently. Without locks, concurrent requests could corrupt the model's internal state.

#### `backend/app/services/prediction_service.py` - Business Logic

This file contains the **business logic** for making predictions. It sits between the API layer and the model layer, orchestrating the prediction process.

**Service Pattern**: The `PredictionService` class follows the service pattern - it encapsulates business logic separate from HTTP concerns. This makes the code more testable and reusable. You could use the same service in a CLI tool or a batch job.

**Single Prediction**: The `predict_single()` method handles one ticket at a time. It validates the input, calls the model, formats the response, and handles errors. If the model fails, it logs the error and returns a meaningful message rather than crashing.

**Bulk Prediction**: The `predict_bulk()` method processes multiple tickets efficiently. It could process them one by one, but that would be slow. Instead, it batches them and processes in parallel where possible. It also handles partial failures - if one ticket fails, the others still get processed.

**Advanced Mode**: The `predict_with_custom_categories()` method is the most complex. It validates both the tickets and categories, creates temporary embeddings for the custom categories, runs predictions, and cleans up. This temporary nature is important - custom categories aren't saved, so they don't pollute the default categories.

**Error Recovery**: Each method has comprehensive error handling. If validation fails, it returns a clear error. If the model fails, it logs the error and returns a fallback response. This defensive programming ensures the service degrades gracefully rather than failing completely.

**Logging**: Every important action is logged with context (ticket ID, category, confidence). This creates an audit trail for debugging and monitoring. If a user reports a wrong prediction, you can trace exactly what happened.

#### `backend/app/services/validation_service.py` - Input Validation

This file ensures all input data is clean and valid before it reaches the model. It's the **gatekeeper** that prevents garbage from entering the system.

**Text Validation**: The `validate_text()` method checks that text isn't empty, isn't too long, and doesn't contain suspicious patterns. For example, it rejects text that's all numbers or special characters, as these aren't meaningful tickets. It also normalizes whitespace and removes control characters.

**CSV Validation**: The `validate_csv()` method checks CSV structure. It ensures required columns exist, validates data types, checks for duplicates, and handles missing values. It returns both valid rows and a list of errors, so users know exactly what's wrong.

**Category Validation**: The `validate_categories()` method ensures custom categories are well-formed. Each category needs a name and description. Names must be unique and not too similar to each other (to avoid confusion). Descriptions must be meaningful (not just "N/A" or empty).

**Security Checks**: The validation service also performs security checks. It limits text length to prevent denial-of-service attacks. It sanitizes input to prevent injection attacks. It validates file sizes to prevent memory exhaustion.

**Business Rules**: Beyond technical validation, the service enforces business rules. For example, it might reject tickets that are too similar to recent tickets (potential duplicates) or flag tickets with unusual patterns for manual review.

#### `backend/app/services/feedback_service.py` - Feedback Loop

This file manages user corrections, implementing the **active learning** component of the system.

**Feedback Storage**: When a user corrects a prediction, the `store_feedback()` method saves it to the ground truth folder. Each feedback entry includes the original text, predicted category, correct category, timestamp, and user ID. This creates a dataset for retraining.

**Feedback Validation**: Not all feedback is accepted. The service validates that the correct category exists and that the feedback isn't spam (e.g., the same user submitting the same correction repeatedly). This prevents poisoning the training data.

**Aggregation**: The `get_feedback_stats()` method aggregates feedback to identify patterns. It calculates metrics like correction rate (how often predictions are wrong), most confused categories (which categories the model mixes up), and improvement over time.

**Retraining Trigger**: The service monitors feedback volume and quality. When enough high-quality feedback accumulates, it triggers the retraining pipeline. The threshold is configurable - you might retrain after 100 corrections or when the correction rate exceeds 10%.

**Feedback Loop Closure**: This service closes the loop between production and training. User corrections in production directly improve the model, creating a **virtuous cycle** of continuous improvement.

#### `backend/app/utils/logger.py` - Logging System

This file sets up structured logging for the entire application. Good logging is crucial for **debugging and monitoring** production systems.

**Structured Logging**: Instead of simple print statements, the logger creates structured log entries with timestamp, level, module, function, and message. This makes logs machine-readable and easy to search. You can query logs like "show all ERROR logs from the prediction service in the last hour."

**Log Levels**: The logger supports different levels (DEBUG, INFO, WARNING, ERROR, CRITICAL). In development, you might log everything (DEBUG), but in production, you'd only log INFO and above to reduce noise. This is configurable without code changes.

**Contextual Information**: Each log entry includes context like request ID, user ID, and ticket ID. This allows you to trace a single request through the entire system. If a user reports an issue, you can find all logs related to their request.

**Log Rotation**: The logger is configured to rotate log files daily and keep 30 days of history. This prevents logs from filling up disk space while maintaining enough history for debugging and compliance.

**Performance**: Logging is asynchronous - log writes don't block the main application thread. This ensures logging doesn't slow down request processing, even when writing to disk.

#### `backend/app/utils/metrics.py` - Prometheus Metrics

This file defines all the metrics that Prometheus collects. Metrics are the **quantitative heartbeat** of your system.

**Counter Metrics**: Counters track cumulative values that only increase. For example, `requests_total` counts every API request. You can query the rate of increase to see requests per second. Counters are useful for tracking throughput and error rates.

**Histogram Metrics**: Histograms track distributions of values. For example, `request_duration_seconds` tracks how long each request takes. Prometheus automatically calculates percentiles (p50, p95, p99), which tell you that 95% of requests complete within X seconds. This is crucial for SLA monitoring.

**Gauge Metrics**: Gauges track values that can go up or down. For example, `active_connections` tracks current connections. Gauges are useful for monitoring resource usage and capacity.

**Labels**: Metrics can have labels for dimensionality. For example, `requests_total` has labels for endpoint and status code. This lets you query "how many 500 errors did the /predict-text endpoint have?" Labels make metrics flexible and powerful.

**Custom Metrics**: Beyond standard metrics, the file defines domain-specific metrics like `confidence_score` and `category_distribution`. These track ML-specific concerns like model confidence and prediction patterns.

**Metrics Collection**: The `MetricsCollector` class provides a clean interface for recording metrics. Instead of calling Prometheus directly throughout the code, you call methods like `record_request()` or `record_prediction()`. This abstraction makes the code cleaner and makes it easy to swap out Prometheus for another monitoring system.

#### `backend/app/utils/preprocessing.py` - Text Preprocessing

This file contains utilities for cleaning and normalizing text before it reaches the model. Preprocessing is crucial because **garbage in, garbage out**.

**Text Cleaning**: The `clean_text()` function removes noise from text. It strips HTML tags, removes URLs, normalizes whitespace, and converts to lowercase. This ensures the model sees consistent input regardless of how users format their tickets.

**Tokenization**: The `tokenize()` function splits text into words or subwords. This is necessary for some NLP tasks, though sentence transformers handle this internally. The function is here for flexibility - you might want to add custom tokenization logic.

**Stop Word Removal**: Common words like "the", "is", "at" don't carry much meaning. The `remove_stopwords()` function removes them to reduce noise. However, this is optional - modern transformers can handle stop words, so removing them might not help.

**Normalization**: The `normalize()` function handles variations like "can't" vs "cannot", "email" vs "e-mail", etc. It expands contractions, normalizes punctuation, and handles special characters. This reduces vocabulary size and helps the model generalize.

**Language Detection**: The `detect_language()` function identifies the language of the text. This is useful if you want to route non-English tickets to a different model or reject them. It uses statistical methods to detect language with high accuracy.

**Preprocessing Pipeline**: The `preprocess()` function chains all these steps together. You can configure which steps to apply. For example, you might skip stop word removal but apply normalization. This flexibility lets you experiment with different preprocessing strategies.

### Frontend Files

#### `frontend/src/App.js` - Main Application Component

This is the **root component** of the React application. It manages the overall application state and layout.

**Component Structure**: The App component uses React hooks (useState) to manage which tab is active. When a user clicks a tab, the state updates, and React re-renders to show the appropriate component. This is React's declarative approach - you describe what the UI should look like for each state, and React handles the updates.

**Tab Navigation**: The application uses Material-UI's Tab component for navigation. Each tab corresponds to an input mode (single text, bulk CSV, advanced). The tabs are styled to be intuitive and accessible, following Material Design guidelines.

**Component Composition**: Instead of putting all code in one file, App.js composes smaller components. It imports SingleTextInput, BulkCSVUpload, and AdvancedMode components and renders them based on the active tab. This makes the code modular and maintainable.

**State Management**: The App component manages global state like the current tab and any shared data. Child components can update this state through callback props. This is a simple state management approach suitable for small applications. For larger apps, you'd use Redux or Context API.

**Styling**: The component applies consistent styling using Material-UI's theme system. Colors, fonts, and spacing are defined in the theme and applied throughout the app. This ensures visual consistency and makes it easy to rebrand.

#### `frontend/src/components/SingleTextInput.js` - Single Ticket Input

This component handles the simplest use case - classifying one ticket at a time. It's designed to be **fast and intuitive**.

**Form Handling**: The component uses controlled inputs - the input value is stored in React state and updated on every keystroke. This gives you full control over the input and makes validation easy. You can disable the submit button if the input is invalid.

**API Integration**: When the user submits, the component calls the API service to get a prediction. It shows a loading spinner while waiting for the response. If the request fails, it shows an error message. This provides clear feedback to the user.

**Results Display**: After receiving a prediction, the component displays the result using the PredictionResults component. It shows the predicted category, confidence score, and all category scores. Users can see not just the top prediction but how confident the model is.

**Feedback Mechanism**: If the prediction is wrong, users can click "Incorrect" and select the correct category. This feedback is sent to the backend and used to improve the model. The UI makes this process seamless - users don't need to understand the technical details.

**Error Handling**: The component handles various error scenarios - network errors, validation errors, server errors. Each error type shows an appropriate message. For example, if the text is too long, it shows "Text must be less than 10,000 characters" rather than a generic error.

**Accessibility**: The component follows accessibility best practices. It uses semantic HTML, provides labels for screen readers, and supports keyboard navigation. This ensures the application is usable by everyone.

#### `frontend/src/components/BulkCSVUpload.js` - Bulk Processing

This component handles CSV file uploads for processing multiple tickets at once. It's designed for **efficiency and clarity**.

**File Upload**: The component uses react-dropzone for drag-and-drop file upload. Users can either click to select a file or drag it onto the upload area. The component validates that the file is a CSV and not too large (to prevent memory issues).

**CSV Parsing**: After upload, the component parses the CSV using a library like PapaParse. It validates the structure (checking for required columns) and shows a preview of the data. This lets users verify they uploaded the correct file before processing.

**Batch Processing**: When the user clicks "Process", the component sends the CSV to the backend. The backend processes all tickets and returns predictions for each. The component shows a progress indicator during processing.

**Results Table**: Results are displayed in a sortable, filterable table. Users can sort by confidence score to find low-confidence predictions that might need review. They can filter by category to see all tickets in a specific category. This makes it easy to review hundreds of predictions.

**Export Functionality**: Users can export the results as a CSV file. This includes the original ticket text, predicted category, confidence score, and any corrections. This is useful for record-keeping and further analysis.

**Error Handling**: If some tickets fail to process, the component shows which ones failed and why. It still displays results for successful tickets. This partial success handling is important for large batches where a few failures shouldn't block everything.

#### `frontend/src/components/AdvancedMode.js` - Custom Categories

This component implements the most complex use case - using custom categories instead of the defaults. It's designed for **flexibility and power users**.

**Dual Upload**: The component requires two files - one with tickets and one with categories. It validates both files and shows previews. Users can see exactly what categories will be used before processing.

**Category Validation**: The component validates that categories have both names and descriptions. It checks for duplicates and warns if categories are too similar (which might confuse the model). This prevents common mistakes.

**Dynamic Processing**: Unlike the other modes, this one doesn't use pre-computed category embeddings. The backend computes embeddings for the custom categories on the fly. This is slower but necessary for flexibility.

**Results Comparison**: The component can optionally show how predictions differ between default and custom categories. This helps users understand if their custom categories are better suited for their use case.

**Category Management**: Users can save their custom categories for reuse. The component stores them in browser local storage. This is convenient for users who frequently use the same custom categories.

**Educational Tooltips**: Because this mode is complex, the component includes tooltips explaining each step. For example, it explains what makes a good category description. This helps users get the most out of the feature.

#### `frontend/src/components/PredictionResults.js` - Results Display

This component displays prediction results in a clear, actionable format. It's designed for **clarity and actionability**.

**Visual Hierarchy**: The component uses visual hierarchy to highlight important information. The predicted category is shown prominently in large text. The confidence score is color-coded (green for high confidence, yellow for medium, red for low). This lets users quickly assess the prediction quality.

**Confidence Visualization**: Instead of just showing a number, the component visualizes confidence with a progress bar. This makes it easier to understand at a glance. It also shows all category scores in a bar chart, so users can see the runner-up categories.

**Feedback Interface**: If the prediction is wrong, users can easily provide feedback. The component shows a dropdown with all categories and a text area for comments. This feedback is sent to the backend to improve the model.

**Explanation**: For high-stakes decisions, users want to understand why the model made a prediction. The component shows which words in the ticket were most important for the prediction. This transparency builds trust.

**Action Buttons**: The component provides action buttons like "Accept", "Reject", or "Needs Review". These actions can trigger workflows - for example, accepting a prediction might automatically assign the ticket to the appropriate team.

#### `frontend/src/services/api.js` - API Client

This file centralizes all API communication. It's the **single source of truth** for how the frontend talks to the backend.

**Axios Configuration**: The file configures Axios (an HTTP client) with the base URL, timeout, and headers. This configuration is applied to all requests, ensuring consistency. For example, all requests include a timeout to prevent hanging indefinitely.

**Request Methods**: The file exports functions for each API endpoint - `predictSingle()`, `uploadCSV()`, etc. Each function handles the HTTP request, error handling, and response parsing. This abstraction means the rest of the frontend doesn't need to know about HTTP details.

**Error Handling**: Each API function has comprehensive error handling. It distinguishes between network errors (can't reach server), client errors (bad request), and server errors (backend crashed). Each error type is handled appropriately - network errors might trigger a retry, while validation errors show the error message to the user.

**Request Interceptors**: The file uses Axios interceptors to add common logic to all requests. For example, it adds an authentication token to every request (if the user is logged in). It also logs all requests for debugging.

**Response Transformation**: The file transforms API responses into a consistent format. For example, it converts date strings to Date objects and normalizes field names. This makes the data easier to work with in React components.

**Retry Logic**: For transient errors (like network timeouts), the file implements retry logic. It retries the request up to 3 times with exponential backoff. This makes the application more resilient to temporary network issues.

### ML Pipeline Files

#### `ml_pipeline/data_preprocessing.py` - Data Preparation

This file handles all data cleaning and preparation before training. It's the **foundation** of the ML pipeline.

**Data Loading**: The `load_data()` function reads data from various sources (CSV, JSON, database). It handles different formats and encodings. It also validates the data structure - checking that required columns exist and have the right types.

**Missing Value Handling**: The `handle_missing_values()` function deals with incomplete data. For text fields, it might fill missing values with empty strings. For categorical fields, it might use the most common value. The strategy depends on the field and how much data is missing.

**Outlier Detection**: The `detect_outliers()` function identifies unusual data points. For example, tickets that are extremely long or short might be outliers. The function flags these for review rather than automatically removing them - sometimes outliers are legitimate edge cases.

**Data Splitting**: The `split_data()` function divides data into training, validation, and test sets. It uses stratified splitting to ensure each set has a representative distribution of categories. This prevents the model from being biased toward common categories.

**Data Augmentation**: The `augment_data()` function creates synthetic training examples. For example, it might paraphrase tickets or add noise. This increases the training data size and helps the model generalize better. However, augmentation is done carefully to avoid introducing unrealistic examples.

**Data Versioning**: The file saves preprocessed data with a version number and timestamp. This ensures reproducibility - you can always go back to a specific version of the data. It also tracks what preprocessing steps were applied, creating an audit trail.

#### `ml_pipeline/feature_engineering.py` - Feature Creation

This file creates features from raw text. While sentence transformers handle this internally, this file provides additional features that might improve performance.

**Text Statistics**: The `extract_text_stats()` function computes statistics like text length, word count, average word length, and punctuation density. These simple features can be surprisingly informative - for example, urgent tickets might be shorter and have more exclamation marks.

**Keyword Extraction**: The `extract_keywords()` function identifies important words in each ticket. It uses TF-IDF (Term Frequency-Inverse Document Frequency) to find words that are common in a ticket but rare overall. These keywords can help distinguish categories.

**Sentiment Analysis**: The `analyze_sentiment()` function determines if a ticket is positive, negative, or neutral. This might be useful for prioritization - negative tickets might need faster response. The function uses a pre-trained sentiment model.

**Entity Recognition**: The `extract_entities()` function identifies named entities like product names, error codes, or dates. These entities can be strong signals for classification. For example, tickets mentioning specific error codes might belong to a "Bug" category.

**Feature Combination**: The `combine_features()` function creates interaction features. For example, it might combine text length with sentiment to create a "frustrated user" feature (long text + negative sentiment). These combinations can capture complex patterns.

**Feature Selection**: Not all features are useful. The `select_features()` function uses statistical tests to identify which features actually help prediction. It removes redundant or noisy features, which speeds up training and can improve accuracy.

#### `ml_pipeline/model_training.py` - Model Training

This file trains the classification model. It's the **core** of the ML pipeline.

**Model Selection**: The `select_model()` function chooses which model architecture to use. For this project, we use sentence transformers, but the function is designed to be flexible. You could easily swap in a different model by changing this function.

**Hyperparameter Tuning**: The `tune_hyperparameters()` function searches for the best model settings. It tries different combinations of learning rate, batch size, and other parameters. It uses techniques like grid search or Bayesian optimization to find the best combination efficiently.

**Training Loop**: The `train()` function implements the training loop. It iterates through the training data multiple times (epochs), computing predictions, calculating loss, and updating model weights. It also validates on the validation set after each epoch to monitor progress.

**Early Stopping**: The training loop includes early stopping - if validation performance stops improving, training stops. This prevents overfitting (where the model memorizes training data but doesn't generalize). Early stopping is crucial for getting a model that works well on new data.

**Model Checkpointing**: During training, the function saves model checkpoints. If training crashes, you can resume from the last checkpoint rather than starting over. It also saves the best model (highest validation accuracy) separately.

**Training Monitoring**: The function logs training metrics like loss, accuracy, and learning rate. These metrics are sent to MLflow for tracking. You can compare different training runs to see what works best.

#### `ml_pipeline/model_evaluation.py` - Model Testing

This file evaluates trained models to ensure they meet quality standards. It's the **quality gate** before deployment.

**Metric Calculation**: The `calculate_metrics()` function computes various metrics - accuracy, precision, recall, F1 score. Each metric captures a different aspect of performance. For example, precision measures how many predictions are correct, while recall measures how many actual instances are found.

**Confusion Matrix**: The `plot_confusion_matrix()` function creates a confusion matrix showing which categories the model confuses. This is incredibly useful for understanding model weaknesses. For example, if the model often confuses "Bug" and "Feature Request", you might need better category descriptions.

**Per-Category Analysis**: The `analyze_per_category()` function breaks down performance by category. Some categories might be easy to predict (high accuracy) while others are hard (low accuracy). This helps prioritize improvements - focus on the hardest categories.

**Error Analysis**: The `analyze_errors()` function examines misclassified examples. It looks for patterns - are errors more common for short tickets? For tickets with certain keywords? Understanding error patterns guides improvements.

**Comparison with Baseline**: The `compare_with_baseline()` function compares the new model with the current production model. The new model must be significantly better to justify deployment. This prevents deploying models that are only marginally better or even worse.

**Statistical Significance**: The function uses statistical tests to determine if performance differences are significant or just random variation. This is important because small datasets can show apparent improvements that aren't real.

#### `ml_pipeline/drift_detection.py` - Data Drift Monitoring

This file monitors for changes in data distribution over time. Data drift is a major cause of **model degradation** in production.

**Baseline Calculation**: The `calculate_baseline()` function computes statistics on the training data - mean, standard deviation, distribution of features. This baseline represents what "normal" data looks like.

**Drift Detection**: The `detect_drift()` function compares new data with the baseline. It uses statistical tests like the Kolmogorov-Smirnov test to determine if distributions have changed significantly. If drift is detected, it triggers an alert.

**Feature Drift**: The function checks each feature separately. Some features might drift while others remain stable. For example, ticket length might change (users writing longer tickets) while sentiment remains stable. Identifying which features drift helps diagnose the cause.

**Concept Drift**: Beyond feature drift, the function detects concept drift - when the relationship between features and labels changes. For example, what users call a "bug" might evolve over time. Concept drift is harder to detect but more serious.

**Drift Visualization**: The function creates visualizations showing how data has changed over time. These plots make it easy to see trends and communicate drift to stakeholders. For example, a plot might show that ticket length has been increasing steadily.

**Retraining Trigger**: If drift exceeds a threshold, the function triggers retraining. The threshold is configurable - you might tolerate small drift but retrain immediately for large drift. This automated response ensures the model stays current.

---

## Key Interconnections

### How Everything Fits Together

**User Journey**: A user opens the frontend, enters a ticket, and clicks submit. The frontend sends an HTTP request to the backend. The backend validates the input, calls the model, gets a prediction, records metrics, and returns the response. The frontend displays the result. If the user provides feedback, it's stored and eventually used to retrain the model.

**Data Flow**: Raw data starts in CSV files. The preprocessing pipeline cleans it and saves to the processed folder. The training pipeline loads processed data, trains a model, and saves it to the models folder. The backend loads the trained model and uses it for predictions. User feedback creates new data that flows back into the training pipeline.

**Monitoring Loop**: Every API request generates metrics. Prometheus scrapes these metrics. Grafana visualizes them in dashboards. If metrics indicate problems (high error rate, low confidence), alerts are triggered. Engineers investigate and fix issues. This creates a feedback loop for system health.

**Continuous Learning**: User corrections accumulate in the ground truth folder. When enough corrections exist, Airflow triggers retraining. The training pipeline loads corrections, trains a new model, evaluates it, and if better, deploys it. The new model is used for future predictions. This creates a feedback loop for model improvement.

**Separation of Concerns**: Each component has a clear responsibility. The frontend handles user interaction. The backend handles API logic. The model handles predictions. The ML pipeline handles training. Monitoring handles observability. This separation makes the system maintainable and scalable.

---

## Conclusion

This project demonstrates a complete MLOps system with:
- **Clean architecture** with separation of concerns
- **Robust data flow** from input to output
- **Continuous learning** through feedback loops
- **Comprehensive monitoring** for production reliability
- **Modular design** for maintainability and scalability

Each component is designed to be independent yet integrated, following best practices for modern ML systems. The structure supports the full ML lifecycle from experimentation to production deployment and continuous improvement.
# DVC Setup Guide with AWS S3

## Overview
This guide walks you through setting up Data Version Control (DVC) with AWS S3 as remote storage for the Ticket Classification MLOps System.

## Prerequisites
- AWS Account with S3 access
- AWS Access Key ID and Secret Access Key
- S3 bucket created (or will create one)
- Python environment with DVC installed

---

## Step-by-Step Setup

### Phase 1: Installation & Initialization

#### Step 1.1: Install DVC with S3 Support
```bash
# Install DVC with S3 dependencies
pip install 'dvc[s3]'

# Verify installation
dvc version
```

#### Step 1.2: Initialize DVC in Project
```bash
# Navigate to project root
cd /Users/mohitsharma/GitHub/ticket-classification-mlops-system

# Initialize DVC (creates .dvc directory and .dvcignore)
dvc init

# Commit DVC initialization
git add .dvc .dvcignore
git commit -m "chore: Initialize DVC for data versioning"
```

---

### Phase 2: AWS Credentials Setup

#### Step 2.1: Create/Update .env File
Add AWS credentials to your `.env` file:

```bash
# AWS S3 Configuration for DVC
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_DEFAULT_REGION=us-east-1  # Change to your region
S3_BUCKET_NAME=ticket-classification-mlops-data  # Your bucket name
```

#### Step 2.2: Configure AWS Credentials for DVC

**Option A: Using Environment Variables (Recommended)**
```bash
# Export AWS credentials (add to ~/.bashrc or ~/.zshrc for persistence)
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=us-east-1
```

**Option B: Using AWS CLI Configuration**
```bash
# Install AWS CLI if not already installed
pip install awscli

# Configure AWS credentials
aws configure
# Enter: Access Key ID, Secret Access Key, Region, Output format (json)
```

**Option C: Using DVC Config (Less Secure)**
```bash
# Set credentials in DVC config (not recommended for production)
dvc remote modify myremote access_key_id your_access_key_here
dvc remote modify myremote secret_access_key your_secret_key_here
```

#### Step 2.3: Configure S3 Remote Storage
```bash
# Add S3 bucket as DVC remote storage
dvc remote add -d myremote s3://ticket-classification-mlops-data/dvc-storage

# Set region
dvc remote modify myremote region us-east-1

# Optional: Enable versioning for better tracking
dvc remote modify myremote version_aware true

# Commit remote configuration
git add .dvc/config
git commit -m "chore: Configure S3 as DVC remote storage"
```

#### Step 2.4: Test S3 Connection
```bash
# Test AWS credentials
aws s3 ls s3://ticket-classification-mlops-data/

# Or test with DVC
dvc remote list
```

---

### Phase 3: Track Data & Models with DVC

#### Step 3.1: Track Raw Data Files
```bash
# Track customer support tickets dataset
dvc add data/raw/customer_support_tickets.csv

# Track default categories
dvc add data/raw/default_categories.csv

# Git add the .dvc files (not the actual data)
git add data/raw/customer_support_tickets.csv.dvc data/raw/default_categories.csv.dvc
git add .gitignore
git commit -m "chore: Track raw data files with DVC"
```

#### Step 3.2: Track Processed Data
```bash
# After data preprocessing, track processed files
dvc add data/processed/

# Commit
git add data/processed.dvc .gitignore
git commit -m "chore: Track processed data with DVC"
```

#### Step 3.3: Track Model Files
```bash
# Track trained models
dvc add models/trained/

# Track embeddings
dvc add models/embeddings/

# Commit
git add models/trained.dvc models/embeddings.dvc .gitignore
git commit -m "chore: Track model files with DVC"
```

#### Step 3.4: Track Drift Baseline
```bash
# Track drift detection baseline
dvc add data/drift_baseline/

# Commit
git add data/drift_baseline.dvc .gitignore
git commit -m "chore: Track drift baseline with DVC"
```

---

### Phase 4: Push to S3 Remote

#### Step 4.1: Push All Tracked Files
```bash
# Push all DVC-tracked files to S3
dvc push

# This uploads:
# - data/raw/customer_support_tickets.csv
# - data/raw/default_categories.csv
# - data/processed/
# - models/trained/
# - models/embeddings/
# - data/drift_baseline/
```

#### Step 4.2: Verify S3 Storage
```bash
# Check S3 bucket contents
aws s3 ls s3://ticket-classification-mlops-data/dvc-storage/ --recursive

# Or use DVC status
dvc status -c
```

#### Step 4.3: Test Pull from S3
```bash
# Remove local data (for testing)
rm -rf data/raw/customer_support_tickets.csv

# Pull from S3
dvc pull data/raw/customer_support_tickets.csv.dvc

# Verify file restored
ls -lh data/raw/customer_support_tickets.csv
```

---

### Phase 5: DVC Pipeline Setup

#### Step 5.1: Create DVC Pipeline Configuration

Create `dvc.yaml` in project root:

```yaml
stages:
  data_preprocessing:
    cmd: python ml_pipeline/data_preprocessing.py
    deps:
      - data/raw/customer_support_tickets.csv
      - data/raw/default_categories.csv
      - ml_pipeline/data_preprocessing.py
    params:
      - params.yaml:
          - preprocessing.max_length
          - preprocessing.min_samples_per_category
    outs:
      - data/processed/train.csv
      - data/processed/val.csv
      - data/processed/test.csv
    metrics:
      - data/processed/preprocessing_metrics.json:
          cache: false

  feature_engineering:
    cmd: python ml_pipeline/feature_engineering.py
    deps:
      - data/processed/train.csv
      - data/processed/val.csv
      - data/processed/test.csv
      - ml_pipeline/feature_engineering.py
    params:
      - params.yaml:
          - feature_engineering.embedding_model
    outs:
      - models/embeddings/train_embeddings.npy
      - models/embeddings/val_embeddings.npy
      - models/embeddings/test_embeddings.npy

  model_training:
    cmd: python ml_pipeline/model_training.py
    deps:
      - models/embeddings/train_embeddings.npy
      - models/embeddings/val_embeddings.npy
      - data/processed/train.csv
      - data/processed/val.csv
      - ml_pipeline/model_training.py
    params:
      - params.yaml:
          - training.epochs
          - training.batch_size
          - training.learning_rate
          - training.hidden_dim
          - training.dropout
    outs:
      - models/trained/mlp_classifier.pth
      - models/trained/label_encoder.pkl
    metrics:
      - models/trained/training_metrics.json:
          cache: false

  model_evaluation:
    cmd: python ml_pipeline/model_evaluation.py
    deps:
      - models/trained/mlp_classifier.pth
      - models/trained/label_encoder.pkl
      - models/embeddings/test_embeddings.npy
      - data/processed/test.csv
      - ml_pipeline/model_evaluation.py
    metrics:
      - models/trained/evaluation_metrics.json:
          cache: false
    plots:
      - models/trained/confusion_matrix.json:
          template: confusion
          x: actual
          y: predicted

  drift_detection:
    cmd: python ml_pipeline/drift_detection.py
    deps:
      - models/embeddings/train_embeddings.npy
      - data/processed/train.csv
      - ml_pipeline/drift_detection.py
    outs:
      - data/drift_baseline/baseline_stats.pkl
    metrics:
      - data/drift_baseline/drift_metrics.json:
          cache: false
```

#### Step 5.2: Update params.yaml

Ensure `params.yaml` has all required parameters:

```yaml
preprocessing:
  max_length: 512
  min_samples_per_category: 10
  test_size: 0.2
  val_size: 0.1
  random_state: 42

feature_engineering:
  embedding_model: "sentence-transformers/all-MiniLM-L6-v2"
  batch_size: 32

training:
  epochs: 50
  batch_size: 32
  learning_rate: 0.001
  hidden_dim: 256
  dropout: 0.3
  early_stopping_patience: 5
  weight_decay: 0.0001

evaluation:
  threshold: 0.5
  top_k: 3

drift_detection:
  threshold: 0.05
  window_size: 100
```

#### Step 5.3: Run DVC Pipeline
```bash
# Run entire pipeline
dvc repro

# Or run specific stage
dvc repro model_training

# Check pipeline status
dvc status

# View metrics
dvc metrics show

# View plots
dvc plots show
```

#### Step 5.4: Track Pipeline Changes
```bash
# Add pipeline files to git
git add dvc.yaml dvc.lock params.yaml
git commit -m "feat: Add DVC pipeline for ML workflow"

# Push pipeline outputs to S3
dvc push
```

---

### Phase 6: Daily Workflow

#### For Data Scientists

**1. Pull Latest Data & Models**
```bash
git pull
dvc pull
```

**2. Make Changes & Experiment**
```bash
# Modify code or parameters
vim ml_pipeline/model_training.py
vim params.yaml

# Run pipeline
dvc repro
```

**3. Track New Versions**
```bash
# DVC automatically tracks changes in dvc.lock
git add dvc.lock params.yaml
git commit -m "experiment: Improved model architecture"

# Push new model versions to S3
dvc push

# Push code changes to Git
git push
```

#### For Team Members

**1. Clone Repository**
```bash
git clone https://github.com/mohitsharmaworkspace/ticket-classification-mlops-system.git
cd ticket-classification-mlops-system
```

**2. Setup Environment**
```bash
# Install dependencies
pip install -r requirements.txt

# Configure AWS credentials
export AWS_ACCESS_KEY_ID=your_key
export AWS_SECRET_ACCESS_KEY=your_secret
```

**3. Pull Data & Models**
```bash
# Pull all DVC-tracked files from S3
dvc pull
```

**4. Run Pipeline**
```bash
# Reproduce entire pipeline
dvc repro
```

---

## DVC Commands Reference

### Basic Commands
```bash
# Initialize DVC
dvc init

# Add file/directory to DVC tracking
dvc add <path>

# Push to remote storage
dvc push

# Pull from remote storage
dvc pull

# Check status
dvc status

# Remove file from DVC tracking
dvc remove <file.dvc>
```

### Remote Management
```bash
# List remotes
dvc remote list

# Add remote
dvc remote add -d <name> <url>

# Modify remote
dvc remote modify <name> <option> <value>

# Remove remote
dvc remote remove <name>
```

### Pipeline Commands
```bash
# Run pipeline
dvc repro

# Run specific stage
dvc repro <stage_name>

# Show pipeline DAG
dvc dag

# Show metrics
dvc metrics show

# Compare metrics
dvc metrics diff

# Show plots
dvc plots show
```

### Version Control
```bash
# List all versions of a file
git log <file.dvc>

# Checkout specific version
git checkout <commit> <file.dvc>
dvc checkout <file.dvc>

# Compare versions
dvc diff
```

---

## Best Practices

### 1. **Separate Data from Code**
- ✅ Track data with DVC
- ✅ Track code with Git
- ✅ Never commit large files to Git

### 2. **Use Meaningful Commit Messages**
```bash
git commit -m "experiment: Increased hidden layer size to 512"
git commit -m "data: Added 1000 new labeled samples"
git commit -m "model: Improved accuracy to 95%"
```

### 3. **Regular Pushes**
```bash
# Push after every significant change
dvc push
git push
```

### 4. **Pipeline Reproducibility**
- Always use `params.yaml` for hyperparameters
- Document dependencies in `dvc.yaml`
- Use fixed random seeds

### 5. **S3 Bucket Organization**
```
s3://bucket-name/
├── dvc-storage/          # DVC cache
│   ├── files/
│   │   ├── md5/
│   │   │   ├── ab/
│   │   │   │   └── cdef123...
```

### 6. **Security**
- ✅ Use environment variables for credentials
- ✅ Never commit AWS keys to Git
- ✅ Use IAM roles when possible
- ✅ Enable S3 bucket versioning
- ✅ Set appropriate bucket policies

---

## Troubleshooting

### Issue: "Permission Denied" on S3
```bash
# Check AWS credentials
aws sts get-caller-identity

# Verify S3 bucket access
aws s3 ls s3://your-bucket-name/

# Check IAM permissions (need s3:PutObject, s3:GetObject, s3:ListBucket)
```

### Issue: "DVC file not found"
```bash
# Pull missing files
dvc pull

# Or pull specific file
dvc pull data/raw/customer_support_tickets.csv.dvc
```

### Issue: "Pipeline stage failed"
```bash
# Check logs
dvc repro --verbose

# Run stage individually
python ml_pipeline/data_preprocessing.py

# Check dependencies
dvc status
```

### Issue: "Merge conflicts in dvc.lock"
```bash
# Accept theirs (remote version)
git checkout --theirs dvc.lock
dvc repro

# Or accept ours (local version)
git checkout --ours dvc.lock
```

---

## S3 Bucket Setup (If Not Created)

### Create S3 Bucket
```bash
# Using AWS CLI
aws s3 mb s3://ticket-classification-mlops-data --region us-east-1

# Enable versioning
aws s3api put-bucket-versioning \
  --bucket ticket-classification-mlops-data \
  --versioning-configuration Status=Enabled

# Set lifecycle policy (optional - for cost optimization)
aws s3api put-bucket-lifecycle-configuration \
  --bucket ticket-classification-mlops-data \
  --lifecycle-configuration file://s3-lifecycle.json
```

### S3 Lifecycle Policy (s3-lifecycle.json)
```json
{
  "Rules": [
    {
      "Id": "DeleteOldVersions",
      "Status": "Enabled",
      "NoncurrentVersionExpiration": {
        "NoncurrentDays": 90
      }
    },
    {
      "Id": "TransitionToIA",
      "Status": "Enabled",
      "Transitions": [
        {
          "Days": 30,
          "StorageClass": "STANDARD_IA"
        }
      ]
    }
  ]
}
```

---

## Cost Optimization

### 1. **Use S3 Lifecycle Policies**
- Move old versions to cheaper storage (IA, Glacier)
- Delete very old versions automatically

### 2. **Compress Large Files**
```bash
# Before adding to DVC
gzip large_file.csv
dvc add large_file.csv.gz
```

### 3. **Use DVC Cache Efficiently**
```bash
# Clean local cache
dvc gc --workspace

# Remove unused files from remote
dvc gc --cloud
```

### 4. **Monitor S3 Costs**
```bash
# Check bucket size
aws s3 ls s3://ticket-classification-mlops-data --recursive --summarize

# Use AWS Cost Explorer for detailed analysis
```

---

## Next Steps

After completing DVC setup:

1. ✅ **MLflow Integration** - Track experiments and model registry
2. ✅ **Docker Containerization** - Package application
3. ✅ **Airflow Orchestration** - Automate pipeline execution
4. ✅ **Monitoring Setup** - Prometheus + Grafana for observability

---

## Resources

- [DVC Documentation](https://dvc.org/doc)
- [DVC with S3](https://dvc.org/doc/user-guide/data-management/remote-storage/amazon-s3)
- [AWS S3 Documentation](https://docs.aws.amazon.com/s3/)
- [DVC Pipeline Tutorial](https://dvc.org/doc/start/data-pipelines)

---

## Support

For issues or questions:
1. Check this guide's troubleshooting section
2. Review DVC documentation
3. Check project's GitHub issues
4. Contact the MLOps team

---

**Last Updated**: 2026-04-10
**Version**: 1.0.0
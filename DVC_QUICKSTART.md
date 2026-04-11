# DVC Quick Start Guide

## 🚀 Quick Commands Reference

### Initial Setup (One-time)

```bash
# 1. Activate virtual environment
source venv/bin/activate

# 2. Export AWS credentials (add to ~/.bashrc or ~/.zshrc for persistence)
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=ap-south-1

# 3. Verify DVC setup
dvc remote list
# Should show: myremote s3://ticket-classification-bucket-v2/dvc-storage (default)
```

---

## 📥 Daily Workflow - Pull Latest Data

```bash
# Pull all DVC-tracked files from S3
dvc pull

# Or pull specific file
dvc pull data/raw/customer_support_tickets.csv.dvc
```

---

## 📤 Daily Workflow - Push Changes

```bash
# After modifying data or models, track with DVC
dvc add data/processed/new_data.csv

# Add .dvc file to Git
git add data/processed/new_data.csv.dvc data/processed/.gitignore

# Commit to Git
git commit -m "data: Add new processed data"

# Push data to S3
dvc push

# Push code changes to Git
git push
```

---

## 🔄 Working with DVC Pipeline

### Run Full Pipeline
```bash
# Run entire ML pipeline
dvc repro

# This will execute all stages:
# 1. data_preprocessing
# 2. feature_engineering
# 3. model_training
# 4. model_evaluation
# 5. drift_detection
```

### Run Specific Stage
```bash
# Run only model training
dvc repro model_training

# Run only data preprocessing
dvc repro data_preprocessing
```

### Check Pipeline Status
```bash
# Check what needs to be run
dvc status

# View pipeline DAG
dvc dag
```

### View Metrics
```bash
# Show all metrics
dvc metrics show

# Compare metrics between commits
dvc metrics diff HEAD~1
```

---

## 📊 Common DVC Commands

### Status & Info
```bash
# Check DVC status
dvc status

# Check remote status
dvc status -c

# List DVC remotes
dvc remote list

# Show DVC version
dvc version
```

### Data Management
```bash
# Add file/directory to DVC
dvc add <path>

# Remove from DVC tracking
dvc remove <file.dvc>

# Pull from remote
dvc pull

# Push to remote
dvc push

# Fetch from remote (download to cache only)
dvc fetch

# Checkout specific version
git checkout <commit> <file.dvc>
dvc checkout <file.dvc>
```

### Pipeline Management
```bash
# Run pipeline
dvc repro

# Run specific stage
dvc repro <stage_name>

# Show pipeline DAG
dvc dag

# Show metrics
dvc metrics show

# Show plots
dvc plots show
```

---

## 🔍 Troubleshooting

### Issue: AWS Credentials Not Found
```bash
# Solution: Export credentials
export AWS_ACCESS_KEY_ID=your_access_key_here
export AWS_SECRET_ACCESS_KEY=your_secret_key_here
export AWS_DEFAULT_REGION=ap-south-1

# Or add to ~/.bashrc or ~/.zshrc for persistence
echo 'export AWS_ACCESS_KEY_ID=your_access_key_here' >> ~/.bashrc
echo 'export AWS_SECRET_ACCESS_KEY=your_secret_key_here' >> ~/.bashrc
echo 'export AWS_DEFAULT_REGION=ap-south-1' >> ~/.bashrc
source ~/.bashrc
```

### Issue: File Not Found
```bash
# Solution: Pull from S3
dvc pull

# Or pull specific file
dvc pull data/raw/customer_support_tickets.csv.dvc
```

### Issue: Pipeline Stage Failed
```bash
# Solution: Run with verbose output
dvc repro --verbose

# Or run the Python script directly to see errors
python ml_pipeline/data_preprocessing.py
```

### Issue: S3 Permission Denied
```bash
# Solution: Check AWS credentials and IAM permissions
aws sts get-caller-identity

# Verify S3 bucket access
aws s3 ls s3://ticket-classification-bucket-v2/
```

---

## 📁 Current DVC-Tracked Files

### Raw Data
- `data/raw/customer_support_tickets.csv` - Main dataset
- `data/raw/default_categories.csv` - Category definitions

### Models (will be tracked after training)
- `models/trained/mlp_classifier.pth` - Trained MLP model
- `models/trained/label_encoder.pkl` - Label encoder
- `models/embeddings/` - Sentence embeddings

### Processed Data (will be tracked after preprocessing)
- `data/processed/train.csv` - Training data
- `data/processed/val.csv` - Validation data
- `data/processed/test.csv` - Test data

---

## 🎯 Best Practices

### 1. Always Pull Before Starting Work
```bash
git pull
dvc pull
```

### 2. Track Large Files with DVC, Not Git
```bash
# ✅ Good: Track with DVC
dvc add large_file.csv

# ❌ Bad: Track with Git
git add large_file.csv
```

### 3. Commit DVC Files to Git
```bash
# After dvc add, always commit .dvc files
git add file.csv.dvc .gitignore
git commit -m "data: Add new dataset"
```

### 4. Push to Both DVC and Git
```bash
# Push data to S3
dvc push

# Push code to Git
git push
```

### 5. Use Meaningful Commit Messages
```bash
git commit -m "data: Add 1000 new labeled samples"
git commit -m "model: Improve accuracy to 95%"
git commit -m "experiment: Test new architecture"
```

---

## 🔐 Security Notes

### ⚠️ NEVER Commit .env File
The `.env` file contains sensitive AWS credentials and should NEVER be committed to Git.

```bash
# Verify .env is in .gitignore
cat .gitignore | grep .env

# If not, add it
echo ".env" >> .gitignore
```

### ✅ Use Environment Variables
Always use environment variables for credentials, never hardcode them.

---

## 📚 Additional Resources

- [DVC Documentation](https://dvc.org/doc)
- [DVC with S3](https://dvc.org/doc/user-guide/data-management/remote-storage/amazon-s3)
- [DVC Pipeline Tutorial](https://dvc.org/doc/start/data-pipelines)
- [Full Setup Guide](./DVC_SETUP_GUIDE.md)

---

## 🆘 Need Help?

1. Check the [DVC Setup Guide](./DVC_SETUP_GUIDE.md) for detailed instructions
2. Review DVC documentation: https://dvc.org/doc
3. Check project's GitHub issues
4. Contact the MLOps team

---

**Last Updated**: 2026-04-11
**Version**: 1.0.0
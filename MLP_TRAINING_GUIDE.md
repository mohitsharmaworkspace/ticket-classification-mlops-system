# MLP Classifier Training Implementation

## Overview

This system now uses a **PyTorch MLP (Multi-Layer Perceptron)** classifier for ticket classification with actual supervised learning through epochs and backpropagation.

## Architecture

### Two-Stage Approach

1. **Feature Extraction (Frozen)**
   - Sentence Transformer: `all-MiniLM-L6-v2`
   - Converts text → 384-dimensional embeddings
   - Pre-trained, not modified during training

2. **Classification (Trainable)**
   - MLP Neural Network
   - Trained with labeled data
   - Uses epochs, backpropagation, and validation

### MLP Structure

```
Input: 384-dim embedding
    ↓
Dense(256) + ReLU + Dropout(0.3)
    ↓
Dense(128) + ReLU + Dropout(0.2)
    ↓
Dense(num_categories) + Softmax
```

## Three Upload Modes

### Mode 1: Single Text Input
- **Endpoint**: `/api/v1/predict-text`
- **Uses**: Trained MLP model
- **Categories**: Default (15 categories)
- **Speed**: Fast (pre-trained)

### Mode 2: Bulk CSV Upload
- **Endpoint**: `/api/v1/upload-csv`
- **Uses**: Trained MLP model
- **Categories**: Default (15 categories)
- **Speed**: Fast batch processing

### Mode 3: Advanced Mode (Custom Categories)
- **Endpoint**: `/api/v1/upload-with-categories`
- **Uses**: Similarity-based (on-the-fly)
- **Categories**: User-provided custom categories
- **Speed**: Slower (generates embeddings)

## Training Configuration

```yaml
training:
  classifier_type: "mlp"
  
  mlp:
    hidden_layers: [256, 128]
    activation: "relu"
    dropout_rate: [0.3, 0.2]
    
  batch_size: 32
  epochs: 50
  learning_rate: 0.001
  optimizer: "adam"
  loss: "cross_entropy"
  
  early_stopping:
    patience: 5
    min_delta: 0.001
    monitor: "val_loss"
  
  validation_split: 0.2
```

## Training the Model

### Option 1: Using Script

```bash
python scripts/train_initial_model.py
```

### Option 2: Using API

```bash
curl -X POST "http://localhost:8000/api/v1/train" \
  -F "file=@data/raw/customer_support_tickets.csv"
```

**Required CSV Format:**
- `Ticket Description`: The ticket text
- `Ticket Type`: The category label

### Option 3: Programmatic

```python
from ml_pipeline.model_training import MLPModelTrainer

trainer = MLPModelTrainer()
results = trainer.run_training_pipeline()
```

## Training Process

1. **Data Loading**
   - Load tickets with labels
   - Preprocess text (clean, normalize)

2. **Feature Generation**
   - Generate embeddings using frozen sentence transformer
   - Shape: (num_samples, 384)

3. **Model Training**
   - Initialize MLP with random weights
   - Split data: 80% train, 20% validation
   - Train for up to 50 epochs
   - Early stopping if validation loss doesn't improve

4. **Model Saving**
   - Save trained weights: `models/trained/mlp_classifier.pth`
   - Save label encoder for category mapping
   - Save training configuration

## Retraining with Feedback

```bash
curl -X POST "http://localhost:8000/api/v1/retrain"
```

This incorporates user corrections from the feedback system:
- Loads original training data
- Merges with user corrections
- Retrains the model
- Updates the deployed model

## API Endpoints

### Training Endpoints

#### POST `/api/v1/train`
Train model with uploaded data

**Request:**
```bash
curl -X POST "http://localhost:8000/api/v1/train" \
  -F "file=@tickets.csv"
```

**Response:**
```json
{
  "status": "success",
  "training_time": 45.2,
  "num_tickets": 1000,
  "num_categories": 15,
  "metrics": {
    "train_accuracy": 0.92,
    "val_accuracy": 0.89,
    "best_val_loss": 0.25
  }
}
```

#### POST `/api/v1/retrain`
Retrain with feedback

**Response:**
```json
{
  "status": "success",
  "training_time": 38.5,
  "num_tickets": 1050,
  "feedback_count": 50,
  "metrics": {...}
}
```

#### GET `/api/v1/training-status`
Check training status

**Response:**
```json
{
  "trained": true,
  "num_categories": 15,
  "model_type": "MLP",
  "last_modified": "2026-04-10T16:00:00"
}
```

### Prediction Endpoints

#### POST `/api/v1/predict-text`
Single text prediction (uses trained MLP)

#### POST `/api/v1/upload-csv`
Bulk prediction (uses trained MLP)

#### POST `/api/v1/upload-with-categories`
Custom categories (uses similarity)

## File Structure

```
ticket-classification-mlops-system/
├── ml_pipeline/
│   ├── models/
│   │   ├── mlp_classifier.py      # MLP model definition
│   │   ├── trainer.py             # Training logic
│   │   └── predictor.py           # Prediction logic
│   ├── model_training.py          # Training pipeline
│   └── data_preprocessing.py      # Data preprocessing
├── backend/
│   └── app/
│       ├── models/
│       │   └── classifier.py      # Classifier wrapper
│       └── services/
│           ├── training_service.py
│           └── prediction_service.py
├── models/
│   └── trained/
│       ├── mlp_classifier.pth     # Trained model
│       └── best_model.pth         # Best checkpoint
├── scripts/
│   └── train_initial_model.py     # Training script
└── data/
    ├── raw/
    │   ├── customer_support_tickets.csv
    │   └── default_categories.csv
    └── ground_truth/
        └── corrected_labels.csv
```

## Training Metrics

During training, the following metrics are tracked:

- **Train Loss**: Cross-entropy loss on training set
- **Train Accuracy**: Accuracy on training set
- **Validation Loss**: Loss on validation set
- **Validation Accuracy**: Accuracy on validation set

Example output:
```
Epoch 1/50 - Train Loss: 2.1234, Train Acc: 0.4521 - Val Loss: 1.9876, Val Acc: 0.5123
Epoch 2/50 - Train Loss: 1.8765, Train Acc: 0.5678 - Val Loss: 1.7654, Val Acc: 0.6012
...
Epoch 15/50 - Train Loss: 0.3456, Train Acc: 0.9123 - Val Loss: 0.4567, Val Acc: 0.8890
Early stopping at epoch 15
```

## Performance

### Expected Results
- **Training Time**: 2-5 minutes for 1000 samples
- **Accuracy**: 85-95% (depends on data quality)
- **Inference Speed**: <10ms per prediction
- **Model Size**: ~2MB

### Hardware Requirements
- **CPU**: Sufficient for training
- **GPU**: Optional, speeds up training 3-5x
- **RAM**: 4GB minimum, 8GB recommended
- **Disk**: 100MB for model files

## Troubleshooting

### Model Not Found
If you see "Trained model not available":
```bash
python scripts/train_initial_model.py
```

### Low Accuracy
- Check data quality
- Ensure balanced classes
- Increase training epochs
- Collect more training data

### Training Fails
- Verify CSV format
- Check for missing values
- Ensure sufficient memory
- Review error logs

## Advantages

1. **Real Supervised Learning**: Actual training with epochs
2. **Better Performance**: Learns from your specific data
3. **Continuous Improvement**: Retraining with feedback
4. **Fast Inference**: Pre-computed model weights
5. **Flexibility**: Easy to adjust architecture
6. **Production Ready**: Proper model versioning

## Technical Details

### Dependencies
- PyTorch 2.0+
- sentence-transformers 2.2+
- scikit-learn 1.3+
- numpy, pandas

### Model Parameters
- Input dimension: 384 (from sentence transformer)
- Hidden layers: [256, 128]
- Output dimension: num_categories
- Total parameters: ~150K (for 15 categories)

### Training Algorithm
- Optimizer: Adam
- Learning rate: 0.001
- Loss function: Cross-Entropy
- Batch size: 32
- Validation strategy: Stratified split

## Next Steps

1. Train initial model:
   ```bash
   python scripts/train_initial_model.py
   ```

2. Start API:
   ```bash
   cd backend
   python -m app.main
   ```

3. Test predictions:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/predict-text" \
     -H "Content-Type: application/json" \
     -d '{"text": "My laptop won't turn on"}'
   ```

4. Monitor and collect feedback

5. Retrain periodically:
   ```bash
   curl -X POST "http://localhost:8000/api/v1/retrain"
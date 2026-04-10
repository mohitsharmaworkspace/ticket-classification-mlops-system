import torch
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class ModelPredictor:
    def __init__(self, model, label_encoder, device=None):
        self.model = model
        self.label_encoder = label_encoder
        self.device = device or torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        self.model.eval()
    
    @classmethod
    def load_from_checkpoint(cls, model_path=None):
        from ml_pipeline.models.mlp_classifier import MLPClassifier
        from ml_pipeline.config import config
        
        if model_path is None:
            model_path = config.mlp_model_path
        else:
            model_path = Path(model_path)
        
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found at {model_path}")
        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        checkpoint = torch.load(str(model_path), map_location=device)
        
        model = MLPClassifier(
            input_dim=checkpoint['input_dim'],
            num_classes=checkpoint['num_classes'],
            hidden_dims=checkpoint['config'].get('hidden_dims', [256, 128]),
            dropout_rates=checkpoint['config'].get('dropout_rates', [0.3, 0.2])
        )
        
        model.load_state_dict(checkpoint['model_state_dict'])
        label_encoder = checkpoint['label_encoder']
        
        logger.info(f"Model loaded from {str(model_path)}")
        return cls(model, label_encoder, device)
    
    def predict(self, embeddings):
        if isinstance(embeddings, np.ndarray):
            embeddings = torch.FloatTensor(embeddings)
        
        if len(embeddings.shape) == 1:
            embeddings = embeddings.unsqueeze(0)
        
        embeddings = embeddings.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(embeddings)
            probs = torch.softmax(outputs, dim=1)
            predicted_indices = torch.argmax(probs, dim=1)
            confidence_scores = torch.max(probs, dim=1)[0]
        
        predicted_labels = self.label_encoder.inverse_transform(
            predicted_indices.cpu().numpy()
        )
        
        return predicted_labels, confidence_scores.cpu().numpy()
    
    def predict_single(self, embedding):
        labels, scores = self.predict(embedding)
        return labels[0], float(scores[0])
    
    def predict_batch(self, embeddings):
        labels, scores = self.predict(embeddings)
        return list(zip(labels, scores))
    
    def predict_with_all_scores(self, embedding):
        if isinstance(embedding, np.ndarray):
            embedding = torch.FloatTensor(embedding)
        
        if len(embedding.shape) == 1:
            embedding = embedding.unsqueeze(0)
        
        embedding = embedding.to(self.device)
        
        with torch.no_grad():
            outputs = self.model(embedding)
            probs = torch.softmax(outputs, dim=1)[0]
        
        all_scores = {}
        for idx, prob in enumerate(probs.cpu().numpy()):
            label = self.label_encoder.inverse_transform([idx])[0]
            all_scores[label] = float(prob)
        
        predicted_label = max(all_scores.items(), key=lambda x: x[1])[0]
        confidence = all_scores[predicted_label]
        
        return predicted_label, confidence, all_scores

# Made with Bob

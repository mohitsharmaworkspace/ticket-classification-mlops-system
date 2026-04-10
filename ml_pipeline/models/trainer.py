import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import logging
import time
from pathlib import Path
import pickle

logger = logging.getLogger(__name__)

class ModelTrainer:
    def __init__(self, model, config):
        self.model = model
        self.config = config
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.model.to(self.device)
        
        self.optimizer = optim.Adam(
            self.model.parameters(),
            lr=config.get('learning_rate', 0.001)
        )
        self.criterion = nn.CrossEntropyLoss()
        self.label_encoder = LabelEncoder()
        
        self.train_losses = []
        self.val_losses = []
        self.train_accs = []
        self.val_accs = []
        
    def prepare_data(self, embeddings, labels, val_split=0.2):
        encoded_labels = self.label_encoder.fit_transform(labels)
        
        X_train, X_val, y_train, y_val = train_test_split(
            embeddings, encoded_labels,
            test_size=val_split,
            stratify=encoded_labels,
            random_state=42
        )
        
        train_dataset = TensorDataset(
            torch.FloatTensor(X_train),
            torch.LongTensor(y_train)
        )
        val_dataset = TensorDataset(
            torch.FloatTensor(X_val),
            torch.LongTensor(y_val)
        )
        
        batch_size = self.config.get('batch_size', 32)
        train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=batch_size)
        
        return train_loader, val_loader
    
    def train_epoch(self, train_loader):
        self.model.train()
        total_loss = 0
        correct = 0
        total = 0
        
        for batch_x, batch_y in train_loader:
            batch_x = batch_x.to(self.device)
            batch_y = batch_y.to(self.device)
            
            self.optimizer.zero_grad()
            outputs = self.model(batch_x)
            loss = self.criterion(outputs, batch_y)
            
            loss.backward()
            self.optimizer.step()
            
            total_loss += loss.item()
            _, predicted = torch.max(outputs.data, 1)
            total += batch_y.size(0)
            correct += (predicted == batch_y).sum().item()
        
        avg_loss = total_loss / len(train_loader)
        accuracy = correct / total
        return avg_loss, accuracy
    
    def validate(self, val_loader):
        self.model.eval()
        total_loss = 0
        correct = 0
        total = 0
        
        with torch.no_grad():
            for batch_x, batch_y in val_loader:
                batch_x = batch_x.to(self.device)
                batch_y = batch_y.to(self.device)
                
                outputs = self.model(batch_x)
                loss = self.criterion(outputs, batch_y)
                
                total_loss += loss.item()
                _, predicted = torch.max(outputs.data, 1)
                total += batch_y.size(0)
                correct += (predicted == batch_y).sum().item()
        
        avg_loss = total_loss / len(val_loader)
        accuracy = correct / total
        return avg_loss, accuracy
    
    def train(self, embeddings, labels, epochs=50, val_split=0.2):
        logger.info(f"Starting training on {self.device}")
        
        train_loader, val_loader = self.prepare_data(embeddings, labels, val_split)
        
        best_val_loss = float('inf')
        patience = self.config.get('early_stopping_patience', 5)
        patience_counter = 0
        
        start_time = time.time()
        
        for epoch in range(epochs):
            train_loss, train_acc = self.train_epoch(train_loader)
            val_loss, val_acc = self.validate(val_loader)
            
            self.train_losses.append(train_loss)
            self.val_losses.append(val_loss)
            self.train_accs.append(train_acc)
            self.val_accs.append(val_acc)
            
            logger.info(
                f"Epoch {epoch+1}/{epochs} - "
                f"Train Loss: {train_loss:.4f}, Train Acc: {train_acc:.4f} - "
                f"Val Loss: {val_loss:.4f}, Val Acc: {val_acc:.4f}"
            )
            
            if val_loss < best_val_loss:
                best_val_loss = val_loss
                patience_counter = 0
                self.save_checkpoint('best_model.pth')
            else:
                patience_counter += 1
                if patience_counter >= patience:
                    logger.info(f"Early stopping at epoch {epoch+1}")
                    break
        
        training_time = time.time() - start_time
        logger.info(f"Training completed in {training_time:.2f}s")
        
        self.load_checkpoint('best_model.pth')
        
        return {
            'train_losses': self.train_losses,
            'val_losses': self.val_losses,
            'train_accs': self.train_accs,
            'val_accs': self.val_accs,
            'training_time': training_time,
            'best_val_loss': best_val_loss,
            'final_val_acc': self.val_accs[-1] if self.val_accs else 0
        }
    
    def save_checkpoint(self, filename):
        from ml_pipeline.config import config
        models_dir = config.project_root / 'models' / 'trained'
        models_dir.mkdir(parents=True, exist_ok=True)
        filepath = models_dir / filename
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'optimizer_state_dict': self.optimizer.state_dict(),
            'label_encoder': self.label_encoder,
            'config': self.config
        }, filepath)
    
    def load_checkpoint(self, filename):
        from ml_pipeline.config import config
        filepath = config.project_root / 'models' / 'trained' / filename
        checkpoint = torch.load(str(filepath), map_location=self.device)
        self.model.load_state_dict(checkpoint['model_state_dict'])
        self.optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
        self.label_encoder = checkpoint['label_encoder']
    
    def save_model(self, model_path=None):
        from ml_pipeline.config import config
        if model_path is None:
            model_path = config.mlp_model_path
        else:
            model_path = Path(model_path)
        
        model_path.parent.mkdir(parents=True, exist_ok=True)
        torch.save({
            'model_state_dict': self.model.state_dict(),
            'label_encoder': self.label_encoder,
            'config': self.config,
            'input_dim': self.model.input_dim,
            'num_classes': self.model.num_classes
        }, model_path)
        logger.info(f"Model saved to {model_path}")

# Made with Bob

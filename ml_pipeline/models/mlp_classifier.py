import torch
import torch.nn as nn
import torch.nn.functional as F

class MLPClassifier(nn.Module):
    def __init__(self, input_dim=384, hidden_dims=[256, 128], num_classes=15, dropout_rates=[0.3, 0.2]):
        super(MLPClassifier, self).__init__()
        
        self.input_dim = input_dim
        self.num_classes = num_classes
        
        layers = []
        prev_dim = input_dim
        
        for i, hidden_dim in enumerate(hidden_dims):
            layers.append(nn.Linear(prev_dim, hidden_dim))
            layers.append(nn.ReLU())
            if i < len(dropout_rates):
                layers.append(nn.Dropout(dropout_rates[i]))
            prev_dim = hidden_dim
        
        layers.append(nn.Linear(prev_dim, num_classes))
        
        self.network = nn.Sequential(*layers)
    
    def forward(self, x):
        return self.network(x)
    
    def predict_proba(self, x):
        with torch.no_grad():
            logits = self.forward(x)
            probs = F.softmax(logits, dim=1)
        return probs
    
    def predict(self, x):
        probs = self.predict_proba(x)
        return torch.argmax(probs, dim=1)

# Made with Bob

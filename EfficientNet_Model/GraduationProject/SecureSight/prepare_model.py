import torch
import torch.nn as nn
import os

class FeatureClassifier(nn.Module):
    def __init__(self, feature_dim=2560, num_classes=9, dropout=0.3):
        super(FeatureClassifier, self).__init__()
        self.feature_dim = feature_dim
        self.num_classes = num_classes
        self.model = nn.Sequential(
            nn.Linear(feature_dim, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(dropout / 2),
            nn.Linear(256, num_classes)
        )

    def forward(self, x):
        return self.model(x)

def main():
    model = FeatureClassifier()
    model.eval()
    
    # Save to multiple possible locations
    paths = [
        "best_model.pth",
        "models/best_model.pth",
        "outputs/checkpoints/best_model.pth"
    ]
    
    for p in paths:
        dir_name = os.path.dirname(p)
        if dir_name and not os.path.exists(dir_name):
            os.makedirs(dir_name, exist_ok=True)
            
        # We save the state dict
        torch.save({"model_state_dict": model.state_dict()}, p)
        print(f"Created dummy weights at {p}")

if __name__ == "__main__":
    main()

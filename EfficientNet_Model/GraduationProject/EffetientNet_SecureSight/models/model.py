"""
SecureSight Model Module (FIXED VERSION)
Feature-based classifier for video anomaly detection
"""

import torch
import torch.nn as nn


class FeatureClassifier(nn.Module):
    """
    Classifier for pre-extracted features (.npz)
    """

    def __init__(
        self,
        feature_dim: int = 2560,   # لازم يطابق الـ .npz
        num_classes: int = 9,
        dropout: float = 0.3,
    ):
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

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # Expected shape: (B, feature_dim)
        if x.dim() != 2:
            raise ValueError(f"Expected input shape (B, {self.feature_dim}), got {x.shape}")
        return self.model(x)

    def get_num_params(self) -> int:
        return sum(p.numel() for p in self.parameters())

    def get_num_trainable_params(self) -> int:
        return sum(p.numel() for p in self.parameters() if p.requires_grad)


def create_model(
    feature_dim: int = 2560,
    num_classes: int = 9,
    dropout: float = 0.3,
    **kwargs
) -> nn.Module:
    return FeatureClassifier(
        feature_dim=feature_dim,
        num_classes=num_classes,
        dropout=dropout,
    )
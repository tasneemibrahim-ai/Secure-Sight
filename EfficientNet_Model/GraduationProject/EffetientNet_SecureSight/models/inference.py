"""
SecureSight Inference Module (FIXED VERSION)

- Supports 9-class classification (matches training)
- Uses precomputed features (2560-dim)
- NO simulation mode (fails loudly if error)
- Consistent with training pipeline
"""

import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path

# Import model
from model import create_model


class SecureSightInference:
    def __init__(self, model_path: str, device: str = None):
        """
        Args:
            model_path: path to trained checkpoint
            device: 'cuda' or 'cpu'
        """

        if not model_path or not Path(model_path).exists():
            raise FileNotFoundError(f"Model not found at {model_path}")

        self.device = torch.device(device or ("cuda" if torch.cuda.is_available() else "cpu"))

        # 🔥 FIX 1: correct number of classes
        self.class_names = [
            "Arrest",
            "Arson",
            "Explosion",
            "Normal",
            "Physical_Violence",
            "RoadAccidents",
            "Shooting",
            "Theft",
            "Vandalism"
        ]

        self.num_classes = len(self.class_names)

        # 🔥 FIX 2: match training config (features mode)
        self.model = create_model(
            num_classes=self.num_classes,
            feature_dim=2560,
            use_image_backbone=False  # IMPORTANT
        ).to(self.device)

        # Load checkpoint
        checkpoint = torch.load(model_path, map_location=self.device)

        if "model_state_dict" in checkpoint:
            self.model.load_state_dict(checkpoint["model_state_dict"])
        else:
            self.model.load_state_dict(checkpoint)

        self.model.eval()

        print("[SECURESIGHT] Inference engine ready (REAL MODE)")

    def predict_features(self, features: np.ndarray):
        """
        Predict from precomputed features

        Args:
            features: numpy array of shape (2560,) or (1, 2560)

        Returns:
            dict with prediction results
        """

        if features.ndim == 1:
            features = np.expand_dims(features, axis=0)

        if features.shape[1] != 2560:
            raise ValueError(f"Expected feature_dim=2560, got {features.shape}")

        x = torch.tensor(features, dtype=torch.float32).to(self.device)

        with torch.no_grad():
            logits = self.model(x)
            probs = F.softmax(logits, dim=1)

        probs = probs.cpu().numpy()[0]
        pred_class = int(np.argmax(probs))

        return {
            "class": pred_class,
            "class_name": self.class_names[pred_class],
            "probabilities": probs.tolist()
        }

    def predict_from_npz(self, npz_path: str):
        """
        Load features from .npz and predict

        Args:
            npz_path: path to feature file

        Returns:
            prediction dict
        """

        data = np.load(npz_path)

        # Try common keys
        for key in ["features", "arr_0"]:
            if key in data:
                features = data[key]
                break
        else:
            raise KeyError("No valid feature key found in npz")

        return self.predict_features(features)


# ===============================
# TEST
# ===============================
if __name__ == "__main__":
    MODEL_PATH = "path/to/your/model.pth"
    SAMPLE_FEATURE = np.random.rand(2560)

    infer = SecureSightInference(MODEL_PATH)

    result = infer.predict_features(SAMPLE_FEATURE)

    print("\nPrediction Result:")
    print(f"Class: {result['class']} ({result['class_name']})")
    print("Top 3 probs:", sorted(result['probabilities'], reverse=True)[:3])
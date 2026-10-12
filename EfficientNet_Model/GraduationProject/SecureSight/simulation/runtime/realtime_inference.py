"""
SecureSight — Real-Time Inference Engine
==========================================
Uses the EXISTING EfficientNet-B0 + MLP pipeline.
NO retraining. NO architecture changes. NO class mapping changes.
Supports CPU inference and future ONNX deployment.
"""

import sys
import time
import logging
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger("SecureSight.RealtimeInference")

TORCH_AVAILABLE = False
try:
    import torch
    import torch.nn as nn
    import torch.nn.functional as F
    TORCH_AVAILABLE = True
except ImportError:
    pass

NUMPY_AVAILABLE = False
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    pass

ONNX_AVAILABLE = False
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except ImportError:
    pass

EFFICIENTNET_AVAILABLE = False
EFFICIENTNET_DEFAULT_WEIGHTS = None
try:
    from torchvision.models import efficientnet_b0
    try:
        from torchvision.models import EfficientNet_B0_Weights
        EFFICIENTNET_DEFAULT_WEIGHTS = EfficientNet_B0_Weights.IMAGENET1K_V1
    except Exception:
        try:
            # Older torchvision versions may support `weights='DEFAULT'`
            EFFICIENTNET_DEFAULT_WEIGHTS = "DEFAULT"
        except Exception:
            EFFICIENTNET_DEFAULT_WEIGHTS = None
    EFFICIENTNET_AVAILABLE = True
except ImportError:
    pass

CLASS_NAMES = [
    "Arrest", "Arson", "Explosion", "Normal", "Physical_Violence",
    "RoadAccidents", "Shooting", "Theft", "Vandalism",
]

ALERT_CLASSES = [c for c in CLASS_NAMES if c != "Normal"]


class InferenceResult:
    """Holds one inference result."""
    def __init__(self, class_idx=-1, class_name="Unknown", confidence=0.0,
                 probabilities=None, latency_ms=0.0, mode="unknown"):
        self.class_idx = class_idx
        self.class_name = class_name
        self.confidence = confidence
        self.probabilities = probabilities or {}
        self.latency_ms = latency_ms
        self.mode = mode
        self.is_alert = class_name in ALERT_CLASSES and confidence > 0.5
        self.timestamp = time.time()

    def to_dict(self):
        return {
            "class_idx": self.class_idx,
            "class_name": self.class_name,
            "confidence": round(self.confidence, 4),
            "is_alert": self.is_alert,
            "latency_ms": round(self.latency_ms, 2),
            "mode": self.mode,
            "timestamp": self.timestamp,
            "top3": sorted(self.probabilities.items(), key=lambda x: x[1], reverse=True)[:3],
        }


# ── Self-contained model definition (mirrors models/model.py) ──
if TORCH_AVAILABLE:
    class _FeatureClassifier(nn.Module):
        def __init__(self, feature_dim=2560, num_classes=9, dropout=0.3):
            super().__init__()
            self.feature_dim = feature_dim
            self.model = nn.Sequential(
                nn.Linear(feature_dim, 512), nn.ReLU(True), nn.Dropout(dropout),
                nn.Linear(512, 256), nn.ReLU(True), nn.Dropout(dropout / 2),
                nn.Linear(256, num_classes),
            )

        def forward(self, x):
            return self.model(x)


class RealtimeInferenceEngine:
    """
    Real-time inference engine for the SecureSight pipeline.
    Loads the existing trained model and runs frame-level predictions.
    """

    def __init__(self, model_path: Optional[str] = None, device: str = "auto",
                 use_onnx: bool = False, onnx_path: Optional[str] = None):
        self._model = None
        self._feature_extractor = None
        self._onnx_session = None
        self._device = None
        self._mode = "uninitialized"
        self._model_path = model_path
        self._use_onnx = use_onnx
        self._onnx_path = onnx_path
        self._warmup_done = False

        # Resolve device
        if device == "auto":
            if TORCH_AVAILABLE and torch.cuda.is_available():
                self._device_str = "cuda"
            else:
                self._device_str = "cpu"
        else:
            self._device_str = device

    def initialize(self) -> bool:
        """Load model and prepare for inference."""
        if self._use_onnx and ONNX_AVAILABLE and self._onnx_path:
            return self._init_onnx()
        if TORCH_AVAILABLE:
            return self._init_pytorch()
        logger.warning("[Inference] PyTorch/ONNX not available. Running in DUMMY mode.")
        self._mode = "dummy"
        return True

    def _init_pytorch(self) -> bool:
        self._device = torch.device(self._device_str)

        # Load feature extractor (EfficientNet-B0)
        if EFFICIENTNET_AVAILABLE:
            try:
                if EFFICIENTNET_DEFAULT_WEIGHTS is not None:
                    backbone = efficientnet_b0(weights=EFFICIENTNET_DEFAULT_WEIGHTS)
                else:
                    backbone = efficientnet_b0(weights=None)
                    logger.warning("[Inference] Pretrained EfficientNet weights unavailable; loading random weights")
                backbone.classifier = nn.Identity()
                backbone.eval()
                self._feature_extractor = backbone.to(self._device)
                logger.info("[Inference] EfficientNet-B0 feature extractor loaded")
            except Exception as exc:
                logger.warning(f"[Inference] EfficientNet feature extractor failed: {exc}")
                self._feature_extractor = None
                logger.warning("[Inference] Will use random 2560-dim features for inference")
        else:
            logger.warning("[Inference] torchvision not available -- feature extraction disabled")
            self._feature_extractor = None
            logger.warning("[Inference] Will use random 2560-dim features (demo mode)")

        # Load classifier
        self._model = _FeatureClassifier(feature_dim=2560, num_classes=9, dropout=0.3)

        if self._model_path and Path(self._model_path).exists():
            ckpt = torch.load(self._model_path, map_location=self._device)
            if isinstance(ckpt, dict):
                if "model_state_dict" in ckpt:
                    self._model.load_state_dict(ckpt["model_state_dict"])
                elif "state_dict" in ckpt:
                    self._model.load_state_dict(ckpt["state_dict"])
                else:
                    self._model.load_state_dict(ckpt)
            else:
                self._model.load_state_dict(ckpt)
            self._mode = "real"
            logger.info(f"[Inference] Loaded checkpoint: {self._model_path}")
        else:
            self._mode = "demo"
            logger.warning("[Inference] No checkpoint -- using random weights (demo)")

        self._model = self._model.to(self._device)
        self._model.eval()
        print(f"[SecureSight] Inference engine ready | device={self._device_str} | mode={self._mode} | model_path={self._model_path}")
        return True

    def _init_onnx(self) -> bool:
        try:
            providers = ["CPUExecutionProvider"]
            self._onnx_session = ort.InferenceSession(self._onnx_path, providers=providers)
            self._mode = "onnx"
            logger.info(f"[Inference] ONNX model loaded: {self._onnx_path}")
            return True
        except Exception as e:
            logger.error(f"[Inference] ONNX init failed: {e}")
            return False

    def warmup(self, runs: int = 5):
        """Run warmup inference passes."""
        if not TORCH_AVAILABLE or self._model is None:
            return
        dummy = torch.randn(1, 2560).to(self._device)
        with torch.no_grad():
            for _ in range(runs):
                self._model(dummy)
        self._warmup_done = True
        logger.info(f"[Inference] Warmup complete ({runs} runs)")

    def predict_frame(self, frame) -> InferenceResult:
        """
        Run inference on a single frame (numpy HWC uint8).
        Pipeline: frame -> EfficientNet features -> MLP classifier -> result
        """
        if not NUMPY_AVAILABLE:
            return InferenceResult(mode="error")

        t0 = time.perf_counter()

        if TORCH_AVAILABLE and self._model is not None:
            return self._predict_pytorch(frame, t0)
        elif self._onnx_session is not None:
            return self._predict_onnx(frame, t0)
        else:
            return self._predict_dummy(t0)

    def _predict_pytorch(self, frame, t0) -> InferenceResult:
        with torch.no_grad():
            # Extract features
            if self._feature_extractor is not None and frame is not None:
                img = self._preprocess_frame(frame)
                features = self._feature_extractor(img)
            else:
                features = torch.randn(1, 2560).to(self._device)

            logits = self._model(features)
            probs = F.softmax(logits, dim=1).cpu().numpy()[0]

        latency = (time.perf_counter() - t0) * 1000
        idx = int(np.argmax(probs))
        prob_dict = {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))}

        return InferenceResult(
            class_idx=idx, class_name=CLASS_NAMES[idx],
            confidence=float(probs[idx]), probabilities=prob_dict,
            latency_ms=latency, mode=self._mode,
        )

    def _predict_onnx(self, frame, t0) -> InferenceResult:
        features = np.random.randn(1, 2560).astype(np.float32)
        input_name = self._onnx_session.get_inputs()[0].name
        output = self._onnx_session.run(None, {input_name: features})[0]
        probs = self._softmax(output[0])
        latency = (time.perf_counter() - t0) * 1000
        idx = int(np.argmax(probs))
        prob_dict = {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))}
        return InferenceResult(idx, CLASS_NAMES[idx], float(probs[idx]),
                               prob_dict, latency, "onnx")

    def _predict_dummy(self, t0) -> InferenceResult:
        probs = np.random.dirichlet(np.ones(9))
        latency = (time.perf_counter() - t0) * 1000
        idx = int(np.argmax(probs))
        prob_dict = {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))}
        return InferenceResult(idx, CLASS_NAMES[idx], float(probs[idx]),
                               prob_dict, latency, "dummy")

    def _preprocess_frame(self, frame):
        """Resize and normalize frame for EfficientNet input."""
        from torchvision import transforms
        transform = transforms.Compose([
            transforms.ToPILImage(),
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        return transform(frame).unsqueeze(0).to(self._device)

    @staticmethod
    def _softmax(x):
        e = np.exp(x - np.max(x))
        return e / e.sum()

    @property
    def mode(self):
        return self._mode

    @property
    def is_ready(self):
        return self._mode != "uninitialized"

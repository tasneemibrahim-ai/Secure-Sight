"""
SecureSight — Inference Starter Script
========================================
Lightweight script to test model loading and run a single inference pass.
Works with or without a real model checkpoint (uses dummy weights as fallback).

Usage:
  python run_inference.py
  python run_inference.py --model-path path/to/best_model.pth
  python run_inference.py --device cpu
"""

import os
import sys
import time
import argparse
from pathlib import Path

# ─── Attempt imports ───
try:
    import torch
    import torch.nn as nn
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    NUMPY_AVAILABLE = False


# ============================================================
#  MODEL DEFINITION (self-contained copy from models/model.py)
# ============================================================

if TORCH_AVAILABLE:
    class FeatureClassifier(nn.Module):
        """Classifier for pre-extracted EfficientNet features (2560-dim)."""

        def __init__(self, feature_dim=2560, num_classes=9, dropout=0.3):
            super().__init__()
            self.feature_dim = feature_dim
            self.num_classes = num_classes
            self.model = nn.Sequential(
                nn.Linear(feature_dim, 512),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout),
                nn.Linear(512, 256),
                nn.ReLU(inplace=True),
                nn.Dropout(dropout / 2),
                nn.Linear(256, num_classes),
            )

        def forward(self, x):
            if x.dim() != 2:
                raise ValueError(f"Expected (B, {self.feature_dim}), got {x.shape}")
            return self.model(x)

        def get_num_params(self):
            return sum(p.numel() for p in self.parameters())


# ============================================================
#  CLASS NAMES
# ============================================================

CLASS_NAMES = [
    "Arrest", "Arson", "Explosion", "Normal", "Physical_Violence",
    "RoadAccidents", "Shooting", "Theft", "Vandalism",
]


# ============================================================
#  INFERENCE FUNCTIONS
# ============================================================

def detect_device(preferred=None):
    """Detect best available device."""
    if not TORCH_AVAILABLE:
        return "N/A (torch not installed)"

    if preferred and preferred != "auto":
        device = torch.device(preferred)
        print(f"  Device (forced): {device}")
        return device

    if torch.cuda.is_available():
        device = torch.device("cuda")
        print(f"  Device: CUDA — {torch.cuda.get_device_name(0)}")
        print(f"  GPU Memory: {torch.cuda.get_device_properties(0).total_mem / 1e9:.2f} GB")
    else:
        device = torch.device("cpu")
        print(f"  Device: CPU")

    return device


def load_model(model_path=None, device="cpu"):
    """Load model from checkpoint or create with random weights."""
    model = FeatureClassifier(feature_dim=2560, num_classes=9, dropout=0.3)

    if model_path and Path(model_path).exists():
        print(f"  Loading checkpoint: {model_path}")
        checkpoint = torch.load(model_path, map_location=device)
        if "model_state_dict" in checkpoint:
            model.load_state_dict(checkpoint["model_state_dict"])
        elif "state_dict" in checkpoint:
            model.load_state_dict(checkpoint["state_dict"])
        else:
            model.load_state_dict(checkpoint)
        print(f"  ✓ Checkpoint loaded successfully")
        real_weights = True
    else:
        print(f"  ⚠ No checkpoint found — using random weights (demo mode)")
        real_weights = False

    model = model.to(device)
    model.eval()

    params = model.get_num_params()
    print(f"  Model parameters: {params:,}")
    print(f"  Model size: ~{params * 4 / 1024 / 1024:.2f} MB (FP32)")

    return model, real_weights


def run_inference(model, device, num_runs=10):
    """Run inference with dummy tensor and measure timing."""
    # Create dummy input (simulates one pre-extracted EfficientNet feature vector)
    dummy_input = torch.randn(1, 2560).to(device)

    # Warmup
    print(f"\n  Running {num_runs} warmup passes...")
    with torch.no_grad():
        for _ in range(num_runs):
            _ = model(dummy_input)
            if device.type == "cuda":
                torch.cuda.synchronize()

    # Timed inference
    print(f"  Running {num_runs} timed inference passes...")
    times = []
    with torch.no_grad():
        for _ in range(num_runs):
            if device.type == "cuda":
                torch.cuda.synchronize()

            t0 = time.perf_counter()
            output = model(dummy_input)
            if device.type == "cuda":
                torch.cuda.synchronize()
            t1 = time.perf_counter()

            times.append((t1 - t0) * 1000)  # ms

    # Results
    probs = torch.softmax(output, dim=1).cpu().numpy()[0]
    pred_class = int(probs.argmax())

    return {
        "mean_ms": sum(times) / len(times),
        "min_ms": min(times),
        "max_ms": max(times),
        "std_ms": (sum((t - sum(times)/len(times))**2 for t in times) / len(times)) ** 0.5,
        "fps": 1000.0 / (sum(times) / len(times)),
        "predicted_class": pred_class,
        "predicted_label": CLASS_NAMES[pred_class],
        "confidence": float(probs[pred_class]),
        "all_probs": {CLASS_NAMES[i]: float(probs[i]) for i in range(len(CLASS_NAMES))},
    }


# ============================================================
#  MAIN
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="SecureSight Inference Test")
    parser.add_argument("--model-path", type=str, default=None,
                        help="Path to .pth checkpoint")
    parser.add_argument("--device", type=str, default="auto",
                        help="Device: auto, cpu, cuda")
    parser.add_argument("--runs", type=int, default=50,
                        help="Number of inference runs for timing")
    args = parser.parse_args()

    print()
    print("=" * 60)
    print("  SecureSight — Inference Test")
    print("  EfficientNet-B0 Feature Classifier")
    print("=" * 60)

    if not TORCH_AVAILABLE:
        print("\n  ✘ PyTorch not installed. Run:")
        print("    pip install torch torchvision")
        print("  then retry this script.")
        sys.exit(1)

    # Search for model checkpoint if not provided
    search_paths = [
        args.model_path,
        "models/best_model.pth",
        "../models/best_model.pth",
        "../tasnim/outputs/checkpoints/best_model.pth",
        "best_model.pth",
    ]
    model_path = None
    for p in search_paths:
        if p and Path(p).exists():
            model_path = p
            break

    print(f"\n── System Detection ──")
    print(f"  PyTorch: {torch.__version__}")
    device = detect_device(args.device)

    print(f"\n── Model Loading ──")
    model, real_weights = load_model(model_path, device)

    print(f"\n── Inference Test ({args.runs} runs) ──")
    results = run_inference(model, device, num_runs=args.runs)

    print(f"\n── Results ──")
    print(f"  Mean latency:  {results['mean_ms']:.3f} ms")
    print(f"  Min latency:   {results['min_ms']:.3f} ms")
    print(f"  Max latency:   {results['max_ms']:.3f} ms")
    print(f"  Std deviation: {results['std_ms']:.3f} ms")
    print(f"  Throughput:    {results['fps']:.1f} FPS")
    print()
    print(f"  Prediction:    {results['predicted_label']} (class {results['predicted_class']})")
    print(f"  Confidence:    {results['confidence']:.4f}")
    mode = "REAL WEIGHTS" if real_weights else "RANDOM WEIGHTS (demo)"
    print(f"  Mode:          {mode}")

    print()
    print(f"  Top-3 predictions:")
    sorted_probs = sorted(results["all_probs"].items(), key=lambda x: x[1], reverse=True)
    for label, prob in sorted_probs[:3]:
        bar = "█" * int(prob * 30)
        print(f"    {label:20s} {prob:.4f} {bar}")

    print()
    if results["fps"] >= 30:
        print("  ✓ REAL-TIME CAPABLE (>= 30 FPS)")
    elif results["fps"] >= 15:
        print("  ~ NEAR REAL-TIME (15-30 FPS)")
    else:
        print("  ⚠ BELOW REAL-TIME (< 15 FPS)")

    print("=" * 60)
    print()


if __name__ == "__main__":
    main()

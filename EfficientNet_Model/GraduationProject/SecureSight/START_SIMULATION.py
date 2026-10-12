#!/usr/bin/env python3
"""
SecureSight Drone Surveillance Simulation Launcher
Real-Time Anomaly Detection Inference Testing

This script provides a minimal simulation environment to test the
trained EfficientNet-B0 anomaly detection model in real-time.

Usage:
    python START_SIMULATION.py                    # Run with synthetic data
    python START_SIMULATION.py --frames 100       # Process 100 frames
    python START_SIMULATION.py --mock              # Force mock mode (default)
"""

import os
import sys
import time
import argparse
import numpy as np
import torch
import torch.nn.functional as F
from pathlib import Path
from datetime import datetime

# ========================================================
# SETUP PATHS
# ========================================================

PROJECT_ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(PROJECT_ROOT))
sys.path.insert(0, str(PROJECT_ROOT / "models"))
sys.path.insert(0, str(PROJECT_ROOT / "simulation"))

# ========================================================
# CONFIGURATION & IMPORTS
# ========================================================

from simulation.configs.simulation_config import (
    MODEL_CONFIG, 
    find_model_path, 
    get_device_string,
    SIMULATION_LOG_DIR,
    SIMULATION_RESULTS_DIR,
)

try:
    from models.model import FeatureClassifier
except ImportError:
    print("[WARN] Could not import FeatureClassifier from models.model")
    
    # Define inline if import fails
    class FeatureClassifier(torch.nn.Module):
        def __init__(self, feature_dim=2560, num_classes=9, dropout=0.3):
            super().__init__()
            self.model = torch.nn.Sequential(
                torch.nn.Linear(feature_dim, 512),
                torch.nn.ReLU(inplace=True),
                torch.nn.Dropout(dropout),
                torch.nn.Linear(512, 256),
                torch.nn.ReLU(inplace=True),
                torch.nn.Dropout(dropout / 2),
                torch.nn.Linear(256, num_classes)
            )
        def forward(self, x):
            return self.model(x)

# ========================================================
# UTILITIES
# ========================================================

class InferenceEngine:
    """Minimal inference engine for testing"""
    
    def __init__(self, model_path=None, device="cpu"):
        self.device = torch.device(device)
        self.class_names = MODEL_CONFIG["classes"]
        self.num_classes = MODEL_CONFIG["num_classes"]
        self.feature_dim = MODEL_CONFIG["feature_dim"]
        
        # Create or load model
        self.model = FeatureClassifier(
            feature_dim=self.feature_dim,
            num_classes=self.num_classes
        )
        
        if model_path and Path(model_path).exists():
            try:
                checkpoint = torch.load(model_path, map_location=self.device)
                if "model_state_dict" in checkpoint:
                    self.model.load_state_dict(checkpoint["model_state_dict"])
                else:
                    self.model.load_state_dict(checkpoint)
                print(f"[ENGINE] Loaded model from: {model_path}")
            except Exception as e:
                print(f"[ENGINE] Failed to load checkpoint: {e}")
                print(f"[ENGINE] Using randomly initialized model")
        else:
            if model_path:
                print(f"[ENGINE] Model path not found: {model_path}")
            print(f"[ENGINE] Using randomly initialized model (DEMO MODE)")
        
        self.model = self.model.to(self.device)
        self.model.eval()
    
    def infer(self, features):
        """Run inference on features"""
        if isinstance(features, np.ndarray):
            features = torch.from_numpy(features).float()
        
        if features.dim() == 1:
            features = features.unsqueeze(0)
        
        features = features.to(self.device)
        
        with torch.no_grad():
            logits = self.model(features)
            probs = F.softmax(logits, dim=1)
        
        probs = probs.cpu().numpy()[0]
        pred_class = int(np.argmax(probs))
        confidence = float(probs[pred_class])
        
        return {
            "class_idx": pred_class,
            "class_name": self.class_names[pred_class],
            "confidence": confidence,
            "probabilities": probs.tolist(),
            "top3": sorted(
                [(self.class_names[i], probs[i]) for i in range(self.num_classes)],
                key=lambda x: x[1],
                reverse=True
            )[:3]
        }

def generate_synthetic_features(num_samples=1):
    """Generate random feature vectors for testing"""
    return np.random.randn(num_samples, 2560).astype(np.float32)

def print_banner():
    print("\n" + "="*70)
    print("  SECURESIGHT - Drone Surveillance Anomaly Detection Simulation")
    print("  EfficientNet-B0 | 9-Class Detection | Real-Time Inference")
    print("="*70 + "\n")

def print_system_info(device):
    print("[INFO] System Configuration:")
    print(f"  Python:       {sys.version.split()[0]}")
    print(f"  PyTorch:      {torch.__version__}")
    print(f"  Device:       {device}")
    if device == "cuda":
        print(f"  GPU:          {torch.cuda.get_device_name(0)}")
    print()

def run_inference_demo(engine, num_frames=10):
    """Run inference demo with synthetic data"""
    print(f"[DEMO] Running inference on {num_frames} synthetic frames...")
    print()
    
    latencies = []
    anomaly_count = 0
    
    for frame_idx in range(num_frames):
        # Generate synthetic features
        features = generate_synthetic_features(1)[0]
        
        # Infer
        start = time.time()
        result = engine.infer(features)
        latency_ms = (time.time() - start) * 1000
        latencies.append(latency_ms)
        
        # Check if anomaly
        is_anomaly = result["class_name"] != "Normal"
        if is_anomaly:
            anomaly_count += 1
        
        # Print result
        status = "[ALERT]" if is_anomaly else "[OK]"
        print(f"  Frame {frame_idx+1:03d}: {status} {result['class_name']:20s} "
              f"({result['confidence']:.2%}) | {latency_ms:.2f}ms")
    
    # Summary
    print()
    print("[SUMMARY]")
    print(f"  Total frames:       {num_frames}")
    print(f"  Anomalies detected: {anomaly_count}")
    print(f"  Avg latency:        {np.mean(latencies):.2f}ms")
    print(f"  Min latency:        {np.min(latencies):.2f}ms")
    print(f"  Max latency:        {np.max(latencies):.2f}ms")
    
    fps = 1000 / np.mean(latencies)
    print(f"  Avg throughput:     {fps:.1f} FPS")
    print()
    
    return {
        "total_frames": num_frames,
        "anomalies": anomaly_count,
        "avg_latency_ms": float(np.mean(latencies)),
        "fps": float(fps),
    }

def main():
    parser = argparse.ArgumentParser(
        description="SecureSight Simulation Launcher",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--model-path", type=str, default=None,
                        help="Path to .pth model checkpoint")
    parser.add_argument("--frames", type=int, default=50,
                        help="Number of frames to process (default: 50)")
    parser.add_argument("--device", type=str, default="auto",
                        choices=["auto", "cpu", "cuda"],
                        help="Device to use (default: auto)")
    parser.add_argument("--mock", action="store_true", default=True,
                        help="Run in mock/synthetic mode (default)")
    
    args = parser.parse_args()
    
    # Setup
    print_banner()
    
    # Determine device
    if args.device == "auto":
        device = get_device_string()
    else:
        device = args.device
    
    print_system_info(device)
    
    # Find model
    model_path = args.model_path or find_model_path()
    if model_path:
        print(f"[MODEL] Found checkpoint: {model_path}")
    else:
        print(f"[MODEL] No checkpoint found - running in DEMO mode")
    print()
    
    # Create engine
    print("[INIT] Initializing inference engine...")
    engine = InferenceEngine(model_path=model_path, device=device)
    print()
    
    # Run inference test
    try:
        summary = run_inference_demo(engine, num_frames=args.frames)
        
        # Status
        if summary["fps"] >= 30:
            print("[OK] REAL-TIME CAPABLE (>= 30 FPS)")
        elif summary["fps"] >= 15:
            print("[~] NEAR REAL-TIME (15-30 FPS)")
        else:
            print("[!!] BELOW REAL-TIME (< 15 FPS)")
        
        print("\n" + "="*70)
        print("✓ SIMULATION COMPLETED SUCCESSFULLY")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())

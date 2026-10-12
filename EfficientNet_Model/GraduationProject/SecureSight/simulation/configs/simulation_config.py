"""
SecureSight Simulation Configuration
Deployment-ready configuration for drone surveillance anomaly detection
"""

import os
from pathlib import Path
from datetime import datetime

TORCH_AVAILABLE = False
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None

# ========================================================
# PATHS
# ========================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent  # e:\tasnim\GraduationProject\SecureSight
SIMULATION_DIR = PROJECT_ROOT / "simulation"
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

SIMULATION_LOG_DIR = SIMULATION_DIR / "logs"
SIMULATION_RESULTS_DIR = SIMULATION_DIR / "results"

# ========================================================
# MODEL CONFIGURATION
# ========================================================

MODEL_CONFIG = {
    "name": "EfficientNet-B0 Feature Classifier",
    "feature_dim": 2560,  # EfficientNet-B0 features (average pooled)
    "num_classes": 9,
    "classes": [
        "Arrest",
        "Arson",
        "Explosion",
        "Normal",
        "Physical_Violence",
        "RoadAccidents",
        "Shooting",
        "Theft",
        "Vandalism"
    ],
    "use_image_backbone": False,  # Use precomputed features
    "dropout": 0.3,
}

# ========================================================
# DRONE CONFIGURATION
# ========================================================

DRONE_CONFIG = {
    "airsim_host": "127.0.0.1",
    "airsim_port": 41451,
    "drone_name": "Drone1",
    "takeoff_altitude": 10.0,
    "cruise_speed": 5.0,
    "position_delay_ms": 100,
    "timeout_seconds": 30,
}

# ========================================================
# INFERENCE CONFIGURATION
# ========================================================

INFERENCE_CONFIG = {
    "device": "auto",  # auto, cpu, cuda
    "use_onnx": False,
    "onnx_model_path": None,
    "confidence_threshold": 0.5,
    "warmup_runs": 3,
    "batch_size": 1,
    "feature_extraction_model": "efficientnet_b0",  # For image input
}

# ========================================================
# STREAM CONFIGURATION
# ========================================================

STREAM_CONFIG = {
    "source": "synthetic",  # synthetic, webcam, video, airsim
    "video_path": None,
    "webcam_index": 0,
    "frame_width": 640,
    "frame_height": 480,
    "frame_rate": 30,
    "synthetic_anomaly_rate": 0.1,  # Synthetic frame anomaly probability
}

# ========================================================
# PIPELINE CONFIGURATION
# ========================================================

PIPELINE_CONFIG = {
    "confidence_threshold": 0.5,
    "alert_cooldown_seconds": 2.0,
    "log_interval_seconds": 5.0,
    "max_runtime_seconds": 3600,  # 1 hour
    "frame_buffer_size": 100,
    "enable_telemetry": True,
    "enable_alerts": True,
}

# ========================================================
# MONITORING CONFIGURATION
# ========================================================

MONITOR_CONFIG = {
    "fps_window_size": 60,
    "latency_window_size": 60,
    "enable_fps_logging": True,
    "enable_memory_logging": False,
}

# ========================================================
# DEPLOYMENT INFORMATION
# ========================================================

DEPLOYMENT_INFO = {
    "app_name": "SecureSight",
    "app_version": "1.0.0",
    "build_date": datetime.now().isoformat(),
    "model_source": "EfficientNet-B0 Feature Classifier",
    "supported_classes": MODEL_CONFIG["classes"],
    "num_classes": MODEL_CONFIG["num_classes"],
}

# ========================================================
# UTILITY FUNCTIONS
# ========================================================

def find_model_path():
    """
    Find the best trained model checkpoint in the project.
    Search direct known locations first, then scan the repository for any .pth/.pt/.ckpt file.
    """
    candidate_paths = [
        PROJECT_ROOT / "best_model.pth",
        PROJECT_ROOT / "models" / "best_model.pth",
        PROJECT_ROOT / "checkpoints" / "best_model.pth",
        PROJECT_ROOT / "EffetientNet_SecureSight" / "outputs" / "checkpoints" / "best_model.pth",
        PROJECT_ROOT / "EffetientNet_SecureSight" / "best_model.pth",
        MODELS_DIR / "best_model.pth",
        PROJECT_ROOT / "EffetientNet_SecureSight" / "models" / "best_model.pth",
        PROJECT_ROOT / "EffetientNet_SecureSight" / "training" / "best_model.pth",
    ]

    found_paths = []
    for path in candidate_paths:
        if path.exists() and path.is_file():
            found_paths.append(path)
            print(f"[find_model_path] Found direct checkpoint: {path}")

    if not found_paths:
        print("[find_model_path] No direct checkpoint found; scanning repository for .pth/.pt/.ckpt files")
        skip_dirs = {".venv310", ".git", "__pycache__"}
        for path in PROJECT_ROOT.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".pth", ".pt", ".ckpt"}:
                if any(part in skip_dirs for part in path.parts):
                    continue
                found_paths.append(path)
                print(f"[find_model_path] Found checkpoint candidate: {path}")

    if not found_paths:
        print("[find_model_path] No model checkpoint found in repository")
        return None

    best_path = sorted(found_paths, key=lambda p: p.stat().st_mtime, reverse=True)[0]
    print(f"[find_model_path] Using checkpoint: {best_path}")
    return str(best_path)

def get_device_string():
    """
    Get the appropriate device string for torch (cuda or cpu)
    """
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        print(f"[get_device_string] GPU available: {device_name}")
        return "cuda"
    else:
        print(f"[get_device_string] GPU not available, using CPU")
        return "cpu"

# ========================================================
# INITIALIZATION
# ========================================================

def initialize_directories():
    """Create necessary directories if they don't exist"""
    dirs = [SIMULATION_LOG_DIR, SIMULATION_RESULTS_DIR, MODELS_DIR, LOGS_DIR]
    for d in dirs:
        d.mkdir(parents=True, exist_ok=True)
        print(f"[init] Ensured directory: {d}")

# Initialize on import
initialize_directories()

if __name__ == "__main__":
    print("SecureSight Simulation Configuration")
    print("=====================================")
    print(f"Project Root: {PROJECT_ROOT}")
    print(f"Simulation Dir: {SIMULATION_DIR}")
    print(f"Model Config: {MODEL_CONFIG}")
    print(f"Model Path: {find_model_path()}")
    print(f"Device: {get_device_string()}")

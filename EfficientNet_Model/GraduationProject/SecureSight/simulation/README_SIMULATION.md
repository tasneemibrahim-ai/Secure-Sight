# SecureSight — Drone Simulation System

## Overview

This module transforms the SecureSight anomaly detection system into a **drone-based real-time surveillance simulation**. It provides a complete pipeline from simulated drone camera feeds through EfficientNet-B0 feature extraction and MLP classification to real-time alert generation.

**No model retraining. No architecture changes. No class mapping modifications.**

## Architecture

```
Drone Camera Feed (AirSim / Webcam / Video / Synthetic)
        ↓
Frame Capture (FrameReceiver)
        ↓
EfficientNet-B0 Feature Extractor (2560-dim)
        ↓
MLP Classifier (512 → 256 → 9)
        ↓
9-Class Anomaly Detection
        ↓
Alert / Telemetry / Visualization
```

## Classes Detected

| Class | Type |
|-------|------|
| Arrest | Anomaly |
| Arson | Anomaly |
| Explosion | Anomaly |
| Normal | Normal |
| Physical_Violence | Anomaly |
| RoadAccidents | Anomaly |
| Shooting | Anomaly |
| Theft | Anomaly |
| Vandalism | Anomaly |

## Quick Start

```bash
# Run with synthetic frames (no dependencies beyond PyTorch + NumPy)
cd simulation
python START_SIMULATION.py

# Run for 100 frames only
python START_SIMULATION.py --frames 100

# Run for 30 seconds
python START_SIMULATION.py --duration 30

# Use webcam (requires opencv-python)
python START_SIMULATION.py --source webcam

# Use a video file
python START_SIMULATION.py --source video --video-path path/to/video.mp4

# Force CPU
python START_SIMULATION.py --device cpu
```

## Directory Structure

```
simulation/
├── START_SIMULATION.py           # Main orchestrator
├── README_SIMULATION.md          # This file
├── __init__.py
├── airsim_bridge/
│   ├── __init__.py
│   ├── drone_connector.py        # AirSim / Mock drone connector
│   └── frame_receiver.py         # Multi-source frame capture
├── configs/
│   ├── __init__.py
│   └── simulation_config.py      # Central configuration
├── runtime/
│   ├── __init__.py
│   ├── realtime_inference.py     # Inference engine
│   ├── pipeline_manager.py       # Main loop orchestrator
│   ├── fps_monitor.py            # FPS tracking
│   └── latency_monitor.py        # Latency tracking
├── telemetry/
│   ├── __init__.py
│   └── drone_telemetry.py        # Telemetry recording & export
├── streams/
│   ├── __init__.py
│   └── video_stream_manager.py   # Stream abstraction layer
├── logs/                          # Runtime logs
├── results/                       # Session results & telemetry
│   ├── simulation_manifest.json
│   └── SIMULATION_SYSTEM_REPORT.json
└── configs/
    └── simulation_config.py
```

## Supported Modes

| Mode | Requirements | Description |
|------|-------------|-------------|
| **Synthetic** | NumPy | Generated gradient frames, always works |
| **Webcam** | OpenCV | USB camera capture |
| **Video** | OpenCV | Recorded video file playback |
| **AirSim** | airsim package + UE5 | Full drone simulation |

## Dependencies

### Required (minimum)
- Python 3.8+
- PyTorch ≥ 1.10
- NumPy

### Optional
- `opencv-python` — webcam/video support
- `torchvision` — EfficientNet feature extraction
- `airsim` — AirSim drone integration
- `onnxruntime` — ONNX model deployment

### Future (not yet required)
- Unreal Engine 5 + AirSim plugin
- NVIDIA Jetson SDK (edge deployment)

## Future Integration

### AirSim + Unreal Engine 5
1. Install Unreal Engine 5
2. Install AirSim plugin
3. `pip install airsim`
4. Launch UE5 environment with AirSim
5. Run: `python START_SIMULATION.py --source airsim`

### ONNX Deployment
1. Export model: `torch.onnx.export(model, dummy, "model.onnx")`
2. `pip install onnxruntime`
3. Update `simulation_config.py`: `use_onnx = True`

### Edge Deployment (Jetson)
1. Flash Jetson with JetPack
2. Install PyTorch for Jetson
3. Transfer model + simulation code
4. Run with `--device cuda`

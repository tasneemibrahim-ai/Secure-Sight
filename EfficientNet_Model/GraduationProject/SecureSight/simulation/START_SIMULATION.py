"""
================================================================
  SecureSight -- Drone Simulation Launcher
  Real-Time Surveillance Anomaly Detection
================================================================

Main orchestrator for the drone-based surveillance simulation.
Loads model, starts simulated drone pipeline, runs inference loop,
and prints system statistics.

Usage:
    python START_SIMULATION.py
    python START_SIMULATION.py --source webcam
    python START_SIMULATION.py --source video --video-path path/to/video.mp4
    python START_SIMULATION.py --frames 100 --duration 30
    python START_SIMULATION.py --mock   (force mock drone, default)
"""

import os
import sys
import time
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime

# -- Resolve paths --
SIMULATION_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SIMULATION_DIR.parent
sys.path.insert(0, str(SIMULATION_DIR))
sys.path.insert(0, str(PROJECT_ROOT))

# -- Safe imports --
TORCH_AVAILABLE = False
try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    torch = None

NUMPY_AVAILABLE = False
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None

CV2_AVAILABLE = False
try:
    import cv2
    CV2_AVAILABLE = True
except ImportError:
    cv2 = None

TORCHVISION_AVAILABLE = False
try:
    import torchvision
    TORCHVISION_AVAILABLE = True
except ImportError:
    torchvision = None

AIRSIM_AVAILABLE = False
try:
    import airsim
    AIRSIM_AVAILABLE = True
except ImportError:
    airsim = None

ONNX_AVAILABLE = False
try:
    import onnxruntime
    ONNX_AVAILABLE = True
except ImportError:
    onnxruntime = None

# -- Local imports --
from configs.simulation_config import (
    MODEL_CONFIG, DRONE_CONFIG, INFERENCE_CONFIG,
    STREAM_CONFIG, PIPELINE_CONFIG, MONITOR_CONFIG,
    DEPLOYMENT_INFO, find_model_path, get_device_string,
    SIMULATION_LOG_DIR, SIMULATION_RESULTS_DIR,
)
from airsim_bridge.drone_connector import DroneConnector
from airsim_bridge.frame_receiver import FrameReceiver
from runtime.realtime_inference import RealtimeInferenceEngine
from runtime.pipeline_manager import PipelineManager
from runtime.fps_monitor import FPSMonitor
from runtime.latency_monitor import LatencyMonitor
from telemetry.drone_telemetry import DroneTelemetry
from streams.video_stream_manager import VideoStreamManager


# -- Logging setup --
def setup_logging():
    SIMULATION_LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = SIMULATION_LOG_DIR / f"simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        handlers=[
            logging.FileHandler(str(log_file)),
            logging.StreamHandler(sys.stdout),
        ],
    )
    return log_file


def print_banner():
    print()
    print("=" * 64)
    print("  +-------------------------------------------------------+")
    print("  |   SecureSight -- Drone Surveillance Simulation         |")
    print("  |   EfficientNet-B0 | 9-Class Anomaly Detection         |")
    print("  |   Real-Time Inference Pipeline                        |")
    print("  +-------------------------------------------------------+")
    print("=" * 64)
    print()


def print_system_info():
    print("-- System Information --")
    print(f"  Python:       {sys.version.split()[0]}")
    print(f"  Platform:     {sys.platform}")

    if TORCH_AVAILABLE:
        print(f"  PyTorch:      {torch.__version__}")
        if torch.cuda.is_available():
            print(f"  GPU:          {torch.cuda.get_device_name(0)}")
            mem = torch.cuda.get_device_properties(0).total_mem / 1e9
            print(f"  GPU Memory:   {mem:.1f} GB")
        else:
            print(f"  GPU:          Not available (CPU mode)")
    else:
        print(f"  PyTorch:      NOT INSTALLED")

    if TORCHVISION_AVAILABLE:
        print(f"  TorchVision:  {torchvision.__version__}")
    else:
        print(f"  TorchVision:  NOT INSTALLED")

    if NUMPY_AVAILABLE:
        print(f"  NumPy:        {np.__version__}")
    else:
        print(f"  NumPy:        NOT INSTALLED")

    if CV2_AVAILABLE:
        print(f"  OpenCV:       {cv2.__version__}")
    else:
        print(f"  OpenCV:       NOT INSTALLED (synthetic frames only)")

    if AIRSIM_AVAILABLE:
        print(f"  AirSim:       Available")
    else:
        print(f"  AirSim:       NOT INSTALLED (mock drone mode)")

    if ONNX_AVAILABLE:
        print(f"  ONNX Runtime: {onnxruntime.__version__}")
    else:
        print(f"  ONNX Runtime: NOT INSTALLED")

    print()


def run_simulation(args):
    """Main simulation entry point."""

    print_banner()
    log_file = setup_logging()
    logger = logging.getLogger("SecureSight.Main")

    print_system_info()

    # ── 1. Model path ──
    print("-- Model Discovery --")
    model_path = args.model_path or find_model_path()
    if model_path:
        print(f"  [OK] Model found: {model_path}")
    else:
        print(f"  [!!] No model checkpoint found -- running in DEMO mode (random weights)")
    print()

    # ── 2. Drone Connector ──
    print("-- Drone Initialization --")
    drone = DroneConnector(config=DRONE_CONFIG, force_mock=args.mock)
    drone.connect()
    state = drone.get_state()
    print(f"  Backend:    {drone.backend_name}")
    print(f"  Altitude:   {state.altitude_agl:.0f}m AGL")
    print(f"  Battery:    {state.battery_percent:.0f}%")
    print(f"  Position:   ({state.position.x:.1f}, {state.position.y:.1f}, {state.position.z:.1f})")
    print()

    # ── 3. Frame Receiver ──
    print("-- Frame Source --")
    stream_cfg = dict(STREAM_CONFIG)
    if args.video_path:
        stream_cfg["video_path"] = args.video_path
    if args.source:
        stream_cfg["source"] = args.source

    frame_rx = FrameReceiver(config=stream_cfg)
    preferred = stream_cfg.get("source", "synthetic")
    if not frame_rx.initialize(preferred):
        print("  [FAIL] Failed to initialize any frame source!")
        return
    print(f"  [OK] Source: {frame_rx.source_type}")
    print()

    # ── 4. Inference Engine ──
    print("-- Inference Engine --")
    device = get_device_string()
    engine = RealtimeInferenceEngine(
        model_path=model_path,
        device=device,
        use_onnx=INFERENCE_CONFIG.get("use_onnx", False),
        onnx_path=INFERENCE_CONFIG.get("onnx_model_path"),
    )
    if not engine.initialize():
        print("  [FAIL] Inference engine failed to initialize!")
        return

    warmup_runs = INFERENCE_CONFIG.get("warmup_runs", 5)
    engine.warmup(runs=warmup_runs)
    print()

    # ── 5. Monitors ──
    fps_monitor = FPSMonitor(window_size=MONITOR_CONFIG.get("fps_window_size", 60))
    latency_monitor = LatencyMonitor(window_size=MONITOR_CONFIG.get("latency_window_size", 60))

    # ── 6. Telemetry ──
    telemetry = DroneTelemetry(max_records=10000)

    # ── 7. Stream Manager ──
    stream_mgr = VideoStreamManager()
    stream_mgr.register_synthetic()
    stream_mgr.set_active("synthetic_default")

    # ── 8. Pipeline ──
    print("-- Pipeline Configuration --")
    pipeline_cfg = dict(PIPELINE_CONFIG)
    pipeline_cfg["confidence_threshold"] = INFERENCE_CONFIG.get("confidence_threshold", 0.5)
    print(f"  Alert threshold: {pipeline_cfg['confidence_threshold']}")
    print(f"  Alert cooldown:  {pipeline_cfg['alert_cooldown_seconds']}s")
    print(f"  Log interval:    {pipeline_cfg['log_interval_seconds']}s")

    max_frames = args.frames or 0
    duration = args.duration or pipeline_cfg.get("max_runtime_seconds", 0)
    if max_frames:
        print(f"  Max frames:      {max_frames}")
    if duration:
        print(f"  Max duration:    {duration}s")
    print()

    pipeline = PipelineManager(
        frame_receiver=frame_rx,
        inference_engine=engine,
        drone_connector=drone,
        telemetry_recorder=telemetry,
        fps_monitor=fps_monitor,
        latency_monitor=latency_monitor,
        config=pipeline_cfg,
    )

    # ── 9. Run ──
    print("-- Starting Simulation --")
    print(f"  Mode:   {'DEMO' if not model_path else 'REAL'}")
    print(f"  Source:  {frame_rx.source_type}")
    print(f"  Drone:   {drone.backend_name}")
    print(f"  Device:  {device}")
    print()
    print("  Press Ctrl+C to stop")
    print("-" * 64)

    summary = pipeline.run(max_frames=max_frames, duration_seconds=duration)

    # ── 10. Results ──
    print()
    print("=" * 64)
    print("  SESSION SUMMARY")
    print("=" * 64)
    fps_s = summary["fps_stats"]
    lat_s = summary["latency_stats"]
    print(f"  Total frames:     {summary['total_frames']}")
    print(f"  Total alerts:     {summary['total_alerts']}")
    print(f"  Avg FPS:          {fps_s['overall_avg_fps']}")
    print(f"  Peak FPS:         {fps_s['peak_fps']}")
    print(f"  Min FPS:          {fps_s['min_fps']}")
    print(f"  Avg E2E latency:  {lat_s['end_to_end']['mean_ms']:.1f} ms")
    print(f"  Avg Inference:    {lat_s['inference']['mean_ms']:.1f} ms")
    print(f"  Runtime:          {fps_s['elapsed_seconds']:.1f} s")
    print()

    # FPS verdict
    avg = fps_s['overall_avg_fps']
    if avg >= 30:
        print("  [OK] REAL-TIME CAPABLE (>= 30 FPS)")
    elif avg >= 15:
        print("  [~] NEAR REAL-TIME (15-30 FPS)")
    else:
        print("  [!!] BELOW REAL-TIME (< 15 FPS)")

    # ── 11. Export results ──
    SIMULATION_RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")

    telem_path = SIMULATION_RESULTS_DIR / f"telemetry_{ts}.json"
    telemetry.export_json(str(telem_path))

    summary_path = SIMULATION_RESULTS_DIR / f"session_summary_{ts}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, default=str)

    print()
    print(f"  [>] Log file:     {log_file}")
    print(f"  [>] Telemetry:    {telem_path}")
    print(f"  [>] Summary:      {summary_path}")
    print("=" * 64)
    print()

    # Cleanup
    frame_rx.close()
    drone.disconnect()


def main():
    parser = argparse.ArgumentParser(
        description="SecureSight Drone Surveillance Simulation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--model-path", type=str, default=None,
                        help="Path to .pth model checkpoint")
    parser.add_argument("--source", type=str, default="synthetic",
                        choices=["synthetic", "webcam", "video", "airsim"],
                        help="Frame source type")
    parser.add_argument("--video-path", type=str, default=None,
                        help="Path to video file (when --source video)")
    parser.add_argument("--mock", action="store_true", default=True,
                        help="Force mock drone mode (default)")
    parser.add_argument("--frames", type=int, default=0,
                        help="Max frames to process (0=unlimited)")
    parser.add_argument("--duration", type=float, default=0,
                        help="Max runtime in seconds (0=unlimited)")
    parser.add_argument("--device", type=str, default="auto",
                        choices=["auto", "cpu", "cuda"],
                        help="Compute device")
    args = parser.parse_args()

    if args.device != "auto":
        INFERENCE_CONFIG["device"] = args.device

    run_simulation(args)


if __name__ == "__main__":
    main()

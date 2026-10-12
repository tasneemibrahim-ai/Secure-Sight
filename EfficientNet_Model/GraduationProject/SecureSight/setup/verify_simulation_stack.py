import sys
from pathlib import Path
import json

def verify_imports():
    print("--- Verifying Imports ---")
    modules_to_test = [
        "simulation.configs.simulation_config",
        "simulation.airsim_bridge.drone_connector",
        "simulation.airsim_bridge.frame_receiver",
        "simulation.runtime.realtime_inference",
        "simulation.runtime.pipeline_manager",
        "simulation.runtime.fps_monitor",
        "simulation.runtime.latency_monitor",
        "simulation.telemetry.drone_telemetry",
        "simulation.streams.video_stream_manager"
    ]
    
    project_root = Path(__file__).resolve().parent.parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        
    success = True
    for mod in modules_to_test:
        try:
            __import__(mod)
            print(f"  [OK] {mod}")
        except ImportError as e:
            print(f"  [FAIL] {mod}: {e}")
            success = False
    return success

def verify_components():
    print("\n--- Verifying Component Initialization ---")
    
    try:
        from simulation.airsim_bridge.drone_connector import DroneConnector
        from simulation.configs.simulation_config import DRONE_CONFIG
        drone = DroneConnector(config=DRONE_CONFIG, force_mock=True)
        drone.connect()
        state = drone.get_state()
        print(f"  [OK] Mock Drone initialized. Altitude: {state.altitude_agl}m")
        drone.disconnect()
    except Exception as e:
        print(f"  [FAIL] Mock Drone: {e}")
        return False

    try:
        from simulation.airsim_bridge.frame_receiver import FrameReceiver
        from simulation.configs.simulation_config import STREAM_CONFIG
        rx = FrameReceiver(config=STREAM_CONFIG)
        if rx.initialize("synthetic"):
            frame = rx.read_frame()
            print(f"  [OK] Synthetic Camera initialized. Frame size: {frame.metadata.width}x{frame.metadata.height}")
            rx.close()
        else:
             print("  [FAIL] Synthetic Camera initialization failed.")
             return False
    except Exception as e:
        print(f"  [FAIL] Synthetic Camera: {e}")
        return False
        
    try:
        from simulation.runtime.realtime_inference import RealtimeInferenceEngine
        engine = RealtimeInferenceEngine(device="cpu")
        engine.initialize()
        print(f"  [OK] Inference Engine initialized (Mode: {engine.mode})")
    except Exception as e:
        print(f"  [FAIL] Inference Engine: {e}")
        return False
        
    try:
        from simulation.runtime.fps_monitor import FPSMonitor
        fps = FPSMonitor()
        print(f"  [OK] FPS Monitor initialized.")
    except Exception as e:
        print(f"  [FAIL] FPS Monitor: {e}")
        return False
        
    try:
        from simulation.telemetry.drone_telemetry import DroneTelemetry
        telem = DroneTelemetry()
        print(f"  [OK] Telemetry Recorder initialized.")
    except Exception as e:
        print(f"  [FAIL] Telemetry Recorder: {e}")
        return False

    return True

def main():
    print("========================================")
    print("  SecureSight Stack Validator           ")
    print("========================================")
    
    imports_ok = verify_imports()
    comps_ok = verify_components()
    
    stack_ok = imports_ok and comps_ok
    
    print("\n========================================")
    if stack_ok:
        print("  [OK] Simulation stack verified successfully.")
    else:
        print("  [FAIL] Simulation stack verification failed.")
    print("========================================")
    
    out_path = Path(__file__).parent / ".stack_report.json"
    with open(out_path, "w") as f:
        json.dump({"stack_verified": stack_ok}, f, indent=2)

if __name__ == "__main__":
    main()

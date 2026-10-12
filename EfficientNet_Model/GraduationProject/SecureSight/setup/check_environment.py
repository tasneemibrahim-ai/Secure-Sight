import sys
import platform
import json
import psutil
from pathlib import Path

def get_system_info():
    info = {
        "os": platform.system(),
        "os_release": platform.release(),
        "architecture": platform.machine(),
        "python_version": sys.version.split()[0],
        "ram_gb": round(psutil.virtual_memory().total / (1024**3), 2)
    }
    return info

def check_package(package_name):
    try:
        if package_name == "cv2":
            import cv2 as pkg
        elif package_name == "airsim":
            import airsim as pkg
        else:
            pkg = __import__(package_name)
        return {"installed": True, "version": getattr(pkg, '__version__', 'unknown')}
    except ImportError:
        return {"installed": False, "version": None}

def main():
    print("========================================")
    print("  SecureSight Environment Checker       ")
    print("========================================")

    sys_info = get_system_info()
    print("\n--- System Information ---")
    for k, v in sys_info.items():
        print(f"  {k}: {v}")

    packages_to_check = ["torch", "torchvision", "numpy", "cv2", "airsim", "onnxruntime"]
    pkg_status = {}
    
    print("\n--- Dependencies ---")
    for pkg in packages_to_check:
        status = check_package(pkg)
        pkg_status[pkg] = status
        if status["installed"]:
            print(f"  [OK] {pkg}: {status['version']}")
        else:
            print(f"  [MISSING] {pkg}")

    cuda_ready = False
    gpu_info = "None detected"
    
    if pkg_status.get("torch", {}).get("installed"):
        import torch
        cuda_ready = torch.cuda.is_available()
        if cuda_ready:
            gpu_info = torch.cuda.get_device_name(0)
            print(f"\n--- GPU Acceleration ---")
            print(f"  [OK] CUDA Available: True")
            print(f"  [OK] Device: {gpu_info}")
        else:
            print(f"\n--- GPU Acceleration ---")
            print(f"  [WARN] CUDA Available: False (Running on CPU)")
    else:
         print(f"\n--- GPU Acceleration ---")
         print(f"  [FAIL] PyTorch not installed, cannot check CUDA.")

    # Generate a partial report. verify_simulation_stack.py will combine this.
    report = {
        "system": sys_info,
        "gpu": {
            "cuda_available": cuda_ready,
            "device_name": gpu_info
        },
        "dependencies": pkg_status
    }
    
    out_path = Path(__file__).parent / ".env_report.json"
    with open(out_path, "w") as f:
        json.dump(report, f, indent=2)
        
    print("\n[OK] Environment check complete.")

if __name__ == "__main__":
    main()

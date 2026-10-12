import sys
import subprocess
import argparse

def install(package):
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        print(f"[OK] Installed {package}")
        return True
    except subprocess.CalledProcessError:
        print(f"[FAIL] Failed to install {package}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Install SecureSight Simulation Dependencies")
    parser.add_argument("--cuda", action="store_true", help="Install CUDA-enabled PyTorch")
    args = parser.parse_args()

    print("========================================")
    print("  SecureSight Dependency Installer      ")
    print("========================================")

    # Core dependencies
    core_deps = [
        "numpy",
        "opencv-python",
        "msgpack-rpc-python", # Required for AirSim
        "airsim",
        "onnxruntime"
    ]

    print("\n--- Installing Core Dependencies ---")
    for dep in core_deps:
        install(dep)

    print("\n--- Installing PyTorch ---")
    if args.cuda:
        print("Installing PyTorch with CUDA support...")
        # Note: The exact URL might change depending on the current PyTorch version and CUDA version.
        # This is a general safe command for Windows with pip.
        try:
             subprocess.check_call([sys.executable, "-m", "pip", "install", "torch", "torchvision", "--index-url", "https://download.pytorch.org/whl/cu118"])
             print("[OK] Installed PyTorch (CUDA)")
        except subprocess.CalledProcessError:
             print("[FAIL] Failed to install PyTorch (CUDA)")
    else:
        print("Installing PyTorch for CPU...")
        try:
             subprocess.check_call([sys.executable, "-m", "pip", "install", "torch", "torchvision"])
             print("[OK] Installed PyTorch (CPU)")
        except subprocess.CalledProcessError:
             print("[FAIL] Failed to install PyTorch (CPU)")

    print("\n========================================")
    print("  Installation Complete                 ")
    print("  Run check_environment.py to verify.   ")
    print("========================================")

if __name__ == "__main__":
    main()

"""
SecureSight Environment Setup Script
Comprehensive setup for Python 3.10 venv with all dependencies
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description="", timeout=600):
    """Run a command and return success status"""
    print(f"\n{'='*60}")
    print(f"[SETUP] {description}")
    print(f"[CMD] {cmd}")
    print('='*60)
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=False,
            text=True,
            timeout=timeout
        )
        if result.returncode == 0:
            print(f"✓ SUCCESS: {description}")
            return True
        else:
            print(f"✗ FAILED: {description} (exit code: {result.returncode})")
            return False
    except subprocess.TimeoutExpired:
        print(f"✗ TIMEOUT: {description} (exceeded {timeout}s)")
        return False
    except Exception as e:
        print(f"✗ ERROR: {description} - {e}")
        return False

def main():
    print("\n" + "="*60)
    print("SecureSight Environment Setup")
    print("="*60 + "\n")
    
    # Get venv python executable
    venv_python = ".\\venv310\\Scripts\\python.exe"
    venv_pip = f"{venv_python} -m pip"
    
    # Step 1: Upgrade pip
    run_command(
        f"{venv_pip} install --upgrade pip setuptools wheel",
        "Upgrade pip, setuptools, and wheel",
        timeout=180
    )
    
    # Step 2: Install PyTorch CPU-safe
    run_command(
        f"{venv_pip} install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu",
        "Install PyTorch (CPU version)",
        timeout=300
    )
    
    # Step 3: Verify PyTorch
    run_command(
        f"{venv_python} -c \"import torch; print(f'PyTorch {{torch.__version__}} loaded'); print(f'CUDA available: {{torch.cuda.is_available()}}')\"",
        "Verify PyTorch installation",
        timeout=30
    )
    
    # Step 4: Install all other dependencies
    deps = [
        "numpy",
        "opencv-python",
        "pillow",
        "matplotlib",
        "scikit-learn",
        "pandas",
        "tqdm",
        "onnx",
        "onnxruntime",
        "psutil",
        "pyyaml",
        "scipy",
        "seaborn",
        "requests",
        "rich",
    ]
    
    deps_str = " ".join(deps)
    run_command(
        f"{venv_pip} install {deps_str}",
        "Install all project dependencies",
        timeout=300
    )
    
    # Step 5: Try to install airsim (may fail)
    run_command(
        f"{venv_pip} install msgpack-rpc-python",
        "Install msgpack-rpc-python (for airsim)",
        timeout=120
    )
    
    run_command(
        f"{venv_pip} install airsim --no-build-isolation",
        "Install airsim (may fail, that's OK for mock mode)",
        timeout=120
    )
    
    # Step 6: Verify all imports
    imports_script = """
import sys
imports = {
    'torch': 'PyTorch',
    'torchvision': 'TorchVision',
    'cv2': 'OpenCV',
    'numpy': 'NumPy',
    'onnxruntime': 'ONNX Runtime',
    'onnx': 'ONNX',
    'sklearn': 'scikit-learn',
    'PIL': 'Pillow',
    'pandas': 'Pandas',
    'yaml': 'PyYAML',
}

print("\\n[IMPORTS] Verifying Python packages:")
failed = []
for module, name in imports.items():
    try:
        __import__(module)
        print(f"  ✓ {name}")
    except ImportError as e:
        print(f"  ✗ {name}: {e}")
        failed.append(name)

if failed:
    print(f"\\n✗ Failed to import: {', '.join(failed)}")
    sys.exit(1)
else:
    print(f"\\n✓ All critical imports successful")
    sys.exit(0)
"""
    
    with open("_verify_imports.py", "w") as f:
        f.write(imports_script)
    
    run_command(
        f"{venv_python} _verify_imports.py",
        "Verify all required imports",
        timeout=30
    )
    
    os.remove("_verify_imports.py")
    
    print("\n" + "="*60)
    print("✓ SETUP COMPLETE")
    print("="*60)
    print(f"\nTo activate the environment, run:")
    print(f"  .\\venv310\\Scripts\\Activate.ps1")
    print(f"\nOr use Python directly:")
    print(f"  {venv_python}")

if __name__ == "__main__":
    main()

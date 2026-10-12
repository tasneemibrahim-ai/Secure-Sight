#!/bin/bash
# ============================================================
#  SecureSight — Environment Setup (Linux/macOS)
#  AI Video Anomaly Detection — EfficientNet-B0
# ============================================================
#  Usage:  bash install_requirements.sh
#  Run from the Recovered_Project/environment_setup/ folder
# ============================================================

set -e

echo "============================================================"
echo "  SecureSight Environment Setup"
echo "============================================================"
echo ""

# Step 1: Check Python
echo "[1/5] Checking Python installation..."
python3 --version || { echo "ERROR: Python3 not found."; exit 1; }

# Step 2: Create virtual environment
echo ""
echo "[2/5] Creating virtual environment..."
if [ ! -d "../venv" ]; then
    python3 -m venv ../venv
    echo "  Virtual environment created at ../venv"
else
    echo "  Virtual environment already exists."
fi

# Step 3: Activate venv
echo ""
echo "[3/5] Activating virtual environment..."
source ../venv/bin/activate

# Step 4: Upgrade pip
echo ""
echo "[4/5] Upgrading pip..."
pip install --upgrade pip

# Step 5: Install requirements
echo ""
echo "[5/5] Installing requirements..."
pip install -r requirements.txt

# Extra: Install deployment dependencies
echo ""
echo "[EXTRA] Installing deployment + benchmarking dependencies..."
pip install fastapi uvicorn paramiko onnx onnxruntime psutil

echo ""
echo "============================================================"
echo "  Setup complete!"
echo "  Activate with: source ../venv/bin/activate"
echo "============================================================"

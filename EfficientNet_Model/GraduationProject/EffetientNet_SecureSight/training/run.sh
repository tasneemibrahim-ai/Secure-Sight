#!/bin/bash
# ============================================
# tasnim - Training Script
# University GPU Server
# ============================================
# Usage:
#   1. Upload tasnim/ folder to server
#   2. SSH into server: ssh secure-sight@10.55.205.205
#   3. cd tasnim
#   4. bash run.sh [epochs] [batch_size] [lr] [run_name]
# ============================================

set -e  # Exit on error

echo "============================================"
echo "  tasnim - Training Pipeline"
echo "============================================"

# Step 1: Check GPU availability
echo ""
echo "[Step 1] Checking system..."
python3 -c "
import torch
print(f'  PyTorch version: {torch.__version__}')
if torch.cuda.is_available():
    print(f'  GPU: {torch.cuda.get_device_name(0)}')
    print(f'  GPU Memory: {torch.cuda.get_device_properties(0).total_mem / 1e9:.2f} GB')
else:
    print('  WARNING: No GPU detected, training will be slow on CPU')
"

# Step 2: Install dependencies
echo ""
echo "[Step 2] Installing dependencies..."
pip install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt

# Step 3: Discover data directory
echo ""
echo "[Step 3] Checking data directory..."
python3 -c "
import os
paths = [
    os.path.expanduser('~/data/UCF-Crime'),
    os.path.expanduser('~/UCF-Crime'),
    '/data/UCF-Crime',
]
for p in paths:
    if os.path.exists(p):
        print(f'  Found data at: {p}')
        for split in ['Train', 'Val']:
            sp = os.path.join(p, split)
            if os.path.exists(sp):
                for cls in ['Normal', 'Anomaly']:
                    cp = os.path.join(sp, cls)
                    if os.path.exists(cp):
                        count = sum(1 for _ in os.scandir(cp))
                        print(f'    {split}/{cls}: {count} items')
        break
else:
    print('  WARNING: Data directory not found automatically!')
    print('  Edit DATA_ROOT in config.py to point to your UCF-Crime frames.')
"

# Step 4: Run training
echo ""
echo "[Step 4] Starting training..."
echo "============================================"

# Parse command-line arguments or use defaults
EPOCHS=${1:-50}
BATCH_SIZE=${2:-32}
LR=${3:-1e-4}
RUN_NAME=${4:-""}

TRAIN_CMD="python3 train.py --epochs $EPOCHS --batch_size $BATCH_SIZE --lr $LR"
if [ -n "$RUN_NAME" ]; then
    TRAIN_CMD="$TRAIN_CMD --run_name $RUN_NAME"
fi

eval $TRAIN_CMD

echo ""
echo "============================================"
echo "  Pipeline Complete!"
echo "  Check: outputs/logs/training_results.csv"
echo "  Check: outputs/logs/training_curves.png"
echo "  Check: outputs/runs/   (per-run results)"
echo "  Check: outputs/all_runs_report.txt"
echo "  Check: outputs/all_runs_comparison.png"
echo "  Check: outputs/checkpoints/best_model.pth"
echo "============================================"
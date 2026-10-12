# SecureSight - Video Anomaly Detection

A production-ready PyTorch implementation for video anomaly detection using EfficientNet-B0, designed for the UCF-Crime dataset.

## Project Structure

```
SecureSight/
├── config.py          # Configuration and hyperparameters
├── dataset.py         # Data loading, augmentation, weighted sampling
├── model.py           # EfficientNet-B0 model definition
├── train.py           # Main training script with CLI
├── utils.py           # Metrics, plotting, checkpoints, latency
├── requirements.txt   # Python dependencies
├── run.sh             # One-command training script
└── README.md          # This file
```

## Quick Start on University Server

### 1. Upload to Server

```bash
# From your local machine (PowerShell / terminal)
scp -r SecureSight/ secure-sight@10.55.205.205:/home/secure-sight/
```

### 2. SSH into Server

```bash
ssh secure-sight@10.55.205.205
cd SecureSight
```

### 3. Run Training (one command)

```bash
bash run.sh
```

This automatically:
- Checks GPU availability
- Installs dependencies
- Discovers the data directory
- Starts training for 50 epochs

### 4. Custom Training

```bash
# With custom parameters
python3 train.py --epochs 30 --batch_size 16 --lr 1e-4

# Resume from checkpoint
python3 train.py --resume outputs/checkpoints/best_model.pth
```

## Dataset Structure

The UCF-Crime extracted frames should be organized as:

```
/home/secure-sight/data/UCF-Crime/
├── Train/
│   ├── Anomaly/
│   │   ├── Abuse001/
│   │   │   ├── frame_0001.jpg
│   │   │   └── ...
│   │   ├── Arrest002/
│   │   └── ...
│   └── Normal/
│       ├── Normal_001/
│       └── ...
├── Val/
│   ├── Anomaly/
│   └── Normal/
```

> **Note**: The data preprocessing code is already on the server. If frames aren't extracted yet, run the server's preprocessing scripts first.

## Configuration

Edit `config.py` to customize:

| Setting | Description | Default |
|---------|-------------|---------|
| `DATA_ROOT` | Path to extracted frames | Auto-detected |
| `BATCH_SIZE` | Training batch size | 32 |
| `LEARNING_RATE` | Initial learning rate | 1e-4 |
| `NUM_EPOCHS` | Maximum training epochs | 50 |
| `DROPOUT` | Dropout probability | 0.3 |
| `EARLY_STOPPING_PATIENCE` | Stop after N epochs without improvement | 10 |

## Key Features

- **EfficientNet-B0 backbone** — lightweight, low latency
- **Class imbalance handling** — weighted loss + WeightedRandomSampler
- **Mixed precision training** — FP16 for faster computation
- **Early stopping** — prevents overfitting
- **Complete metrics** — Loss, Accuracy, Precision, Recall, F1, AUC-ROC
- **CSV logging** — epoch-by-epoch results saved automatically
- **Training curves** — loss, accuracy, F1 plotted as PNG
- **Latency profiling** — mean, P50, P95, P99 inference latency
- **Checkpoint saving** — best model + periodic checkpoints

## Output Files

After training:

| File | Description |
|------|-------------|
| `outputs/logs/training_results.csv` | Per-epoch metrics |
| `outputs/logs/training_curves.png` | Loss/Accuracy/F1 plots |
| `outputs/checkpoints/best_model.pth` | Best model weights |

## CLI Options

| Option | Description | Default |
|--------|-------------|---------|
| `--epochs` | Number of training epochs | 50 |
| `--batch_size` | Batch size | 32 |
| `--lr` | Learning rate | 1e-4 |
| `--dropout` | Dropout rate | 0.3 |
| `--resume` | Resume from checkpoint path | None |
| `--no_aug` | Disable data augmentation | False |
| `--no_mixed_precision` | Disable FP16 training | False |

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Out of Memory | Reduce batch size: `--batch_size 16` |
| No GPU | Code auto-falls back to CPU |
| Dataset not found | Edit `DATA_ROOT` in `config.py` |
| Permission denied | Run `chmod +x run.sh` |
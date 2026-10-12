"""
SecureSight Configuration File (FINAL FIXED)
"""

import os

CODE_ROOT = os.environ.get("SECURESIGHT_CODE_ROOT", "/home/secure-sight/Code")

# ========================
# DATA PATHS
# ========================

DATA_ROOT = os.path.join(CODE_ROOT, "clean_split", "train")
VAL_ROOT = os.path.join(CODE_ROOT, "clean_split", "val")

CLASS_NAMES = sorted([
    d for d in os.listdir(DATA_ROOT)
    if os.path.isdir(os.path.join(DATA_ROOT, d))
])

TRAIN_DIRS = [os.path.join(DATA_ROOT, c) for c in CLASS_NAMES]
VAL_DIRS = [os.path.join(VAL_ROOT, c) for c in CLASS_NAMES]

NUM_CLASSES = len(CLASS_NAMES)

CLASS_DISPLAY_NAMES = [
    "Normal" if c == "Normal_Videos" else c for c in CLASS_NAMES
]

# ========================
# IMAGE / FEATURE CONFIG
# ========================
FRAME_SIZE = (224, 224)
AUG_PROBS = {
    "horizontal_flip": 0.5,
}

# ========================
# FEATURES
# ========================

FEATURE_DIM = 2560
USE_PRECOMPUTED_FEATURES = True
USE_IMAGE_BACKBONE = False

# ========================
# OUTPUT
# ========================

OUTPUT_DIR = os.path.join(CODE_ROOT, "output")
CHECKPOINT_DIR = os.path.join(OUTPUT_DIR, "checkpoints")
LOG_DIR = os.path.join(OUTPUT_DIR, "logs")

# ========================
# MODEL
# ========================

MODEL_NAME = "efficientnet_b0"
PRETRAINED = True
DROPOUT = 0.3

# ========================
# TRAINING
# ========================

BATCH_SIZE = 32
NUM_WORKERS = 4
NUM_EPOCHS = 50

LEARNING_RATE = 5e-5
WEIGHT_DECAY = 1e-5

OPTIMIZER = "adamw"

EARLY_STOPPING_PATIENCE = 10

OVERSAMPLE_MINORITY = True
SAMPLING_STRATEGY = "ratio"

USE_MIXED_PRECISION = True

# ========================
# 🔥 FOCAL LOSS
# ========================

USE_FOCAL_LOSS = True
FOCAL_GAMMA = 2.0
FOCAL_ALPHA = None  # None = use class weights

# ========================
# SYSTEM
# ========================

DEVICE = "cuda"
SEED = 42

# ========================
# LOGGING
# ========================

SAVE_INTERVAL = 5
RESULTS_CSV = "training_results.csv"
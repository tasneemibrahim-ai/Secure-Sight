# Sample Inputs — README
# =======================
#
# This folder holds test inputs for the SecureSight anomaly detection pipeline.
#
# EXPECTED INPUT FORMAT:
# ──────────────────────
#
# The model operates on PRE-EXTRACTED EfficientNet-B0 features, NOT raw images.
#
# Primary Input Format:
#   .npz files containing:
#     - Key: "fused_features"
#     - Shape: (num_clips, 2560)  — each clip is a 2560-dimensional feature vector
#     - Type: float32
#
# Alternative Input (for future raw-frame mode):
#   .jpg / .png images:
#     - Resolution: 224 × 224 pixels (resized by pipeline)
#     - Color: RGB (3 channels)
#     - Normalization: ImageNet (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
#
# Video Input (for real-time emulation):
#   .mp4 / .avi files:
#     - Frames extracted and processed individually
#     - Recommended: 30 FPS, 720p or 1080p
#
# HOW TO CREATE TEST INPUTS:
# ──────────────────────────
#
# Option 1: Dummy features (for testing pipeline)
#   import numpy as np
#   features = np.random.randn(10, 2560).astype(np.float32)
#   np.savez("sample_features.npz", fused_features=features)
#
# Option 2: Extract from real video (requires timm + EfficientNet-B0)
#   # See exports/export_onnx.py or training/server_efficientnet_pipeline.py
#
# Option 3: Use UCF-Crime dataset samples
#   # Download from: https://www.crcv.ucf.edu/projects/real-world/
#
# PLACEHOLDER FILES:
# ──────────────────
#   sample_features.npz      — TODO: Generate with dummy data
#   test_frame_normal.jpg     — TODO: Add sample normal surveillance frame
#   test_frame_anomaly.jpg    — TODO: Add sample anomaly frame
#   test_video_clip.mp4       — TODO: Add short test video clip
#
# CLASSES (9):
#   0: Arrest
#   1: Arson
#   2: Explosion
#   3: Normal
#   4: Physical_Violence
#   5: RoadAccidents
#   6: Shooting
#   7: Theft
#   8: Vandalism

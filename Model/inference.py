#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import ResNet50_Weights, resnet50
from torchvision.models.video import R2Plus1D_18_Weights, r2plus1d_18


CLASSES = [
    "Normal_Videos",
    "Physical_Violence",
    "Theft",
    "Arrest",
    "Arson",
    "Explosion",
    "RoadAccidents",
    "Shooting",
    "Vandalism",
]
DISPLAY_LABELS = {
    "Normal_Videos": "Normal",
    "Physical_Violence": "Physical Violence",
}
NORMAL_CLASS = "Normal"
CONFIDENCE_THRESHOLD = 0.7
TEMPERATURE = 1.5  # softens overconfident softmax; increase to spread more, decrease to sharpen
SPATIAL_MEAN = torch.tensor([0.485, 0.456, 0.406], dtype=torch.float32).view(3, 1, 1)
SPATIAL_STD = torch.tensor([0.229, 0.224, 0.225], dtype=torch.float32).view(3, 1, 1)
TEMPORAL_MEAN = torch.tensor([0.43216, 0.394666, 0.37645], dtype=torch.float32).view(3, 1, 1, 1)
TEMPORAL_STD = torch.tensor([0.22803, 0.22145, 0.216989], dtype=torch.float32).view(3, 1, 1, 1)


class FeatureFusion(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.linear = nn.Linear(2560, 512)
        self.norm = nn.LayerNorm(512)

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.norm(F.relu(self.linear(features)))


class TemporalClassifier(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.cls_token = nn.Parameter(torch.zeros(1, 1, 512))
        self.position_embedding = nn.Parameter(torch.zeros(1, 9, 512))
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=512,
            nhead=8,
            dim_feedforward=2048,
            dropout=0.0,
            activation="relu",
            batch_first=True,
        )
        self.encoder = nn.TransformerEncoder(encoder_layer, num_layers=4)
        self.norm = nn.LayerNorm(512)
        self.head = nn.Linear(512, len(CLASSES))

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        if features.shape[1] > self.position_embedding.shape[1] - 1:
            features = features[:, : self.position_embedding.shape[1] - 1, :]
        cls_token = self.cls_token.expand(features.shape[0], -1, -1)
        tokens = torch.cat([cls_token, features], dim=1)
        tokens = tokens + self.position_embedding[:, : tokens.shape[1], :]
        encoded = self.encoder(tokens)
        return self.head(self.norm(encoded[:, 0]))


class SecureSightModel(nn.Module):
    def __init__(self) -> None:
        super().__init__()
        self.fusion = FeatureFusion()
        self.transformer = TemporalClassifier()

    def forward(self, fused_features: torch.Tensor) -> torch.Tensor:
        return self.transformer(self.fusion(fused_features))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run SecureSight video classification.")
    parser.add_argument("--video", required=True, help="Local path or camera/video URL.")
    parser.add_argument("--model", default=str(Path(__file__).with_name("best.pt")))
    parser.add_argument("--timestamp", type=float, default=0.0)
    parser.add_argument("--window-seconds", type=float, default=5.0)
    parser.add_argument("--device", default="cuda" if torch.cuda.is_available() else "cpu")
    return parser.parse_args()


def safe_load_state_dict(model_path: Path) -> dict[str, torch.Tensor]:
    checkpoint = torch.load(model_path, map_location="cpu")
    if isinstance(checkpoint, dict):
        return checkpoint.get("model_state_dict") or checkpoint.get("state_dict") or checkpoint
    raise RuntimeError("Unsupported checkpoint format.")


def display_label(class_name: str) -> str:
    return DISPLAY_LABELS.get(class_name, class_name)


def build_feature_extractors(device: torch.device) -> tuple[nn.Module, nn.Module]:
    spatial_model = resnet50(weights=ResNet50_Weights.DEFAULT)
    spatial_model.fc = nn.Identity()
    spatial_model.eval().to(device)

    temporal_model = r2plus1d_18(weights=R2Plus1D_18_Weights.DEFAULT)
    temporal_model.fc = nn.Identity()
    temporal_model.eval().to(device)

    return spatial_model, temporal_model


def load_window(video: str, timestamp: float, window_seconds: float, target_fps: float = 5.0) -> tuple[list[np.ndarray], float]:
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video source: {video}")

    source_fps = cap.get(cv2.CAP_PROP_FPS)
    if not source_fps or math.isnan(source_fps) or source_fps <= 0:
        source_fps = 30.0

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / source_fps if frame_count > 0 else 0.0
    start_time = max(0.0, timestamp)
    if duration:
        start_time = min(start_time, max(0.0, duration - 0.1))

    sample_times = np.arange(start_time, start_time + window_seconds, 1.0 / target_fps, dtype=np.float64)
    if duration:
        sample_times = sample_times[sample_times < duration]

    frames: list[np.ndarray] = []
    for sample_time in sample_times:
        cap.set(cv2.CAP_PROP_POS_MSEC, float(sample_time * 1000.0))
        ok, frame_bgr = cap.read()
        if ok:
            frames.append(cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB))

    cap.release()
    return frames, duration


def build_clips(frames: list[np.ndarray], clip_len: int = 16) -> list[np.ndarray]:
    if not frames:
        return []
    while len(frames) < clip_len:
        frames.append(frames[-1])
    return [np.stack(frames[start : start + clip_len], axis=0) for start in range(0, len(frames) - clip_len + 1, clip_len)]


def preprocess_spatial(center_frame: np.ndarray, image_size: int = 224) -> torch.Tensor:
    frame = torch.from_numpy(center_frame).permute(2, 0, 1).float() / 255.0
    frame = F.interpolate(frame.unsqueeze(0), size=(image_size, image_size), mode="bilinear", align_corners=False)
    return (frame.squeeze(0) - SPATIAL_MEAN) / SPATIAL_STD


def preprocess_temporal(clip: np.ndarray, image_size: int = 112) -> torch.Tensor:
    clip_tensor = torch.from_numpy(clip).permute(3, 0, 1, 2).float() / 255.0
    clip_tensor = F.interpolate(
        clip_tensor.permute(1, 0, 2, 3),
        size=(image_size, image_size),
        mode="bilinear",
        align_corners=False,
    ).permute(1, 0, 2, 3)
    return (clip_tensor - TEMPORAL_MEAN) / TEMPORAL_STD


def classify(args: argparse.Namespace) -> dict[str, object]:
    device = torch.device(args.device)
    model = SecureSightModel()
    model.load_state_dict(safe_load_state_dict(Path(args.model)), strict=True)
    model.eval().to(device)

    frames, duration = load_window(args.video, args.timestamp, args.window_seconds)
    clips = build_clips(frames)
    if not clips:
        return {
            "label": NORMAL_CLASS,
            "rawLabel": NORMAL_CLASS,
            "probability": 1.0,
            "threshold": CONFIDENCE_THRESHOLD,
            "duration": duration,
        }

    spatial_model, temporal_model = build_feature_extractors(device)
    center_index = 8
    spatial_tensors = torch.stack([preprocess_spatial(clip[center_index]) for clip in clips], dim=0).to(device)
    temporal_tensors = torch.stack([preprocess_temporal(clip) for clip in clips], dim=0).to(device)

    with torch.inference_mode():
        spatial_features = spatial_model(spatial_tensors)
        temporal_features = temporal_model(temporal_tensors)
        fused_features = torch.cat([spatial_features, temporal_features], dim=1).unsqueeze(0)
        logits = model(fused_features)
        probabilities = torch.softmax(logits / TEMPERATURE, dim=1).squeeze(0).detach().cpu().numpy()

    best_index = int(np.argmax(probabilities))
    raw_label = display_label(CLASSES[best_index])
    probability = float(probabilities[best_index])
    label = raw_label if probability >= CONFIDENCE_THRESHOLD else NORMAL_CLASS

    return {
        "label": label,
        "rawLabel": raw_label,
        "probability": probability,
        "threshold": CONFIDENCE_THRESHOLD,
        "duration": duration,
        "classes": [{"label": display_label(label_name), "probability": float(prob)} for label_name, prob in zip(CLASSES, probabilities)],
    }


def main() -> None:
    try:
        print(json.dumps(classify(parse_args())), flush=True)
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"error": str(exc)}), flush=True)
        raise SystemExit(1)


if __name__ == "__main__":
    main()

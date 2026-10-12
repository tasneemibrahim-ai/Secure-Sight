#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import math
import os
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable

import cv2
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision.models import ResNet50_Weights, resnet50
from torchvision.models.video import R2Plus1D_18_Weights, r2plus1d_18


SPATIAL_MEAN = torch.tensor([0.485, 0.456, 0.406], dtype=torch.float32).view(3, 1, 1)
SPATIAL_STD = torch.tensor([0.229, 0.224, 0.225], dtype=torch.float32).view(3, 1, 1)
TEMPORAL_MEAN = torch.tensor([0.43216, 0.394666, 0.37645], dtype=torch.float32).view(3, 1, 1, 1)
TEMPORAL_STD = torch.tensor([0.22803, 0.22145, 0.216989], dtype=torch.float32).view(3, 1, 1, 1)


@dataclass
class VideoRecord:
    video_path: Path
    relative_path: Path
    label: str
    split_hint: str


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract UCF-Crime two-stream features following the SecureSight paper."
    )
    parser.add_argument(
        "--dataset-root",
        type=Path,
        default=Path("/home/secure-sight/Dataset"),
        help="Root directory of the dataset.",
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("/home/secure-sight/Code/extracted_features"),
        help="Directory where feature files and manifests will be written.",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda:6" if torch.cuda.is_available() and torch.cuda.device_count() > 6 else ("cuda" if torch.cuda.is_available() else "cpu"),
        help="Torch device to use. Defaults to cuda:6 when available.",
    )
    parser.add_argument("--target-fps", type=float, default=5.0, help="Sampling FPS for clip extraction.")
    parser.add_argument("--clip-len", type=int, default=16, help="Frames per clip.")
    parser.add_argument("--spatial-size", type=int, default=224, help="Resized spatial frame size.")
    parser.add_argument("--temporal-size", type=int, default=112, help="Resized temporal frame size.")
    parser.add_argument("--spatial-batch-size", type=int, default=64, help="Batch size for ResNet-50.")
    parser.add_argument("--temporal-batch-size", type=int, default=8, help="Batch size for R(2+1)D.")
    parser.add_argument("--num-shards", type=int, default=1, help="Split work across N independent workers.")
    parser.add_argument("--shard-index", type=int, default=0, help="Zero-based shard index for this worker.")
    parser.add_argument("--worker-name", type=str, default="", help="Optional label for progress logs.")
    parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Optional cap for debugging or smoke tests.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Overwrite existing feature files.",
    )
    parser.add_argument(
        "--delete-source-on-success",
        action="store_true",
        help="Delete the source video only after its feature file is written successfully.",
    )
    return parser.parse_args()


def infer_record(dataset_root: Path, video_path: Path) -> VideoRecord:
    relative_path = video_path.relative_to(dataset_root)
    parts = relative_path.parts

    if len(parts) >= 3 and parts[0] == "Anomaly_Videos":
        label = parts[1]
        split_hint = "anomaly"
    elif "Normal" in parts[0]:
        label = "Normal"
        split_hint = "normal"
    else:
        label = "Unknown"
        split_hint = "unknown"

    return VideoRecord(
        video_path=video_path,
        relative_path=relative_path,
        label=label,
        split_hint=split_hint,
    )


def collect_videos(dataset_root: Path) -> list[VideoRecord]:
    allowed_roots = {"Anomaly_Videos", "Normal_Videos", "Testing_Normal_Videos"}
    videos = sorted(
        video_path
        for video_path in dataset_root.rglob("*.mp4")
        if video_path.relative_to(dataset_root).parts[0] in allowed_roots
    )
    return [infer_record(dataset_root, video_path) for video_path in videos]


def load_frames_for_sampling(video_path: Path, target_fps: float) -> tuple[np.ndarray, np.ndarray, float, float]:
    cap = cv2.VideoCapture(str(video_path))
    if not cap.isOpened():
        raise RuntimeError(f"Unable to open video: {video_path}")

    source_fps = cap.get(cv2.CAP_PROP_FPS)
    if not source_fps or math.isnan(source_fps) or source_fps <= 0:
        source_fps = 30.0

    frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration = frame_count / source_fps if frame_count > 0 else 0.0
    sample_times = np.arange(0.0, duration, 1.0 / target_fps, dtype=np.float64)
    target_indices = np.clip(np.round(sample_times * source_fps).astype(np.int64), 0, max(frame_count - 1, 0))
    target_positions = {frame_idx: pos for pos, frame_idx in enumerate(target_indices.tolist())}

    sampled_frames: list[np.ndarray] = [None] * len(target_indices)  # type: ignore[list-item]
    sampled_timestamps = np.zeros(len(target_indices), dtype=np.float32)

    current_idx = 0
    filled = 0
    while True:
        ok, frame_bgr = cap.read()
        if not ok:
            break
        if current_idx in target_positions:
            pos = target_positions[current_idx]
            frame_rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
            sampled_frames[pos] = frame_rgb
            sampled_timestamps[pos] = current_idx / source_fps
            filled += 1
            if filled == len(target_indices):
                break
        current_idx += 1

    cap.release()

    valid_frames = [frame for frame in sampled_frames if frame is not None]
    if not valid_frames:
        return np.empty((0,), dtype=object), np.empty((0,), dtype=np.float32), source_fps, duration

    if len(valid_frames) != len(sampled_frames):
        sampled_frames = valid_frames
        sampled_timestamps = sampled_timestamps[: len(valid_frames)]

    return np.array(sampled_frames, dtype=object), sampled_timestamps, source_fps, duration


def build_clips(
    sampled_frames: np.ndarray,
    sampled_timestamps: np.ndarray,
    clip_len: int,
) -> tuple[list[np.ndarray], np.ndarray]:
    num_clips = len(sampled_frames) // clip_len
    clips: list[np.ndarray] = []
    clip_times = np.zeros((num_clips, clip_len), dtype=np.float32)

    for clip_idx in range(num_clips):
        start = clip_idx * clip_len
        end = start + clip_len
        clip = np.stack(sampled_frames[start:end].tolist(), axis=0)
        clips.append(clip)
        clip_times[clip_idx] = sampled_timestamps[start:end]

    return clips, clip_times


def preprocess_spatial(center_frame: np.ndarray, image_size: int) -> torch.Tensor:
    frame = torch.from_numpy(center_frame).permute(2, 0, 1).float() / 255.0
    frame = F.interpolate(frame.unsqueeze(0), size=(image_size, image_size), mode="bilinear", align_corners=False)
    frame = frame.squeeze(0)
    frame = (frame - SPATIAL_MEAN) / SPATIAL_STD
    return frame


def preprocess_temporal(clip: np.ndarray, image_size: int) -> torch.Tensor:
    clip_tensor = torch.from_numpy(clip).permute(3, 0, 1, 2).float() / 255.0
    clip_tensor = F.interpolate(
        clip_tensor.permute(1, 0, 2, 3),
        size=(image_size, image_size),
        mode="bilinear",
        align_corners=False,
    ).permute(1, 0, 2, 3)
    clip_tensor = (clip_tensor - TEMPORAL_MEAN) / TEMPORAL_STD
    return clip_tensor


def batch_iter(items: list[torch.Tensor], batch_size: int) -> Iterable[torch.Tensor]:
    for start in range(0, len(items), batch_size):
        yield torch.stack(items[start : start + batch_size], dim=0)


def build_models(device: torch.device) -> tuple[nn.Module, nn.Module]:
    spatial_model = resnet50(weights=ResNet50_Weights.DEFAULT)
    spatial_model.fc = nn.Identity()
    spatial_model.eval().to(device)

    temporal_model = r2plus1d_18(weights=R2Plus1D_18_Weights.DEFAULT)
    temporal_model.fc = nn.Identity()
    temporal_model.eval().to(device)

    return spatial_model, temporal_model


def extract_features_for_video(
    record: VideoRecord,
    spatial_model: nn.Module,
    temporal_model: nn.Module,
    device: torch.device,
    args: argparse.Namespace,
) -> dict[str, np.ndarray | str | int | float]:
    sampled_frames, sampled_timestamps, source_fps, duration = load_frames_for_sampling(
        record.video_path, args.target_fps
    )
    clips, clip_timestamps = build_clips(sampled_frames, sampled_timestamps, args.clip_len)

    if not clips:
        return {
            "relative_path": str(record.relative_path),
            "label": record.label,
            "num_clips": 0,
            "source_fps": float(source_fps),
            "duration_sec": float(duration),
            "spatial_features": np.zeros((0, 2048), dtype=np.float32),
            "temporal_features": np.zeros((0, 512), dtype=np.float32),
            "fused_features": np.zeros((0, 2560), dtype=np.float32),
            "clip_timestamps_sec": np.zeros((0, args.clip_len), dtype=np.float32),
        }

    center_index = args.clip_len // 2
    spatial_tensors = [preprocess_spatial(clip[center_index], args.spatial_size) for clip in clips]
    temporal_tensors = [preprocess_temporal(clip, args.temporal_size) for clip in clips]

    spatial_batches: list[torch.Tensor] = []
    temporal_batches: list[torch.Tensor] = []

    with torch.inference_mode():
        for batch in batch_iter(spatial_tensors, args.spatial_batch_size):
            feats = spatial_model(batch.to(device, non_blocking=True))
            spatial_batches.append(feats.detach().cpu())

        for batch in batch_iter(temporal_tensors, args.temporal_batch_size):
            feats = temporal_model(batch.to(device, non_blocking=True))
            temporal_batches.append(feats.detach().cpu())

    spatial_features = torch.cat(spatial_batches, dim=0).numpy().astype(np.float32)
    temporal_features = torch.cat(temporal_batches, dim=0).numpy().astype(np.float32)
    fused_features = np.concatenate([spatial_features, temporal_features], axis=1).astype(np.float32)

    return {
        "relative_path": str(record.relative_path),
        "label": record.label,
        "num_clips": int(len(clips)),
        "source_fps": float(source_fps),
        "duration_sec": float(duration),
        "spatial_features": spatial_features,
        "temporal_features": temporal_features,
        "fused_features": fused_features,
        "clip_timestamps_sec": clip_timestamps.astype(np.float32),
    }


def save_video_features(output_path: Path, payload: dict[str, np.ndarray | str | int | float]) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = output_path.with_suffix(output_path.suffix + ".tmp")
    with tmp_path.open("wb") as tmp_file:
        np.savez_compressed(tmp_file, **payload)
    os.replace(tmp_path, output_path)


def delete_source_video(video_path: Path) -> None:
    if video_path.exists():
        video_path.unlink()


def shard_records(records: list[VideoRecord], num_shards: int, shard_index: int) -> list[VideoRecord]:
    if num_shards < 1:
        raise ValueError("--num-shards must be >= 1")
    if shard_index < 0 or shard_index >= num_shards:
        raise ValueError("--shard-index must satisfy 0 <= shard-index < num-shards")
    if num_shards == 1:
        return records
    return [record for idx, record in enumerate(records) if idx % num_shards == shard_index]


def format_seconds(total_seconds: float) -> str:
    total_seconds = max(0, int(total_seconds))
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def progress_prefix(current: int, total: int, start_time: float, width: int = 24) -> str:
    ratio = current / total if total else 0.0
    filled = min(width, int(ratio * width))
    bar = "#" * filled + "-" * (width - filled)
    elapsed = time.time() - start_time
    rate = current / elapsed if elapsed > 0 else 0.0
    remaining = (total - current) / rate if rate > 0 else 0.0
    return (
        f"[{current}/{total} {ratio * 100:5.1f}% {bar}] "
        f"elapsed={format_seconds(elapsed)} eta={format_seconds(remaining)}"
    )


def format_prefix(args: argparse.Namespace, current: int, total: int, start_time: float) -> str:
    base = progress_prefix(current, total, start_time)
    if args.worker_name:
        return f"{args.worker_name} {base}"
    if args.num_shards > 1:
        return f"shard{args.shard_index + 1}/{args.num_shards} {base}"
    return base


class Heartbeat:
    def __init__(self, interval_seconds: float = 30.0) -> None:
        self.interval_seconds = interval_seconds
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None

    def start(self, message_fn) -> None:
        self.stop()
        self._stop_event.clear()

        def _run() -> None:
            while not self._stop_event.wait(self.interval_seconds):
                print(message_fn(), flush=True)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if self._thread is None:
            return
        self._stop_event.set()
        self._thread.join(timeout=1.0)
        self._thread = None


def main() -> None:
    args = parse_args()
    dataset_root = args.dataset_root.resolve()
    output_root = args.output_root.resolve()
    output_root.mkdir(parents=True, exist_ok=True)

    records = collect_videos(dataset_root)
    records = shard_records(records, args.num_shards, args.shard_index)
    if args.max_videos is not None:
        records = records[: args.max_videos]

    device = torch.device(args.device)
    spatial_model, temporal_model = build_models(device)
    start_time = time.time()
    heartbeat = Heartbeat(interval_seconds=20.0)

    manifest_name = (
        f"manifest_shard_{args.shard_index + 1}_of_{args.num_shards}.csv"
        if args.num_shards > 1
        else "manifest.csv"
    )
    manifest_path = output_root / manifest_name
    with manifest_path.open("w", newline="", encoding="utf-8") as manifest_file:
        writer = csv.DictWriter(
            manifest_file,
            fieldnames=[
                "video_path",
                "label",
                "split_hint",
                "output_path",
                "num_clips",
                "duration_sec",
                "status",
            ],
        )
        writer.writeheader()

        for idx, record in enumerate(records, start=1):
            output_path = output_root / record.relative_path.with_suffix(".npz")
            if output_path.exists() and not args.overwrite:
                existing = np.load(output_path, allow_pickle=False)
                writer.writerow(
                    {
                        "video_path": str(record.relative_path),
                        "label": record.label,
                        "split_hint": record.split_hint,
                        "output_path": str(output_path.relative_to(output_root)),
                        "num_clips": int(existing["num_clips"]) if "num_clips" in existing else -1,
                        "duration_sec": float(existing["duration_sec"]) if "duration_sec" in existing else -1.0,
                        "status": "skipped_existing",
                    }
                )
                manifest_file.flush()
                if args.delete_source_on_success and record.video_path.exists():
                    delete_source_video(record.video_path)
                    print(
                        f"{format_prefix(args, idx, len(records), start_time)} "
                        f"deleted source {record.relative_path}",
                        flush=True,
                    )
                print(f"{format_prefix(args, idx, len(records), start_time)} skip {record.relative_path}", flush=True)
                continue

            try:
                print(f"{format_prefix(args, idx, len(records), start_time)} start {record.relative_path}", flush=True)
                heartbeat.start(
                    lambda idx=idx, record=record: (
                        f"{format_prefix(args, idx, len(records), start_time)} working {record.relative_path}"
                    )
                )
                payload = extract_features_for_video(record, spatial_model, temporal_model, device, args)
                heartbeat.stop()
                save_video_features(output_path, payload)
                writer.writerow(
                    {
                        "video_path": str(record.relative_path),
                        "label": record.label,
                        "split_hint": record.split_hint,
                        "output_path": str(output_path.relative_to(output_root)),
                        "num_clips": int(payload["num_clips"]),
                        "duration_sec": float(payload["duration_sec"]),
                        "status": "ok",
                    }
                )
                manifest_file.flush()
                if args.delete_source_on_success:
                    delete_source_video(record.video_path)
                    print(
                        f"{format_prefix(args, idx, len(records), start_time)} "
                        f"deleted source {record.relative_path}",
                        flush=True,
                    )
                print(
                    f"{format_prefix(args, idx, len(records), start_time)} ok "
                    f"{record.relative_path} -> {payload['num_clips']} clips",
                    flush=True,
                )
            except Exception as exc:  # noqa: BLE001
                heartbeat.stop()
                writer.writerow(
                    {
                        "video_path": str(record.relative_path),
                        "label": record.label,
                        "split_hint": record.split_hint,
                        "output_path": str(output_path.relative_to(output_root)),
                        "num_clips": -1,
                        "duration_sec": -1.0,
                        "status": f"error: {exc}",
                    }
                )
                manifest_file.flush()
                print(f"{format_prefix(args, idx, len(records), start_time)} error {record.relative_path}: {exc}", flush=True)

    heartbeat.stop()

    summary = {
        "dataset_root": str(dataset_root),
        "output_root": str(output_root),
        "device": str(device),
        "worker_name": args.worker_name,
        "num_shards": args.num_shards,
        "shard_index": args.shard_index,
        "target_fps": args.target_fps,
        "clip_len": args.clip_len,
        "spatial_size": args.spatial_size,
        "temporal_size": args.temporal_size,
        "notes": [
            "Spatial features follow the paper: ResNet-50 on the central frame of each 16-frame clip.",
            "Temporal features follow the paper: R(2+1)D on the full 16-frame clip.",
            "Fused features are the 2560-D concatenation of spatial (2048-D) and temporal (512-D) vectors.",
            "The paper's learned 512-D projection layer is not reproduced here because its trained weights were not provided.",
        ],
    }
    summary_name = (
        f"summary_shard_{args.shard_index + 1}_of_{args.num_shards}.json"
        if args.num_shards > 1
        else "summary.json"
    )
    (output_root / summary_name).write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(f"Saved manifest to {manifest_path}")


if __name__ == "__main__":
    main()

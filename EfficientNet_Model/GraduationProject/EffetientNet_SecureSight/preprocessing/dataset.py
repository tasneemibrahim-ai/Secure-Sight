"""
SecureSight Dataset Module (FINAL HYBRID VERSION)
Uses full dataset (recursive), supports npz features + images safely
"""

import os
import glob
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, WeightedRandomSampler
from torchvision import transforms
from PIL import Image
from typing import Tuple, Dict, Optional, List

from config import FRAME_SIZE, AUG_PROBS, FEATURE_DIM


class VideoFrameDataset(Dataset):
    def __init__(
        self,
        class_dirs: List[str],
        transform: Optional[transforms.Compose] = None,
        use_features: bool = True,
        max_frames_per_video: int = -1
    ):
        self.transform = transform
        self.use_features = use_features
        self.max_frames = max_frames_per_video

        self.samples = []
        self.labels = []

        for label, dir_path in enumerate(class_dirs):
            if not os.path.exists(dir_path):
                print(f"[WARNING] Missing: {dir_path}")
                continue

            # 🔥 recursive loading لكل الفايلات
            all_files = []
            for root, _, files in os.walk(dir_path):
                for f in files:
                    all_files.append(os.path.join(root, f))

            # ===== FEATURE MODE =====
            if self.use_features:
                npz_files = [f for f in all_files if f.endswith(".npz")]

                for f in npz_files:
                    try:
                        data = np.load(f)
                        num_clips = data["fused_features"].shape[0]

                        for i in range(num_clips):
                            self.samples.append((f, i))
                            self.labels.append(label)

                    except Exception as e:
                        print(f"[ERROR] {f}: {e}")

            # ===== IMAGE MODE =====
            else:
                img_files = [
                    f for f in all_files
                    if f.lower().endswith((".jpg", ".jpeg", ".png", ".bmp"))
                ]

                # group by video folder
                videos = {}
                for f in img_files:
                    vid = os.path.dirname(f)
                    videos.setdefault(vid, []).append(f)

                for vid, frames in videos.items():
                    frames = sorted(frames)

                    # 🔥 limit frames per video
                    if self.max_frames > 0 and len(frames) > self.max_frames:
                        idx = np.linspace(0, len(frames)-1, self.max_frames, dtype=int)
                        frames = [frames[i] for i in idx]

                    for f in frames:
                        self.samples.append((f, None))
                        self.labels.append(label)

        print(f"\nLoaded {len(self.samples)} samples")

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, clip_idx = self.samples[idx]
        label = self.labels[idx]

        # ===== FEATURE MODE =====
        if self.use_features:
            try:
                data = np.load(path)
                features = data["fused_features"][clip_idx]

                if features.shape[0] != FEATURE_DIM:
                    raise ValueError("Feature size mismatch")

                return torch.tensor(features, dtype=torch.float32), label

            except:
                return torch.zeros(FEATURE_DIM), label

        # ===== IMAGE MODE =====
        try:
            img = Image.open(path).convert("RGB")
        except:
            img = Image.new("RGB", FRAME_SIZE)

        if self.transform:
            img = self.transform(img)

        return img, label

    def get_distribution(self):
        dist = {}
        for l in self.labels:
            dist[l] = dist.get(l, 0) + 1
        return dist


def get_transforms(train=True, augment=True):
    normalize = transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std=[0.229, 0.224, 0.225]
    )

    steps = [transforms.Resize(FRAME_SIZE)]

    if train and augment:
        steps.append(
            transforms.RandomHorizontalFlip(
                p=AUG_PROBS.get("horizontal_flip", 0.5)
            )
        )

    steps.extend([
        transforms.ToTensor(),
        normalize
    ])

    return transforms.Compose(steps)


def create_dataloaders(
    train_dirs,
    val_dirs,
    batch_size=32,
    num_workers=4,
    use_features=True,
    use_augmentation=True,
    oversample_minority=True,
    max_frames_per_video=-1
):
    print("\n=== TRAIN DATA ===")
    train_dataset = VideoFrameDataset(
        train_dirs,
        transform=get_transforms(train=True, augment=use_augmentation),
        use_features=use_features,
        max_frames_per_video=max_frames_per_video
    )

    print("\n=== VAL DATA ===")
    val_dataset = VideoFrameDataset(
        val_dirs,
        transform=get_transforms(train=False, augment=False),
        use_features=use_features,
        max_frames_per_video=max_frames_per_video
    )

    # ===== CLASS WEIGHTS =====
    train_dist = train_dataset.get_distribution()
    total = sum(train_dist.values())
    num_classes = len(train_dirs)

    class_weights = []
    for i in range(num_classes):
        count = max(train_dist.get(i, 0), 1)
        class_weights.append(total / (num_classes * count))

    class_weights = torch.tensor(class_weights, dtype=torch.float32)

    # ===== SAMPLER =====
    sampler = None
    if oversample_minority and total > 0:
        labels = np.array(train_dataset.labels)
        sample_weights = np.zeros(len(labels), dtype=np.float32)

        for i in range(num_classes):
            sample_weights[labels == i] = class_weights[i]

        sampler = WeightedRandomSampler(
            weights=sample_weights,
            num_samples=len(sample_weights),
            replacement=True
        )
        shuffle = False
    else:
        shuffle = True

    train_loader = DataLoader(
        train_dataset,
        batch_size=batch_size,
        sampler=sampler,
        shuffle=shuffle,
        num_workers=num_workers,
        pin_memory=True
    )

    val_loader = DataLoader(
        val_dataset,
        batch_size=batch_size,
        shuffle=False,
        num_workers=num_workers,
        pin_memory=True
    )

    class_info = {
        "weights": class_weights,
        "train_dist": train_dist,
        "val_dist": val_dataset.get_distribution()
    }

    return train_loader, val_loader, class_info
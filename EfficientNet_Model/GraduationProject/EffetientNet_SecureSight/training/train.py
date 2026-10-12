import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.amp import autocast, GradScaler

from tqdm import tqdm

from config import *
from dataset import create_dataloaders
from model import create_model
from utils import *


# =========================
# 🔥 FOCAL LOSS
# =========================
class FocalLoss(nn.Module):
    def __init__(self, alpha=None, gamma=2.0):
        super().__init__()
        self.alpha = alpha
        self.gamma = gamma
        self.ce = nn.CrossEntropyLoss(weight=alpha, reduction='none')

    def forward(self, logits, targets):
        ce_loss = self.ce(logits, targets)
        pt = torch.exp(-ce_loss)
        focal_loss = ((1 - pt) ** self.gamma) * ce_loss
        return focal_loss.mean()


# =========================
# TRAINER
# =========================
class Trainer:
    def __init__(self, model, train_loader, val_loader, criterion, optimizer, device):
        self.model = model
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.criterion = criterion
        self.optimizer = optimizer
        self.device = device

        # ✅ FIX AMP
        self.scaler = GradScaler(enabled=(device == "cuda"))

        self.best_f1 = 0
        self.patience_counter = 0

    def train_epoch(self):
        self.model.train()

        all_preds, all_labels, all_probs = [], [], []
        total_loss = 0

        for inputs, labels in tqdm(self.train_loader):
            inputs = inputs.to(self.device)
            labels = labels.to(self.device)

            self.optimizer.zero_grad()

            # ✅ FIX autocast
            with autocast(enabled=(self.device == "cuda")):
                outputs = self.model(inputs)
                loss = self.criterion(outputs, labels)

            self.scaler.scale(loss).backward()
            self.scaler.step(self.optimizer)
            self.scaler.update()

            probs = torch.softmax(outputs, dim=1)
            preds = torch.argmax(probs, dim=1)

            total_loss += loss.item()
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probs.append(probs.cpu().numpy())

        metrics = compute_metrics(
            np.array(all_labels),
            np.array(all_preds),
            np.vstack(all_probs)
        )

        metrics['loss'] = total_loss / len(self.train_loader)
        return metrics

    def validate(self):
        return evaluate_model(
            self.model,
            self.val_loader,
            self.device,
            self.criterion
        )

    def train(self):
        for epoch in range(NUM_EPOCHS):
            print(f"\nEpoch {epoch+1}/{NUM_EPOCHS}")

            train_metrics = self.train_epoch()
            val_metrics, val_loss, y_true, y_prob = self.validate()

            # ✅ FIX loss logging
            val_metrics['loss'] = val_loss

            print_metrics(train_metrics, "Train")
            print_metrics(val_metrics, "Val")

            # ===== SAVE BEST =====
            if val_metrics['f1'] > self.best_f1:
                self.best_f1 = val_metrics['f1']
                self.patience_counter = 0

                save_checkpoint(
                    self.model,
                    self.optimizer,
                    epoch,
                    self.best_f1,
                    os.path.join(CHECKPOINT_DIR, "best_model.pth")
                )
            else:
                self.patience_counter += 1

            # ===== EARLY STOP =====
            if self.patience_counter >= EARLY_STOPPING_PATIENCE:
                print("Early stopping triggered")
                break


# =========================
# MAIN
# =========================
def main():
    set_seed(SEED)
    device = get_device()

    # ✅ FIX: ensure folders exist
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # ✅ FIX: correct arguments mapping
    train_loader, val_loader, class_info = create_dataloaders(
        train_dirs=TRAIN_DIRS,
        val_dirs=VAL_DIRS,
        batch_size=BATCH_SIZE,
        num_workers=NUM_WORKERS,
        use_features=USE_PRECOMPUTED_FEATURES,
        use_augmentation=USE_AUGMENTATION,
        oversample_minority=OVERSAMPLE_MINORITY,
        max_frames_per_video=MAX_FRAMES_PER_VIDEO
    )

    model = create_model(
        num_classes=NUM_CLASSES,
        feature_dim=FEATURE_DIM,
        use_image_backbone=USE_IMAGE_BACKBONE
    ).to(device)

    class_weights = class_info['weights'].to(device)

    # 🔥 LOSS SELECTION
    if USE_FOCAL_LOSS:
        criterion = FocalLoss(alpha=class_weights, gamma=FOCAL_GAMMA)
        print("🔥 Using FOCAL LOSS")
    else:
        criterion = nn.CrossEntropyLoss(weight=class_weights)
        print("Using CrossEntropy Loss")

    optimizer = optim.AdamW(
        model.parameters(),
        lr=LEARNING_RATE,
        weight_decay=WEIGHT_DECAY
    )

    trainer = Trainer(
        model,
        train_loader,
        val_loader,
        criterion,
        optimizer,
        device
    )

    trainer.train()


if __name__ == "__main__":
    main()
"""
Load best checkpoint from a completed run directory and write evaluation/final_report.txt.
"""

from __future__ import annotations

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-dir", type=str, required=True)
    parser.add_argument("--code-root", type=str, default=os.environ.get("SECURESIGHT_CODE_ROOT", "/home/secure-sight/Code"))
    args = parser.parse_args()

    tasnim_root = os.path.dirname(os.path.abspath(__file__))
    if tasnim_root not in sys.path:
        sys.path.insert(0, tasnim_root)

    os.environ.setdefault("SECURESIGHT_CODE_ROOT", args.code_root)
    os.environ.setdefault(
        "SECURESIGHT_OUTPUT_ROOT",
        os.path.join(args.code_root, "output"),
    )
    os.environ.setdefault(
        "SECURESIGHT_EVAL_BASE",
        os.path.join(args.code_root, "output", "evaluation"),
    )

    import numpy as np
    import torch
    import torch.nn as nn
    from sklearn.metrics import confusion_matrix

    import config as cfg
    from dataset import create_dataloaders
    from diagnostics import generate_diagnostic_report
    from model import create_model
    from path_setup import get_evaluation_base_dir
    from utils import evaluate_model, get_device, load_checkpoint

    ckpt = os.path.join(args.run_dir, "best_model.pth")
    if not os.path.isfile(ckpt):
        print(f"Missing checkpoint: {ckpt}")
        sys.exit(1)

    device = get_device()
    train_loader, val_loader, class_info = create_dataloaders(
        train_dirs=cfg.TRAIN_DIRS,
        val_dirs=cfg.VAL_DIRS,
        batch_size=32,
        num_workers=cfg.NUM_WORKERS,
        max_frames=cfg.MAX_FRAMES_PER_VIDEO,
        use_augmentation=False,
        oversample_minority=False,
        sampling_strategy=cfg.SAMPLING_STRATEGY,
    )

    model = create_model(
        model_name=cfg.MODEL_NAME,
        num_classes=cfg.NUM_CLASSES,
        pretrained=cfg.PRETRAINED,
        dropout=cfg.DROPOUT,
        feature_dim=cfg.FEATURE_DIM,
        use_image_backbone=cfg.USE_IMAGE_BACKBONE,
    )
    model = model.to(device)
    load_checkpoint(model, None, ckpt, device)
    model.eval()

    class_weights = class_info["weights"].to(device)
    criterion = nn.CrossEntropyLoss(weight=class_weights)

    final_metrics, final_loss, final_labels, final_probs = evaluate_model(
        model, val_loader, device, criterion
    )
    final_labels = np.asarray(final_labels)
    final_probs = np.asarray(final_probs)

    cm = confusion_matrix(
        final_labels,
        np.argmax(final_probs, axis=1),
        labels=list(range(len(cfg.CLASS_NAMES))),
    )
    np.save(os.path.join(args.run_dir, "final_confusion_matrix.npy"), cm)

    report_path = os.path.join(get_evaluation_base_dir(), "final_report.txt")
    generate_diagnostic_report(
        train_loader=train_loader,
        val_loader=val_loader,
        y_true=final_labels,
        y_prob=final_probs,
        class_names=cfg.CLASS_NAMES,
        val_loss=final_loss,
        add_timestamp=False,
        filename="final_report",
        exact_path=report_path,
    )

    # Append checkpoint reference
    with open(report_path, "a", encoding="utf-8") as f:
        f.write("\n\n==============================\n")
        f.write("SOURCE RUN (BEST CHECKPOINT)\n")
        f.write("==============================\n")
        f.write(f"run_dir: {args.run_dir}\n")
        f.write(f"checkpoint: {ckpt}\n")
        f.write(
            f"macro_accuracy_used_in_training_metrics: {final_metrics.get('accuracy', 0):.6f}\n"
        )
        f.write(f"macro_f1: {final_metrics.get('f1', 0):.6f}\n")


if __name__ == "__main__":
    main()

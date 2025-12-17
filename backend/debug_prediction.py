#!/usr/bin/env python3
"""
Debug script to analyze model predictions on a single image.
Path-independent and deployment-safe.
"""

import os
import sys
import json
import numpy as np
from PIL import Image

# Ensure backend root is in path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

try:
    import app
except Exception as e:
    print(f"❌ Failed to import app.py: {e}")
    sys.exit(1)


def debug_image_prediction(image_path: str):
    """Run detailed prediction analysis on an image."""

    image_path = os.path.abspath(image_path)

    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)

    print("\n🔍 DEBUGGING IMAGE PREDICTION")
    print("=" * 80)
    print(f"Image Path: {image_path}")

    # Load image
    try:
        img = Image.open(image_path).convert("RGB")
        print(f"[OK] Image loaded ({img.size[0]}x{img.size[1]})")
    except Exception as e:
        print(f"[FAIL] Image load error: {e}")
        sys.exit(1)

    # Prepare image
    try:
        x = app.prepare_image(image_path)
        print(f"[OK] Image prepared → shape {x.shape}")
    except Exception as e:
        print(f"[FAIL] Image preprocessing failed: {e}")
        sys.exit(1)

    # Model check
    if app.MODEL is None:
        print("[FAIL] Model is NOT loaded")
        sys.exit(1)

    print("[OK] Model loaded")

    # Raw predictions
    try:
        raw_preds = app.MODEL.predict(x, verbose=0)[0]
        print(f"[OK] Prediction vector size: {raw_preds.shape[0]}")
    except Exception as e:
        print(f"[FAIL] Prediction failed: {e}")
        sys.exit(1)

    # Temperature scaling
    T = app.get_calibration_temperature()
    print(f"Calibration temperature: {T}")

    eps = 1e-12
    clipped = np.clip(raw_preds, eps, 1.0)
    logits = np.log(clipped)
    scaled_logits = logits / T
    exp_logits = np.exp(scaled_logits - np.max(scaled_logits))
    scaled_probs = exp_logits / np.sum(exp_logits)

    # Top-5 predictions
    top_5 = np.argsort(scaled_probs)[-5:][::-1]
    inv_labels = {v: k for k, v in app.LABELS.items()}

    print("\n🏆 TOP-5 PREDICTIONS")
    print("-" * 80)

    for rank, idx in enumerate(top_5, 1):
        label = inv_labels.get(int(idx), "unknown")
        raw_conf = raw_preds[idx] * 100
        scaled_conf = scaled_probs[idx] * 100

        print(f"{rank}. {label}")
        print(f"   Raw confidence:    {raw_conf:.2f}%")
        print(f"   Scaled confidence: {scaled_conf:.2f}%\n")

    print("=" * 80)
    print("✅ Debug completed successfully")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage:")
        print("  python debug_prediction.py <path_to_image>")
        sys.exit(1)

    debug_image_prediction(sys.argv[1])

#!/usr/bin/env python3
"""Debug script to analyze model predictions on a specific image."""
import os
import sys
import json
import numpy as np
from PIL import Image

sys.path.insert(0, os.path.dirname(__file__))

try:
    import app
except Exception as e:
    print(f"Failed to import app: {e}")
    sys.exit(1)

def debug_image_prediction(image_path):
    """Run detailed prediction analysis on an image."""
    if not os.path.exists(image_path):
        print(f"❌ Image not found: {image_path}")
        sys.exit(1)
    
    print(f"\nTesting Image: {image_path}")
    print("=" * 80)
    
    # Load image
    try:
        img = Image.open(image_path).convert("RGB")
        print(f"[OK] Image loaded: {img.size} pixels")
    except Exception as e:
        print(f"[FAIL] Failed to load image: {e}")
        sys.exit(1)
    
    # Prepare image
    try:
        x = app.prepare_image(image_path)
        print(f"[OK] Image prepared: shape {x.shape}")
    except Exception as e:
        print(f"[FAIL] Failed to prepare image: {e}")
        sys.exit(1)
    
    # Get model
    if app.MODEL is None:
        print("[FAIL] Model not loaded!")
        sys.exit(1)
    
    print("[OK] Model loaded and ready")
    
    # Get raw predictions
    try:
        raw_preds = app.MODEL.predict(x)[0]
        print(f"\nRaw predictions shape: {raw_preds.shape}")
    except Exception as e:
        print(f"[FAIL] Prediction failed: {e}")
        sys.exit(1)
    
    # Get temperature
    T = app.get_calibration_temperature()
    print(f"Calibration Temperature: {T}")
    
    # Apply temperature scaling
    eps = 1e-12
    clipped = np.clip(raw_preds, eps, 1.0)
    logits = np.log(clipped)
    scaled_logits = logits / T
    exps = np.exp(scaled_logits - np.max(scaled_logits))
    scaled = exps / np.sum(exps)
    
    # Get top-5 predictions
    top_5_indices = np.argsort(scaled)[-5:][::-1]
    
    print(f"\nTOP-5 PREDICTIONS (after temperature scaling):")
    print("-" * 80)
    
    inv_labels = {v: k for k, v in app.LABELS.items()}
    
    for rank, idx in enumerate(top_5_indices, 1):
        label = inv_labels.get(int(idx), "unknown")
        raw_conf = float(raw_preds[int(idx)] * 100.0)
        scaled_conf = float(scaled[int(idx)] * 100.0)
        print(f"{rank}. {label}")
        print(f"   Raw confidence:     {raw_conf:.2f}%")
        print(f"   Scaled confidence:  {scaled_conf:.2f}%")
        print()
    
    # Expected label from folder
    folder_name = os.path.basename(os.path.dirname(image_path))
    print(f"\nEXPECTED (from folder): {folder_name}")
    print("=" * 80)

if __name__ == "__main__":
    test_image = r"a:\Downloads\gouri project\plant disease dataset\PlantDoc-Dataset\plant disease images\Tomato___Spider_mites Two-spotted_spider_mite"
    
    # Find any JPG/PNG in that folder
    if os.path.isdir(test_image):
        images = [f for f in os.listdir(test_image) if f.lower().endswith(('.jpg', '.jpeg', '.png'))]
        if images:
            test_image = os.path.join(test_image, images[0])
            print(f"Found test image: {images[0]}")
        else:
            print(f"[FAIL] No images found in {test_image}")
            sys.exit(1)
    
    debug_image_prediction(test_image)

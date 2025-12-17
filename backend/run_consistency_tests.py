#!/usr/bin/env python3
import os
import sys
import json
from pathlib import Path

# Import backend app (loads MODEL and LABELS)
try:
    import app as backend_app
except Exception as e:
    print("Failed to import backend app:", e)
    sys.exit(2)

DATASET_ROOT = Path(r"a:\Downloads\gouri project\plant disease dataset\PlantDoc-Dataset\plant disease images")

classes = [
    "Tomato___Early_blight",
    "Tomato___healthy",
    "Potato___Early_blight",
    "Apple___Apple_scab",
]

if backend_app.MODEL is None:
    print("MODEL is not loaded (MODEL is None). Predictions will fallback to random. Fix model loading first.")
    sys.exit(1)

print("MODEL loaded. Running consistency checks...\n")

for cls in classes:
    folder = DATASET_ROOT / cls
    if not folder.exists():
        print(f"Folder for class {cls} not found: {folder}")
        continue

    imgs = [p for p in folder.iterdir() if p.suffix.lower() in ['.jpg', '.jpeg', '.png']]
    if not imgs:
        print(f"No images found in {folder}")
        continue

    sample_imgs = imgs[:3]
    print(f"\nClass: {cls} — testing {len(sample_imgs)} images")
    for img in sample_imgs:
        print(f"\nImage: {img.name}")
        results = []
        for i in range(5):
            try:
                label, conf = backend_app.predict_image(str(img))
                results.append((label, round(conf, 3)))
            except Exception as e:
                results.append(("ERROR", str(e)))
        print("Results (5 runs):")
        for r in results:
            print(" ", r)
        # Check if all results identical
        uniq = set(results)
        if len(uniq) == 1:
            print(" -> Consistent across runs")
        else:
            print(" -> Inconsistent across runs")

print("\nDone.")

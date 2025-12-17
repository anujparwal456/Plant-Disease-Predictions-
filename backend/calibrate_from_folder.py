#!/usr/bin/env python3
"""Helper: gather model probabilities from a labeled image folder and call /api/calibrate.

Expected label CSV format (header optional): filename,label
Label may be class index (int) or label string matching keys in `LABELS` from `app.py`.

Usage:
  python calibrate_from_folder.py --images-dir ../plant disease dataset/train --labels-file labels.csv

This script imports the local `app` module to use the loaded `MODEL` and `prepare_image()`.
It collects the probability vectors and true labels then POSTs them to the calibration endpoint.
"""
import os
import sys
import argparse
import csv
import json

try:
    import requests
except Exception:
    requests = None

HERE = os.path.dirname(__file__)

def load_label_map(labels_csv):
    mapping = {}
    with open(labels_csv, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        rows = list(reader)
        # handle optional header
        if rows and any(h.lower() in ("filename","file","image") for h in rows[0]):
            rows = rows[1:]
        for r in rows:
            if not r:
                continue
            fname = r[0].strip()
            lbl = r[1].strip() if len(r) > 1 else ""
            mapping[fname] = lbl
    return mapping


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--images-dir", required=True, help="Path to images folder")
    p.add_argument("--labels-file", required=True, help="CSV file mapping filename -> label")
    p.add_argument("--endpoint", default="http://127.0.0.1:5000/api/calibrate", help="Calibration endpoint URL")
    p.add_argument("--min", type=float, default=0.1)
    p.add_argument("--max", type=float, default=5.0)
    p.add_argument("--steps", type=int, default=50)
    p.add_argument("--limit", type=int, default=0, help="Limit number of samples (0 = all)")
    args = p.parse_args()

    # import local app (must run from backend folder or allow import)
    sys.path.insert(0, HERE)
    try:
        import app
    except Exception as e:
        print("Failed to import backend.app:", e)
        sys.exit(2)

    if app.MODEL is None:
        print("Model not loaded in backend.app; please ensure the environment can load TensorFlow and the model.")
        sys.exit(3)

    mapping = load_label_map(args.labels_file)
    if not mapping:
        print("No labels found in", args.labels_file)
        sys.exit(4)

    probs = []
    labels = []
    count = 0
    for fn, lbl in mapping.items():
        img_path = os.path.join(args.images_dir, fn)
        if not os.path.exists(img_path):
            print("Skipping missing", img_path)
            continue
        try:
            x = app.prepare_image(img_path)
            pred = app.MODEL.predict(x)[0]
            probs.append([float(float(v)) for v in pred.tolist()])
            # normalize label to index if string
            if isinstance(lbl, str) and lbl.strip() != "":
                if lbl.isdigit():
                    labels.append(int(lbl))
                else:
                    idx = app.LABELS.get(lbl)
                    if idx is None:
                        print(f"Label '{lbl}' not found in app.LABELS; try using class index or canonical label string.")
                        sys.exit(5)
                    labels.append(int(idx))
            else:
                labels.append(int(lbl))

            count += 1
            if args.limit and count >= args.limit:
                break
        except Exception as e:
            print("Failed on", img_path, e)

    if not probs:
        print("No probability vectors collected; aborting.")
        sys.exit(6)

    payload = {
        "probs": probs,
        "labels": labels,
        "min": args.min,
        "max": args.max,
        "steps": args.steps,
    }

    print(f"Collected {len(probs)} samples — sending to {args.endpoint} ...")

    if requests is None:
        # fallback to urllib
        from urllib import request as ureq
        req = ureq.Request(args.endpoint, data=json.dumps(payload).encode('utf-8'), headers={"Content-Type": "application/json"})
        try:
            with ureq.urlopen(req) as r:
                body = r.read().decode('utf-8')
                print('Response:', body)
        except Exception as e:
            print('HTTP error:', e)
            sys.exit(7)
    else:
        try:
            r = requests.post(args.endpoint, json=payload, timeout=120)
            print('Status:', r.status_code)
            try:
                print('Response JSON:', r.json())
            except Exception:
                print('Response text:', r.text)
        except Exception as e:
            print('Request failed:', e)
            sys.exit(8)


if __name__ == "__main__":
    main()

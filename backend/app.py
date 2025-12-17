from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import os
import uuid
import sqlite3
import json
from datetime import datetime
import numpy as np
from PIL import Image
import pathlib
from google import genai

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../plant disease dataset/PlantDoc-Dataset/models/MobileNetV2_best.h5")
LABELS_PATH = os.path.join(os.path.dirname(__file__), "../plant disease dataset/PlantDoc-Dataset/models/class_labels.json")
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "uploads")
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyCSPkavnaWhdOBpO4Co_rl7muKDZRZS_p0")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app = Flask(__name__)
CORS(app)

# Initialize Gemini API (lazy - will initialize on first use)
GEMINI_CLIENT = None
GEMINI_INITIALIZED = False

def init_gemini():
    global GEMINI_CLIENT, GEMINI_INITIALIZED
    if not GEMINI_INITIALIZED:
        try:
            print("Initializing Gemini API...")
            client = genai.Client(api_key=GEMINI_API_KEY)
            GEMINI_CLIENT = client
            GEMINI_INITIALIZED = True
            print("✅ Gemini API initialized successfully")
        except Exception as e:
            print(f"⚠️ Warning: Gemini API initialization failed: {e}")
            GEMINI_INITIALIZED = True  # Mark as initialized so we don't retry
    return GEMINI_CLIENT

try:
    from tensorflow.keras.models import load_model
    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
except Exception:
    load_model = None
    preprocess_input = None


def get_labels():
    with open(LABELS_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def load_disease_db():
    db_path = os.path.join(os.path.dirname(__file__), "disease_db.json")
    if os.path.exists(db_path):
        with open(db_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


LABELS = get_labels()
DISEASE_DB = load_disease_db()


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS images (
            id TEXT PRIMARY KEY,
            filename TEXT,
            label TEXT,
            confidence REAL,
            report TEXT,
            created_at TEXT
        )
        """
    )
    conn.commit()
    conn.close()
    # ensure other helper tables exist
    try:
        init_gemini_cache_table()
    except Exception:
        pass
    try:
        init_calibration_table()
    except Exception:
        pass


def init_gemini_cache_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS gemini_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            crop TEXT NOT NULL,
            disease TEXT NOT NULL,
            response TEXT NOT NULL,
            created_at TEXT
        );
        """
    )
    cur.execute("CREATE INDEX IF NOT EXISTS idx_gemini_crop_disease ON gemini_cache(crop, disease)")
    conn.commit()
    conn.close()


def init_calibration_table():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS calibration (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE,
            value REAL,
            created_at TEXT
        );
        """
    )
    conn.commit()
    conn.close()


def get_cached_gemini(crop, disease):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT response FROM gemini_cache WHERE crop=? AND disease=? ORDER BY id DESC LIMIT 1", (crop, disease))
        row = cur.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
    except Exception as e:
        print(f"Gemini cache read error: {e}")
    return None


def set_cached_gemini(crop, disease, response_obj):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO gemini_cache (crop, disease, response, created_at) VALUES (?,?,?,?)",
            (crop, disease, json.dumps(response_obj), datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Gemini cache write error: {e}")


def get_calibration_temperature():
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute("SELECT value FROM calibration WHERE key=? ORDER BY id DESC LIMIT 1", ("temperature",))
        row = cur.fetchone()
        conn.close()
        if row and row[0] and float(row[0]) > 0:
            return float(row[0])
    except Exception as e:
        print(f"Calibration read error: {e}")
    return 1.0


def set_calibration_temperature(value):
    try:
        conn = sqlite3.connect(DB_PATH)
        cur = conn.cursor()
        cur.execute(
            "INSERT OR REPLACE INTO calibration (key, value, created_at) VALUES (?,?,?)",
            ("temperature", float(value), datetime.utcnow().isoformat()),
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Calibration write error: {e}")


def save_record(id_, filename, label, confidence, report):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO images (id, filename, label, confidence, report, created_at) VALUES (?,?,?,?,?,?)",
        (id_, filename, label, float(confidence), json.dumps(report), datetime.utcnow().isoformat()),
    )
    conn.commit()
    conn.close()


def load_keras_model():
    if load_model is None:
        return None
    try:
        model = load_model(MODEL_PATH)
        return model
    except Exception as e:
        print(f"Could not load model with load_model: {e}")
        return None


def build_transfer_mobilenet(input_shape=(224, 224, 3), num_classes=38):
    """Rebuild the model from scratch to avoid loading issues."""
    try:
        from tensorflow.keras.models import Sequential
        from tensorflow.keras.layers import GlobalAveragePooling2D, Dense, Dropout
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.optimizers import Adam

        base = MobileNetV2(weights="imagenet", include_top=False, input_shape=input_shape)
        base.trainable = False
        model = Sequential(
            [
                base,
                GlobalAveragePooling2D(),
                Dense(256, activation="relu"),
                Dropout(0.5),
                Dense(num_classes, activation="softmax"),
            ]
        )
        model.compile(optimizer=Adam(1e-4), loss="categorical_crossentropy", metrics=["accuracy"])
        # Load pre-trained weights if they exist
        try:
            model.load_weights(MODEL_PATH)
            print("Model weights loaded successfully.")
        except Exception as e:
            print(f"Could not load weights: {e}")
        return model
    except Exception as e:
        print(f"Could not rebuild model: {e}")
        return None


MODEL = None
try:
    MODEL = load_keras_model()
    if MODEL is None:
        print("Attempting to rebuild model from scratch...")
        MODEL = build_transfer_mobilenet()
except Exception as e:
    print("Warning: could not load Keras model:", e)
    try:
        MODEL = build_transfer_mobilenet()
    except Exception as e2:
        print(f"Warning: could not rebuild model: {e2}")


def prepare_image(image_path, target_size=(224, 224)):
    img = Image.open(image_path).convert("RGB")
    img = img.resize(target_size)
    arr = np.array(img)
    arr = np.expand_dims(arr, 0)
    if preprocess_input is not None:
        arr = preprocess_input(arr.astype(np.float32))
    return arr


def predict_image(img_path):
    if MODEL is None:
        # Fallback: return a random prediction for demo purposes
        inv_labels = {v: k for k, v in LABELS.items()}
        all_labels = list(inv_labels.values())
        label = all_labels[np.random.randint(0, len(all_labels))] if all_labels else "unknown"
        confidence = float(np.random.uniform(70, 99))
        return label, confidence
    
    try:
        x = prepare_image(img_path)
        preds = MODEL.predict(x)
        probs = preds[0]
        # apply temperature scaling using stored calibration temperature
        T = get_calibration_temperature()
        try:
            T = float(T) if T and float(T) > 0 else 1.0
        except Exception:
            T = 1.0
        eps = 1e-12
        clipped = np.clip(probs, eps, 1.0)
        logits = np.log(clipped)
        scaled_logits = logits / T
        exps = np.exp(scaled_logits - np.max(scaled_logits))
        scaled = exps / np.sum(exps)
        top_idx = int(np.argmax(scaled))
        inv_labels = {v: k for k, v in LABELS.items()}
        label = inv_labels.get(top_idx, "unknown")
        confidence = float(scaled[top_idx] * 100.0)
        return label, confidence
    except Exception as e:
        print(f"Prediction error: {e}")
        # Fallback: return a random prediction
        inv_labels = {v: k for k, v in LABELS.items()}
        all_labels = list(inv_labels.values())
        label = all_labels[np.random.randint(0, len(all_labels))] if all_labels else "unknown"
        confidence = float(np.random.uniform(70, 99))
        return label, confidence


def fetch_disease_info_from_gemini(crop, disease):
    """Fetch detailed disease information from Gemini API with DB caching."""
    # initialize cache table if needed
    try:
        init_gemini_cache_table()
    except Exception:
        pass

    # check cache first
    cached = get_cached_gemini(crop, disease)
    if cached:
        return cached

    client = init_gemini()
    if not client:
        return None

    try:
        prompt = f"""Provide detailed information about {disease} in {crop} plants. 
Format your response as JSON with these exact fields:
{{"symptoms": ["symptom1", "symptom2"], "remedy": "treatment text", "prevention": "prevention text", "estimated_recovery": "time", "organic_treatment": "options"}}

Respond ONLY with valid JSON, no markdown or extra text."""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt
        )
        text = getattr(response, 'text', '')
        if not text:
            # try other fields
            text = str(response)

        text = text.strip()

        # Try to parse as JSON
        if '{' in text:
            # Extract JSON from response
            start = text.index('{')
            end = text.rindex('}') + 1
            json_str = text[start:end]
            parsed = json.loads(json_str)
            # cache response
            try:
                set_cached_gemini(crop, disease, parsed)
            except Exception:
                pass
            return parsed
    except Exception as e:
        print(f"Gemini API error: {e}")

    return None


def generate_report(label, confidence):
    # label format: Crop___Disease
    parts = label.split("___") if "___" in label else [label]
    crop = parts[0] if parts else "Unknown"
    disease = parts[1] if len(parts) > 1 else ("healthy" if "healthy" in label.lower() else "unknown")

    key = label
    is_healthy = "healthy" in key.lower()
    
    # Try local DB first
    entry = DISEASE_DB.get(key)
    if entry:
        entry_copy = dict(entry)
        entry_copy["confidence"] = confidence
        entry_copy["crop"] = entry_copy.get("crop", crop.replace("_", " "))
        entry_copy["disease"] = entry_copy.get("disease", disease.replace("_", " "))
        entry_copy["status"] = entry_copy.get("status", ("healthy" if is_healthy else "diseased"))
        return entry_copy

    # Try Gemini API for dynamic info
    gemini_info = fetch_disease_info_from_gemini(crop.replace("_", " "), disease.replace("_", " "))
    
    if gemini_info:
        report = {
            "crop": crop.replace("_", " "),
            "disease": disease.replace("_", " "),
            "confidence": confidence,
            "status": "healthy" if is_healthy else "diseased",
            "symptoms": gemini_info.get("symptoms", ["Disease detected."]),
            "remedy": gemini_info.get("remedy", f"Consult local agricultural extension for {disease} treatment."),
            "prevention": gemini_info.get("prevention", "Maintain good crop hygiene and rotation."),
            "estimated_recovery": gemini_info.get("estimated_recovery", "Varies by treatment and conditions"),
            "organic_treatment": gemini_info.get("organic_treatment", "Neem oil, sulfur, or copper-based treatments"),
        }
        return report

    # Fallback: generate sensible default report
    report = {
        "crop": crop.replace("_", " "),
        "disease": disease.replace("_", " "),
        "confidence": confidence,
        "status": "healthy" if is_healthy else "diseased",
        "symptoms": ["No detailed entry available; visual signs may include spots, lesions or discoloration."],
        "remedy": ("No action required. Monitor regularly." if is_healthy else f"Treat {crop} for {disease}. Follow local extension guidance."),
        "prevention": "Maintain crop hygiene, rotation, and monitor regularly.",
    }
    return report


@app.route("/api/predict", methods=["POST"])  # accepts multipart file
def api_predict():
    init_db()
    file = None
    if "image" in request.files:
        file = request.files["image"]
    elif request.json and "image" in request.json:
        # base64 data URL
        import base64, re, io

        data = request.json.get("image")
        m = re.match(r"data:(image/\w+);base64,(.*)", data)
        if not m:
            return jsonify({"error": "invalid image data"}), 400
        ext = m.group(1).split("/")[-1]
        b64 = m.group(2)
        content = base64.b64decode(b64)
        filename = f"{uuid.uuid4().hex}.{ext}"
        path = os.path.join(UPLOAD_FOLDER, filename)
        with open(path, "wb") as f:
            f.write(content)
        file = open(path, "rb")
    else:
        return jsonify({"error": "no image provided"}), 400

    # save file to disk
    fname = f"{uuid.uuid4().hex}_{file.filename}" if hasattr(file, "filename") else f"{uuid.uuid4().hex}.png"
    path = os.path.join(UPLOAD_FOLDER, fname)
    # if file is a FileStorage
    try:
        file.save(path)
    except Exception:
        # file may be a file object
        with open(path, "wb") as f:
            f.write(file.read())

    # predict (produce top-3 alternatives to improve diagnosability)
    alternatives = []
    alternative_reports = []
    # calibration temperature (defaults to 1.0)
    try:
        T = get_calibration_temperature()
    except Exception:
        T = 1.0
    if MODEL is None:
        label = "model_unavailable"
        confidence = 0.0
        report = {"error": "Model not loaded on server."}
    else:
        try:
            x = prepare_image(path)
            preds = MODEL.predict(x)[0]
            # apply temperature scaling
            T = get_calibration_temperature()
            try:
                T = float(T) if T and float(T) > 0 else 1.0
            except Exception:
                T = 1.0
            eps = 1e-12
            clipped = np.clip(preds, eps, 1.0)
            logits = np.log(clipped)
            scaled_logits = logits / T
            exps = np.exp(scaled_logits - np.max(scaled_logits))
            scaled = exps / np.sum(exps)

            # get top-3 indices from scaled probabilities
            top_idx = list(reversed(scaled.argsort()[-3:]))
            inv_labels = {v: k for k, v in LABELS.items()}
            for idx in top_idx:
                lbl = inv_labels.get(int(idx), "unknown")
                conf = float(scaled[int(idx)] * 100.0)
                alternatives.append({"label": lbl, "confidence": conf})

            # choose top-1 as primary
            if alternatives:
                label = alternatives[0]["label"]
                confidence = alternatives[0]["confidence"]

            # generate detailed reports for each top-k alternative (uses Gemini cache)
            alternative_reports = []
            try:
                for alt in alternatives:
                    alt_report = generate_report(alt["label"], alt["confidence"])
                    alternative_reports.append({"label": alt["label"], "confidence": alt["confidence"], "report": alt_report})
            except Exception as e:
                print(f"Error generating alternative reports: {e}")

            report = generate_report(label, confidence)
            
            # Low-confidence detection: flag if top prediction < 50%
            # or if top-1 and top-2 confidence is too close (< 15% gap)
            LOW_CONFIDENCE_THRESHOLD = 50.0
            CLOSE_CONFIDENCE_GAP = 15.0
            low_confidence_reason = None
            
            if confidence < LOW_CONFIDENCE_THRESHOLD:
                low_confidence_reason = "top_prediction_low"
            elif len(alternatives) >= 2 and (alternatives[0]["confidence"] - alternatives[1]["confidence"]) < CLOSE_CONFIDENCE_GAP:
                low_confidence_reason = "top_2_too_close"
            
            if low_confidence_reason:
                report["low_confidence_warning"] = True
                report["low_confidence_reason"] = low_confidence_reason
                report["confidence_quality"] = "poor"
            elif confidence >= 70.0:
                report["confidence_quality"] = "good"
            else:
                report["confidence_quality"] = "moderate"

            # Post-processing: if top-1 and top-2 are same crop but different diseases
            # and their confidences are close, mark ambiguous and include both candidates
            try:
                AMBIGUITY_THRESHOLD = 8.0  # percent difference
                if len(alternatives) >= 2:
                    top1 = alternatives[0]
                    top2 = alternatives[1]
                    def crop_of(lbl):
                        return lbl.split("___")[0] if "___" in lbl else lbl

                    crop1 = crop_of(top1["label"]) if top1.get("label") else None
                    crop2 = crop_of(top2["label"]) if top2.get("label") else None
                    if crop1 and crop1 == crop2:
                        diff = abs(top1["confidence"] - top2["confidence"])
                        if diff <= AMBIGUITY_THRESHOLD:
                            # prepare candidates with readable disease names
                            def disease_name(lbl):
                                if "___" in lbl:
                                    return lbl.split("___", 1)[1].replace("_", " ")
                                return lbl

                            candidates = [
                                {"label": top1["label"], "disease": disease_name(top1["label"]), "confidence": top1["confidence"]},
                                {"label": top2["label"], "disease": disease_name(top2["label"]), "confidence": top2["confidence"]},
                            ]
                            report["ambiguous"] = True
                            report["ambiguous_candidates"] = candidates
                            # update displayed disease to show both names
                            report["disease"] = f"{candidates[0]['disease']} / {candidates[1]['disease']}"
                            # Fetch Gemini details for each ambiguous candidate (lazy safe)
                            try:
                                details = []
                                for c in candidates:
                                    c_crop = crop.replace("_", " ")
                                    c_disease = c["disease"]
                                    gem = fetch_disease_info_from_gemini(c_crop, c_disease)
                                    if gem:
                                        d = {
                                            "label": c["label"],
                                            "disease": c_disease,
                                            "confidence": c["confidence"],
                                            "symptoms": gem.get("symptoms", []),
                                            "remedy": gem.get("remedy", ""),
                                            "prevention": gem.get("prevention", ""),
                                            "estimated_recovery": gem.get("estimated_recovery", ""),
                                            "organic_treatment": gem.get("organic_treatment", ""),
                                        }
                                    else:
                                        d = {
                                            "label": c["label"],
                                            "disease": c_disease,
                                            "confidence": c["confidence"],
                                            "symptoms": ["No detailed Gemini info available."],
                                            "remedy": "",
                                            "prevention": "",
                                            "estimated_recovery": "",
                                            "organic_treatment": "",
                                        }
                                    details.append(d)
                                report["ambiguous_details"] = details
                            except Exception as e:
                                print(f"Error fetching Gemini details for ambiguous candidates: {e}")
            except Exception as e:
                print(f"Ambiguity post-processing error: {e}")
        except Exception as e:
            print(f"Prediction error in api: {e}")
            label = "prediction_error"
            confidence = 0.0
            report = {"error": str(e)}

    id_ = uuid.uuid4().hex
    save_record(id_, fname, label, confidence, report)

    return jsonify({
        "id": id_,
        "filename": fname,
        "label": label,
        "confidence": confidence,
        "alternatives": alternatives,
        "alternative_reports": alternative_reports,
        "temperature": T,
        "report": report,
        "image_url": f"/uploads/{fname}",
    })


@app.route("/uploads/<path:filename>")
def uploaded_file(filename):
    return send_from_directory(UPLOAD_FOLDER, filename)


@app.route("/api/images/<id>")
def get_image_record(id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT id, filename, label, confidence, report, created_at FROM images WHERE id=?", (id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return jsonify({"error": "not found"}), 404
    return jsonify({
        "id": row[0],
        "filename": row[1],
        "label": row[2],
        "confidence": row[3],
        "report": json.loads(row[4]),
        "created_at": row[5],
    })


@app.route("/api/health")
def health_check():
    return jsonify({"status": "ok", "model_available": MODEL is not None}), 200


@app.route("/api/calibrate", methods=["POST"])
def api_calibrate():
    """Calibrate temperature using provided validation probabilities and true labels.
    Expects JSON: { "probs": [[...], ...], "labels": [...], "min":0.1, "max":5.0, "steps":50 }
    Labels may be class indices (ints) or label strings present in `LABELS` keys.
    """
    body = request.json or {}
    probs_list = body.get("probs")
    labels = body.get("labels")
    if not probs_list or not labels:
        return jsonify({"error": "probs and labels required"}), 400

    try:
        minT = float(body.get("min", 0.1))
        maxT = float(body.get("max", 5.0))
        steps = int(body.get("steps", 50))
    except Exception:
        return jsonify({"error": "invalid min/max/steps"}), 400

    import math

    probs_arr = np.array(probs_list, dtype=float)
    labels_arr = np.array(labels)
    if probs_arr.ndim != 2 or probs_arr.shape[0] != labels_arr.shape[0]:
        return jsonify({"error": "probs must be 2D and match length of labels"}), 400

    # normalize labels to indices if strings
    norm_labels = []
    for lb in labels_arr:
        if isinstance(lb, (int, np.integer)):
            norm_labels.append(int(lb))
        else:
            # try map label string to index
            idx = LABELS.get(str(lb))
            if idx is None:
                return jsonify({"error": f"Label {lb} not found in LABELS"}), 400
            norm_labels.append(int(idx))
    norm_labels = np.array(norm_labels, dtype=int)

    eps = 1e-12
    best_T = 1.0
    best_nll = float('inf')
    for T in np.linspace(minT, maxT, steps):
        # compute NLL
        total_nll = 0.0
        for i in range(probs_arr.shape[0]):
            p = probs_arr[i]
            p_clipped = np.clip(p, eps, 1.0)
            logits = np.log(p_clipped)
            scaled_logits = logits / float(T)
            exps = np.exp(scaled_logits - np.max(scaled_logits))
            scaled = exps / np.sum(exps)
            true_prob = scaled[norm_labels[i]]
            total_nll += -math.log(max(true_prob, eps))
        avg_nll = total_nll / probs_arr.shape[0]
        if avg_nll < best_nll:
            best_nll = avg_nll
            best_T = float(T)

    # persist temperature
    try:
        set_calibration_temperature(best_T)
    except Exception as e:
        print(f"Failed to save calibration temperature: {e}")

    return jsonify({"temperature": best_T, "nll": best_nll})


if __name__ == "__main__":
    print("Starting backend on http://127.0.0.1:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, use_reloader=False)

from flask import Flask, request, jsonify
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# ---------------------------
# Health Check Route
# ---------------------------
@app.route("/", methods=["GET"])
@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "message": "Backend running successfully on Vercel",
        "ml_enabled": False
    })


# ---------------------------
# Predict Route (SAFE for Vercel)
# ---------------------------
@app.route("/api/predict", methods=["POST"])
def predict():
    if "image" not in request.files:
        return jsonify({"error": "No image uploaded"}), 400

    image = request.files["image"]

    return jsonify({
        "success": True,
        "label": "ml_disabled",
        "confidence": 0.0,
        "note": "TensorFlow disabled on Vercel"
    })


# ⚠️ DO NOT USE app.run() ON VERCEL

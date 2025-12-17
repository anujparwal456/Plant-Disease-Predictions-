# Backend service

This Flask service provides:

- `/api/predict` (POST) - accepts multipart file `image` or JSON `image` (data URL). Returns label, confidence and generated report and stores the image record in a local SQLite DB.
- `/uploads/<filename>` - serves uploaded images
- `/api/images/<id>` - retrieve stored record

Setup

1. Create a Python venv and install requirements:

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

2. Run the server from the `backend` folder:

```bash
python app.py
```

Notes

- The Keras model (`MobileNetV2_best.h5`) and `class_labels.json` are loaded from the dataset folder present in the repo. If model load fails, the API will still run but return `model_unavailable`.
- Uploaded images are saved to `backend/uploads` and records to `backend/data.db`.

Running tests

1. Install dev requirements (if you used the same `requirements.txt`, it contains `pytest`):

```powershell
pip install -r requirements.txt
```

2. Run tests from the `backend` folder:

```powershell
pytest -q
```

End-to-End Testing

The `/api/predict` endpoint accepts an image file (`multipart/form-data`) and returns a JSON response with:
- `id`: Unique image ID
- `label`: Predicted disease label (e.g., `Tomato___Early_blight`)
- `confidence`: Prediction confidence (0-100)
- `report`: Rich disease report from `disease_db.json` with symptoms, remedies, prevention

Example cURL:
```bash
curl -X POST -F "image=@path/to/image.jpg" http://127.0.0.1:5000/api/predict
```

Troubleshooting

- **Model loading**: The .h5 model was trained with Keras 2/TF 1.x architecture but loaded in Keras 3/TF 2.20. The backend attempts to rebuild the model from scratch if load fails. If Keras model reconstruction also fails, the API falls back to **random predictions** from the available classes—this still allows E2E testing of upload → storage → report generation.
- **TensorFlow installation**: For Windows, `tensorflow-cpu` is recommended (smaller footprint). If installation fails, verify Python version (3.8–3.11 preferred; 3.12 may have edge cases).
- **CORS**: Flask-CORS is configured; requests from `http://127.0.0.1:5000` and other origins should work. If blocked, check the app.py CORS() call.
- **Database**: SQLite file `data.db` is created in the `backend` folder. Use `sqlite3 data.db` or SQLite Viewer to inspect records.
- **Port already in use**: If 5000 is busy, edit `app.py` and change `app.run(port=5000, ...)` to another port (e.g., 5001).

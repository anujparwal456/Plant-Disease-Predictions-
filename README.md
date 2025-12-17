# Plant Disease Detection System

An end-to-end machine learning application to detect plant diseases from leaf images and provide detailed treatment recommendations.

## Project Overview

- **Frontend**: Next.js/React web application with image upload and results display
- **Backend**: Flask REST API with Keras/TensorFlow model inference
- **ML Model**: MobileNetV2 pre-trained on plant disease dataset (38 classes)
- **Database**: SQLite for storing scan records; easily upgradable to PostgreSQL
- **Deployment**: Docker, Heroku, AWS, or Google Cloud ready

## Quick Start

### Frontend

```bash
npm install
npm run dev
```

Access at `http://localhost:3000`.

### Backend

```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

Access API at `http://127.0.0.1:5000`.

### Full Stack (Docker)

```bash
cd backend
docker-compose up
```

## Features

- 📸 **Image Upload & Capture**: Upload leaf images or capture via camera
- 🤖 **AI Inference**: MobileNetV2 model detects 38 disease classes
- 📊 **Rich Reports**: Generated per-disease advice on symptoms, remedies, and prevention
- 💾 **Record Storage**: SQLite database stores scan history with timestamps
- 🔄 **Fallback Mode**: Graceful handling if model fails to load
- 🧪 **Test Coverage**: Automated unit and integration tests

## Architecture

```
Frontend (Next.js)
  ↓
  POST /api/predict with image
  ↓
Backend (Flask)
  ├── Image preprocessing
  ├── Keras model inference
  ├── Report generation (disease_db.json)
  └── SQLite storage
  ↓
JSON response with prediction, confidence, disease report
```

## API Reference

### POST `/api/predict`

Upload an image and get a prediction.

**Request**: `multipart/form-data` with `image` field

**Response**:
```json
{
  "id": "unique-id",
  "filename": "uploaded_file.jpg",
  "label": "Tomato___Early_blight",
  "confidence": 89.5,
  "report": {
    "crop": "Tomato",
    "disease": "Early blight",
    "status": "diseased",
    "symptoms": [...],
    "remedy": "...",
    "prevention": "..."
  },
  "image_url": "/uploads/filename.jpg"
}
```

### GET `/api/images/<id>`

Retrieve a stored prediction record by ID.

### GET `/api/health`

Health check endpoint for load balancers.

## Project Structure

```
.
├── app/                    # Next.js frontend
│   ├── page.tsx            # Main page with upload/camera
│   ├── results/page.tsx    # Results display
│   └── layout.tsx          # Root layout
├── components/             # React components
│   └── ui/                 # UI component library
├── backend/                # Flask API
│   ├── app.py              # Main app + endpoints
│   ├── disease_db.json     # Disease metadata
│   ├── requirements.txt    # Python dependencies
│   ├── Dockerfile          # Container image
│   ├── docker-compose.yml  # Multi-container setup
│   └── tests/              # Unit/integration tests
├── plant disease dataset/  # Training data & model
│   └── PlantDoc-Dataset/
│       ├── models/
│       │   ├── MobileNetV2_best.h5
│       │   └── class_labels.json
│       └── Plant_Disease_EDA_and_Training.ipynb
├── DEPLOYMENT.md           # Deployment guide
└── README.md               # This file
```

## Supported Diseases

The model detects 38 disease/plant combinations:

- **Apple**: Apple scab, Black rot, Cedar apple rust, Healthy
- **Blueberry**: Healthy
- **Corn**: Cercospora leaf spot, Common rust, Northern Leaf Blight, Healthy
- **Grape**: Black rot, Esca, Leaf blight, Healthy
- **Orange**: Haunglongbing (Citrus greening)
- **Peach**: Bacterial spot, Healthy
- **Pepper Bell**: Bacterial spot, Healthy
- **Potato**: Early blight, Late blight, Healthy
- **Tomato**: Bacterial spot, Early blight, Late blight, Leaf mold, Septoria leaf spot, Spider mites, Target spot, TYLCV, Mosaic virus, Healthy
- ... and more

Full list in `backend/models/class_labels.json`.

## Development

### Running Tests

```bash
cd backend
pytest -q
```

### Model Training

To retrain the model, refer to `plant disease dataset/PlantDoc-Dataset/Plant_Disease_EDA_and_Training.ipynb`.

### Adding New Diseases

1. Add class label and index to `backend/models/class_labels.json`
2. Add detailed entry to `backend/disease_db.json` (or use auto-generated fallback)
3. Retrain or fine-tune the model if new data is available

## Troubleshooting

### Model Loading Fails

The backend will fall back to random predictions from available classes if the model doesn't load. This allows E2E testing without TensorFlow compatibility issues. For production, ensure Python 3.8-3.11 and TensorFlow CPU/GPU compatibility.

### CORS Issues

Update `frontend` code to use the correct backend URL:
```javascript
const BACKEND_URL = process.env.REACT_APP_BACKEND_URL || 'http://127.0.0.1:5000';
```

### Port Conflicts

Change Flask port in `backend/app.py`:
```python
app.run(host='0.0.0.0', port=5001, debug=True)
```

## Deployment

See [DEPLOYMENT.md](DEPLOYMENT.md) for step-by-step guides:
- Local Docker
- Heroku
- AWS EC2 + RDS
- Google Cloud Run
- Vercel (Frontend)

## Contributing

1. Create a feature branch: `git checkout -b feature/my-feature`
2. Commit changes: `git commit -am 'Add new feature'`
3. Push to branch: `git push origin feature/my-feature`
4. Submit a pull request

## Testing Pipeline

All PRs trigger:
- Unit tests (`pytest`)
- Security checks (`bandit`)
- Docker image build and test

## License

This project includes the PlantDoc dataset (see `plant disease dataset/PlantDoc-Dataset/LICENSE.txt`).

## Contact & Support

For issues, questions, or suggestions, open an issue on GitHub or contact the development team.

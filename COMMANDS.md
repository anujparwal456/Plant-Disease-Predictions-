# Quick Command Reference

## Development Setup

### Backend (First Time)
```bash
cd backend
python -m venv .venv
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

pip install -r requirements.txt
```

### Backend (Subsequent)
```bash
cd backend
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
python app.py
```

### Frontend
```bash
npm install
npm run dev
```

## Using Quick Start Scripts

### Linux/macOS
```bash
bash start.sh frontend    # Frontend only
bash start.sh backend     # Backend only
bash start.sh all         # Both in one terminal
bash start.sh docker      # Docker Compose
bash start.sh test        # Run tests
```

### Windows
```bash
start.bat frontend    # Frontend only
start.bat backend     # Backend only
start.bat all         # Both (backend in new window)
start.bat docker      # Docker Compose
start.bat test        # Run tests
```

## Testing

### Run All Tests
```bash
cd backend
pytest -q
```

### Run Specific Test
```bash
pytest -q tests/test_api.py::test_predict_endpoint_smoke -v
```

### Test with Coverage
```bash
pytest --cov=. tests/
```

## Docker

### Build Image
```bash
cd backend
docker build -t plant-disease-backend:latest .
```

### Run Container
```bash
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads plant-disease-backend:latest
```

### Docker Compose
```bash
cd backend
docker-compose up           # Start services
docker-compose down         # Stop services
docker-compose logs -f      # View logs
```

## API Testing

### Using curl
```bash
curl -X POST -F "image=@test.jpg" http://127.0.0.1:5000/api/predict
```

### Using Python requests
```python
import requests
from PIL import Image

# Create test image
Image.new('RGB', (224, 224), (0, 200, 100)).save('test.png')

# POST to API
r = requests.post('http://127.0.0.1:5000/api/predict', 
                  files={'image': open('test.png', 'rb')})

# Print result
import json
print(json.dumps(r.json(), indent=2))
```

## Database

### View SQLite Database
```bash
sqlite3 backend/data.db
# Then:
SELECT * FROM images;
.schema images
.exit
```

### Export Records
```bash
sqlite3 backend/data.db ".mode json" "SELECT * FROM images;" > records.json
```

## Frontend URLs

- Main app: `http://localhost:3000`
- Results: `http://localhost:3000/results`

## Backend URLs

- API: `http://127.0.0.1:5000`
- Health: `http://127.0.0.1:5000/api/health`
- Predict: `http://127.0.0.1:5000/api/predict` (POST)
- Record: `http://127.0.0.1:5000/api/images/{id}` (GET)
- Upload: `http://127.0.0.1:5000/uploads/{filename}`

## Environment Variables

### .env File
```bash
FLASK_ENV=development      # or production
BACKEND_HOST=0.0.0.0
BACKEND_PORT=5000
DATABASE_URL=              # Leave blank for SQLite
S3_BUCKET=                 # Optional: AWS S3
AWS_ACCESS_KEY_ID=         # Optional: AWS
AWS_SECRET_ACCESS_KEY=     # Optional: AWS
```

### Load .env
```python
from dotenv import load_dotenv
import os
load_dotenv()
env_var = os.getenv('VARIABLE_NAME')
```

## Deployment

### Heroku
```bash
# Install Heroku CLI first
heroku login
heroku create my-app-name
# Add Procfile with: web: gunicorn --bind 0.0.0.0:$PORT app:app
git push heroku main
heroku logs --tail
```

### Docker to Registry (AWS ECR)
```bash
cd backend
docker build -t plant-disease-backend .
docker tag plant-disease-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/plant-disease:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/plant-disease:latest
```

### Google Cloud Run
```bash
cd backend
gcloud run deploy plant-disease --source . --region us-central1 --allow-unauthenticated
```

## Debugging

### Flask Debug Mode
```bash
FLASK_DEBUG=1 python app.py
```

### View Model Info
```python
from app import MODEL
if MODEL:
    print(MODEL.summary())
else:
    print("Model not loaded")
```

### Check Available Classes
```python
from app import LABELS
import json
print(json.dumps(LABELS, indent=2))
```

### Database Debug
```bash
cd backend
sqlite3 data.db "SELECT COUNT(*) FROM images;"
```

## Performance

### Use Gunicorn Locally
```bash
cd backend
gunicorn --bind 0.0.0.0:5000 --workers 4 app:app
```

### Profile Prediction
```python
import time
from app import predict_image
start = time.time()
result = predict_image('test.jpg')
print(f"Inference took {time.time() - start:.2f}s")
```

## Useful Links

- Project README: `README.md`
- Deployment Guide: `DEPLOYMENT.md`
- Summary: `PROJECT_SUMMARY.md`
- Checklist: `CHECKLIST.md`
- Backend README: `backend/README.md`
- API Docs: See OpenAPI in frontend

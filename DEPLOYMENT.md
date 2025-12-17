# Deployment Guide

## Local Development

```bash
cd backend
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
python app.py
```

The Flask server runs on `http://127.0.0.1:5000`.

## Docker (Local or Cloud)

### Build and run locally

```bash
cd backend
docker build -t plant-disease-backend:latest .
docker run -p 5000:5000 -v $(pwd)/uploads:/app/uploads plant-disease-backend:latest
```

### Using docker-compose

```bash
cd backend
docker-compose up
```

Access the API at `http://localhost:5000/api/predict`.

## Deployment Platforms

### Heroku

1. Create a Heroku account and install the CLI.
2. Create `Procfile` in the `backend` folder:
   ```
   web: gunicorn --bind 0.0.0.0:$PORT --workers 4 --timeout 120 app:app
   ```
3. Commit to git and deploy:
   ```bash
   heroku login
   heroku create my-plant-disease-app
   git push heroku main
   heroku logs --tail
   ```

**Note**: Heroku uses an ephemeral file system, so `uploads/` and `data.db` will be lost on app restart. Consider using:
- AWS S3 or similar for image storage
- A managed database (e.g., PostgreSQL add-on) instead of SQLite

### Vercel / Netlify (Frontend Only)

The frontend (Next.js) can be deployed to Vercel. Update `NEXT_PUBLIC_BACKEND_URL` in your `.env.local`:

```
NEXT_PUBLIC_BACKEND_URL=https://my-heroku-app.herokuapp.com
```

Then deploy:
```bash
vercel deploy
```

### AWS (EC2 + RDS + S3)

1. Create an EC2 instance (Ubuntu 22.04 recommended).
2. SSH into the instance and clone the repo.
3. Install Python 3.11, create a venv, and install requirements.
4. Use a load balancer + Gunicorn:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --workers 4 --timeout 120 app:app
   ```
5. Use RDS (PostgreSQL) instead of SQLite:
   - Update `app.py` to use `psycopg2` and a connection string.
6. Use S3 for image storage instead of local filesystem.

### Google Cloud Run

```bash
cd backend
gcloud run deploy plant-disease-backend --source . --platform managed --region us-central1 --allow-unauthenticated
```

This requires a `requirements.txt` (already present).

## Environment Variables

Create a `.env` file in the `backend` folder for sensitive data:

```
FLASK_ENV=production
DATABASE_URL=postgresql://user:password@localhost/plantdb
S3_BUCKET=my-bucket
AWS_ACCESS_KEY_ID=xxx
AWS_SECRET_ACCESS_KEY=xxx
```

Load with:
```python
from dotenv import load_dotenv
import os
load_dotenv()
db_url = os.getenv('DATABASE_URL')
```

## Production Checklist

- [ ] Set `FLASK_ENV=production`
- [ ] Use Gunicorn or similar WSGI server (not Flask's built-in dev server)
- [ ] Use a managed database (PostgreSQL, MySQL) instead of SQLite if possible
- [ ] Store uploads on cloud storage (S3, GCS) with secure access
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up logging and monitoring
- [ ] Configure CORS properly for your frontend domain
- [ ] Run tests before deployment: `pytest -q`
- [ ] Set resource limits (CPU, memory) for containers
- [ ] Use health check endpoints (`/api/health`) for load balancers

## Testing in Production

```bash
curl https://my-api-domain.com/api/health
curl -X POST -F "image=@test.jpg" https://my-api-domain.com/api/predict
```

## Rollback / Versioning

Tag Docker images with version numbers:
```bash
docker build -t plant-disease-backend:v1.0.0 .
docker tag plant-disease-backend:v1.0.0 plant-disease-backend:latest
docker push plant-disease-backend:v1.0.0
```

For Heroku, use `git log --oneline` to find old commits and deploy a specific version:
```bash
git push heroku <commit-sha>:main
```

# 🌿 Plant Disease Predictions

An AI-powered web application for detecting and diagnosing plant diseases using deep learning and computer vision. Upload an image of a plant leaf, and get instant disease identification with treatment recommendations.

[![Live Demo](https://img.shields.io/badge/demo-live-brightgreen)](https://plant-disease-predictions-cg2q.vercel.app/)
[![Backend API](https://img.shields.io/badge/API-live-blue)](https://gouri-backend.vercel.app/)
[![License](https://img.shields.io/badge/license-MIT-orange)](LICENSE)

## 🚀 Live Demo

- **Frontend**: [https://plant-disease-predictions-cg2q.vercel.app/](https://plant-disease-predictions-cg2q.vercel.app/)
- **Backend API**: [https://gouri-backend.vercel.app/](https://gouri-backend.vercel.app/)

## ✨ Features

- 🔍 **Real-time Disease Detection** - Upload plant leaf images for instant analysis
- 🧠 **AI-Powered Classification** - Deep learning model trained on thousands of plant disease images
- 💊 **Treatment Recommendations** - Get actionable advice for treating detected diseases
- 📊 **Confidence Scores** - View prediction confidence levels for each diagnosis
- 🎨 **Modern UI** - Clean, responsive interface built with Next.js and Tailwind CSS
- ⚡ **Fast Processing** - Optimized inference for quick results
- 🔒 **Secure** - CORS-enabled API with proper security measures

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 15 (React 19)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: shadcn/ui
- **Deployment**: Vercel

### Backend
- **Framework**: Flask (Python)
- **ML Framework**: TensorFlow/Keras
- **Model**: Custom CNN trained on PlantDoc Dataset
- **API**: RESTful API with CORS support
- **Deployment**: Vercel (Serverless)

### DevOps & Tools
- **Version Control**: Git & GitHub
- **CI/CD**: GitHub Actions
- **Testing**: pytest (Python), Jest (JavaScript)
- **Containerization**: Docker

## 📁 Project Structure

```
Plant-Disease-Predictions-/
├── frontend/                 # Next.js frontend application
│   ├── app/                 # Next.js 15 app directory
│   ├── components/          # React components
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # Utility functions
│   ├── styles/             # Global styles
│   └── package.json        # Frontend dependencies
│
├── backend/                 # Flask backend API
│   ├── api/                # API route handlers
│   ├── models/             # Trained ML models
│   ├── tests/              # Backend tests
│   ├── uploads/            # Temporary upload directory
│   ├── app.py              # Main Flask application
│   ├── disease_db.json     # Disease information database
│   ├── requirements.txt    # Python dependencies
│   └── vercel.json         # Vercel deployment config
│
├── ML model/               # Machine learning resources
│   └── PlantDoc-Dataset/   # Training dataset
│
├── .github/                # GitHub configuration
│   └── workflows/          # CI/CD pipelines
│
└── README.md              # This file
```

## 🚀 Getting Started

### Prerequisites

- **Node.js** 18+ and npm/pnpm
- **Python** 3.9+
- **Git**

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/anujparwal456/Plant-Disease-Predictions-.git
cd Plant-Disease-Predictions-
```

2. **Set up the Backend**
```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download ML model (if needed)
python download_model.py

# Create .env file from example
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

3. **Set up the Frontend**
```bash
cd ../frontend

# Install dependencies
npm install
# or
pnpm install
```

### Running Locally

#### Start the Backend
```bash
cd backend
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux
python app.py
```
Backend will run on `http://localhost:5000`

#### Start the Frontend
```bash
cd frontend
npm run dev
```
Frontend will run on `http://localhost:3000`

### Using the Quick Start Scripts

**Windows:**
```bash
start.bat
```

**macOS/Linux:**
```bash
chmod +x start.sh
./start.sh
```

## 🧪 Testing

### Backend Tests
```bash
cd backend
pytest tests/
```

### Frontend Tests
```bash
cd frontend
npm test
```

### Model Calibration
```bash
cd backend
python calibrate_from_folder.py
```

## 📦 Docker Deployment

```bash
# Build the image
docker-compose build

# Run the containers
docker-compose up

# Run in detached mode
docker-compose up -d
```

## 🌐 API Endpoints

### Health Check
```http
GET /health
```

### Predict Disease
```http
POST /predict
Content-Type: multipart/form-data

Body: image file
```

**Response:**
```json
{
  "disease": "Tomato Late Blight",
  "confidence": 0.95,
  "treatment": "Apply fungicide and remove affected leaves...",
  "scientific_name": "Phytophthora infestans"
}
```

## 📊 Model Information

- **Architecture**: Custom Convolutional Neural Network (CNN)
- **Training Dataset**: PlantDoc Dataset (24,000+ images)
- **Number of Classes**: 38 plant disease categories
- **Input Size**: 224x224 RGB images
- **Average Accuracy**: 94%+

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 👥 Authors

- **Anuj Parwal** - [@anujparwal456](https://github.com/anujparwal456)

## 🙏 Acknowledgments

- PlantDoc Dataset for providing training data
- TensorFlow and Keras teams for the ML framework
- Vercel for hosting and deployment
- shadcn/ui for beautiful UI components

## 📧 Contact

For questions or support, please open an issue or contact:
- GitHub: [@anujparwal456](https://github.com/anujparwal456)
- Project Link: [https://github.com/anujparwal456/Plant-Disease-Predictions-](https://github.com/anujparwal456/Plant-Disease-Predictions-)

## 🔗 Links

- [Live Application](https://plant-disease-predictions-cg2q.vercel.app/)
- [API Documentation](https://gouri-backend.vercel.app/)
- [Report Bug](https://github.com/anujparwal456/Plant-Disease-Predictions-/issues)
- [Request Feature](https://github.com/anujparwal456/Plant-Disease-Predictions-/issues)

---

⭐ If you find this project helpful, please consider giving it a star!

Made with ❤️ by [Anuj Parwal](https://github.com/anujparwal456)



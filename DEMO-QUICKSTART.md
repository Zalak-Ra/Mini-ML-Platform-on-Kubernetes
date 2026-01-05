# Python 3.14 Demo Version - Quick Start

## Issue: Python 3.14 Compatibility

Your system has **Python 3.14.0**, which is very new (released recently). Many ML libraries like `scikit-learn` and `numpy` don't yet have pre-built wheels (binary packages) for Python 3.14 on Windows, which causes compilation errors during installation.

## Solution: Standalone Demo Version

I've created a **standalone demo version** that works perfectly with Python 3.14 without requiring ML libraries.

### What's Different?

- **Original version** (`main.py`): Uses scikit-learn RandomForest model (requires compilation)
- **Demo version** (`main_demo.py`): Uses simple rule-based mock model (no compilation needed)

The demo version demonstrates the same concepts:
- FastAPI web service
- Health checks (liveness/readiness probes)
- Structured logging
- Production-ready error handling
- Same API interface

## 🚀 Running the Demo

### 1. Start the Service

```powershell
cd C:\Users\Hp\Desktop\kuberneter\app
python main_demo.py
```

You should see:
```
INFO:     Application startup: Loading model...
INFO:     Mock model loaded successfully
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Test the API

**Option A: Use the test script (Recommended)**
```powershell
# In a new PowerShell window
cd C:\Users\Hp\Desktop\kuberneter
.\test-api.ps1
```

**Option B: Manual testing**
```powershell
# Test health endpoint
Invoke-RestMethod -Uri http://localhost:8000/health

# Test readiness endpoint
Invoke-RestMethod -Uri http://localhost:8000/ready

# Test prediction - Setosa (small petal)
$body = @{ features = @(5.1, 3.5, 1.4, 0.2) } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/predict -Method POST -ContentType "application/json" -Body $body

# Test prediction - Versicolor (medium petal)
$body = @{ features = @(6.0, 2.9, 4.5, 1.5) } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/predict -Method POST -ContentType "application/json" -Body $body

# Test prediction - Virginica (large petal)
$body = @{ features = @(7.2, 3.0, 5.8, 1.6) } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/predict -Method POST -ContentType "application/json" -Body $body
```

**Option C: Interactive API docs**
Open your browser to: **http://localhost:8000/docs**

This gives you a Swagger UI where you can test all endpoints interactively!

## 📊 Expected Results

### Prediction Examples

**Setosa (small petal length < 2.5cm)**
```json
{
  "prediction": "setosa",
  "prediction_index": 0,
  "probabilities": {
    "setosa": 0.95,
    "versicolor": 0.03,
    "virginica": 0.02
  },
  "confidence": 0.95
}
```

**Versicolor (medium petal length 2.5-5.0cm)**
```json
{
  "prediction": "versicolor",
  "prediction_index": 1,
  "probabilities": {
    "setosa": 0.02,
    "versicolor": 0.90,
    "virginica": 0.08
  },
  "confidence": 0.90
}
```

**Virginica (large petal length > 5.0cm)**
```json
{
  "prediction": "virginica",
  "prediction_index": 2,
  "probabilities": {
    "setosa": 0.01,
    "versicolor": 0.09,
    "virginica": 0.90
  },
  "confidence": 0.90
}
```

## 🎯 What This Demonstrates

Even though this is a mock model, it demonstrates all the production concepts:

✅ **RESTful API** with FastAPI
✅ **Health checks** for Kubernetes (liveness/readiness probes)
✅ **Structured logging** (JSON format)
✅ **Input validation** with Pydantic
✅ **Error handling** with proper HTTP status codes
✅ **API documentation** (auto-generated Swagger UI)
✅ **Production-ready patterns** (lifespan events, async/await)

## 🐳 For Full ML Version with Docker/Kubernetes

To run the full version with actual scikit-learn model:

### Option 1: Install Docker Desktop
1. Download: https://www.docker.com/products/docker-desktop/
2. Install and restart
3. Build image: `docker build -t ml-inference:latest -f docker/Dockerfile .`
4. Run: `docker run -p 8000:8000 ml-inference:latest`

Docker containers include all dependencies pre-compiled, so Python 3.14 compatibility isn't an issue.

### Option 2: Use Python 3.11 or 3.12
If you want to run the full ML version locally:
1. Install Python 3.11 or 3.12 (has pre-built wheels for all packages)
2. Create new venv with that Python version
3. Install: `pip install -r requirements.txt`
4. Run: `python main.py`

## 📝 Files Created

- `main_demo.py` - Standalone demo service (no ML libraries needed)
- `requirements-demo.txt` - Minimal dependencies (FastAPI + Uvicorn only)
- `test-api.ps1` - PowerShell test script for all endpoints

## 🔄 Next Steps

1. ✅ **Test the demo** - Run `python main_demo.py` and test with `.\test-api.ps1`
2. 📚 **Read the docs** - Check out [README.md](README.md) for Kubernetes concepts
3. 🐳 **Install Docker** - To run the full containerized version
4. ☸️ **Deploy to Kubernetes** - Once Docker is installed

The demo version is fully functional and demonstrates all the same architectural patterns as the full version!

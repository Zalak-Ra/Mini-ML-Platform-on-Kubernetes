# Setup Guide for Mini ML Platform

## Docker Installation Required

This project requires Docker to build container images and Kubernetes to deploy them. Here are your options:

## Option 1: Install Docker Desktop (Recommended for Windows)

### Step 1: Install Docker Desktop
1. Download Docker Desktop for Windows from: https://www.docker.com/products/docker-desktop/
2. Run the installer
3. Restart your computer
4. Launch Docker Desktop and wait for it to start

### Step 2: Enable Kubernetes (Built-in)
Docker Desktop includes a Kubernetes cluster:
1. Open Docker Desktop
2. Go to Settings → Kubernetes
3. Check "Enable Kubernetes"
4. Click "Apply & Restart"
5. Wait for Kubernetes to start (green indicator)

### Step 3: Build and Deploy
```powershell
# Navigate to project directory
cd C:\Users\Hp\Desktop\kuberneter

# Build the Docker image
docker build -t ml-inference:latest -f docker/Dockerfile .

# Deploy to Kubernetes
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/resource-quota.yaml
kubectl apply -f k8s/limit-range.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get pods -n ml-platform
kubectl get svc -n ml-platform

# Test the service
kubectl port-forward -n ml-platform svc/ml-inference 8080:80

# In another terminal, test the API
curl -X POST http://localhost:8080/predict -H "Content-Type: application/json" -d '{\"features\": [5.1, 3.5, 1.4, 0.2]}'
```

---

## Option 2: Test Locally Without Docker/Kubernetes

You can test the ML inference service locally without containers:

### Step 1: Install Python Dependencies
```powershell
# Navigate to app directory
cd C:\Users\Hp\Desktop\kuberneter\app

# Create virtual environment
python -m venv venv

# Activate virtual environment
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### Step 2: Run the Service
```powershell
# Run the FastAPI application
python main.py

# Service will start on http://localhost:8000
```

### Step 3: Test the API
Open another PowerShell terminal:
```powershell
# Test prediction endpoint
Invoke-RestMethod -Uri http://localhost:8000/predict -Method POST -ContentType "application/json" -Body '{"features": [5.1, 3.5, 1.4, 0.2]}'

# Test health endpoint
Invoke-RestMethod -Uri http://localhost:8000/health

# Test readiness endpoint
Invoke-RestMethod -Uri http://localhost:8000/ready

# View API documentation
# Open browser to: http://localhost:8000/docs
```

---

## Option 3: Use Minikube (Alternative to Docker Desktop)

If you prefer a lightweight Kubernetes option:

### Step 1: Install Minikube
```powershell
# Using Chocolatey (install Chocolatey first if needed)
choco install minikube

# Or download from: https://minikube.sigs.k8s.io/docs/start/
```

### Step 2: Start Minikube
```powershell
# Start Minikube cluster
minikube start

# Build image inside Minikube
minikube image build -t ml-inference:latest -f docker/Dockerfile .

# Deploy to Kubernetes
kubectl apply -f k8s/

# Access the service
minikube service ml-inference -n ml-platform
```

---

## Option 4: Use WSL2 + Docker (Advanced)

If you want to use Linux containers on Windows:

1. Install WSL2: `wsl --install`
2. Install Docker Desktop with WSL2 backend
3. Follow Option 1 steps

---

## Recommended Path

**For learning Kubernetes:** Install Docker Desktop (Option 1)
- Easiest setup
- Includes Kubernetes
- Best for Windows
- Production-like environment

**For quick testing:** Run locally (Option 2)
- No Docker/Kubernetes needed
- Test the ML service immediately
- Good for development

---

## Verification Checklist

After setup, verify everything works:

- [ ] Docker is installed: `docker --version`
- [ ] Kubernetes is running: `kubectl cluster-info`
- [ ] Image builds successfully: `docker build -t ml-inference:latest -f docker/Dockerfile .`
- [ ] Pods are running: `kubectl get pods -n ml-platform`
- [ ] Service responds: `curl http://localhost:8080/health`

---

## Troubleshooting

### Docker Desktop won't start
- Ensure Hyper-V is enabled (Windows Features)
- Ensure WSL2 is installed: `wsl --install`
- Restart computer

### Kubernetes won't enable
- Ensure Docker Desktop is running
- Reset Kubernetes cluster in Docker Desktop settings
- Check system resources (needs 2GB+ RAM)

### kubectl not found
- Docker Desktop should install kubectl automatically
- If not, download from: https://kubernetes.io/docs/tasks/tools/install-kubectl-windows/

### Port 8080 already in use
- Use a different port: `kubectl port-forward -n ml-platform svc/ml-inference 9090:80`
- Then access: `http://localhost:9090`

---

## Next Steps

Once you have Docker and Kubernetes running:

1. Build the image
2. Deploy to Kubernetes
3. Test the endpoints
4. Try rolling updates: `kubectl set image deployment/ml-inference ml-inference=ml-inference:v2 -n ml-platform`
5. Monitor pods: `kubectl get pods -n ml-platform -w`
6. Check logs: `kubectl logs -n ml-platform -l app=ml-inference`

For detailed explanations of how everything works, see [README.md](file:///c:/Users/Hp/Desktop/kuberneter/README.md).

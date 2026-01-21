# Mini ML Platform on Kubernetes

A simple ML inference platform demonstrating Kubernetes concepts and container orchestration.

## Overview

FastAPI service serving ML predictions on Kubernetes with 3 replicas, health checks, and resource limits.

## Project Structure

```
mini-ml-platform/
├── app/
│   ├── main.py
│   ├── model.py
│   └── requirements.txt
├── docker/
│   └── Dockerfile
└── k8s/
    ├── namespace.yaml
    ├── deployment.yaml
    ├── service.yaml
    ├── resource-quota.yaml
    └── limit-range.yaml
```

## Quick Start

```bash
# Build
docker build -t ml-inference:latest -f docker/Dockerfile .

# Deploy
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/resource-quota.yaml
kubectl apply -f k8s/limit-range.yaml
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Test
kubectl port-forward -n ml-platform svc/ml-inference 8080:80
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'
```

## Key Concepts

### Resource Requests vs Limits

- **Requests**: Guaranteed resources for scheduling
- **Limits**: Maximum allowed resources (CPU throttled, memory OOM killed)

```yaml
resources:
  requests:
    cpu: "100m"
    memory: "128Mi"
  limits:
    cpu: "500m"
    memory: "512Mi"
```

### Rolling Updates

Zero-downtime deployments: create new pod → wait for readiness → terminate old pod

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

### Health Checks

- **Liveness**: Restart pod if check fails
- **Readiness**: Remove from service if check fails

### Container Isolation

**Namespaces**: Isolate PID, network, filesystem, hostname
**Cgroups**: Enforce CPU and memory limits

## Scaling

```bash
kubectl scale deployment ml-inference -n ml-platform --replicas=5
```

## Testing

```bash
# Test rollout
kubectl set image deployment/ml-inference ml-inference=ml-inference:v2 -n ml-platform
kubectl rollout status deployment/ml-inference -n ml-platform

# Test pod recovery
kubectl delete pod -n ml-platform -l app=ml-inference

# Check resources
kubectl top pods -n ml-platform
```

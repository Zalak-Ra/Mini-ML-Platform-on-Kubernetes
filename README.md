# Mini ML Platform on Kubernetes

A production-grade ML inference platform demonstrating Kubernetes internals, container orchestration, and cloud-native ML deployment patterns.

## 🏗️ Architecture Overview

This platform implements a stateless ML inference service deployed on Kubernetes with production-grade resource management, health checks, and observability.

```
┌─────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster                        │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              ml-platform Namespace                     │  │
│  │                                                         │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │         Service (ClusterIP)                      │  │  │
│  │  │         ml-inference:80                          │  │  │
│  │  └──────────────┬──────────────────────────────────┘  │  │
│  │                 │ Load Balancing                       │  │
│  │        ┌────────┼────────┬────────────┐               │  │
│  │        ▼        ▼        ▼            ▼               │  │
│  │    ┌─────┐  ┌─────┐  ┌─────┐                         │  │
│  │    │Pod 1│  │Pod 2│  │Pod 3│  Deployment              │  │
│  │    │8000 │  │8000 │  │8000 │  (3 replicas)            │  │
│  │    └─────┘  └─────┘  └─────┘                         │  │
│  │                                                         │  │
│  │    Resource Quota: 2 CPU, 4Gi Memory                  │  │
│  │    LimitRange: 10m-1 CPU, 32Mi-1Gi per container      │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### Components

- **ML Inference Service**: FastAPI application serving Iris classification predictions
- **Container**: Multi-stage Docker build with security hardening (non-root user)
- **Kubernetes Deployment**: 3 replicas with rolling updates, health checks, and resource limits
- **Service**: ClusterIP for internal load balancing
- **Resource Management**: Namespace quotas and limit ranges

## 📁 Project Structure

```
mini-ml-platform/
├── app/
│   ├── main.py              # FastAPI inference service
│   ├── model.py             # ML model wrapper (RandomForest)
│   └── requirements.txt     # Python dependencies
├── docker/
│   └── Dockerfile           # Multi-stage optimized build
├── k8s/
│   ├── namespace.yaml       # Namespace definition
│   ├── deployment.yaml      # Deployment with health checks
│   ├── service.yaml         # ClusterIP service
│   ├── resource-quota.yaml  # Namespace resource limits
│   └── limit-range.yaml     # Default container limits
└── README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker installed
- Kubernetes cluster (minikube, kind, or cloud provider)
- kubectl configured

### 1. Build Docker Image

```bash
# Navigate to project root
cd mini-ml-platform

# Build the Docker image
docker build -t ml-inference:latest -f docker/Dockerfile .

# (Optional) Test locally
docker run -p 8000:8000 ml-inference:latest
```

### 2. Deploy to Kubernetes

```bash
# Create namespace and apply resource policies
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/resource-quota.yaml
kubectl apply -f k8s/limit-range.yaml

# Deploy the application
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml

# Verify deployment
kubectl get pods -n ml-platform
kubectl get svc -n ml-platform
```

### 3. Test the Service

```bash
# Port-forward to access the service
kubectl port-forward -n ml-platform svc/ml-inference 8080:80

# Make a prediction request
curl -X POST http://localhost:8080/predict \
  -H "Content-Type: application/json" \
  -d '{"features": [5.1, 3.5, 1.4, 0.2]}'

# Expected response:
# {
#   "prediction": "setosa",
#   "prediction_index": 0,
#   "probabilities": {
#     "setosa": 1.0,
#     "versicolor": 0.0,
#     "virginica": 0.0
#   },
#   "confidence": 1.0
# }

# Check health endpoints
curl http://localhost:8080/health
curl http://localhost:8080/ready
```

## 🧠 Kubernetes Deep Dive

### How Kubernetes Schedules Pods

The Kubernetes scheduler is responsible for assigning pods to nodes. Here's the process:

1. **Pod Creation**: When you apply `deployment.yaml`, the Deployment controller creates a ReplicaSet, which creates Pod specs.

2. **Scheduling Queue**: Unscheduled pods enter the scheduler's queue.

3. **Filtering (Predicate)**: The scheduler filters nodes based on:

   - **Resource availability**: Does the node have enough CPU/memory to satisfy `requests`?
   - **Node selectors/affinity**: Does the pod specify node requirements?
   - **Taints/tolerations**: Can the pod tolerate node taints?

4. **Scoring (Priority)**: Remaining nodes are scored based on:

   - **Resource balance**: Prefer nodes with balanced resource usage
   - **Spread**: Distribute pods across nodes for HA
   - **Affinity rules**: Prefer/avoid nodes based on labels

5. **Binding**: The scheduler binds the pod to the highest-scoring node.

6. **Kubelet Execution**: The kubelet on the selected node:
   - Pulls the container image
   - Creates container using CRI (containerd/Docker)
   - Starts the container process

### Resource Requests vs Limits

| Aspect              | Requests                                 | Limits                       |
| ------------------- | ---------------------------------------- | ---------------------------- |
| **Purpose**         | Guaranteed resources                     | Maximum resources            |
| **Scheduling**      | Used by scheduler to find suitable nodes | Not used in scheduling       |
| **Enforcement**     | Not enforced (pod may use more)          | Enforced by cgroups          |
| **CPU behavior**    | Minimum CPU share                        | CPU throttling when exceeded |
| **Memory behavior** | Minimum memory                           | OOM kill when exceeded       |

**In our deployment:**

```yaml
resources:
  requests:
    cpu: "100m" # Guaranteed 0.1 CPU core
    memory: "128Mi" # Guaranteed 128 MiB
  limits:
    cpu: "500m" # Throttled above 0.5 CPU core
    memory: "512Mi" # OOM killed above 512 MiB
```

### Rolling Update Strategy

Our deployment uses a zero-downtime rolling update strategy:

```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1 # Allow 1 extra pod during update
    maxUnavailable: 0 # Never have fewer than 3 pods running
```

**Update Process:**

1. **Initial state**: 3 pods running (v1)
2. **Create new pod**: 4 pods total (3 v1, 1 v2)
3. **Wait for readiness**: New pod passes readiness probe
4. **Terminate old pod**: 3 pods total (2 v1, 1 v2)
5. **Repeat**: Until all pods are v2
6. **Final state**: 3 pods running (v2)

**Result**: Always maintain at least 3 ready pods, ensuring zero downtime.

### Health Checks

#### Liveness Probe

- **Purpose**: Detect if the application is alive
- **Action**: Restart the pod if it fails
- **Endpoint**: `/health`
- **Use case**: Deadlocked application, crashed process

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  failureThreshold: 3 # Restart after 30s of failures
```

#### Readiness Probe

- **Purpose**: Detect if the application can serve traffic
- **Action**: Remove from service endpoints if it fails
- **Endpoint**: `/ready`
- **Use case**: Model loading, warming up, temporary unavailability

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  failureThreshold: 3 # Remove from service after 15s of failures
```

**Key Difference**: Liveness restarts the pod, readiness just stops routing traffic.

## 🐧 Linux & Systems Internals

### Containers = Processes + Isolation

A container is fundamentally a Linux process with isolation and resource limits:

#### 1. Namespaces (Isolation)

Namespaces provide process isolation:

| Namespace   | Isolation                                                 |
| ----------- | --------------------------------------------------------- |
| **PID**     | Process IDs (container sees its own PID 1)                |
| **Network** | Network interfaces, IP addresses, routing tables          |
| **Mount**   | Filesystem mounts (container has its own root filesystem) |
| **UTS**     | Hostname and domain name                                  |
| **IPC**     | Inter-process communication (shared memory, semaphores)   |
| **User**    | User and group IDs (map container root to host non-root)  |

**Example**: When you run a container, it sees itself as PID 1, but on the host it's just another process (e.g., PID 12345).

```bash
# Inside container
$ ps aux
USER  PID  COMMAND
root    1  uvicorn main:app

# On host
$ ps aux | grep uvicorn
1000  12345  /opt/venv/bin/python /opt/venv/bin/uvicorn main:app
```

#### 2. Cgroups (Resource Control)

Cgroups (Control Groups) enforce resource limits:

| Cgroup      | Purpose         | Enforcement            |
| ----------- | --------------- | ---------------------- |
| **cpu**     | CPU usage       | Throttling (CFS quota) |
| **memory**  | Memory usage    | OOM killer             |
| **blkio**   | Disk I/O        | I/O throttling         |
| **net_cls** | Network traffic | Traffic shaping        |

**CPU Limiting:**

```bash
# Our limit: 500m (0.5 CPU core)
# Cgroup setting: cpu.cfs_quota_us = 50000 (50ms out of 100ms period)
# If process tries to use more, it's throttled (paused until next period)
```

**Memory Limiting:**

```bash
# Our limit: 512Mi
# Cgroup setting: memory.limit_in_bytes = 536870912
# If process exceeds this, the OOM killer terminates it
# Kubernetes then restarts the pod (liveness probe failure)
```

#### 3. Kubernetes Pod = Shared Namespaces

A Kubernetes pod is a group of containers sharing certain namespaces:

- **Shared**: Network namespace (same IP, localhost communication)
- **Shared**: IPC namespace (can use shared memory)
- **Isolated**: PID namespace (each container has its own PID 1)
- **Isolated**: Mount namespace (each container has its own filesystem)

### How Resource Limits Affect ML Workloads

#### CPU Limits

- **Impact**: Model inference is CPU-bound (matrix operations)
- **Throttling**: If inference takes too long, CPU is throttled
- **Result**: Increased latency, slower predictions
- **Mitigation**: Set appropriate limits based on load testing

#### Memory Limits

- **Impact**: Model loading requires memory (scikit-learn model in RAM)
- **OOM Kill**: If model + data exceeds limit, pod is killed
- **Result**: Pod restart, service disruption
- **Mitigation**:
  - Profile memory usage during model loading
  - Set limits with headroom (e.g., model uses 200Mi, set limit to 512Mi)
  - Use model compression techniques

#### Resource Quota Impact

- **Namespace quota**: Limits total resources across all pods
- **Example**: With 3 replicas requesting 100m CPU each, we use 300m of our 2 CPU quota
- **Scaling**: Can scale up to ~20 pods before hitting quota (2000m / 100m)

## 🔄 Production Considerations

### Scaling

```bash
# Horizontal scaling (more replicas)
kubectl scale deployment ml-inference -n ml-platform --replicas=5

# Check resource quota usage
kubectl describe resourcequota -n ml-platform
```

### Monitoring

Add Prometheus metrics:

```python
from prometheus_client import Counter, Histogram

prediction_counter = Counter('predictions_total', 'Total predictions')
prediction_latency = Histogram('prediction_latency_seconds', 'Prediction latency')
```

### Logging

Our service uses structured JSON logging:

```json
{
  "timestamp": "2026-01-04T17:15:00",
  "level": "INFO",
  "logger": "main",
  "message": "Prediction successful: setosa"
}
```

Aggregate logs with:

- **Fluentd/Fluent Bit**: Log collection
- **Elasticsearch**: Log storage
- **Kibana**: Log visualization

### High Availability

Current setup provides:

- **3 replicas**: Survive 2 pod failures
- **Rolling updates**: Zero downtime deployments
- **Health checks**: Automatic pod restart and traffic removal

For production:

- Add **pod anti-affinity** to spread across nodes
- Use **pod disruption budgets** to limit voluntary disruptions
- Deploy across **multiple availability zones**

### Security

Implemented:

- ✅ Non-root user (UID 1000)
- ✅ Read-only root filesystem (where possible)
- ✅ Drop all capabilities
- ✅ Resource limits (prevent DoS)

Additional recommendations:

- Use **network policies** to restrict traffic
- Enable **pod security standards** (restricted)
- Scan images for vulnerabilities
- Use **secrets** for sensitive data (not environment variables)

## 🎯 How This Mirrors Real Production ML Platforms

This mini platform demonstrates core concepts used in production ML systems:

| Concept                 | This Platform             | Real Production (e.g., Uber Michelangelo, Netflix)               |
| ----------------------- | ------------------------- | ---------------------------------------------------------------- |
| **Containerization**    | Docker multi-stage builds | Same, plus image scanning and signing                            |
| **Orchestration**       | Kubernetes Deployment     | Same, plus service mesh (Istio/Linkerd)                          |
| **Resource Management** | Requests/limits, quotas   | Same, plus autoscaling (HPA/VPA)                                 |
| **Health Checks**       | Liveness/readiness probes | Same, plus custom health metrics                                 |
| **Load Balancing**      | ClusterIP service         | Same, plus ingress controllers and external LBs                  |
| **Observability**       | Structured logging        | Same, plus distributed tracing (Jaeger) and metrics (Prometheus) |
| **Rolling Updates**     | Zero-downtime deployments | Same, plus canary/blue-green deployments                         |
| **Model Serving**       | In-process (scikit-learn) | Same pattern, plus TensorFlow Serving, TorchServe                |

**Key Differences from Managed Platforms:**

- **SageMaker/Vertex AI**: Abstract Kubernetes away, provide higher-level APIs
- **This platform**: Exposes Kubernetes internals for learning and control
- **Trade-off**: More complexity, but deeper understanding and flexibility

## 📚 Learning Resources

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Container Networking](https://www.oreilly.com/library/view/container-networking/9781492036845/)
- [Linux Namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)
- [Cgroups](https://www.kernel.org/doc/Documentation/cgroup-v2.txt)

## 🧪 Testing & Verification

### Test Rolling Update

```bash
# Update the image
kubectl set image deployment/ml-inference ml-inference=ml-inference:v2 -n ml-platform

# Watch the rollout
kubectl rollout status deployment/ml-inference -n ml-platform

# Verify zero downtime (run in separate terminal during update)
while true; do curl -s http://localhost:8080/health && echo " - $(date)"; sleep 1; done
```

### Test Pod Restart

```bash
# Delete a pod
kubectl delete pod -n ml-platform -l app=ml-inference --force --grace-period=0

# Watch automatic recreation
kubectl get pods -n ml-platform -w
```

### Test Resource Limits

```bash
# Check resource usage
kubectl top pods -n ml-platform

# Describe pod to see limits
kubectl describe pod -n ml-platform -l app=ml-inference
```

## 📝 License

MIT License - Feel free to use this for learning and production projects.

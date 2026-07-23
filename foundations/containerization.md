# Containerization for Data Engineers

Docker and Kubernetes concepts every DE needs for modern data
platforms — Airflow on K8s, Spark on K8s, Flink on K8s.

---

## 1. Docker Fundamentals

### Images vs Containers

| Concept | Analogy |
|---|---|
| **Image** | A class / blueprint — read-only template with OS + app + dependencies |
| **Container** | An instance — running process with its own filesystem, network, and process namespace |
| **Dockerfile** | Recipe for building an image |
| **Registry** | Storage for images (Docker Hub, ECR, GCR, ACR) |
| **Layer** | Each instruction in a Dockerfile adds a layer (cached, reusable) |

### Dockerfile for Data Engineering

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    openjdk-17-jre-headless \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV SPARK_HOME=/opt/spark
CMD ["spark-submit", "main.py"]
```

**Best practices:**
- Use slim/base images, not full OS images
- Combine `RUN` commands to reduce layers
- Multi-stage builds for compiled dependencies
- Never hardcode credentials (use env vars or secrets mounts)

### Key Docker Commands for DEs

```bash
docker build -t my-spark-job:latest .   # Build image
docker run my-spark-job:latest           # Run locally
docker push my-repo/my-spark-job:latest  # Push to registry
docker rmi my-spark-job:latest           # Remove image
docker system prune -a                   # Clean unused images/containers
```

---

## 2. Kubernetes Fundamentals

### Architecture

```
┌──────────────────────────────────────────────────┐
│                  Control Plane                    │
│  ┌──────────┐  ┌──────────┐  ┌────────────────┐  │
│  │ API      │  │ Scheduler │  │ Controller     │  │
│  │ Server   │  │           │  │ Manager        │  │
│  └────┬─────┘  └──────────┘  └────────────────┘  │
│       │                                            │
│  ┌────▼─────┐                                      │
│  │ etcd     │  (cluster state, like a brain)       │
│  └──────────┘                                      │
└──────────────────────────┬───────────────────────┘
                           │
     ┌─────────────────────┼─────────────────────┐
     ▼                     ▼                     ▼
┌──────────┐        ┌──────────┐        ┌──────────┐
│ Worker 1 │        │ Worker 2 │        │ Worker 3 │
│ ┌──────┐ │        │ ┌──────┐ │        │ ┌──────┐ │
│ │Pods  │ │        │ │Pods  │ │        │ │Pods  │ │
│ │  ▼   │ │        │ │  ▼   │ │        │ │  ▼   │ │
│ │Container│       │ │Container│       │ │Container│
│ └──────┘ │        │ └──────┘ │        │ └──────┘ │
│ ┌──────┐ │        │ ┌──────┐ │        │ ┌──────┐ │
│ │Kubelet│ │        │ │Kubelet│ │        │ │Kubelet│ │
│ └──────┘ │        │ └──────┘ │        │ └──────┘ │
└──────────┘        └──────────┘        └──────────┘
```

### Core Concepts

| Concept | What It Is | DE Relevance |
|---|---|---|
| **Pod** | Smallest unit — one or more containers with shared network/storage | Your Spark executor runs in a pod |
| **Deployment** | Declares desired replica count, handles rollouts | Deploying Airflow webserver/scheduler |
| **Service** | Stable network endpoint to access pods | Airflow UI, Spark UI access |
| **ConfigMap / Secret** | Configuration and sensitive data injection | DB credentials, Spark configs |
| **PersistentVolumeClaim** | Storage request (not ephemeral) | Flink checkpoint storage |
| **Namespace** | Virtual cluster within a K8s cluster | Separate dev/staging/prod |
| **HorizontalPodAutoscaler** | Auto-scale pods based on CPU/memory/custom metrics | Dynamic executor scaling for Spark |

### Resource Management

```yaml
# Pod resource spec for a Spark executor
apiVersion: v1
kind: Pod
spec:
  containers:
  - name: spark-executor
    resources:
      requests:       # Guaranteed minimum
        memory: "4Gi"
        cpu: "1"
      limits:         # Maximum allowed
        memory: "8Gi"
        cpu: "2"
```

**OOM risk:** No limits → pod consumes all node memory.
Limits = requests → guaranteed QoS (no eviction).

---

## 3. Data Engineering on Kubernetes

### Apache Spark on K8s

| Mode | How It Works | When to Use |
|---|---|---|
| **Client mode** | Driver runs outside cluster (e.g., your laptop); executors in pods | Dev/testing |
| **Cluster mode** | Driver runs inside a pod; all components on K8s | Production |

```bash
spark-submit \
  --master k8s://https://${K8S_API_SERVER} \
  --deploy-mode cluster \
  --conf spark.kubernetes.container.image=my-repo/spark-job:latest \
  --conf spark.kubernetes.executor.instances=10 \
  --conf spark.executor.memory=8g \
  main.py
```

### Airflow on K8s

```
KubernetesExecutor (recommended over CeleryExecutor):

1. Each task runs in its own pod (isolated)
2. Pods are created on-demand, killed after completion
3. No need to pre-provision worker pools
4. Resource per task can differ (e.g., memory-heavy task gets a bigger pod)
```

### Flink on K8s

| Mode | Description |
|---|---|
| **Session cluster** | Long-running JobManager; multiple jobs share it |
| **Job cluster** | JobManager per job; dedicated resources |
| **Flink Kubernetes Operator** | Declarative lifecycle via CRDs (e.g., `FlinkDeployment` custom resource) |

---

## 4. Common DE Interview Questions

**Q: Why run Spark on K8s instead of YARN?**
- No need for separate Hadoop cluster
- Better resource isolation (cgroups)
- Easier CI/CD with container images
- Multi-tenancy with namespaces
- Cloud-agnostic (run on EKS, GKE, AKS)

**Q: What happens when a pod fails during a Spark job?**
Spark detects executor loss via the driver's heartbeat. It re-schedules
lost tasks on other executors (or new pods if using dynamic allocation).
Tasks are idempotent — re-running produces the same result.

**Q: How does the Kubernetes scheduler differ from Spark's scheduler?**
K8s schedules pods to nodes based on resource requests/limits and node
affinity. Spark schedules tasks to executors within the application
itself. In K8s mode, the Spark driver requests pods from K8s, then
distributes tasks among them.

**Q: What is pod eviction and how do you handle it?**
K8s evicts pods when a node runs out of resources (preemption).
Mitigations:
- Set resource `requests = limits` (Guaranteed QoS)
- Use pod disruption budgets
- Enable Spark dynamic allocation for graceful replacement
- Store checkpoints on durable storage (S3/GCS/ABS)

---

## Quick Reference

| Task | Best Practice |
|---|---|
| Build images | Slim base, multi-stage, no hardcoded creds |
| Spark deployment | Cluster mode on K8s for production |
| Airflow executor | KubernetesExecutor (pod-per-task) |
| Resource requests | Always set both `requests` and `limits` |
| Config injection | ConfigMaps for non-sensitive, Secrets for credentials |
| Pod failure handling | Idempotent tasks + checkpointing |
| Local testing | Docker Compose, kind, or minikube |
| Production cluster | Managed K8s (EKS, GKE, AKS) |

>

---

> [!TIP]
> DE interviews increasingly ask about Kubernetes because Airflow,
> Spark, and Flink all run on K8s in modern setups. Know the
> `KubernetesExecutor` pattern for Airflow and cluster-mode for Spark.

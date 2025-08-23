# Kubernetes Deployments and ReplicaSets Tutorial

This tutorial demonstrates Kubernetes Deployments, ReplicaSets, and their behavior during updates. You'll learn about rolling updates, blue-green deployments, and the limitations of basic Kubernetes constructs.

## Prerequisites

- A running Kubernetes cluster
- `kubectl` configured to communicate with your cluster
- Basic understanding of Kubernetes concepts

## 1. Basic Deployment with 2 Replicas

Let's start with a simple deployment that runs 2 replicas of an nginx web server.

### Create the initial deployment

```bash
# Apply deployment directly without creating files
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        ports:
        - containerPort: 80
EOF
```

## 2. Monitoring Deployments and ReplicaSets

### Key Display Commands

Let's explore the essential commands to monitor our deployment and its components:

```bash
# View deployments
kubectl get deployments
kubectl get deployments -o wide

# View ReplicaSets
kubectl get replicasets
kubectl get rs -o wide

# View pods
kubectl get pods
kubectl get pods -o wide

# Get detailed information
kubectl describe deployment nginx-deployment
kubectl describe rs
kubectl describe pods

# Watch resources in real-time
kubectl get pods -w
```

### Understanding the Relationship

When you create a deployment, Kubernetes automatically creates a ReplicaSet that manages the pods:

```bash
# See the hierarchy
kubectl get all -l app=nginx

# Expected output shows:
# - 1 Deployment
# - 1 ReplicaSet (managed by the deployment)
# - 2 Pods (managed by the ReplicaSet)
```

## 3. Triggering a New ReplicaSet

Now let's see what happens when we update the deployment. Any change to the pod template will trigger a new ReplicaSet.

### Method 1: Update the Image Version

```bash
# Update the nginx image to a newer version
kubectl set image deployment/nginx-deployment nginx=nginx:1.21

# Watch the rollout
kubectl rollout status deployment/nginx-deployment
```

### Method 2: Edit the Deployment YAML

Update the deployment directly:

```bash
# Apply updated deployment with new version and labels
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  labels:
    app: nginx
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
        version: "v2"  # Adding a new label triggers update
    spec:
      containers:
      - name: nginx
        image: nginx:1.21  # Updated image version
        ports:
        - containerPort: 80
        env:  # Adding environment variables
        - name: ENVIRONMENT
          value: "production"
EOF
```

### Observing the ReplicaSet Behavior

During the update, observe how Kubernetes manages ReplicaSets:

```bash
# Watch ReplicaSets during update
kubectl get rs -w

# You'll see:
# - Old ReplicaSet scaling down (2 -> 1 -> 0)
# - New ReplicaSet scaling up (0 -> 1 -> 2)
```

## 4. Rolling Updates (Default Strategy)

Rolling updates are the default deployment strategy in Kubernetes.

### Rolling Update Configuration

```bash
# Apply deployment with rolling update configuration
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 4  # More replicas to see rolling behavior better
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1      # Max pods that can be unavailable
      maxSurge: 1           # Max extra pods during update
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        ports:
        - containerPort: 80
EOF
```

### Demonstrating Rolling Update

```bash
# Apply the configuration with 4 replicas (if not already applied above)
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        ports:
        - containerPort: 80
EOF

# Trigger an update and watch the rolling process
kubectl set image deployment/nginx-deployment nginx=nginx:1.21
kubectl get pods -w

# Monitor the rollout progress
kubectl rollout status deployment/nginx-deployment

# View rollout history
kubectl rollout history deployment/nginx-deployment
```

### Rolling Update Behavior

During a rolling update, you'll observe:
- Old pods are terminated gradually
- New pods are created gradually
- Application remains available throughout the update
- Both old and new versions run simultaneously for a brief period

## 5. Blue-Green Deployment Strategy

### Cleanup Previous Deployment

Before demonstrating blue-green deployment, let's clean up the previous deployment to avoid confusion:

```bash
# Clean up the previous rolling update deployment
kubectl delete deployment nginx-deployment

# Verify cleanup
kubectl get deployments
kubectl get pods
```

Kubernetes doesn't have built-in blue-green deployment, but we can simulate it using labels and services.

### Blue-Green Setup

```bash
# Deploy blue-green setup with service and both deployments
kubectl apply -f - << 'EOF'
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx
    version: blue  # Initially points to blue
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
---
# Blue deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-blue
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
      version: blue
  template:
    metadata:
      labels:
        app: nginx
        version: blue
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        ports:
        - containerPort: 80
---
# Green deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-green
spec:
  replicas: 2
  selector:
    matchLabels:
      app: nginx
      version: green
  template:
    metadata:
      labels:
        app: nginx
        version: green
    spec:
      containers:
      - name: nginx
        image: nginx:1.21  # New version
        ports:
        - containerPort: 80
EOF
```

### Blue-Green Deployment Process

```bash
# 1. Deploy blue-green setup (use the command above if not already deployed)

# 2. Verify blue deployment is serving traffic
kubectl get pods -l version=blue
kubectl get pods -l version=green
kubectl get pods --show-labels

# 3. Test the service (points to blue initially)
kubectl get service nginx-service

# 4. Switch traffic to green (manual step)
kubectl get pod -o wide
kubectl get pods --show-labels
kubectl describe  service nginx-service
kubectl patch service nginx-service -p '{"spec":{"selector":{"version":"green"}}}'

# 5. Verify traffic switched
kubectl describe service nginx-service

# 6. Clean up blue deployment after verification
kubectl delete deployment nginx-blue
```

### Blue-Green Characteristics

- **Instant switch**: Traffic switches immediately from blue to green
- **Zero downtime**: No service interruption during switch
- **Easy rollback**: Can quickly switch back to blue if issues arise
- **Resource overhead**: Requires running both versions simultaneously

## 6. Recreate Deployment Strategy

For applications that cannot handle multiple versions running simultaneously:

```bash
# Apply deployment with recreate strategy
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 2
  strategy:
    type: Recreate  # All pods terminated before new ones created
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        ports:
        - containerPort: 80
EOF
```

### Recreate Strategy Behavior

```bash
# Apply recreate deployment (if not already applied above)
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
spec:
  replicas: 2
  strategy:
    type: Recreate
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
        ports:
        - containerPort: 80
EOF

# Trigger update and observe
kubectl set image deployment/nginx-deployment nginx=nginx:1.21
kubectl get pods -w

# You'll see:
# - All old pods terminated first
# - Brief period with no running pods
# - New pods created after old ones are gone
```

## 7. Rollback Operations

Kubernetes provides built-in rollback capabilities:

```bash
# View rollout history
kubectl rollout history deployment/nginx-deployment

# Rollback to previous version
kubectl rollout undo deployment/nginx-deployment

# Rollback to specific revision
kubectl rollout undo deployment/nginx-deployment --to-revision=2

# Check rollback status
kubectl rollout status deployment/nginx-deployment
```

## 8. Limitations: Advanced Deployment Patterns

While Kubernetes deployments are powerful, they have limitations for advanced patterns:

### Canary Deployments - Not Directly Supported

Basic Kubernetes deployments cannot easily implement true canary deployments because:

1. **No traffic splitting**: Deployments don't provide fine-grained traffic control
2. **Binary scaling**: You can't easily send 5% traffic to new version
3. **No metrics-based promotion**: No built-in automated promotion based on metrics

### Manual Canary Simulation (Limited)

```bash
# Deploy canary setup with stable and canary deployments
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-stable
spec:
  replicas: 9  # 90% of traffic (approximately)
  selector:
    matchLabels:
      app: nginx
      track: stable
  template:
    metadata:
      labels:
        app: nginx
        track: stable
    spec:
      containers:
      - name: nginx
        image: nginx:1.20
---
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-canary
spec:
  replicas: 1  # 10% of traffic (approximately)
  selector:
    matchLabels:
      app: nginx
      track: canary
  template:
    metadata:
      labels:
        app: nginx
        track: canary
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
spec:
  selector:
    app: nginx  # Matches both stable and canary
  ports:
  - port: 80
EOF
```

**Issues:**
- Traffic distribution is not precise (depends on pod scheduling)
- No automatic promotion/rollback based on metrics
- Difficult to control traffic percentage precisely
- Manual management required

### Solutions for Advanced Patterns

For true canary deployments and advanced patterns, you need additional tools:

1. **Istio Service Mesh**: Provides traffic splitting, A/B testing
2. **Argo Rollouts**: Advanced deployment controller
3. **Flagger**: Progressive delivery operator
4. **Nginx Ingress**: Can provide some traffic splitting capabilities

Example with Argo Rollouts (advanced):
```yaml
# This requires Argo Rollouts operator (not basic Kubernetes)
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: nginx-rollout
spec:
  replicas: 5
  strategy:
    canary:
      steps:
      - setWeight: 20  # 20% traffic to new version
      - pause: {duration: 1m}
      - setWeight: 40
      - pause: {duration: 1m}
      - setWeight: 60
      - pause: {duration: 1m}
      - setWeight: 80
      - pause: {duration: 1m}
```

## 9. Best Practices and Key Takeaways

### Deployment Best Practices

1. **Use Rolling Updates**: Default for zero-downtime deployments
2. **Set Resource Limits**: Ensure predictable behavior
3. **Configure Readiness Probes**: Prevent traffic to unready pods
4. **Use Deployment History**: Keep track of changes
5. **Test Rollbacks**: Ensure you can quickly revert changes

### Resource Management

```bash
# Apply production-ready deployment template
kubectl apply -f - << 'EOF'
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-production
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 1
  selector:
    matchLabels:
      app: nginx
  template:
    metadata:
      labels:
        app: nginx
    spec:
      containers:
      - name: nginx
        image: nginx:1.21
        ports:
        - containerPort: 80
        resources:
          requests:
            memory: "64Mi"
            cpu: "50m"
          limits:
            memory: "128Mi"
            cpu: "100m"
        readinessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 5
          periodSeconds: 5
        livenessProbe:
          httpGet:
            path: /
            port: 80
          initialDelaySeconds: 15
          periodSeconds: 20
EOF
```

### Key Takeaways

1. **Deployments manage ReplicaSets**: Each update creates a new ReplicaSet
2. **ReplicaSets manage Pods**: Ensure desired number of replicas
3. **Rolling updates are default**: Provide zero-downtime deployments
4. **Blue-green requires manual setup**: Not built into basic deployments
5. **Advanced patterns need additional tools**: Basic Kubernetes has limitations
6. **Always test rollback procedures**: Critical for production environments

## 10. Cleanup

When you're done with the tutorial:

```bash
# Clean up all resources
kubectl delete deployment nginx-deployment nginx-blue nginx-green nginx-stable nginx-canary nginx-production
kubectl delete service nginx-service
```

## Summary

This tutorial covered:
- ✅ Basic deployments with 2 replicas
- ✅ Triggering new ReplicaSets through spec changes
- ✅ Essential display commands for monitoring
- ✅ Rolling update behavior and configuration
- ✅ Blue-green deployment simulation
- ✅ Limitations of basic Kubernetes for advanced patterns like canary deployments

For production environments, consider using specialized tools like Argo Rollouts, Istio, or Flagger for advanced deployment patterns that basic Kubernetes deployments cannot easily provide.
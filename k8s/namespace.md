# Kubernetes Namespaces Demo

## Overview
Kubernetes namespaces provide a mechanism for isolating groups of resources within a single cluster. Think of namespaces as virtual clusters backed by the same physical cluster. They are intended for use in environments with many users spread across multiple teams or projects.

## Key Concepts
- **Resource Isolation**: Namespaces provide a scope for names - resources in different namespaces can have the same name
- **Resource Quotas**: Apply limits on compute resources (CPU, memory) and object counts per namespace
- **Access Control**: Use RBAC to control who can access resources in specific namespaces
- **Network Policies**: Isolate network traffic between namespaces
- **Multi-tenancy**: Enable multiple teams to share the same cluster safely

## Default Namespaces in AKS

Every AKS cluster starts with several built-in namespaces:

```bash
# List all namespaces
kubectl get namespaces
# or short form
kubectl get ns

# Expected output shows default namespaces:
# default           Active   1d    # Default namespace for objects with no other namespace
# kube-system       Active   1d    # For objects created by Kubernetes system
# kube-public       Active   1d    # Readable by all users (including unauthenticated)
# kube-node-lease   Active   1d    # For node heartbeat data
```

## Demo Commands

### 1. Basic Namespace Operations

#### Create Namespaces
```bash
# Method 1: Using kubectl create
kubectl create namespace development
kubectl create namespace staging  
kubectl create namespace production

# Method 2: Using YAML manifest
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: testing
  labels:
    env: test
    team: qa
EOF

# Method 3: Using kubectl create with labels
kubectl create namespace demo --dry-run=client -o yaml | kubectl apply -f -
```

#### List and Inspect Namespaces
```bash
# List all namespaces
kubectl get namespaces

# Show namespace details
kubectl describe namespace development

# Get namespace with labels
kubectl get namespace --show-labels

# Filter by labels
kubectl get namespace -l env=test
```

#### Delete Namespaces
```bash
# Delete a namespace (this deletes ALL resources in the namespace)
kubectl delete namespace testing

# Delete multiple namespaces
kubectl delete namespace development staging
```

### 2. Working with Resources in Namespaces

#### Deploy Resources to Specific Namespaces
```bash
# Create a namespace for our demo
kubectl create namespace demo-app

# Deploy nginx to specific namespace
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-deployment
  namespace: demo-app
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
        image: nginx:latest
        ports:
        - containerPort: 80
---
apiVersion: v1
kind: Service
metadata:
  name: nginx-service
  namespace: demo-app
spec:
  selector:
    app: nginx
  ports:
  - port: 80
    targetPort: 80
  type: ClusterIP
EOF

# Alternative: Use -n flag to specify namespace
kubectl create deployment nginx --image=nginx -n demo-app
kubectl expose deployment nginx --port=80 -n demo-app
```

#### View Resources in Namespaces
```bash
# List resources in specific namespace
kubectl get pods -n demo-app
kubectl get services -n demo-app
kubectl get deployments -n demo-app

# Get all resources in a namespace
kubectl get all -n demo-app

# List resources across all namespaces
kubectl get pods --all-namespaces
# or short form
kubectl get pods -A

# Compare resources in different namespaces
kubectl get pods -n default
kubectl get pods -n kube-system
kubectl get pods -n demo-app
```

### 3. Namespace Context and Configuration

#### Set Default Namespace Context
```bash
# View current context
kubectl config current-context

# View current namespace context
kubectl config view --minify | grep namespace

# Set default namespace for current context
kubectl config set-context --current --namespace=demo-app

# Verify the change
kubectl config view --minify | grep namespace

# Now kubectl commands default to demo-app namespace
kubectl get pods  # Shows pods in demo-app namespace

# Reset to default namespace
kubectl config set-context --current --namespace=default
```


### 4. Resource Quotas and Limits

#### Apply Resource Quotas
```bash
# Create namespace with resource quota
kubectl create namespace quota-demo

# Apply resource quota
# Here you can realize how a cluster is divided and allocated to a namespace  (virtual cluster concept)
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: compute-quota
  namespace: quota-demo
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    limits.cpu: "4" 
    limits.memory: 8Gi
    persistentvolumeclaims: "10"
    pods: "10"
    services: "5"
    secrets: "10"
    configmaps: "10"
EOF

# View resource quota
kubectl describe resourcequota compute-quota -n quota-demo

# Try to deploy without resource limits (will fail)
kubectl create deployment nginx --image=nginx -n quota-demo

# Deploy with resource limits (will succeed)
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: nginx-with-limits
  namespace: quota-demo
spec:
  replicas: 1
  selector:
    matchLabels:
      app: nginx-limited
  template:
    metadata:
      labels:
        app: nginx-limited
    spec:
      containers:
      - name: nginx
        image: nginx:latest
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 200m
            memory: 256Mi
        ports:
        - containerPort: 80
EOF

# Check quota usage
kubectl describe resourcequota compute-quota -n quota-demo

# Try to exceed quota limits to see how it works
# This deployment will fail due to CPU quota exceeded (requests 3 CPUs but quota allows only 2)
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: quota-breaker
  namespace: quota-demo
spec:
  replicas: 2
  selector:
    matchLabels:
      app: quota-breaker
  template:
    metadata:
      labels:
        app: quota-breaker
    spec:
      containers:
      - name: resource-hog
        image: nginx:latest
        resources:
          requests:
            cpu: 1500m    # 1.5 CPU per pod, 2 pods = 3 CPU total (exceeds 2 CPU quota)
            memory: 1Gi   # 1 GB per pod, 2 pods = 2 GB total (within 4 GB quota)
          limits:
            cpu: 2000m    # 2 CPU per pod, 2 pods = 4 CPU total (matches 4 CPU limit quota)
            memory: 2Gi   # 2 GB per pod, 2 pods = 4 GB total (within 8 GB limit quota)
        ports:
        - containerPort: 80
EOF

# Check the deployment status - it should show issues with replica creation
kubectl get deployment quota-breaker -n quota-demo
kubectl describe deployment quota-breaker -n quota-demo

# Check replica set status to see quota enforcement
kubectl get replicaset -n quota-demo
kubectl describe replicaset -l app=quota-breaker -n quota-demo

# View current quota usage after attempting to exceed limits
kubectl describe resourcequota compute-quota -n quota-demo

# Try a deployment that exceeds pod count limit (quota allows max 10 pods)
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: pod-count-breaker
  namespace: quota-demo
spec:
  replicas: 15  # Exceeds 10 pod limit
  selector:
    matchLabels:
      app: pod-count-breaker
  template:
    metadata:
      labels:
        app: pod-count-breaker
    spec:
      containers:
      - name: small-pod
        image: nginx:latest
        resources:
          requests:
            cpu: 50m      # Small CPU request to stay within quota
            memory: 64Mi  # Small memory request
          limits:
            cpu: 100m
            memory: 128Mi
        ports:
        - containerPort: 80
EOF

# Check how many pods actually get created vs requested
kubectl get pods -n quota-demo -l app=pod-count-breaker
kubectl get deployment pod-count-breaker -n quota-demo
k get events  -n quota-demo

# View final quota usage
kubectl describe resourcequota compute-quota -n quota-demo
```

#### Apply Limit Ranges
```bash
# Create default resource limits for the namespace
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: LimitRange
metadata:
  name: default-limits
  namespace: quota-demo
spec:
  limits:
  - default:
      cpu: 200m
      memory: 256Mi
    defaultRequest:
      cpu: 100m
      memory: 128Mi
    type: Container
EOF

# View limit range
kubectl describe limitrange default-limits -n quota-demo

# Now deployments without explicit limits will get defaults
kubectl create deployment auto-limits --image=busybox -n quota-demo -- sleep 3600

# Check the applied limits
kubectl describe pod -l app=auto-limits -n quota-demo
```

### 5. Cross-Namespace Communication

#### Deploy Services in Different Namespaces
```bash
# Create frontend and backend namespaces
kubectl create namespace frontend
kubectl create namespace backend

# Deploy backend service
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: backend-api
  namespace: backend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: backend-api
  template:
    metadata:
      labels:
        app: backend-api
    spec:
      containers:
      - name: api
        image: nicolaka/netshoot
        command: ['sh', '-c', 'while true; do echo "Backend API Response" | nc -l -p 8080; done']
        ports:
        - containerPort: 8080
---
apiVersion: v1
kind: Service
metadata:
  name: backend-service
  namespace: backend
spec:
  selector:
    app: backend-api
  ports:
  - port: 8080
    targetPort: 8080
  type: ClusterIP
EOF

# Deploy frontend service
cat <<EOF | kubectl apply -f -
apiVersion: apps/v1
kind: Deployment
metadata:
  name: frontend-app
  namespace: frontend
spec:
  replicas: 1
  selector:
    matchLabels:
      app: frontend-app
  template:
    metadata:
      labels:
        app: frontend-app
    spec:
      containers:
      - name: frontend
        image: nicolaka/netshoot
        command: ['sleep', '3600']
        ports:
        - containerPort: 80
EOF
```

#### Test Cross-Namespace Communication
```bash
# Get backend service details
kubectl get service backend-service -n backend

# Test communication from frontend to backend
# Service DNS format: <service-name>.<namespace>.svc.cluster.local
kubectl exec -it deployment/frontend-app -n frontend -- nslookup backend-service.backend.svc.cluster.local

# Test HTTP communication
kubectl exec -it deployment/frontend-app -n frontend -- curl http://backend-service.backend.svc.cluster.local:8080

# Test short DNS name (works across namespaces)
kubectl exec -it deployment/frontend-app -n frontend -- curl http://backend-service.backend:8080

# From same namespace, only service name needed
kubectl exec -it deployment/backend-api -n backend -- curl http://backend-service:8080
```


#### Monitor Namespace Resource Usage
```bash
# Install metrics server if not already available (AKS usually has it)
# kubectl apply -f https://github.com/kubernetes-sigs/metrics-server/releases/latest/download/components.yaml
# AKS installs metrics server by default

# View resource usage by namespace
kubectl top pods --all-namespaces
kubectl top nodes

# View resource usage for specific namespace
kubectl top pods -n demo-app

# Get resource quota status
kubectl get resourcequota --all-namespaces
```


### Namespace Cleanup and Management

#### Clean Up Resources
```bash
# Delete specific resources from namespace
kubectl delete deployment webapp -n dev
kubectl delete service webapp-service -n dev

# Delete all resources in a namespace (keeps the namespace)
kubectl delete all --all -n test

# Delete entire namespace (removes namespace and all resources)
kubectl delete namespace staging

# Bulk delete namespaces by label
kubectl delete namespace -l environment=test

# Safe cleanup with confirmation
kubectl get all -n demo-app
read -p "Delete all resources in demo-app namespace? (y/N): " confirm
if [ "$confirm" = "y" ]; then
  kubectl delete namespace demo-app
fi
```

#### Namespace Lifecycle Management
```bash
# Create namespace with finalizers for cleanup hooks
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Namespace
metadata:
  name: managed-ns
  finalizers:
  - example.com/cleanup-hook
spec: {}
EOF

# View namespace status
kubectl get namespace managed-ns -o yaml

# Remove finalizer to allow deletion
kubectl patch namespace managed-ns -p '{"metadata":{"finalizers":null}}' --type=merge

# Delete the namespace
kubectl delete namespace managed-ns
```

## Real-World Scenarios

### Scenario 1: Multi-Tenant SaaS Application
```bash
# Create tenant namespaces
kubectl create namespace tenant-acme
kubectl create namespace tenant-globex

# Apply tenant-specific resource quotas
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: ResourceQuota
metadata:
  name: tenant-quota
  namespace: tenant-acme
spec:
  hard:
    requests.cpu: "2"
    requests.memory: 4Gi
    pods: "20"
    services: "10"
    persistentvolumeclaims: "5"
EOF

# Deploy tenant applications with isolation
# Each tenant gets their own database, cache, and application instances
```

### Scenario 2: Development Team Isolation
```bash
# Create team namespaces
kubectl create namespace team-frontend
kubectl create namespace team-backend
kubectl create namespace team-data

# Apply RBAC for team access control
# Each team can only access their namespace
```

### Scenario 3: Environment Promotion Pipeline
```bash
# Application flows through: dev → test → staging → prod
# Each environment is a separate namespace with appropriate controls
# Automated CI/CD pipelines promote applications between namespaces
```

## Troubleshooting Common Issues

### Issue 1: Resource Quota Exceeded
```bash
# Symptom: Pods stuck in Pending state
kubectl get pods -n quota-demo
kubectl describe pod <pending-pod> -n quota-demo

# Check resource quota usage
kubectl describe resourcequota -n quota-demo

# Solution: Increase quota or reduce resource requests
```

### Issue 2: Cross-Namespace Communication Failed
```bash
# Debug DNS resolution
kubectl exec -it <pod> -n frontend -- nslookup backend-service.backend.svc.cluster.local

# Check network policies
kubectl get networkpolicy -n backend
kubectl describe networkpolicy <policy-name> -n backend

# Test connectivity
kubectl exec -it <pod> -n frontend -- curl -v backend-service.backend:8080
```

### Issue 3: Namespace Stuck in Terminating State
```bash
# Check for finalizers
kubectl get namespace <stuck-namespace> -o yaml

# Remove finalizers if safe
kubectl patch namespace <stuck-namespace> -p '{"metadata":{"finalizers":null}}' --type=merge

# Check for remaining resources
kubectl api-resources --verbs=list --namespaced -o name | xargs -n 1 kubectl get --show-kind --ignore-not-found -n <stuck-namespace>
```

## Best Practices Summary

1. **Naming Convention**: Use descriptive names like `production-web`, `staging-api`
2. **Resource Quotas**: Always apply quotas to prevent resource exhaustion
3. **Network Policies**: Implement zero-trust networking between namespaces
4. **RBAC**: Use role-based access control for namespace isolation
5. **Monitoring**: Track resource usage and set up alerts
6. **Cleanup**: Regularly clean up unused namespaces and resources
7. **Documentation**: Document namespace purpose and ownership
8. **Automation**: Use Infrastructure as Code for namespace management

## Cleanup

```bash
# Clean up all demo resources
namespaces=("demo-app" "quota-demo" "frontend" "backend" "isolated" "dev" "test" "staging" "prod" "production-web" "staging-api" "tenant-acme" "tenant-globex" "team-frontend" "team-backend" "team-data")

for ns in "${namespaces[@]}"; do
  kubectl delete namespace $ns --ignore-not-found
done

# Reset context to default
kubectl config set-context --current --namespace=default

echo "Cleanup completed!"
```

## Key Takeaways

1. **Namespaces are Virtual Clusters**: Provide logical separation within a physical cluster
2. **Resource Management**: Essential for multi-tenancy and resource control
3. **Network Isolation**: Can be enforced using network policies
4. **RBAC Integration**: Namespaces are the foundation for access control
5. **DNS Scoping**: Services are discoverable across namespaces using FQDN
6. **Operational Benefits**: Easier management, monitoring, and troubleshooting

Namespaces are fundamental to operating Kubernetes clusters at scale, enabling multiple teams and applications to coexist safely and efficiently.

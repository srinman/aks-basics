# Kubernetes Pods Demo

## Overview
A Pod is the smallest deployable unit in Kubernetes. It represents a group of one or more containers that share storage, network, and specifications for how to run the containers. Think of a Pod as a "logical host" similar to a VM, but much more lightweight.

## Demo Commands

### 1. Deploy a Simple Pod

Create and deploy a basic nginx pod using bash EOF syntax:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: demo-pod
  labels:
    app: demo
spec:
  containers:
  - name: nginx
    image: nginx:latest
    ports:
    - containerPort: 80
EOF
```

### 2. Deploy a Debug Pod (Full Linux Tools)

Since nginx containers have limited utilities, deploy a netshoot pod for full Linux exploration with networking tools:

```bash
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: debug-pod
spec:
  containers:
  - name: netshoot
    image: nicolaka/netshoot
    command: ['sleep', '3600']
EOF
```

### 3. Basic Pod Display Commands

```bash
# List all pods
kubectl get pods

# Show detailed pod information
kubectl describe pod demo-pod
kubectl describe pod debug-pod

# Get pod YAML configuration
kubectl get pod demo-pod -o yaml

# Get pod details with node placement
kubectl get pod demo-pod -o wide

# Watch pod status in real-time
kubectl get pods -w
```

### 4. Inspect Pod's Linux Environment

#### System Information (VM-like inspection)
```bash
# Show kernel and system info (like uname on a VM)
kubectl exec -it demo-pod -- uname -a

# Show container OS details
kubectl exec -it demo-pod -- cat /etc/os-release

# Show hostname (each pod has unique hostname)
kubectl exec -it demo-pod -- hostname

# Show environment variables
kubectl exec -it demo-pod -- env
```



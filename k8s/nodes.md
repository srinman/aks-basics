# Kubernetes Nodes Demo

## Overview
A Kubernetes Node is a worker machine (physical or virtual) that runs containerized applications. Each node contains the services necessary to run pods and is managed by the control plane. Think of nodes as the "compute resources" that actually execute your workloads.

## Key Concepts
- **Node as Infrastructure**: Nodes are the physical/virtual machines that provide CPU, memory, and storage
- **Worker vs Control Plane**: Worker nodes run applications; control plane nodes manage the cluster
- **Node Components**: kubelet, kube-proxy, container runtime (Docker/containerd)
- **Resource Management**: CPU, memory, and storage allocation per node
- **Node Labels**: Key-value pairs for scheduling decisions and organization

## Demo Commands

### 1. Basic Node Information

```bash
# List all nodes in the cluster
kubectl get nodes

# Show detailed node information
kubectl get nodes -o wide

# Describe a specific node (replace NODE_NAME with actual node name)
kubectl describe node NODE_NAME

# Get first node name for subsequent commands
NODE_NAME=$(kubectl get nodes -o jsonpath='{.items[0].metadata.name}')
echo "Using node: $NODE_NAME"
```

### 2. Node Labels and Annotations

#### View Node Labels
```bash
# Show all labels for all nodes
kubectl get nodes --show-labels

# Show specific labels in columns
kubectl get nodes -L kubernetes.io/os,kubernetes.io/arch,node.kubernetes.io/instance-type

# Get labels for a specific node
kubectl get node $NODE_NAME -o jsonpath='{.metadata.labels}' | jq

# Show labels in a readable format
kubectl describe node $NODE_NAME | grep -A 20 "Labels:"
```

#### Common Node Labels (Kubernetes Standard)
```bash
# Operating System
kubectl get nodes -L kubernetes.io/os

# Architecture (amd64, arm64, etc.)
kubectl get nodes -L kubernetes.io/arch


# Zone and region (cloud providers)
kubectl get nodes -L topology.kubernetes.io/zone,topology.kubernetes.io/region

# Instance type (cloud providers)
kubectl get nodes -L node.kubernetes.io/instance-type
```

#### AKS-Specific Labels (Azure Kubernetes Service)
```bash
# AKS node pool information
kubectl get nodes -L agentpool,kubernetes.azure.com/agentpool

# Azure availability zone
kubectl get nodes -L topology.kubernetes.io/zone

# Azure instance SKU
kubectl get nodes -L node.kubernetes.io/instance-type

# AKS cluster name
kubectl get nodes -L kubernetes.azure.com/cluster

# Node image version
kubectl get nodes -L kubernetes.azure.com/node-image-version

# Show all AKS-specific labels
kubectl get nodes -o json | jq '.items[].metadata.labels | to_entries[] | select(.key | contains("azure"))'
```

### 3. Node Resource Information

#### CPU and Memory Capacity
```bash
# Show node resource capacity and allocatable resources
kubectl describe node $NODE_NAME | grep -A 5 "Capacity:"
kubectl describe node $NODE_NAME | grep -A 5 "Allocatable:"

# Get resource information in JSON format
kubectl get node $NODE_NAME -o jsonpath='{.status.capacity}' | jq
kubectl get node $NODE_NAME -o jsonpath='{.status.allocatable}' | jq

# Compare capacity vs allocatable for all nodes
kubectl get nodes -o custom-columns=NAME:.metadata.name,CPU_CAPACITY:.status.capacity.cpu,CPU_ALLOCATABLE:.status.allocatable.cpu,MEMORY_CAPACITY:.status.capacity.memory,MEMORY_ALLOCATABLE:.status.allocatable.memory
```

#### Node Resource Usage (requires metrics-server)
```bash
# Show current resource usage for all nodes
kubectl top nodes

# Show resource usage for specific node
kubectl top node $NODE_NAME

```

### 4. Pods Running on Nodes

```bash
# Show all pods running on a specific node
kubectl get pods --all-namespaces -o wide --field-selector spec.nodeName=$NODE_NAME

# Count pods per node
kubectl get pods --all-namespaces -o json | jq -r '.items[] | .spec.nodeName' | sort | uniq -c

# Get detailed pod information for a node
kubectl describe node $NODE_NAME | grep -A 50 "Non-terminated Pods:"
```

### 5. Node Conditions and Health

```bash
# Check node conditions (Ready, MemoryPressure, DiskPressure, etc.)
kubectl get nodes -o custom-columns=NAME:.metadata.name,STATUS:.status.conditions[-1].type,REASON:.status.conditions[-1].reason

# Show detailed node conditions
kubectl describe node $NODE_NAME | grep -A 10 "Conditions:"

# Get all recent events and filter for the node
kubectl get events --all-namespaces --sort-by='.lastTimestamp' | grep $NODE_NAME

# Monitor node status changes
kubectl get nodes -w
```

### 6. Node Taints and Tolerations

```bash
# Show node taints
kubectl describe node $NODE_NAME | grep -A 5 "Taints:"

# List all taints across all nodes
kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, taints: .spec.taints}'

# Add a taint to a node (example)
# kubectl taint nodes $NODE_NAME key=value:NoSchedule

# Remove a taint from a node (example)
# kubectl taint nodes $NODE_NAME key=value:NoSchedule-
```

### 7. Node Scheduling and Affinity

#### Node Selection Examples
```bash
# Deploy pod to specific node using nodeSelector
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: node-selector-pod
spec:
  nodeSelector:
    kubernetes.io/os: linux
  containers:
  - name: nginx
    image: nginx
EOF

# Deploy pod with node affinity
cat <<EOF | kubectl apply -f -
apiVersion: v1
kind: Pod
metadata:
  name: node-affinity-pod
spec:
  affinity:
    nodeAffinity:
      requiredDuringSchedulingIgnoredDuringExecution:
        nodeSelectorTerms:
        - matchExpressions:
          - key: kubernetes.io/arch
            operator: In
            values:
            - amd64
  containers:
  - name: nginx
    image: nginx
EOF

# Check where pods were scheduled
kubectl get pods -o wide
```

### 8. Node System Information

#### Node Operating System and Kernel
```bash
# Get OS information for all nodes
kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, os: .status.nodeInfo.osImage, kernel: .status.nodeInfo.kernelVersion}'

# Show detailed system information
kubectl describe node $NODE_NAME | grep -A 10 "System Info:"

# Get container runtime information
kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, runtime: .status.nodeInfo.containerRuntimeVersion}'
```

#### Node Network and Storage
```bash
# Show node addresses (internal IP, external IP, hostname)
kubectl get nodes -o json | jq '.items[] | {name: .metadata.name, addresses: .status.addresses}'

# Get storage information
kubectl describe node $NODE_NAME | grep -A 5 "ephemeral-storage"

# Show node network configuration (if available)
kubectl get node $NODE_NAME -o jsonpath='{.status.addresses[*].address}'
```

### 9. Advanced Node Commands

#### Custom Node Labels for Organization
```bash
# Add custom labels to nodes
kubectl label node $NODE_NAME environment=production
kubectl label node $NODE_NAME team=backend
kubectl label node $NODE_NAME workload-type=cpu-intensive

# View custom labels
kubectl get nodes -L environment,team,workload-type

# Remove custom labels
# kubectl label node $NODE_NAME environment-
```

#### Node Maintenance
```bash
# Cordon a node (prevent new pods from being scheduled)
kubectl cordon $NODE_NAME

# Drain a node (evict all pods for maintenance)
# kubectl drain $NODE_NAME --ignore-daemonsets --delete-emptydir-data

# Uncordon a node (allow scheduling again)
kubectl uncordon $NODE_NAME

# Check node scheduling status
kubectl get nodes | grep -E "Ready|SchedulingDisabled"
```

#### Node Resource Quotas and Limits
```bash
# Show resource requests and limits for all pods on a node
kubectl describe node $NODE_NAME | grep -A 20 "Allocated resources:"

# Calculate node utilization
kubectl describe node $NODE_NAME | grep -E "cpu|memory" -A 1 | grep -E "requests|limits"

# Show node capacity utilization summary
kubectl top node $NODE_NAME
```

### 10. Troubleshooting Node Issues

```bash
# Check node logs (if accessible)
# kubectl debug node/$NODE_NAME -it --image=nicolaka/netshoot

# Get kubelet logs (platform specific)
# For systemd systems: journalctl -u kubelet

# Check node disk space and pressure
kubectl describe node $NODE_NAME | grep -E "DiskPressure|disk"

# Monitor node events
kubectl get events --all-namespaces | grep $NODE_NAME

# Check node readiness and conditions
kubectl get node $NODE_NAME -o jsonpath='{.status.conditions[?(@.type=="Ready")].status}'
```

### 11. Multi-Node Cluster Analysis

```bash
# Compare nodes side by side
kubectl get nodes -o custom-columns=NAME:.metadata.name,STATUS:.status.conditions[-1].type,ROLES:.metadata.labels.node-role\.kubernetes\.io/master,VERSION:.status.nodeInfo.kubeletVersion,OS:.status.nodeInfo.osImage

# Show cluster-wide resource summary
kubectl top nodes

# Analyze workload distribution
kubectl get pods --all-namespaces -o json | jq '.items | group_by(.spec.nodeName) | map({node: .[0].spec.nodeName, count: length})'

# Find nodes with specific characteristics
kubectl get nodes -l kubernetes.io/arch=amd64
kubectl get nodes -l '!node-role.kubernetes.io/control-plane'
```

### 12. AKS-Specific Node Commands

```bash
# Show AKS node pools
kubectl get nodes -L agentpool

# Display AKS cluster information through nodes
kubectl get nodes -o json | jq '.items[0].metadata.labels | to_entries[] | select(.key | contains("azure"))'

# Check AKS node image versions
kubectl get nodes -L kubernetes.azure.com/node-image-version

# Show AKS availability zones
kubectl get nodes -L topology.kubernetes.io/zone

# Display node pool scaling information
kubectl describe nodes | grep -E "agentpool|instance-type"
```

### 13. Cleanup

```bash
# Remove demo pods
kubectl delete pod node-selector-pod node-affinity-pod --ignore-not-found

# Remove custom labels (if added)
# kubectl label node $NODE_NAME environment- team- workload-type-
```

## Key Takeaways for Trainees

### Node Concepts
1. **Nodes are Infrastructure**: Physical or virtual machines that provide compute resources
2. **Resource Management**: Each node has CPU, memory, and storage that can be allocated to pods
3. **Labels for Organization**: Use labels to categorize and select nodes for pod placement
4. **Health Monitoring**: Nodes have conditions that indicate their health status
5. **Scheduling Control**: Use taints, tolerations, and affinity to control pod placement

### Best Practices
1. **Label Consistently**: Use standard labels for environment, role, and workload types
2. **Monitor Resources**: Keep track of node resource utilization
3. **Plan Maintenance**: Use cordon/drain for safe node maintenance
4. **Understand Limits**: Know the difference between capacity and allocatable resources
5. **Use Node Selectors**: Leverage labels for intelligent pod scheduling

### Troubleshooting Tips
1. **Check Node Conditions**: Ready, MemoryPressure, DiskPressure conditions
2. **Monitor Events**: Node events provide insights into issues
3. **Resource Pressure**: Watch for resource exhaustion on nodes
4. **Network Issues**: Verify node connectivity and addresses
5. **Kubelet Health**: Ensure kubelet service is running on nodes

## Node vs Pod vs Container Comparison

| Aspect | Node | Pod | Container |
|--------|------|-----|-----------|
| **Definition** | Physical/virtual machine | Smallest deployable unit | Application runtime |
| **Lifespan** | Long-lived infrastructure | Ephemeral workload | Process lifetime |
| **Resources** | CPU, Memory, Storage pool | Resource requests/limits | Isolated processes |
| **Networking** | Cluster network endpoint | Pod IP address | Shared pod network |
| **Management** | Infrastructure team | Kubernetes scheduler | Container runtime |
| **Scaling** | Add/remove machines | Replica count | Not directly scalable |
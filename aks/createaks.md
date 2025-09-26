# Azure Kubernetes Service (AKS) - Beginner Demo Guide

This document provides a step-by-step guide to create and explore an AKS cluster for beginners.

## Prerequisites

- Azure CLI installed and logged in (`az login`)
- kubectl installed
- An active Azure subscription

## 1. Create AKS Cluster

Create a simple AKS cluster with minimal configuration and admin access enabled:

```bash
# Create a resource group
az group create --name democlusterrg --location eastus2

# Create AKS cluster with minimum nodes and admin enabled
az aks create \
    --resource-group democlusterrg \
    --name democluster \
    --node-count 1 \
    --generate-ssh-keys \
    --network-plugin kubenet \
    --enable-cluster-autoscaler \
    --min-count 1 \
    --max-count 3
```

**Note**: This creates a kubenet cluster (Azure's basic networking) with:
- 1 node minimum
- Cluster autoscaler enabled (scales 1-3 nodes)
- SSH keys auto-generated
- Admin access enabled by default

## 2. Get Cluster Credentials

Configure kubectl to connect to your AKS cluster:

```bash
# Get credentials for the AKS cluster
az aks get-credentials --resource-group democlusterrg --name democluster

# Verify connection
kubectl config current-context
```

## 3. Basic Cluster Exploration Commands

### Display Nodes
```bash
# List all nodes in the cluster
kubectl get nodes

# Get detailed node information
kubectl get nodes -o wide

# Describe a specific node (replace <node-name> with actual node name)
kubectl describe node <node-name>
```

### Display Namespaces
```bash
# List all namespaces
kubectl get namespaces

# List namespaces with more details
kubectl get ns -o wide
```

### Basic Pod Commands
```bash
# List all pods in default namespace
kubectl get pods

# List all pods in all namespaces
kubectl get pods --all-namespaces

# List pods in kube-system namespace
kubectl get pods -n kube-system
```

### Basic Service Commands
```bash
# List all services in default namespace
kubectl get services

# List all services in all namespaces
kubectl get svc --all-namespaces
```

### Cluster Information
```bash
# Get cluster information
kubectl cluster-info

# Get cluster version
kubectl version

# Get cluster resources overview
kubectl get all
```

## 4. Deploy a Simple Test Application

Create a simple nginx deployment to test your cluster:

```bash
# Create nginx deployment
kubectl create deployment nginx-demo --image=nginx

# Expose the deployment as a service
kubectl expose deployment nginx-demo --port=80 --type=LoadBalancer

# Check the deployment status
kubectl get deployments

# Check the service (wait for EXTERNAL-IP)
kubectl get services
```

## 5. Basic Troubleshooting Commands

```bash
# Check pod logs (replace <pod-name> with actual pod name)
kubectl logs <pod-name>

# Get events in current namespace
kubectl get events

# Get events sorted by timestamp
kubectl get events --sort-by='.metadata.creationTimestamp'

# Check resource usage
kubectl top nodes
kubectl top pods
```

## 6. Cleanup

When you're done with the demo:

```bash
# Delete the test deployment and service
kubectl delete deployment nginx-demo
kubectl delete service nginx-demo

# Delete the AKS cluster and resource group
az group delete --name democlusterrg --yes --no-wait
```

## Quick Reference Commands

| Command | Description |
|---------|-------------|
| `kubectl get nodes` | List cluster nodes |
| `kubectl get ns` | List namespaces |
| `kubectl get pods` | List pods in default namespace |
| `kubectl get svc` | List services |
| `kubectl get all` | List all resources |
| `kubectl cluster-info` | Show cluster info |
| `kubectl config current-context` | Show current cluster context |
| `kubectl describe <resource> <name>` | Get detailed info about a resource |
| `kubectl logs <pod-name>` | View pod logs |

This basic setup gives you a functional AKS cluster to explore Kubernetes concepts and commands.

---

## 🏗️ AKS Architecture Deep Dive

Understanding the architecture of your AKS cluster helps you better utilize and troubleshoot your Kubernetes environment.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           AKS Architecture Overview                         │
└─────────────────────────────────────────────────────────────────────────────┘

Azure Subscription
┌─────────────────────────────────────────────────────────────────────────────┐
│                                                                             │
│  Resource Group: democlusterrg                                              │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                                                                       │  │
│  │  AKS Cluster: democluster                                             │  │
│  │  ┌─────────────────────────────────────────────────────────────────┐  │  │
│  │  │                                                                 │  │  │
│  │  │  Control Plane (Azure Managed)                                  │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐│  │  │
│  │  │  │  • API Server                                               ││  │  │
│  │  │  │  • etcd                                                     ││  │  │
│  │  │  │  • Controller Manager                                       ││  │  │
│  │  │  │  • Scheduler                                                ││  │  │
│  │  │  └─────────────────────────────────────────────────────────────┘│  │  │
│  │  │                                                                 │  │  │
│  │  │  Node Pools (Your VMs)                                         │  │  │
│  │  │  ┌─────────────────────────────────────────────────────────────┐│  │  │
│  │  │  │  Worker Node 1          Worker Node 2          Worker Node 3││  │  │
│  │  │  │  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐││  │  │
│  │  │  │  │  • kubelet      │    │  • kubelet      │    │  • kubelet  │││  │  │
│  │  │  │  │  • kube-proxy   │    │  • kube-proxy   │    │  • kube-proxy│││  │  │
│  │  │  │  │  • Container    │    │  • Container    │    │  • Container │││  │  │
│  │  │  │  │    Runtime      │    │    Runtime      │    │    Runtime   │││  │  │
│  │  │  │  │  • Your Pods    │    │  • Your Pods    │    │  • Your Pods │││  │  │
│  │  │  │  └─────────────────┘    └─────────────────┘    └─────────────┘││  │  │
│  │  │  └─────────────────────────────────────────────────────────────────┘│  │  │
│  │  └─────────────────────────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────────────────────────┘  │
│                                                                               │
│  Additional Azure Resources (Auto-created):                                  │
│  • Virtual Network & Subnets                                                 │
│  • Network Security Groups                                                   │
│  • Load Balancers                                                            │
│  • Public IPs                                                                │
│  • Storage Accounts                                                          │
└─────────────────────────────────────────────────────────────────────────────┘

Key Benefits:
• Azure manages the control plane (no cost for control plane)
• Automatic updates and patches for Kubernetes
• Integration with Azure services (Monitor, Security Center, etc.)
• Built-in scaling and availability features
```

### 🎯 What Makes AKS Special

#### Azure Integration Benefits
- **Managed Control Plane**: Azure handles master nodes, updates, and maintenance
- **Azure Active Directory**: Native integration for authentication and RBAC
- **Azure Monitor**: Built-in monitoring and logging capabilities
- **Azure Security Center**: Integrated security recommendations and threat protection
- **Azure Policy**: Governance and compliance at scale
- **Azure DevOps**: Seamless CI/CD integration

#### Cost Optimization
- **No control plane costs**: You only pay for worker nodes
- **Cluster Autoscaler**: Automatically scale nodes based on demand
- **Spot Instances**: Use Azure Spot VMs for cost-effective workloads
- **Reserved Instances**: Long-term savings for predictable workloads

#### Networking Options
- **kubenet**: Basic networking (default, simpler setup) - what we used in this demo
- **Azure CNI**: Advanced networking with Azure Virtual Network integration
- **Private Clusters**: Enhanced security with private API endpoints

### 📖 Core Concepts

#### Resource Hierarchy
```
Azure Subscription
└── Resource Group (democlusterrg)
    └── AKS Cluster (democluster)
        └── Node Pools
            └── Virtual Machines (Worker Nodes)
                └── Pods (Your Applications)
```

#### Key AKS Components
- **Cluster**: The entire managed Kubernetes environment
- **Node Pools**: Groups of VMs with similar configuration
- **Nodes**: Individual virtual machines running your workloads
- **Pods**: Smallest deployable units containing your applications

### 🛠️ Common AKS Operations

#### Cluster Management
```bash
# Create cluster
az aks create --resource-group myRG --name myCluster --node-count 1

# Get credentials
az aks get-credentials --resource-group myRG --name myCluster

# Scale cluster
az aks scale --resource-group myRG --name myCluster --node-count 3

# Upgrade cluster
az aks upgrade --resource-group myRG --name myCluster --kubernetes-version 1.28.0

# Delete cluster
az aks delete --resource-group myRG --name myCluster
```

#### Node Pool Operations
```bash
# Add node pool
az aks nodepool add --resource-group myRG --cluster-name myCluster --name mynodepool

# List node pools
az aks nodepool list --resource-group myRG --cluster-name myCluster

# Delete node pool
az aks nodepool delete --resource-group myRG --cluster-name myCluster --name mynodepool
```

### 📋 Best Practices

#### Security
- Use Azure Active Directory integration
- Enable RBAC (Role-Based Access Control)
- Use network policies for pod-to-pod communication
- Regularly update Kubernetes version
- Use Azure Security Center recommendations

#### Monitoring
- Enable Azure Monitor for containers
- Set up log analytics workspace
- Configure alerts for cluster health
- Monitor resource utilization

#### Cost Management
- Use cluster autoscaler
- Right-size your node pools
- Consider Azure Spot instances for non-critical workloads
- Regular cleanup of unused resources

---

## 🔗 Next Steps

After completing this demo:

1. **Master kubectl**: Review [kubectl fundamentals](../k8s/kubectl.md)
2. **Explore workloads**: Learn about [pods and deployments](../k8s/README.md)
3. **Practice more**: Deploy different applications and explore Kubernetes concepts
4. **Production readiness**: Implement monitoring, security, and scaling for real workloads
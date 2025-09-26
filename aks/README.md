# Azure Kubernetes Service (AKS) - Learning Guide

Welcome to the **Azure Kubernetes Service (AKS)** learning section. This comprehensive guide focuses on Azure-specific Kubernetes deployment, management, and best practices for running containerized workloads in Azure cloud.

## 📋 Overview

Azure Kubernetes Service (AKS) simplifies deploying a managed Kubernetes cluster in Azure by offloading the operational overhead to Azure. As a hosted Kubernetes service, Azure handles critical tasks like health monitoring and maintenance for you.

## 📚 Available Guides

### 🚀 Getting Started

#### [Creating Your First AKS Cluster](./createaks.md)
**Level**: Beginner | **Duration**: 45-60 minutes  
Step-by-step guide to create and explore your first AKS cluster with minimal configuration. Perfect for beginners getting started with Azure Kubernetes Service.

**Topics Covered:**
- AKS cluster creation with Azure CLI
- Basic cluster configuration (kubenet networking)
- Cluster autoscaling setup
- Getting cluster credentials
- Basic kubectl commands for cluster exploration
- Simple nginx deployment example
- Cleanup and resource management

**Prerequisites**: Azure CLI, kubectl, active Azure subscription

---

## 🎯 Learning Paths

### Path 1: AKS Fundamentals (Recommended for Beginners)
```
1. 📖 Read this overview
2. 🚀 [Create your first AKS cluster](./createaks.md)
3. 🔄 Practice basic operations and cleanup
4. 📈 Move to advanced topics (coming soon)
```

### Path 2: Azure-First Approach (For Azure Professionals)
```
1. 🚀 [Quick AKS cluster setup](./createaks.md)
2. 🔧 Explore Azure integrations
3. 🛡️ Implement security best practices
4. 📊 Set up monitoring and logging
```

---

## 🔧 Prerequisites

Before starting with AKS, ensure you have:

### Required Tools
- **Azure CLI** (`az`) - [Installation Guide](https://docs.microsoft.com/en-us/cli/azure/install-azure-cli)
- **kubectl** - [Installation Guide](https://kubernetes.io/docs/tasks/tools/install-kubectl/)
- **Azure Account** - Active subscription with contributor access
- **Local Environment** - Terminal/command prompt access

### Recommended Knowledge
- Basic Azure concepts (resource groups, subscriptions)
- Containerization fundamentals (Docker)
- Command-line interface usage
- Basic networking concepts

---

## 🏗️ AKS Architecture Overview

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

---

## 🎯 What Makes AKS Special

### Azure Integration Benefits
- **Managed Control Plane**: Azure handles master nodes, updates, and maintenance
- **Azure Active Directory**: Native integration for authentication and RBAC
- **Azure Monitor**: Built-in monitoring and logging capabilities
- **Azure Security Center**: Integrated security recommendations and threat protection
- **Azure Policy**: Governance and compliance at scale
- **Azure DevOps**: Seamless CI/CD integration

### Cost Optimization
- **No control plane costs**: You only pay for worker nodes
- **Cluster Autoscaler**: Automatically scale nodes based on demand
- **Spot Instances**: Use Azure Spot VMs for cost-effective workloads
- **Reserved Instances**: Long-term savings for predictable workloads

### Networking Options
- **kubenet**: Basic networking (default, simpler setup)
- **Azure CNI**: Advanced networking with Azure Virtual Network integration
- **Private Clusters**: Enhanced security with private API endpoints

---

## 📖 Core Concepts

### Resource Hierarchy
```
Azure Subscription
└── Resource Group (democlusterrg)
    └── AKS Cluster (democluster)
        └── Node Pools
            └── Virtual Machines (Worker Nodes)
                └── Pods (Your Applications)
```

### Key AKS Components
- **Cluster**: The entire managed Kubernetes environment
- **Node Pools**: Groups of VMs with similar configuration
- **Nodes**: Individual virtual machines running your workloads
- **Pods**: Smallest deployable units containing your applications

---

## 🚀 Quick Start Checklist

- [ ] **Azure CLI installed and configured** (`az --version`)
- [ ] **Azure login completed** (`az login`)
- [ ] **kubectl installed** (`kubectl version --client`)
- [ ] **Active Azure subscription verified** (`az account show`)
- [ ] **Resource group location decided** (e.g., eastus2)
- [ ] **Ready to create your first cluster** → [Start Here](./createaks.md)

---

## 🛠️ Common AKS Operations

### Cluster Management
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

### Node Pool Operations
```bash
# Add node pool
az aks nodepool add --resource-group myRG --cluster-name myCluster --name mynodepool

# List node pools
az aks nodepool list --resource-group myRG --cluster-name myCluster

# Delete node pool
az aks nodepool delete --resource-group myRG --cluster-name myCluster --name mynodepool
```

---

## 📋 Best Practices

### Security
- Use Azure Active Directory integration
- Enable RBAC (Role-Based Access Control)
- Use network policies for pod-to-pod communication
- Regularly update Kubernetes version
- Use Azure Security Center recommendations

### Monitoring
- Enable Azure Monitor for containers
- Set up log analytics workspace
- Configure alerts for cluster health
- Monitor resource utilization

### Cost Management
- Use cluster autoscaler
- Right-size your node pools
- Consider Azure Spot instances for non-critical workloads
- Regular cleanup of unused resources

---

## 🔗 Related Resources

### Azure Documentation
- [AKS Official Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [Azure CLI Reference](https://docs.microsoft.com/en-us/cli/azure/aks)
- [AKS Best Practices](https://docs.microsoft.com/en-us/azure/aks/best-practices)

### Kubernetes Fundamentals
- [Kubernetes Basics Guide](../k8s/README.md) - Essential Kubernetes concepts
- [kubectl Commands Reference](../k8s/kubectl.md) - Master kubectl operations

---

## 🎯 Next Steps

1. **Start with the basics**: [Create your first AKS cluster](./createaks.md)
2. **Master kubectl**: Review [kubectl fundamentals](../k8s/kubectl.md)
3. **Explore workloads**: Learn about [pods and deployments](../k8s/README.md)
4. **Production readiness**: Implement monitoring, security, and scaling (guides coming soon)

---

*Ready to start your AKS journey? Begin with [Creating Your First AKS Cluster](./createaks.md)!*

**Happy Cloud Computing! ☁️🚀**

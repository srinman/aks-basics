# Kubernetes (AKS) Learning Guides

Welcome to the comprehensive collection of Kubernetes learning guides specifically designed for Azure Kubernetes Service (AKS). These hands-on tutorials provide practical experience with core Kubernetes concepts, from basic resources to advanced internals.

## 📚 Available Guides

### 🔰 Fundamentals

#### [Pods - Basic Concepts](./pods.md)
**Level**: Beginner | **Duration**: 30-45 minutes  
Introduction to Kubernetes Pods, the smallest deployable units in Kubernetes. Learn how to create, manage, and inspect pods using practical examples.

**Topics Covered:**
- Pod creation and basic operations
- Container inspection and debugging
- Process and network exploration
- Multi-container pod examples
- Pod lifecycle management

**Key Learning Outcomes:**
- Understand what pods are and why they exist
- Learn basic pod management commands
- Explore pod networking and process isolation
- Practice debugging techniques

---

#### [Pods - Deep Dive & Internals](./pods_deepdive.md)
**Level**: Advanced | **Duration**: 2-3 hours  
Comprehensive deep dive into pod architecture, Linux namespaces, container runtime internals, and the complete pod creation process from API server to running processes.

**Topics Covered:**
- Linux namespaces and cgroups
- Pod sandbox architecture with pause containers
- Container runtime internals (containerd, runc)
- Process tree analysis with crictl
- Complete API server → kubelet → CRI → OCI → Linux syscalls flow
- Network namespace sharing vs process isolation

**Key Learning Outcomes:**
- Master Linux namespace concepts underlying pods
- Understand how containers share resources while maintaining isolation
- Learn to use crictl for low-level container inspection
- Trace pod creation from Kubernetes API to Linux processes
- Debug container runtime issues

---

#### [Namespaces - Multi-tenancy & Resource Isolation](./namespace.md)
**Level**: Intermediate | **Duration**: 1-2 hours  
Complete guide to Kubernetes namespaces for organizing resources, implementing multi-tenancy, and managing resource quotas across different environments.

**Topics Covered:**
- Namespace creation and management
- Resource quotas and limit ranges
- Cross-namespace communication
- Network policies for isolation
- RBAC integration
- Multi-environment setups (dev/test/staging/prod)
- Best practices for production

**Key Learning Outcomes:**
- Implement proper namespace organization strategies
- Configure resource quotas and limits
- Set up secure multi-tenant environments
- Manage cross-namespace service communication
- Apply network policies for security

---

#### [Nodes - Cluster Infrastructure](./nodes.md)
**Level**: Intermediate | **Duration**: 45-60 minutes  
Understanding Kubernetes worker nodes, their components, resource management, and troubleshooting techniques for AKS clusters.

**Topics Covered:**
- Node architecture and components
- Resource allocation and management
- Node conditions and status monitoring
- Taints, tolerations, and node affinity
- Troubleshooting node issues
- AKS-specific node pool management

**Key Learning Outcomes:**
- Understand node role in Kubernetes architecture
- Monitor and manage node resources
- Configure workload placement with node selectors
- Troubleshoot node-related issues

---

### 🚀 Workload Management

#### [Deployments & ReplicaSets](./deploymentdemo.md)
**Level**: Intermediate | **Duration**: 1-1.5 hours  
Comprehensive tutorial on Kubernetes Deployments and ReplicaSets, covering rolling updates, scaling strategies, and advanced deployment patterns.

**Topics Covered:**
- Deployment creation and management
- ReplicaSet behavior and scaling
- Rolling updates and rollback strategies
- Blue-green deployment patterns
- Update strategies and limitations
- Troubleshooting failed deployments

**Key Learning Outcomes:**
- Master deployment lifecycle management
- Implement various update strategies
- Handle deployment failures and rollbacks
- Understand ReplicaSet behavior
- Apply production-ready deployment practices

---

### 🔧 Configuration & Secrets

#### [ConfigMaps & Secrets](./cmsecret.md)
**Level**: Beginner-Intermediate | **Status**: 🚧 Coming Soon  
Learn to manage application configuration and sensitive data using ConfigMaps and Secrets.

**Planned Topics:**
- ConfigMap creation and usage patterns
- Secret management and security best practices
- Environment variable injection
- Volume mounting for configuration
- Configuration hot-reloading

---

#### [Services & Networking](./services.md)
**Level**: Intermediate | **Status**: 🚧 Coming Soon  
Deep dive into Kubernetes Services, load balancing, and networking concepts.

**Planned Topics:**
- Service types (ClusterIP, NodePort, LoadBalancer)
- Service discovery and DNS
- Ingress controllers and traffic routing
- Network policies and security
- AKS-specific networking features

---

## 🎯 Learning Path Recommendations

### **Beginner Path** (New to Kubernetes)
1. [Pods - Basic Concepts](./pods.md) - Start here to understand the fundamental building blocks
2. [Namespaces](./namespace.md) - Learn resource organization and isolation
3. [Deployments & ReplicaSets](./deploymentdemo.md) - Master workload management
4. [Nodes](./nodes.md) - Understand cluster infrastructure

### **Intermediate Path** (Some Kubernetes Experience)
1. [Namespaces](./namespace.md) - Advanced multi-tenancy and resource management
2. [Deployments & ReplicaSets](./deploymentdemo.md) - Production deployment strategies
3. [Nodes](./nodes.md) - Infrastructure optimization
4. [Pods - Deep Dive](./pods_deepdive.md) - Internal architecture understanding

### **Advanced Path** (Deep Technical Understanding)
1. [Pods - Deep Dive](./pods_deepdive.md) - Master container runtime internals
2. [Namespaces](./namespace.md) - Implement enterprise-grade multi-tenancy
3. [Nodes](./nodes.md) - Advanced cluster management
4. [Services & Networking](./services.md) - Network architecture (when available)

## 🛠 Prerequisites

### Required Tools
- **kubectl** - Kubernetes command-line tool
- **Azure CLI** - For AKS cluster management
- **Access to AKS cluster** - Running Kubernetes cluster

### Optional Tools (for advanced tutorials)
- **crictl** - Container runtime interface tool (for deep dive tutorials)
- **docker/podman** - Container management (helpful for understanding)
- **jq** - JSON processor for parsing kubectl output

### Setup Instructions
```bash
# Verify cluster access
kubectl cluster-info

# Check available nodes
kubectl get nodes

# Verify permissions
kubectl auth can-i create pods
```

## 📋 Tutorial Format

Each guide follows a consistent structure:

- **Overview** - What you'll learn and why it matters
- **Prerequisites** - Required knowledge and tools
- **Hands-on Demos** - Step-by-step practical exercises
- **Real-world Scenarios** - Production use cases
- **Troubleshooting** - Common issues and solutions
- **Best Practices** - Production-ready recommendations
- **Cleanup** - Resource cleanup instructions

## 🎯 Learning Objectives

By completing these guides, you will:

✅ **Understand Core Concepts** - Master fundamental Kubernetes building blocks  
✅ **Gain Practical Skills** - Learn through hands-on exercises and real scenarios  
✅ **Learn Best Practices** - Apply production-ready patterns and security measures  
✅ **Troubleshoot Issues** - Develop debugging skills for common problems  
✅ **Optimize Performance** - Understand resource management and scaling  
✅ **Implement Security** - Apply proper isolation and access controls  

## 🤝 Contributing

These guides are continuously updated based on:
- Latest Kubernetes and AKS features
- Community feedback and common questions
- Real-world production experiences
- Best practices from the field

## 📖 Additional Resources

### Official Documentation
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/aks/)
- [kubectl Reference](https://kubernetes.io/docs/reference/kubectl/)

### Useful Commands Reference
```bash
# Quick cluster overview
kubectl get all --all-namespaces

# Resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Troubleshooting
kubectl describe pod <pod-name>
kubectl logs <pod-name> -f
kubectl get events --sort-by=.metadata.creationTimestamp
```

---

**Happy Learning!** 🚀 Start with any guide that matches your current level and gradually work through the collection to build comprehensive Kubernetes expertise.

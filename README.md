# AKS Basics - Learning Hub

Welcome to **AKS Basics**, a comprehensive learning repository for Azure Kubernetes Service (AKS) and Kubernetes fundamentals. This repository is designed to provide hands-on experience and practical knowledge for beginners and professionals working with Kubernetes in Azure environments.

## 📖 Repository Structure

This repository is organized into focused learning modules, each containing detailed guides, examples, and hands-on exercises.

### 🚀 [AKS - Azure Kubernetes Service](./aks/README.md)

**Focus**: Azure-specific Kubernetes deployment and management

Learn how to create, configure, and manage AKS clusters in Azure. This section covers Azure-specific features, integrations, and best practices for running Kubernetes workloads in the cloud.

**What you'll find:**
- AKS cluster creation and configuration
- Azure integrations (Azure AD, Azure Monitor, etc.)
- Networking with Azure CNI and kubenet
- Security and access management
- Scaling and performance optimization
- Cost management strategies

---

### ⚙️ [Kubernetes Fundamentals](./k8s/README.md)

**Focus**: Core Kubernetes concepts and operations

Master the fundamental concepts of Kubernetes through practical examples and hands-on exercises. This section covers essential kubectl operations, resource management, and troubleshooting techniques.

**What you'll find:**
- Pod lifecycle and management
- Services and networking
- Deployments and scaling
- ConfigMaps and Secrets
- Namespaces and resource organization
- kubectl mastery and troubleshooting
- Architecture deep-dives

---

## 🎯 Learning Path Recommendations

### For Complete Beginners:
1. Start with **[Kubernetes Fundamentals](./k8s/README.md)** to understand core concepts
2. Practice with basic kubectl commands and resource creation
3. Move to **[AKS](./aks/README.md)** for cloud-specific implementations

### For Azure Professionals:
1. Begin with **[AKS](./aks/README.md)** to understand Azure integrations
2. Supplement with **[Kubernetes Fundamentals](./k8s/README.md)** for deeper technical knowledge
3. Focus on production-ready patterns and best practices

### For Kubernetes Practitioners:
1. Review **[kubectl advanced techniques](./k8s/kubectl.md)** for operational efficiency
2. Explore **[AKS-specific features](./aks/README.md)** for Azure optimizations
3. Practice troubleshooting scenarios across both sections

---

## 🔧 Prerequisites

- **Azure Account**: Active Azure subscription for AKS exercises
- **Tools Required**:
  - Azure CLI (`az`)
  - kubectl
  - Docker (for local testing)
  - Git (for cloning and managing code)
- **Basic Knowledge**: 
  - Command line familiarity
  - Basic containerization concepts
  - Fundamental networking understanding

---

## 📋 Quick Start

1. **Clone the repository**:
   ```bash
   git clone https://github.com/srinman/aks-basics.git
   cd aks-basics
   ```

2. **Choose your learning path**:
   - **New to Kubernetes**: Start with [k8s/README.md](./k8s/README.md)
   - **Azure-focused**: Begin with [aks/README.md](./aks/README.md)

3. **Set up your environment**:
   - Install required tools (Azure CLI, kubectl)
   - Configure Azure authentication (`az login`)
   - Verify access to Azure subscription

---

## 🤝 How to Use This Repository

### Document Navigation
- Each folder contains a **README.md** that serves as the index for that section
- Individual guides are focused on specific topics with hands-on examples
- Cross-references between documents help build comprehensive understanding

### Hands-On Approach
- Most guides include practical exercises you can run in your own environment
- Commands are provided with explanations of expected outcomes
- Real-world scenarios and troubleshooting examples

### Progressive Learning
- Content is organized from basic to advanced concepts
- Each guide builds upon previously introduced concepts
- References to prerequisite knowledge are clearly marked

---

## 📚 Additional Resources

### External Learning Materials
- [Official Kubernetes Documentation](https://kubernetes.io/docs/)
- [Azure Kubernetes Service Documentation](https://docs.microsoft.com/en-us/azure/aks/)
- [kubectl Reference](https://kubernetes.io/docs/reference/kubectl/)

### Community and Support
- [Kubernetes Community](https://kubernetes.io/community/)
- [Azure Community](https://techcommunity.microsoft.com/t5/azure/ct-p/Azure)
- [CNCF Landscape](https://landscape.cncf.io/)

---

## 🎯 Repository Goals

This repository aims to provide:
- **Practical Knowledge**: Real-world applicable skills
- **Clear Documentation**: Step-by-step guidance with explanations
- **Hands-On Experience**: Interactive learning through examples
- **Azure Integration**: Specific focus on Azure Kubernetes Service
- **Progressive Learning**: Structured path from beginner to advanced concepts

---

*Last Updated: September 2025*

**Happy Learning! 🚀**

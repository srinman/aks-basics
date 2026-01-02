# AKS Basics - Learning Hub

Welcome to **AKS Basics**, a comprehensive learning repository for Azure Kubernetes Service (AKS) and Kubernetes fundamentals. This repository is designed to provide hands-on experience and practical knowledge for beginners and professionals working with Kubernetes in Azure environments.

## 📖 Repository Structure

This repository is organized into focused learning modules, each containing detailed guides, examples, and hands-on exercises.

### 🚀 [AKS - Azure Kubernetes Service](./aks/README.md)

**Focus**: Azure-specific Kubernetes deployment and management

Learn how to create, configure, and manage AKS clusters in Azure. This section covers Azure-specific features, integrations, and best practices for running Kubernetes workloads in the cloud.


---

### 📦 [Containers & Docker](./containers/README.md)

**Focus**: Container fundamentals, Docker, and Azure Container Registry

Build and manage container images using Docker and Azure Container Registry (ACR). This section covers containerization basics, building images without local Docker, pushing to ACR, and deploying to Azure Container Instances (ACI).

**Key Topics**:
- Container basics and Docker fundamentals
- Building images with `az acr build` (no local Docker needed)
- Azure Container Registry (ACR) setup and management
- Deploying to Azure Container Instances (ACI)
- Docker VM setup for hands-on practice
- Dockerfile best practices and multi-stage builds

---

### ⚙️ [Kubernetes Fundamentals](./k8s/README.md)

**Focus**: Core Kubernetes concepts and operations

Master the fundamental concepts of Kubernetes through practical examples and hands-on exercises. This section covers essential kubectl operations, resource management, and troubleshooting techniques.


---

## 🎯 Learning Path Recommendations

### For Complete Beginners:
1. Start with **[Containers & Docker](./containers/README.md)** to understand containerization
2. Learn **[Kubernetes Fundamentals](./k8s/README.md)** to understand core concepts
3. Practice with basic kubectl commands and resource creation
4. Move to **[AKS](./aks/README.md)** for cloud-specific implementations

### For Azure Professionals:
1. Review **[Containers & Docker](./containers/README.md)** for ACR and ACI basics
2. Begin with **[AKS](./aks/README.md)** to understand Azure integrations
3. Supplement with **[Kubernetes Fundamentals](./k8s/README.md)** for deeper technical knowledge
4. Focus on production-ready patterns and best practices


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

*Last Updated: September 2025*

**Happy Learning! 🚀**

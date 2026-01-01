# Container Basics

Welcome to the Container Basics learning path! This guide will help you understand containerization fundamentals and how to work with OCI-compliant container images.

## Learning Objectives

By completing this module, you will learn to:

- Understand container fundamentals and OCI standards
- Build OCI-compliant container images
- Create Dockerfiles for different application types
- Run containers locally
- Manage multiple containers
- Use Azure Container Registry (ACR) for building and storing images
- Package applications with their dependencies

## Topics Covered

### 1. [Container Fundamentals](container-basics.md)
Learn about containerization concepts, OCI standards, and why containers matter.

### 2. [Dockerfile Guide](dockerfile-guide.md)
Deep dive into Dockerfile syntax, best practices, and creating efficient container images.

### 3. [Running Containers Locally](running-containers.md)
Learn how to run containers on your local machine, manage container lifecycle, and work with multiple containers.

### 4. [Docker VM Setup with Azure Bastion](docker-vm-setup.md)
Set up a cloud-based Docker environment using Azure VM and Bastion for hands-on learning without local Docker installation.

### 5. [Azure Container Registry (ACR)](acr-guide.md)
Understand ACR's role in storing OCI-compliant images and how to use `az acr build` for building images remotely.

### 6. [Multi-Container Scenarios](multi-container.md)
Learn to work with multiple containers and understand inter-container communication.

## Practical Examples

This module includes two complete Python application examples:

### Flask Echo Application
Location: `examples/flask-echo/`
- Simple REST API using Flask framework
- Demonstrates packaging Python dependencies
- Includes Dockerfile and deployment instructions

### FastAPI Echo Application
Location: `examples/fastapi-echo/`
- Modern async API using FastAPI framework
- Shows alternative dependency management
- Includes Dockerfile with different base image approach

## Prerequisites

- Basic understanding of command-line interfaces
- Azure CLI installed (`az`)
- Azure subscription (for ACR examples)
- Docker Desktop installed (optional, for local testing)
  - **Alternative**: Follow the [Docker VM Setup guide](docker-vm-setup.md) to create a cloud-based Docker environment

## Getting Started

Start with [Container Fundamentals](container-basics.md) to build a strong foundation, then proceed through the topics in order. Each guide builds upon the previous one.

## Quick Reference

Common commands you'll use:

```bash
# Build image remotely with ACR
az acr build --registry <registry-name> --image <image-name>:<tag> .

# List images in ACR
az acr repository list --name <registry-name>

# Run container locally (if Docker available)
docker run -p 8080:8080 <image-name>

# View running containers
docker ps
```

## Additional Resources

- [OCI Specification](https://github.com/opencontainers/image-spec)
- [Dockerfile Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Azure Container Registry Documentation](https://docs.microsoft.com/azure/container-registry/)

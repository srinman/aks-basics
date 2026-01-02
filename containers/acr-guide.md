# Azure Container Registry (ACR) Guide

Azure Container Registry (ACR) is a managed Docker registry service for storing and managing private container images and related artifacts. This guide covers building images remotely using `az acr build` and understanding ACR's role in container workflows.

## Why Azure Container Registry?

### Key Benefits

1. **No Local Docker Required**: Build images in the cloud without Docker Desktop
2. **Private & Secure**: Keep images private with Azure AD integration
3. **Geo-Replication**: Replicate images across multiple Azure regions
4. **Build Service**: Build images remotely using ACR Tasks
5. **Vulnerability Scanning**: Integrated security scanning
6. **Azure Integration**: Native support for AKS, App Service, Container Instances
7. **OCI Compliant**: Stores Docker images and OCI artifacts

### ACR vs Other Registries

| Feature | ACR | Docker Hub | Amazon ECR | Google GCR |
|---------|-----|------------|------------|------------|
| Private by Default | ✅ | ❌ | ✅ | ✅ |
| Geo-Replication | ✅ | ❌ | ❌ | ✅ |
| Built-in Build | ✅ | ✅ | ❌ | ✅ |
| Azure Integration | ✅ | ⚠️ | ❌ | ❌ |
| Vulnerability Scan | ✅ | ✅ | ✅ | ✅ |
| Pricing | Per Storage | Free + Paid | Per Storage | Per Storage |

## ACR Service Tiers

**For Learning**: This guide uses the **Basic** tier, which is perfect for learning and development.

### Basic (Used in This Guide)
- **Use Case**: Development and learning
- **Storage**: 10 GB included
- **Webhooks**: 2
- **Cost**: ~$5/month
- **Best For**: Learning, small projects, development

### Standard & Premium
For production workloads, Azure offers Standard (~$20/month, 100GB storage) and Premium (~$500/month, geo-replication, private endpoints) tiers. For learning purposes, Basic tier is sufficient.

## Creating an ACR

### Using Azure CLI

```bash
# Set variables
REGISTRY_NAME="mycontainerreg$(date +%s)"  # Must be globally unique
RESOURCE_GROUP="rg-containers"
LOCATION="eastus"

# Create resource group
az group create \
  --name $RESOURCE_GROUP \
  --location $LOCATION

# Create ACR (Basic tier for learning)
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic \
  --admin-enabled true

# Note: --admin-enabled true simplifies authentication for learning
# In production, use managed identities or service principals instead
```

### Verify ACR Creation

```bash
# Show ACR details
az acr show \
  --name $REGISTRY_NAME \
  --resource-group $RESOURCE_GROUP

# Get login server
az acr show \
  --name $REGISTRY_NAME \
  --query loginServer \
  --output tsv

# List all registries in subscription
az acr list --output table
```

## Authentication with ACR

For building images with `az acr build`, authentication is automatic when you're logged into Azure CLI. No additional login required!

```bash
# Verify you're logged in to Azure
az account show

# If not logged in
az login

# That's it! You can now use az acr build
```

For pulling images with Azure Container Instances (ACI), we'll use admin credentials that were enabled during ACR creation.

```bash
# Get ACR credentials (needed for ACI)
az acr credential show --name $REGISTRY_NAME

# These credentials will be used when deploying to ACI
```

## Building Images with az acr build

The `az acr build` command builds container images in Azure without requiring local Docker.

### Why Use az acr build?

✅ **No local Docker needed**: Build without Docker Desktop  
✅ **Cloud resources**: Use Azure compute for builds  
✅ **Automatic push**: Image pushed to registry after build  
✅ **Build logs**: Detailed logs of the build process  
✅ **Cost-effective**: Pay only for build time  
✅ **Multi-platform**: Build for different architectures  

### Basic Build

```bash
# Build from specific directory (recommended)
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  ./containers/examples/flask-echo

# Build with specific Dockerfile
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --file ./containers/examples/flask-echo/Dockerfile \
  ./containers/examples/flask-echo

# Build from current directory (if you're already in the app folder)
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  .
```

### Build with Multiple Tags

```bash
# Tag image with multiple tags
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --image flask-echo:latest \
  --image flask-echo:stable \
  ./containers/examples/flask-echo
```

### Build with Arguments - optional

```bash
# Pass build arguments
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --build-arg PYTHON_VERSION=3.10 \
  --build-arg APP_ENV=production \
  ./containers/examples/flask-echo
```

### Build from Git Repository - optional

```bash
# Build from GitHub
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  https://github.com/yourusername/yourrepo.git

# Build from specific branch
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:dev \
  https://github.com/yourusername/yourrepo.git#develop

# Build from specific path in repo
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  https://github.com/yourusername/yourrepo.git#main:containers/flask-echo
```

### Build with Platform Specification  - optional

```bash
# Build for specific platform
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --platform linux/amd64 \
  ./containers/examples/flask-echo

# Build multi-platform image
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --platform linux/amd64,linux/arm64 \
  ./containers/examples/flask-echo
```

## Building the Echo Applications

### Build Flask Echo App

```bash
# Build and push to ACR (run from project root)
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --image flask-echo:latest \
  ./containers/examples/flask-echo

# Build with custom version
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v2.0.0 \
  --build-arg APP_VERSION=2.0.0 \
  ./containers/examples/flask-echo

# View build logs
az acr task logs --registry $REGISTRY_NAME
```


### Build FastAPI Echo App

```bash
# Build multi-stage image (run from project root)
az acr build \
  --registry $REGISTRY_NAME \
  --image fastapi-echo:v1.0.0 \
  --image fastapi-echo:latest \
  ./containers/examples/fastapi-echo

# Check build output for stage information
# You'll see:
# - Stage 1: builder (compiling dependencies)
# - Stage 2: runtime (final image)
```



## Managing Images in ACR

### List Images

```bash
# List all repositories
az acr repository list \
  --name $REGISTRY_NAME \
  --output table

# List tags for a repository
az acr repository show-tags \
  --name $REGISTRY_NAME \
  --repository flask-echo \
  --output table

# Show tags with metadata
az acr repository show-tags \
  --name $REGISTRY_NAME \
  --repository flask-echo \
  --detail \
  --output table

# Order by time
az acr repository show-tags \
  --name $REGISTRY_NAME \
  --repository flask-echo \
  --orderby time_desc \
  --output table
```

### Image Details

```bash
# Show image manifest
az acr repository show \
  --name $REGISTRY_NAME \
  --image flask-echo:latest

# Show specific tag details
az acr repository show \
  --name $REGISTRY_NAME \
  --image flask-echo:v1.0.0

# Get image digest
az acr repository show \
  --name $REGISTRY_NAME \
  --image flask-echo:latest \
  --query digest \
  --output tsv
```

## Deploy to Azure Container Instances

Azure Container Instances (ACI) is the easiest way to run your ACR images in the cloud without managing VMs or clusters.

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Create container instance
az container create \
  --resource-group $RESOURCE_GROUP \
  --name flask-echo \
  --image ${REGISTRY_NAME}.azurecr.io/flask-echo:latest \
  --dns-name-label flask-echo-${RANDOM} \
  --ports 8080 \
  --os-type Linux \
  --cpu 1 \
  --memory 1 \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD

# Get FQDN and test
FQDN=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name flask-echo \
  --query ipAddress.fqdn \
  --output tsv)

echo "Application URL: http://${FQDN}:8080"

# Test the application
curl http://${FQDN}:8080/

# View container logs
az container logs \
  --resource-group $RESOURCE_GROUP \
  --name flask-echo

# Check container status
az container show \
  --resource-group $RESOURCE_GROUP \
  --name flask-echo \
  --query '{Name:name,State:containers[0].instanceView.currentState.state,IP:ipAddress.ip}' \
  --output table
```

### Deploy FastAPI App to ACI

```bash
# Get ACR credentials
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Deploy FastAPI app
az container create \
  --resource-group $RESOURCE_GROUP \
  --name fastapi-echo \
  --image ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest \
  --dns-name-label fastapi-echo-${RANDOM} \
  --ports 8080 \
  --os-type Linux \
  --cpu 1 \
  --memory 1 \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD

# Get URL and test
FQDN=$(az container show \
  --resource-group $RESOURCE_GROUP \
  --name fastapi-echo \
  --query ipAddress.fqdn \
  --output tsv)

echo "FastAPI URL: http://${FQDN}:8080"
echo "API Docs: http://${FQDN}:8080/docs"
curl http://${FQDN}:8080/
```

## Best Practices for Learning

### 1. Tagging Strategy

```bash
# ✅ Good: Use version tags
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --image flask-echo:latest \
  ./containers/examples/flask-echo

# ✅ Good: Tag by feature
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:feature-logging \
  ./containers/examples/flask-echo

# ❌ Avoid: Only using latest (hard to track changes)
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:latest \
  ./containers/examples/flask-echo
```

### 2. Image Naming

```bash
# ✅ Good: Descriptive names
flask-echo
fastapi-echo
web-frontend
api-backend

# ❌ Avoid: Generic names
app
test
my-container
```

### 3. Clean Up Old Images

```bash
# List all images
az acr repository list --name $REGISTRY_NAME --output table

# Delete specific tag
az acr repository delete \
  --name $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --yes

# Delete entire repository
az acr repository delete \
  --name $REGISTRY_NAME \
  --repository flask-echo \
  --yes
```

## Troubleshooting

### Build Fails

```bash
# View detailed build logs
az acr task logs \
  --registry $REGISTRY_NAME \
  --run-id <run-id>

# Test build locally (if Docker available)
docker build -t test ./containers/examples/flask-echo

# Check Dockerfile syntax
cat ./containers/examples/flask-echo/Dockerfile
```

### Authentication Issues

```bash
# Re-login to ACR
az acr login --name $REGISTRY_NAME

# Verify credentials
az acr credential show --name $REGISTRY_NAME

# Check token expiration
docker logout ${REGISTRY_NAME}.azurecr.io
az acr login --name $REGISTRY_NAME
```

### Image Pull Fails

```bash
# Verify image exists
az acr repository show-tags \
  --name $REGISTRY_NAME \
  --repository flask-echo

# Check permissions
az acr show \
  --name $REGISTRY_NAME \
  --query id \
  --output tsv

az role assignment list \
  --scope <registry-id>
```

## Cleanup

```bash
# Delete specific images
az acr repository delete \
  --name $REGISTRY_NAME \
  --repository flask-echo \
  --yes

# Delete registry
az acr delete \
  --name $REGISTRY_NAME \
  --resource-group $RESOURCE_GROUP \
  --yes

# Delete resource group (removes everything)
az group delete \
  --name $RESOURCE_GROUP \
  --yes \
  --no-wait
```

## Next Steps

- Explore [multi-container scenarios](multi-container.md)
- Deploy to [Azure Kubernetes Service](../aks/README.md)
- Learn about [Docker fundamentals](container-basics.md)

---

## Appendix: Running Images Locally with Docker

If you have Docker installed locally or on a VM, you can pull and run your ACR images:

### Prerequisites

- Docker Desktop installed, OR
- Docker VM set up (see [docker-vm-setup.md](docker-vm-setup.md))

### Pull and Run Locally

```bash
# Login to ACR (requires Docker installed)
az acr login --name $REGISTRY_NAME

# Pull image from ACR
docker pull ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Run the container
docker run -d \
  --name flask-echo \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Test locally
curl http://localhost:8080/

# View logs
docker logs flask-echo

# Stop and remove
docker stop flask-echo
docker rm flask-echo
```

### Using Docker VM

If you don't have Docker Desktop locally, use a Docker VM:

```bash
# 1. Set up Docker VM first (see docker-vm-setup.md)
# 2. Connect to VM via Azure Portal

# Once connected to the VM:
az login
az acr login --name <your-registry-name>

# Pull and run
docker pull <your-registry-name>.azurecr.io/flask-echo:latest
docker run -d --name flask-echo -p 8080:8080 <your-registry-name>.azurecr.io/flask-echo:latest

# Test from within VM
curl http://localhost:8080/
```

### Compare: Local Docker vs ACI

| Aspect | Local Docker | Azure Container Instances |
|--------|--------------|---------------------------|
| Setup | Requires Docker installed | No installation needed |
| Access | localhost only | Public URL provided |
| Cost | Free (uses local resources) | Pay per second of usage |
| Best For | Development/testing | Demos, temporary workloads |
| Limitations | Local machine only | Internet-accessible |

### When to Use Each

**Use Local Docker when:**
- Developing and testing code changes
- Running containers offline
- Learning Docker commands
- Need full control over networking

**Use ACI when:**
- Sharing a demo with others
- Running temporary workloads
- No local Docker installation
- Need public internet access
- Learning cloud deployments

## Additional Resources

- [ACR Documentation](https://docs.microsoft.com/azure/container-registry/)
- [ACR Best Practices](https://docs.microsoft.com/azure/container-registry/container-registry-best-practices)
- [ACR Tasks](https://docs.microsoft.com/azure/container-registry/container-registry-tasks-overview)
- [Container Security](https://docs.microsoft.com/azure/container-registry/container-registry-content-trust)

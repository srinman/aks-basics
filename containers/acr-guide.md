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

Azure Container Registry offers three service tiers:

### Basic
- **Use Case**: Development and learning
- **Storage**: 10 GB included
- **Webhooks**: 2
- **Geo-replication**: ❌
- **Best For**: Small projects, learning

### Standard
- **Use Case**: Production workloads
- **Storage**: 100 GB included
- **Webhooks**: 10
- **Geo-replication**: ❌
- **Best For**: Most production scenarios

### Premium
- **Use Case**: High-scale production
- **Storage**: 500 GB included
- **Webhooks**: 500
- **Geo-replication**: ✅
- **Content Trust**: ✅
- **Private Link**: ✅
- **Best For**: Enterprise, multi-region deployments

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

# Create ACR (Basic tier)
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic

# Create ACR (Standard tier - recommended for production)
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Standard

# Create ACR with admin enabled (for learning - not for production)
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Basic \
  --admin-enabled true
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

### Method 1: Azure CLI (Recommended for Development)

```bash
# Login to ACR
az acr login --name $REGISTRY_NAME

# This command:
# 1. Gets an Azure AD token
# 2. Exchanges it for a Docker token
# 3. Logs Docker into the registry
# Valid for 3 hours
```

### Method 2: Admin Account (Not Recommended for Production)

```bash
# Enable admin account
az acr update \
  --name $REGISTRY_NAME \
  --admin-enabled true

# Get credentials
az acr credential show \
  --name $REGISTRY_NAME

# Use credentials
docker login ${REGISTRY_NAME}.azurecr.io \
  --username <username> \
  --password <password>
```

### Method 3: Service Principal (Recommended for Production)

```bash
# Create service principal
SP_NAME="acr-service-principal"
ACR_REGISTRY_ID=$(az acr show --name $REGISTRY_NAME --query id --output tsv)

SP_PASSWD=$(az ad sp create-for-rbac \
  --name $SP_NAME \
  --scopes $ACR_REGISTRY_ID \
  --role acrpull \
  --query password \
  --output tsv)

SP_APP_ID=$(az ad sp list \
  --display-name $SP_NAME \
  --query [].appId \
  --output tsv)

# Login with service principal
docker login ${REGISTRY_NAME}.azurecr.io \
  --username $SP_APP_ID \
  --password $SP_PASSWD
```

### Method 4: Managed Identity (Best for Azure Services)

```bash
# Attach identity to AKS cluster
az aks update \
  --name myAKSCluster \
  --resource-group $RESOURCE_GROUP \
  --attach-acr $REGISTRY_NAME

# No credentials needed - AKS automatically authenticates
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
# Build from current directory
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  .

# Build with specific Dockerfile
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --file Dockerfile \
  .

# Build from specific directory
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  ./containers/examples/flask-echo
```

### Build with Multiple Tags

```bash
# Tag image with multiple tags
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --image flask-echo:latest \
  --image flask-echo:stable \
  .
```

### Build with Arguments

```bash
# Pass build arguments
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --build-arg PYTHON_VERSION=3.10 \
  --build-arg APP_ENV=production \
  .
```

### Build from Git Repository

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

### Build with Platform Specification

```bash
# Build for specific platform
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --platform linux/amd64 \
  .

# Build multi-platform image
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --platform linux/amd64,linux/arm64 \
  .
```

## Building the Echo Applications

### Build Flask Echo App

```bash
# Navigate to Flask app directory
cd containers/examples/flask-echo

# Build and push to ACR
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --image flask-echo:latest \
  .

# Build with custom version
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:v2.0.0 \
  --build-arg APP_VERSION=2.0.0 \
  .

# View build logs
az acr task logs --registry $REGISTRY_NAME
```

### Build FastAPI Echo App

```bash
# Navigate to FastAPI app directory
cd containers/examples/fastapi-echo

# Build multi-stage image
az acr build \
  --registry $REGISTRY_NAME \
  --image fastapi-echo:v1.0.0 \
  --image fastapi-echo:latest \
  .

# Check build output for stage information
# You'll see:
# - Stage 1: builder (compiling dependencies)
# - Stage 2: runtime (final image)
```

### Build Both Apps at Once

```bash
# Build Flask app
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:latest \
  ./containers/examples/flask-echo &

# Build FastAPI app (in parallel)
az acr build \
  --registry $REGISTRY_NAME \
  --image fastapi-echo:latest \
  ./containers/examples/fastapi-echo &

# Wait for both to complete
wait

echo "Both images built successfully!"
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

### Delete Images

```bash
# Delete specific tag
az acr repository delete \
  --name $REGISTRY_NAME \
  --image flask-echo:v1.0.0 \
  --yes

# Delete all tags in repository
az acr repository delete \
  --name $REGISTRY_NAME \
  --repository flask-echo \
  --yes

# Delete untagged manifests
az acr repository show-manifests \
  --name $REGISTRY_NAME \
  --repository flask-echo \
  --query "[?tags[0]==null].digest" \
  --output tsv | \
  xargs -I {} az acr repository delete \
    --name $REGISTRY_NAME \
    --image flask-echo@{} \
    --yes
```

## ACR Tasks (Advanced)

ACR Tasks enable automated builds triggered by events.

### Create a Build Task

```bash
# Create task that builds on git commit
az acr task create \
  --name build-flask-echo \
  --registry $REGISTRY_NAME \
  --context https://github.com/yourusername/yourrepo.git \
  --file Dockerfile \
  --image flask-echo:{{.Run.ID}} \
  --git-access-token <PAT>

# Run task manually
az acr task run \
  --name build-flask-echo \
  --registry $REGISTRY_NAME

# List tasks
az acr task list \
  --registry $REGISTRY_NAME \
  --output table

# View task runs
az acr task list-runs \
  --registry $REGISTRY_NAME \
  --output table
```

### Quick Task (One-time Build)

```bash
# Quick build without creating a task
az acr build \
  --registry $REGISTRY_NAME \
  --image flask-echo:{{.Run.ID}} \
  https://github.com/yourusername/yourrepo.git
```

## Image Scanning and Security

### Azure Defender for Container Registries

```bash
# Enable Azure Defender (requires Premium tier)
az security pricing create \
  --name ContainerRegistry \
  --tier Standard

# View vulnerability assessment results
az security assessment list \
  --query "[?id contains(@, 'containerRegistry')]"
```

### Manually Scan Images

```bash
# Use Trivy for scanning
docker run --rm \
  -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest
```

## Geo-Replication (Premium Tier Only)

```bash
# Create Premium registry
az acr create \
  --resource-group $RESOURCE_GROUP \
  --name $REGISTRY_NAME \
  --sku Premium

# Replicate to another region
az acr replication create \
  --registry $REGISTRY_NAME \
  --location westeurope

# List replications
az acr replication list \
  --registry $REGISTRY_NAME \
  --output table

# Delete replication
az acr replication delete \
  --registry $REGISTRY_NAME \
  --name westeurope
```

## Integration Examples

### Pull Image to Local Docker

**Option 1: Local Docker Desktop**

```bash
# Login to ACR
az acr login --name $REGISTRY_NAME

# Pull image
docker pull ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Run locally
docker run -d \
  --name flask-echo \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest
```

**Option 2: Docker VM (No Local Docker Needed)**

If you don't have Docker installed locally, use a Docker VM:

```bash
# Connect to Docker VM (see docker-vm-setup.md for setup)
docker-vm

# Login to ACR from VM
az login
az acr login --name $REGISTRY_NAME

# Pull and run image
docker pull ${REGISTRY_NAME}.azurecr.io/flask-echo:latest
docker run -d --name flask-echo -p 8080:8080 ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Test from within VM
curl http://localhost:8080/
```

### Deploy to Azure Container Instances

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
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD

# Get FQDN
az container show \
  --resource-group $RESOURCE_GROUP \
  --name flask-echo \
  --query ipAddress.fqdn \
  --output tsv
```

### Deploy to Azure Kubernetes Service

```bash
# Create AKS cluster
az aks create \
  --resource-group $RESOURCE_GROUP \
  --name myAKSCluster \
  --node-count 2 \
  --generate-ssh-keys \
  --attach-acr $REGISTRY_NAME

# Get credentials
az aks get-credentials \
  --resource-group $RESOURCE_GROUP \
  --name myAKSCluster

# Deploy to AKS
kubectl run flask-echo \
  --image=${REGISTRY_NAME}.azurecr.io/flask-echo:latest \
  --port=8080

# Expose as service
kubectl expose pod flask-echo \
  --type=LoadBalancer \
  --port=80 \
  --target-port=8080
```

## Best Practices

### 1. Tagging Strategy

```bash
# ✅ Good: Semantic versioning + latest
az acr build \
  --image flask-echo:1.2.3 \
  --image flask-echo:1.2 \
  --image flask-echo:1 \
  --image flask-echo:latest \
  ...

# ✅ Good: Include git commit
az acr build \
  --image flask-echo:$(git rev-parse --short HEAD) \
  ...

# ❌ Bad: Only using latest
az acr build --image flask-echo:latest ...
```

### 2. Image Naming

```bash
# ✅ Good: Descriptive names
flask-echo
fastapi-echo
api-gateway
user-service

# ❌ Bad: Generic names
app
service
container
```

### 3. Build Context

```bash
# ✅ Good: Use .dockerignore
cat > .dockerignore << EOF
.git
.venv
__pycache__
*.pyc
EOF

# ✅ Good: Specific context
az acr build --image app:v1 ./src

# ❌ Bad: Entire repo as context
az acr build --image app:v1 .
```

### 4. Security

```bash
# ✅ Good: Use managed identity
az aks update --attach-acr $REGISTRY_NAME

# ✅ Good: Scan images
az acr task create --name scan-on-push ...

# ✅ Good: Use private networking (Premium)
az acr private-endpoint-connection create ...

# ❌ Bad: Enable admin account in production
az acr update --admin-enabled true
```

### 5. Cost Optimization

```bash
# ✅ Good: Clean up old images
az acr repository show-tags ... | \
  tail -n +10 | \
  xargs -I {} az acr repository delete ...

# ✅ Good: Use retention policy (Premium)
az acr config retention update \
  --registry $REGISTRY_NAME \
  --status enabled \
  --days 30 \
  --type UntaggedManifests

# ✅ Good: Use Basic tier for dev/test
az acr create --sku Basic ...
```

## Troubleshooting

### Build Fails

```bash
# View detailed build logs
az acr task logs \
  --registry $REGISTRY_NAME \
  --run-id <run-id>

# Test build locally (if Docker available)
docker build -t test .

# Check Dockerfile syntax
cat Dockerfile
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
- Learn about [ACR Tasks automation](https://docs.microsoft.com/azure/container-registry/container-registry-tasks-overview)

## Additional Resources

- [ACR Documentation](https://docs.microsoft.com/azure/container-registry/)
- [ACR Best Practices](https://docs.microsoft.com/azure/container-registry/container-registry-best-practices)
- [ACR Tasks](https://docs.microsoft.com/azure/container-registry/container-registry-tasks-overview)
- [Container Security](https://docs.microsoft.com/azure/container-registry/container-registry-content-trust)

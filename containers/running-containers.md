# Running Containers Locally

This guide covers running containers on your local machine, managing container lifecycle, and working with multiple containers.

## Prerequisites

### Option 1: Docker Desktop (Local Container Runtime)

If you have Docker Desktop installed:

```bash
# Verify Docker is running
docker --version

# Check Docker daemon status
docker ps
```

### Option 2: Azure Container Instances (Cloud-based)

If local Docker is not available, use Azure Container Instances (ACI):

```bash
# Verify Azure CLI is installed
az --version

# Login to Azure
az login

# Create a resource group
az group create --name rg-containers --location eastus
```

## Container Lifecycle

Understanding container states and transitions:

```
┌─────────┐
│  Image  │  (Stored template)
└────┬────┘
     │ docker/podman run
     ▼
┌─────────┐
│ Created │  (Container created, not started)
└────┬────┘
     │ start
     ▼
┌─────────┐
│ Running │  (Container actively running)
└────┬────┘
     │
┌────┼────┐
│    │    │
▼    ▼    ▼
pause stop kill
│    │    │
└────┴────┘
     │
     ▼
┌─────────┐
│ Stopped │  (Container stopped, can be restarted)
└────┬────┘
     │ remove
     ▼
  [Deleted]
```

## Running Your First Container

### Using Docker (Local)

```bash
# Run a simple container
docker run hello-world

# Run with interactive terminal
docker run -it ubuntu:22.04 /bin/bash

# Run in detached mode (background)
docker run -d nginx:latest

# Run with port mapping
docker run -d -p 8080:80 nginx:latest

# Run with name
docker run -d --name my-nginx -p 8080:80 nginx:latest
```

### Using Azure Container Instances

```bash
# Run a simple container
az container create \
  --resource-group rg-containers \
  --name hello-world \
  --image mcr.microsoft.com/azuredocs/aci-helloworld \
  --dns-name-label aci-demo-${RANDOM} \
  --ports 80

# Get the FQDN
az container show \
  --resource-group rg-containers \
  --name hello-world \
  --query ipAddress.fqdn -o tsv

# View logs
az container logs \
  --resource-group rg-containers \
  --name hello-world
```

## Running the Echo Applications

### Flask Echo App

#### With Docker

```bash
# Pull from ACR (if already built)
REGISTRY_NAME="myregistry"
docker login ${REGISTRY_NAME}.azurecr.io
docker pull ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Run the container
docker run -d \
  --name flask-echo \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Test it
curl http://localhost:8080/
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Flask!"}'
```

#### With Azure Container Instances

```bash
# Set variables
REGISTRY_NAME="myregistry"
ACR_USERNAME=$(az acr credential show --name $REGISTRY_NAME --query username -o tsv)
ACR_PASSWORD=$(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Create container
az container create \
  --resource-group rg-containers \
  --name flask-echo \
  --image ${REGISTRY_NAME}.azurecr.io/flask-echo:latest \
  --dns-name-label flask-echo-${RANDOM} \
  --ports 8080 \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD

# Get the URL
FLASK_URL=$(az container show --resource-group rg-containers --name flask-echo --query ipAddress.fqdn -o tsv)
echo "Flask app: http://${FLASK_URL}:8080"

# Test it
curl http://${FLASK_URL}:8080/
```

### FastAPI Echo App

#### With Docker

```bash
# Run FastAPI container
docker run -d \
  --name fastapi-echo \
  -p 8081:8080 \
  ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest

# Test it
curl http://localhost:8081/

# Open API documentation
open http://localhost:8081/docs
```

#### With Azure Container Instances

```bash
# Create container
az container create \
  --resource-group rg-containers \
  --name fastapi-echo \
  --image ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest \
  --dns-name-label fastapi-echo-${RANDOM} \
  --ports 8080 \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $ACR_USERNAME \
  --registry-password $ACR_PASSWORD

# Get the URL
FASTAPI_URL=$(az container show --resource-group rg-containers --name fastapi-echo --query ipAddress.fqdn -o tsv)
echo "FastAPI app: http://${FASTAPI_URL}:8080"
echo "API docs: http://${FASTAPI_URL}:8080/docs"
```

## Container Management Commands

### Docker Commands

#### Listing Containers

```bash
# List running containers
docker ps

# List all containers (including stopped)
docker ps -a

# List containers with custom format
docker ps --format "table {{.ID}}\t{{.Names}}\t{{.Status}}\t{{.Ports}}"
```

#### Container Information

```bash
# Inspect container details
docker inspect flask-echo

# View container logs
docker logs flask-echo

# Follow logs in real-time
docker logs -f flask-echo

# Show last 50 lines
docker logs --tail 50 flask-echo

# View resource usage
docker stats flask-echo

# View all stats
docker stats
```

#### Container Control

```bash
# Stop container
docker stop flask-echo

# Start stopped container
docker start flask-echo

# Restart container
docker restart flask-echo

# Pause container (freeze processes)
docker pause flask-echo

# Unpause container
docker unpause flask-echo

# Remove container (must be stopped first)
docker rm flask-echo

# Force remove running container
docker rm -f flask-echo
```

#### Executing Commands in Containers

```bash
# Run command in running container
docker exec flask-echo ls -l /app

# Interactive shell
docker exec -it flask-echo /bin/bash

# Run as different user
docker exec -u root flask-echo apt-get update

# Check process list
docker exec flask-echo ps aux

# Test connectivity
docker exec flask-echo curl http://localhost:8080/health
```

### Azure Container Instances Commands

```bash
# List containers
az container list --resource-group rg-containers --output table

# Show container details
az container show \
  --resource-group rg-containers \
  --name flask-echo

# View logs
az container logs \
  --resource-group rg-containers \
  --name flask-echo

# Stream logs
az container attach \
  --resource-group rg-containers \
  --name flask-echo

# Execute command
az container exec \
  --resource-group rg-containers \
  --name flask-echo \
  --exec-command "/bin/bash"

# Stop container (ACI doesn't support stop/start)
# Delete and recreate instead
az container delete \
  --resource-group rg-containers \
  --name flask-echo \
  --yes
```

## Working with Multiple Containers

### Running Multiple Containers with Docker

```bash
# Run Flask app on port 8080
docker run -d \
  --name flask-echo \
  -p 8080:8080 \
  -e APP_VERSION=1.0.0 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Run FastAPI app on port 8081
docker run -d \
  --name fastapi-echo \
  -p 8081:8080 \
  -e APP_VERSION=1.0.0 \
  ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest

# List both containers
docker ps

# View logs from both
docker logs flask-echo
docker logs fastapi-echo

# Compare responses
curl http://localhost:8080/
curl http://localhost:8081/

# Test both echo endpoints
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Flask test"}'

curl -X POST http://localhost:8081/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "FastAPI test"}'
```

### Container Networking with Docker

```bash
# Create a custom network
docker network create echo-network

# Run containers on the same network
docker run -d \
  --name flask-echo \
  --network echo-network \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

docker run -d \
  --name fastapi-echo \
  --network echo-network \
  -p 8081:8080 \
  ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest

# Containers can communicate by name
docker exec flask-echo ping -c 3 fastapi-echo
docker exec fastapi-echo curl http://flask-echo:8080/health

# List networks
docker network ls

# Inspect network
docker network inspect echo-network

# Remove network (containers must be stopped first)
docker network rm echo-network
```

## Environment Variables

### Passing Environment Variables

```bash
# Single variable
docker run -e APP_VERSION=2.0.0 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Multiple variables
docker run \
  -e APP_VERSION=2.0.0 \
  -e PORT=9090 \
  -p 9090:9090 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# From file
cat > .env << EOF
APP_VERSION=2.0.0
PORT=8080
DEBUG=false
EOF

docker run --env-file .env \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest
```

### With Azure Container Instances

```bash
az container create \
  --resource-group rg-containers \
  --name flask-echo \
  --image ${REGISTRY_NAME}.azurecr.io/flask-echo:latest \
  --environment-variables \
    APP_VERSION=2.0.0 \
    CUSTOM_VAR=value \
  --ports 8080
```

## Volumes and Persistence

### Docker Volumes

```bash
# Create a volume
docker volume create app-data

# Run container with volume
docker run -d \
  --name flask-echo \
  -v app-data:/data \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# List volumes
docker volume ls

# Inspect volume
docker volume inspect app-data

# Remove volume
docker volume rm app-data
```

### Bind Mounts (Local Development)

```bash
# Mount local directory into container
docker run -d \
  --name flask-echo \
  -v $(pwd)/app:/app \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Changes to local files are reflected in container
echo "print('Updated!')" >> app/app.py
docker restart flask-echo
```

## Resource Limits

### Docker Resource Constraints

```bash
# Limit CPU and memory
docker run -d \
  --name flask-echo \
  --cpus="0.5" \
  --memory="256m" \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Check resource usage
docker stats flask-echo
```

### Azure Container Instances Resource Limits

```bash
az container create \
  --resource-group rg-containers \
  --name flask-echo \
  --image ${REGISTRY_NAME}.azurecr.io/flask-echo:latest \
  --cpu 0.5 \
  --memory 0.5 \
  --ports 8080
```

## Troubleshooting

### Container Won't Start

```bash
# Check logs
docker logs flask-echo

# Run interactively to see errors
docker run -it --rm \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Check if port is already in use
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows
```

### Can't Connect to Container

```bash
# Verify container is running
docker ps

# Check port mapping
docker port flask-echo

# Test from within container
docker exec flask-echo curl http://localhost:8080/health

# Check container IP
docker inspect flask-echo | grep IPAddress

# Test with container IP
curl http://172.17.0.2:8080/
```

### Container Exits Immediately

```bash
# Check exit code
docker ps -a

# View logs
docker logs flask-echo

# Run with shell to debug
docker run -it --rm --entrypoint /bin/bash \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest
```

### Performance Issues

```bash
# Monitor resource usage
docker stats

# Check container processes
docker exec flask-echo ps aux

# View system resource usage
docker system df

# Clean up unused resources
docker system prune -a
```

## Best Practices

### 1. Container Naming

```bash
# ✅ Good: Use descriptive names
docker run -d --name flask-echo-prod ...

# ❌ Bad: Auto-generated names
docker run -d ...  # Gets random name
```

### 2. Port Management

```bash
# ✅ Good: Explicit port mapping
docker run -d -p 8080:8080 ...

# ⚠️ Caution: Random host port
docker run -d -P ...

# ❌ Bad: Publishing all ports
docker run -d -p 0.0.0.0:0:8080 ...
```

### 3. Resource Limits

```bash
# ✅ Good: Set reasonable limits
docker run -d --memory="512m" --cpus="1.0" ...

# ❌ Bad: No limits (can consume all resources)
docker run -d ...
```

### 4. Container Cleanup

```bash
# ✅ Good: Remove when done
docker run --rm ...

# ✅ Good: Regular cleanup
docker container prune
docker image prune

# ❌ Bad: Accumulate stopped containers
docker ps -a  # Shows hundreds of stopped containers
```

### 5. Health Checks

```bash
# ✅ Good: Use health checks
docker run -d \
  --health-cmd="curl -f http://localhost:8080/health || exit 1" \
  --health-interval=30s \
  ...

# Check health status
docker ps  # Shows health status
docker inspect flask-echo | grep -A 10 Health
```

## Cleaning Up

### Docker Cleanup

```bash
# Stop all running containers
docker stop $(docker ps -q)

# Remove all containers
docker rm $(docker ps -a -q)

# Remove all images
docker rmi $(docker images -q)

# Clean up everything (careful!)
docker system prune -a --volumes

# Selective cleanup
docker container prune  # Remove stopped containers
docker image prune     # Remove unused images
docker volume prune    # Remove unused volumes
docker network prune   # Remove unused networks
```

### Azure Container Instances Cleanup

```bash
# Delete specific container
az container delete \
  --resource-group rg-containers \
  --name flask-echo \
  --yes

# Delete all containers in resource group
az container list \
  --resource-group rg-containers \
  --query "[].name" -o tsv | \
  xargs -I {} az container delete \
    --resource-group rg-containers \
    --name {} \
    --yes

# Delete resource group (removes everything)
az group delete --name rg-containers --yes --no-wait
```

## Next Steps

- Learn about [Azure Container Registry](acr-guide.md)
- Explore [multi-container scenarios](multi-container.md)
- Deploy to [Azure Kubernetes Service](../aks/README.md)

## Additional Resources

- [Docker Run Reference](https://docs.docker.com/engine/reference/run/)
- [Azure Container Instances](https://docs.microsoft.com/azure/container-instances/)
- [Container Networking](https://docs.docker.com/network/)
- [Docker Volumes](https://docs.docker.com/storage/volumes/)

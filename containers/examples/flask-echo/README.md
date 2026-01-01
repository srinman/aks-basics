# Flask Echo Application

A simple REST API built with Flask that demonstrates containerizing a Python web application with dependencies.

## Application Features

- **Echo Endpoint**: POST messages and receive them back with metadata
- **Health Check**: Kubernetes-ready health check endpoint
- **Container Info**: View container and environment details
- **Framework**: Flask 3.0 with Werkzeug

## API Endpoints

### GET /
Returns API information and available endpoints.

```bash
curl http://localhost:8080/
```

### POST /echo
Echo back a message with metadata.

**Request:**
```bash
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from Flask!"}'
```

**Response:**
```json
{
  "echo": "Hello from Flask!",
  "timestamp": "2026-01-01T12:00:00",
  "hostname": "flask-echo-abc123",
  "client_ip": "192.168.1.1",
  "metadata": {
    "framework": "Flask",
    "version": "1.0.0",
    "python_version": "3.11.5"
  }
}
```

### GET /health
Health check endpoint for container orchestration.

```bash
curl http://localhost:8080/health
```

### GET /info
Get container and environment information.

```bash
curl http://localhost:8080/info
```

## Dockerfile Explanation

The Dockerfile demonstrates several best practices:

```dockerfile
# Use Python slim image for smaller size
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy and install dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Document the port
EXPOSE 8080

# Set environment variables
ENV PORT=8080 \
    APP_VERSION=1.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "app.py"]
```

### Key Dockerfile Concepts

1. **Base Image**: `python:3.11-slim` (~120MB vs ~900MB for full image)
2. **Layer Caching**: Dependencies installed before copying code
3. **Security**: Runs as non-root user (uid 1000)
4. **Health Check**: Kubernetes-compatible health endpoint
5. **Configuration**: Environment variables for runtime config

## Building the Container Image

### Option 1: Using Azure Container Registry (Recommended)

Since local Docker may not be available, use Azure Container Registry to build:

```bash
# Set variables
REGISTRY_NAME="myregistry"
IMAGE_NAME="flask-echo"
TAG="v1.0.0"

# Build image with ACR
az acr build \
  --registry $REGISTRY_NAME \
  --image ${IMAGE_NAME}:${TAG} \
  --image ${IMAGE_NAME}:latest \
  --file Dockerfile \
  .
```

### Option 2: Using Docker VM (Local-like Experience)

For hands-on learning with Docker commands, set up a Docker VM:

```bash
# Follow the Docker VM setup guide first:
# See: ../../docker-vm-setup.md

# Connect to Docker VM
docker-vm

# Clone repository or copy files
cd ~/containers
git clone <your-repo> && cd <repo>/containers/examples/flask-echo

# Build locally on VM
docker build -t flask-echo:v1.0.0 -t flask-echo:latest .

# Run on VM
docker run -d -p 8080:8080 flask-echo:latest

# Test
curl http://localhost:8080/
```

### Build with Custom Arguments

```bash
# Build with custom Python version
az acr build \
  --registry $REGISTRY_NAME \
  --image ${IMAGE_NAME}:${TAG} \
  --build-arg PYTHON_VERSION=3.10 \
  .

# Build for different environment
az acr build \
  --registry $REGISTRY_NAME \
  --image ${IMAGE_NAME}:dev \
  --build-arg APP_ENV=development \
  .
```

## Running the Container

### Run Locally (if Docker available)

```bash
# Run the container
docker run -d \
  --name flask-echo \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${TAG}

# Test the application
curl http://localhost:8080/

# View logs
docker logs flask-echo

# Stop and remove
docker stop flask-echo
docker rm flask-echo
```

### Run with Environment Variables

```bash
docker run -d \
  --name flask-echo \
  -p 9090:9090 \
  -e PORT=9090 \
  -e APP_VERSION=2.0.0 \
  ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${TAG}
```

### Run with Azure Container Instances

```bash
# Create resource group if needed
az group create --name rg-container-demo --location eastus

# Run with ACI
az container create \
  --resource-group rg-container-demo \
  --name flask-echo \
  --image ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${TAG} \
  --dns-name-label flask-echo-demo \
  --ports 8080 \
  --environment-variables \
    APP_VERSION=1.0.0 \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $(az acr credential show --name $REGISTRY_NAME --query username -o tsv) \
  --registry-password $(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Get the FQDN
az container show \
  --resource-group rg-container-demo \
  --name flask-echo \
  --query ipAddress.fqdn -o tsv

# Test the application
FQDN=$(az container show --resource-group rg-container-demo --name flask-echo --query ipAddress.fqdn -o tsv)
curl http://${FQDN}:8080/

# View logs
az container logs --resource-group rg-container-demo --name flask-echo

# Clean up
az container delete --resource-group rg-container-demo --name flask-echo --yes
```

## Testing the Application

### Basic Tests

```bash
# Test home endpoint
curl http://localhost:8080/

# Test echo endpoint
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Testing Flask echo!"}'

# Test health endpoint
curl http://localhost:8080/health

# Test info endpoint
curl http://localhost:8080/info
```

### Load Testing

```bash
# Send multiple requests
for i in {1..10}; do
  curl -X POST http://localhost:8080/echo \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Message $i\"}"
  echo ""
done
```

## Project Structure

```
flask-echo/
├── app.py              # Flask application code
├── requirements.txt    # Python dependencies
├── Dockerfile          # Container image definition
├── .dockerignore      # Files to exclude from build context
└── README.md          # This file
```

## Dependencies

The application uses minimal dependencies:

- **Flask 3.0.0**: Web framework
- **Werkzeug 3.0.1**: WSGI utility library (Flask dependency)

Total installed size: ~15MB (in addition to Python base image)

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 8080 | Port the application listens on |
| APP_VERSION | 1.0.0 | Application version (for metadata) |

## Security Considerations

1. **Non-root User**: Application runs as `appuser` (uid 1000)
2. **No Secrets**: No hardcoded credentials or secrets
3. **Minimal Base**: Uses slim Python image
4. **Updated Dependencies**: Latest stable versions
5. **Health Checks**: Supports container health monitoring

## Troubleshooting

### Container won't start

```bash
# Check logs
docker logs flask-echo

# Run interactively
docker run -it --rm \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${TAG}
```

### Can't connect to application

```bash
# Check if container is running
docker ps

# Check port mapping
docker port flask-echo

# Test from within container
docker exec flask-echo curl http://localhost:8080/health
```

### Build failures

```bash
# Check ACR build logs
az acr task logs --registry $REGISTRY_NAME

# Validate Dockerfile syntax
docker build --no-cache -t test .
```

## Next Steps

- Compare with [FastAPI Echo App](../fastapi-echo/README.md)
- Learn about [running multiple containers](../../multi-container.md)
- Deploy to [Azure Kubernetes Service](../../../aks/README.md)

## Additional Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Dockerfile Best Practices](../../dockerfile-guide.md)
- [Azure Container Registry](../../acr-guide.md)

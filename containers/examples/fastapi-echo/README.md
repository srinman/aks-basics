# FastAPI Echo Application

A modern async REST API built with FastAPI that demonstrates containerizing a Python web application with a different framework and dependency set compared to Flask.

## Application Features

- **Async Architecture**: Built on ASGI for high performance
- **Automatic API Documentation**: Swagger UI and ReDoc included
- **Type Safety**: Pydantic models for request/response validation
- **Modern Framework**: FastAPI with Uvicorn ASGI server
- **Health Checks**: Kubernetes-ready health endpoint

## Why FastAPI vs Flask?

| Feature | FastAPI | Flask |
|---------|---------|-------|
| Performance | High (async) | Moderate (sync) |
| API Docs | Auto-generated | Manual |
| Validation | Built-in (Pydantic) | Extensions needed |
| Type Hints | Native support | Limited |
| Learning Curve | Moderate | Easy |
| Use Case | Modern APIs | Traditional web apps |

## API Endpoints

### GET /
Returns API information and available endpoints.

```bash
curl http://localhost:8080/
```

### POST /echo
Echo back a message with metadata and validation.

**Request:**
```bash
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello from FastAPI!"}'
```

**Response:**
```json
{
  "echo": "Hello from FastAPI!",
  "timestamp": "2026-01-01T12:00:00",
  "hostname": "fastapi-echo-xyz789",
  "client_ip": "container",
  "metadata": {
    "framework": "FastAPI",
    "version": "1.0.0",
    "python_version": "3.11.5",
    "async": true
  }
}
```

### GET /health
Health check endpoint.

```bash
curl http://localhost:8080/health
```

### GET /info
Container and environment information.

```bash
curl http://localhost:8080/info
```

### GET /docs
Interactive API documentation (Swagger UI).

Open in browser: `http://localhost:8080/docs`

### GET /redoc
Alternative API documentation (ReDoc).

Open in browser: `http://localhost:8080/redoc`

## Dockerfile Explanation

The Dockerfile uses a multi-stage build for optimization:

```dockerfile
# Build stage - install dependencies
FROM python:3.11-slim AS builder

WORKDIR /build

# Copy requirements and create wheels
COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# Runtime stage - minimal final image
FROM python:3.11-slim

WORKDIR /app

# Copy and install wheels from builder
COPY --from=builder /build/wheels /tmp/wheels
RUN pip install --no-cache-dir --no-index --find-links=/tmp/wheels /tmp/wheels/* && \
    rm -rf /tmp/wheels

# Copy application code
COPY app.py .

# Security: create and use non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Document port
EXPOSE 8080

# Environment variables
ENV PORT=8080 \
    APP_VERSION=1.0.0

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run with Uvicorn
CMD ["python", "app.py"]
```

### Key Differences from Flask Dockerfile

1. **Multi-stage Build**: Separates build and runtime
2. **Wheel Installation**: Pre-builds wheels for faster installs
3. **Different Dependencies**: FastAPI + Uvicorn instead of Flask
4. **ASGI Server**: Uvicorn for async support
5. **Longer Start Period**: Async apps may take longer to start

## Building the Container Image

### Option 1: Using Azure Container Registry

```bash
# Set variables
REGISTRY_NAME="myregistry"
IMAGE_NAME="fastapi-echo"
TAG="v1.0.0"

# Build image with ACR
az acr build \
  --registry $REGISTRY_NAME \
  --image ${IMAGE_NAME}:${TAG} \
  --image ${IMAGE_NAME}:latest \
  --file Dockerfile \
  .
```

### Option 2: Using Docker VM

For hands-on learning and testing multi-stage builds:

```bash
# Connect to Docker VM (see ../../docker-vm-setup.md)
docker-vm

# Clone or copy files
cd ~/containers
git clone <your-repo> && cd <repo>/containers/examples/fastapi-echo

# Build multi-stage image on VM
docker build -t fastapi-echo:v1.0.0 -t fastapi-echo:latest .

# Verify multi-stage build worked (smaller final image)
docker images fastapi-echo

# Run on VM
docker run -d -p 8080:8080 fastapi-echo:latest

# Test
curl http://localhost:8080/
curl http://localhost:8080/docs  # API documentation
```

### Compare Image Sizes

```bash
# List both Flask and FastAPI images
az acr repository show-tags \
  --name $REGISTRY_NAME \
  --repository flask-echo \
  --orderby time_desc

az acr repository show-tags \
  --name $REGISTRY_NAME \
  --repository fastapi-echo \
  --orderby time_desc

# Note: FastAPI image may be larger due to additional dependencies
# but offers better performance for async operations
```

## Running the Container

### Run Locally (if Docker available)

```bash
# Run the container
docker run -d \
  --name fastapi-echo \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${TAG}

# Test the application
curl http://localhost:8080/

# Open API documentation in browser
open http://localhost:8080/docs

# View logs
docker logs -f fastapi-echo

# Stop and remove
docker stop fastapi-echo
docker rm fastapi-echo
```

### Run with Environment Variables

```bash
docker run -d \
  --name fastapi-echo \
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
  --name fastapi-echo \
  --image ${REGISTRY_NAME}.azurecr.io/${IMAGE_NAME}:${TAG} \
  --dns-name-label fastapi-echo-demo \
  --ports 8080 \
  --environment-variables \
    APP_VERSION=1.0.0 \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $(az acr credential show --name $REGISTRY_NAME --query username -o tsv) \
  --registry-password $(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Get the FQDN
FQDN=$(az container show --resource-group rg-container-demo --name fastapi-echo --query ipAddress.fqdn -o tsv)

# Test the application
curl http://${FQDN}:8080/

# Open API docs in browser
echo "API Docs: http://${FQDN}:8080/docs"

# Clean up
az container delete --resource-group rg-container-demo --name fastapi-echo --yes
```

## Testing the Application

### Basic Tests

```bash
# Test home endpoint
curl http://localhost:8080/

# Test echo endpoint
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Testing FastAPI echo!"}'

# Test health endpoint
curl http://localhost:8080/health

# Test info endpoint
curl http://localhost:8080/info

# Test with invalid data (Pydantic validation)
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: application/json" \
  -d '{"invalid": "field"}'
```

### Interactive API Testing

1. Open Swagger UI: `http://localhost:8080/docs`
2. Click on any endpoint to expand
3. Click "Try it out"
4. Fill in the request body
5. Click "Execute"
6. View the response

### Load Testing

```bash
# Send multiple concurrent requests
for i in {1..20}; do
  curl -X POST http://localhost:8080/echo \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Async message $i\"}" &
done
wait
```

## Project Structure

```
fastapi-echo/
├── app.py              # FastAPI application code
├── requirements.txt    # Python dependencies
├── Dockerfile          # Multi-stage container image
├── .dockerignore      # Files to exclude from build
└── README.md          # This file
```

## Dependencies

The application uses modern async dependencies:

- **FastAPI 0.109.0**: Modern web framework
- **Uvicorn 0.27.0**: ASGI server with websocket support
- **Pydantic 2.5.3**: Data validation using Python type hints

Total installed size: ~40MB (in addition to Python base image)

## Comparing with Flask

### Dependency Size Comparison

| Framework | Dependencies | Total Size |
|-----------|-------------|------------|
| Flask | Flask, Werkzeug | ~15MB |
| FastAPI | FastAPI, Uvicorn, Pydantic | ~40MB |

### Performance Comparison

FastAPI excels in:
- Async I/O operations
- High concurrency scenarios
- WebSocket support
- Streaming responses

Flask is better for:
- Simple synchronous apps
- Smaller deployments
- Quick prototypes
- Traditional web apps

### When to Use Each

**Choose Flask when:**
- Building simple REST APIs
- Minimal dependencies needed
- Team familiar with Flask
- Synchronous operations sufficient

**Choose FastAPI when:**
- Need high performance
- Want automatic API docs
- Using async operations
- Building modern microservices

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| PORT | 8080 | Port the application listens on |
| APP_VERSION | 1.0.0 | Application version |

## Security Considerations

1. **Non-root User**: Runs as `appuser` (uid 1000)
2. **Multi-stage Build**: Build tools not in final image
3. **No Secrets**: No hardcoded credentials
4. **Minimal Base**: Slim Python image
5. **Updated Dependencies**: Latest stable versions
6. **Input Validation**: Pydantic models validate all inputs

## Troubleshooting

### Startup is slower than Flask

FastAPI with Uvicorn may take a few extra seconds to start. The health check has a longer `start-period` to accommodate this.

### Module import errors

```bash
# Check installed packages
docker exec fastapi-echo pip list

# Verify requirements were installed
docker exec fastapi-echo python -c "import fastapi; import uvicorn; print('OK')"
```

### Cannot access /docs

Make sure you're accessing via HTTP (not HTTPS) and the correct port:
```bash
curl http://localhost:8080/docs
```

## Next Steps

- Compare with [Flask Echo App](../flask-echo/README.md)
- Learn about [running multiple containers](../../multi-container.md)
- Deploy both apps simultaneously to see differences
- Explore [Azure Container Registry](../../acr-guide.md)

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Uvicorn Documentation](https://www.uvicorn.org/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Async Python Guide](https://docs.python.org/3/library/asyncio.html)

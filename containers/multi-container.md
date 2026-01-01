# Multi-Container Scenarios

This guide covers working with multiple containers simultaneously, including container networking, inter-container communication, and orchestration basics.

## Why Multiple Containers?

Modern applications are often composed of multiple services:

- **Microservices Architecture**: Each service runs in its own container
- **Separation of Concerns**: Database, API, frontend in separate containers
- **Scalability**: Scale individual services independently
- **Technology Diversity**: Use different languages/frameworks per service
- **Fault Isolation**: One container failure doesn't crash entire application

## Multi-Container Patterns

### 1. Frontend + Backend

```
┌──────────────┐      ┌──────────────┐
│   Frontend   │─────>│   Backend    │
│  (Web UI)    │      │   (API)      │
└──────────────┘      └──────────────┘
```

### 2. API + Database

```
┌──────────────┐      ┌──────────────┐
│     API      │─────>│   Database   │
│  (Flask)     │      │  (Postgres)  │
└──────────────┘      └──────────────┘
```

### 3. Multiple APIs

```
┌──────────────┐
│   Gateway    │
└──────┬───────┘
       │
   ────┼────
   │       │
   ▼       ▼
┌─────┐ ┌─────┐
│Flask│ │Fast │
│ API │ │ API │
└─────┘ └─────┘
```

### 4. Sidecar Pattern

```
┌─────────────────────┐
│  Main Container     │
│  (Application)      │
└──────┬──────────────┘
       │
       ├─────> ┌──────────────┐
       │       │   Logging    │
       │       │   Sidecar    │
       │       └──────────────┘
       │
       └─────> ┌──────────────┐
               │  Monitoring  │
               │   Sidecar    │
               └──────────────┘
```

## Running Multiple Containers with Docker

### Example 1: Flask + FastAPI

```bash
# Set registry name
REGISTRY_NAME="myregistry"

# Start Flask app on port 8080
docker run -d \
  --name flask-echo \
  -p 8080:8080 \
  -e APP_VERSION=1.0.0 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Start FastAPI app on port 8081
docker run -d \
  --name fastapi-echo \
  -p 8081:8080 \
  -e APP_VERSION=1.0.0 \
  ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest

# Verify both are running
docker ps

# Test both applications
curl http://localhost:8080/
curl http://localhost:8081/

# Compare frameworks
echo "=== Flask ==="
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello Flask"}'

echo ""
echo "=== FastAPI ==="
curl -X POST http://localhost:8081/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello FastAPI"}'
```

### Example 2: With Container Networking

```bash
# Create a custom network
docker network create echo-network

# Run Flask with network
docker run -d \
  --name flask-echo \
  --network echo-network \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# Run FastAPI with network
docker run -d \
  --name fastapi-echo \
  --network echo-network \
  -p 8081:8080 \
  ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest

# Containers can communicate by name
docker exec flask-echo ping -c 3 fastapi-echo
docker exec fastapi-echo curl http://flask-echo:8080/health

# Test inter-container communication
docker exec flask-echo curl http://fastapi-echo:8080/info
```

### Example 3: With Nginx Load Balancer

```bash
# Create nginx configuration
cat > nginx.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream backend {
        server flask-echo:8080;
        server fastapi-echo:8080;
    }

    server {
        listen 80;
        
        location / {
            proxy_pass http://backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF

# Run nginx as load balancer
docker run -d \
  --name nginx-lb \
  --network echo-network \
  -p 80:80 \
  -v $(pwd)/nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine

# Test load balancing
for i in {1..10}; do
  curl http://localhost/
  echo ""
done
```

## Container Networking

### Network Types

| Type | Description | Use Case |
|------|-------------|----------|
| bridge | Default network, isolated | Single host, multiple containers |
| host | Use host network directly | Performance-critical apps |
| none | No networking | Isolated containers |
| custom | User-defined bridge | Multi-container apps |

### Managing Networks

```bash
# List networks
docker network ls

# Create custom network
docker network create \
  --driver bridge \
  --subnet 172.25.0.0/16 \
  my-network

# Inspect network
docker network inspect my-network

# Connect container to network
docker network connect my-network flask-echo

# Disconnect from network
docker network disconnect my-network flask-echo

# Remove network
docker network rm my-network
```

### Network Communication Examples

```bash
# Create network
docker network create app-network

# Run database
docker run -d \
  --name postgres \
  --network app-network \
  -e POSTGRES_PASSWORD=secret \
  postgres:15-alpine

# Run app that connects to database
docker run -d \
  --name my-app \
  --network app-network \
  -e DATABASE_URL=postgresql://postgres:secret@postgres:5432/mydb \
  -p 8080:8080 \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

# App can access database by name "postgres"
```

## Running Multiple Containers on Azure

### Azure Container Instances - Container Groups

Container Groups allow multiple containers to share resources and networking:

```bash
# Create a container group with both apps
az container create \
  --resource-group rg-containers \
  --name echo-apps \
  --image ${REGISTRY_NAME}.azurecr.io/flask-echo:latest \
  --cpu 1 \
  --memory 1 \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $(az acr credential show --name $REGISTRY_NAME --query username -o tsv) \
  --registry-password $(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv) \
  --ports 8080 8081 \
  --dns-name-label echo-apps-${RANDOM}

# Note: ACI container groups have limitations
# Better approach: Deploy each as separate container instance
```

### Separate Container Instances

```bash
# Deploy Flask
az container create \
  --resource-group rg-containers \
  --name flask-echo \
  --image ${REGISTRY_NAME}.azurecr.io/flask-echo:latest \
  --dns-name-label flask-${RANDOM} \
  --ports 8080 \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $(az acr credential show --name $REGISTRY_NAME --query username -o tsv) \
  --registry-password $(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Deploy FastAPI
az container create \
  --resource-group rg-containers \
  --name fastapi-echo \
  --image ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest \
  --dns-name-label fastapi-${RANDOM} \
  --ports 8080 \
  --registry-login-server ${REGISTRY_NAME}.azurecr.io \
  --registry-username $(az acr credential show --name $REGISTRY_NAME --query username -o tsv) \
  --registry-password $(az acr credential show --name $REGISTRY_NAME --query passwords[0].value -o tsv)

# Get both URLs
FLASK_URL=$(az container show --resource-group rg-containers --name flask-echo --query ipAddress.fqdn -o tsv)
FASTAPI_URL=$(az container show --resource-group rg-containers --name fastapi-echo --query ipAddress.fqdn -o tsv)

echo "Flask: http://${FLASK_URL}:8080"
echo "FastAPI: http://${FASTAPI_URL}:8080"
```

## Docker Compose (Local Development)

Docker Compose simplifies multi-container applications:

### Basic docker-compose.yml

```yaml
version: '3.8'

services:
  flask-echo:
    image: ${REGISTRY_NAME}.azurecr.io/flask-echo:latest
    ports:
      - "8080:8080"
    environment:
      - APP_VERSION=1.0.0
    networks:
      - echo-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3
  
  fastapi-echo:
    image: ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest
    ports:
      - "8081:8080"
    environment:
      - APP_VERSION=1.0.0
    networks:
      - echo-network
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3

networks:
  echo-network:
    driver: bridge
```

### Using Docker Compose

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f flask-echo

# List running services
docker-compose ps

# Scale a service
docker-compose up -d --scale flask-echo=3

# Stop all services
docker-compose stop

# Remove all containers
docker-compose down

# Remove containers and volumes
docker-compose down -v
```

### Advanced docker-compose.yml

```yaml
version: '3.8'

services:
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
    depends_on:
      - flask-echo
      - fastapi-echo
    networks:
      - echo-network

  flask-echo:
    image: ${REGISTRY_NAME}.azurecr.io/flask-echo:latest
    environment:
      - APP_VERSION=1.0.0
      - PORT=8080
    networks:
      - echo-network
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3

  fastapi-echo:
    image: ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest
    environment:
      - APP_VERSION=1.0.0
      - PORT=8080
    networks:
      - echo-network
    deploy:
      replicas: 2
      resources:
        limits:
          cpus: '0.5'
          memory: 512M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8080/health"]
      interval: 30s
      timeout: 3s
      retries: 3

networks:
  echo-network:
    driver: bridge
```

## Communication Patterns

### 1. REST API Calls

```python
# Container A calling Container B
import requests

response = requests.get('http://fastapi-echo:8080/health')
print(response.json())
```

### 2. Shared Volume

```bash
# Create shared volume
docker volume create shared-data

# Container A writes data
docker run -d \
  --name writer \
  -v shared-data:/data \
  alpine sh -c "echo 'Hello' > /data/message.txt"

# Container B reads data
docker run --rm \
  -v shared-data:/data \
  alpine cat /data/message.txt
```

### 3. Network Discovery

```bash
# Containers can discover each other by service name
docker exec flask-echo nslookup fastapi-echo
docker exec flask-echo ping -c 3 fastapi-echo
```

## Monitoring Multiple Containers

### View All Container Stats

```bash
# Resource usage for all containers
docker stats

# Specific containers
docker stats flask-echo fastapi-echo

# One-time snapshot
docker stats --no-stream
```

### Aggregate Logs

```bash
# View logs from multiple containers
docker logs flask-echo &
docker logs fastapi-echo &

# With timestamps
docker logs -t flask-echo &
docker logs -t fastapi-echo &

# Follow multiple logs (requires separate terminals)
# Terminal 1:
docker logs -f flask-echo

# Terminal 2:
docker logs -f fastapi-echo
```

### Health Checks

```bash
# Check health status
docker ps --format "table {{.Names}}\t{{.Status}}"

# Inspect health
docker inspect flask-echo --format='{{.State.Health.Status}}'
docker inspect fastapi-echo --format='{{.State.Health.Status}}'
```

## Load Testing Multiple Containers

```bash
# Test Flask endpoint
echo "Testing Flask..."
for i in {1..100}; do
  curl -s -X POST http://localhost:8080/echo \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test $i\"}" > /dev/null &
done
wait

# Test FastAPI endpoint
echo "Testing FastAPI..."
for i in {1..100}; do
  curl -s -X POST http://localhost:8081/echo \
    -H "Content-Type: application/json" \
    -d "{\"message\": \"Test $i\"}" > /dev/null &
done
wait

# Compare resource usage
docker stats --no-stream flask-echo fastapi-echo
```

## Practical Example: Complete Multi-Container App

### Scenario: API Gateway Pattern

```bash
# 1. Create network
docker network create api-network

# 2. Start backend services
docker run -d \
  --name flask-service \
  --network api-network \
  ${REGISTRY_NAME}.azurecr.io/flask-echo:latest

docker run -d \
  --name fastapi-service \
  --network api-network \
  ${REGISTRY_NAME}.azurecr.io/fastapi-echo:latest

# 3. Create simple gateway config
cat > gateway.conf << 'EOF'
events {
    worker_connections 1024;
}

http {
    upstream flask_backend {
        server flask-service:8080;
    }
    
    upstream fastapi_backend {
        server fastapi-service:8080;
    }
    
    server {
        listen 80;
        
        location /flask/ {
            proxy_pass http://flask_backend/;
        }
        
        location /fastapi/ {
            proxy_pass http://fastapi_backend/;
        }
        
        location / {
            return 200 'API Gateway\nRoutes:\n/flask/ - Flask API\n/fastapi/ - FastAPI\n';
            add_header Content-Type text/plain;
        }
    }
}
EOF

# 4. Start gateway
docker run -d \
  --name gateway \
  --network api-network \
  -p 80:80 \
  -v $(pwd)/gateway.conf:/etc/nginx/nginx.conf:ro \
  nginx:alpine

# 5. Test routing
curl http://localhost/
curl http://localhost/flask/
curl http://localhost/fastapi/

# 6. View architecture
docker ps --format "table {{.Names}}\t{{.Networks}}\t{{.Ports}}"
```

## Troubleshooting Multi-Container Setup

### Containers Can't Communicate

```bash
# Verify network
docker network inspect echo-network

# Check if containers are on same network
docker inspect flask-echo --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}'
docker inspect fastapi-echo --format='{{range $k, $v := .NetworkSettings.Networks}}{{$k}}{{end}}'

# Test connectivity
docker exec flask-echo ping -c 3 fastapi-echo
```

### Port Conflicts

```bash
# Check what's using a port
lsof -i :8080  # macOS/Linux
netstat -ano | findstr :8080  # Windows

# Use different host port
docker run -d -p 8082:8080 ...
```

### Resource Exhaustion

```bash
# Check resource usage
docker stats

# Set resource limits
docker run -d \
  --memory="256m" \
  --cpus="0.5" \
  ...

# Clean up unused resources
docker system prune -a
```

## Best Practices

### 1. Use Custom Networks

```bash
# ✅ Good: Custom network
docker network create my-network
docker run --network my-network ...

# ❌ Bad: Default bridge
docker run ...  # Uses default bridge
```

### 2. Health Checks

```bash
# ✅ Good: Define health checks
HEALTHCHECK --interval=30s CMD curl -f http://localhost/health

# Monitor health
docker ps  # Shows health status
```

### 3. Resource Limits

```bash
# ✅ Good: Set limits
docker run --memory="512m" --cpus="1.0" ...

# ❌ Bad: No limits
docker run ...
```

### 4. Logging

```bash
# ✅ Good: Structured logging
docker run --log-driver json-file --log-opt max-size=10m ...

# View logs
docker logs -f container-name
```

### 5. Cleanup

```bash
# ✅ Good: Regular cleanup
docker system prune -a

# ✅ Good: Use --rm for temporary containers
docker run --rm ...
```

## Transitioning to Kubernetes

Multi-container patterns in Docker translate to Kubernetes:

| Docker | Kubernetes |
|--------|-----------|
| Container | Pod Container |
| docker-compose.yml | Deployment YAML |
| Custom Network | Service |
| Volume | PersistentVolumeClaim |
| Container Group | Pod |

### Example Kubernetes Deployment

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: echo-apps
spec:
  replicas: 2
  selector:
    matchLabels:
      app: echo
  template:
    metadata:
      labels:
        app: echo
    spec:
      containers:
      - name: flask-echo
        image: myregistry.azurecr.io/flask-echo:latest
        ports:
        - containerPort: 8080
      - name: fastapi-echo
        image: myregistry.azurecr.io/fastapi-echo:latest
        ports:
        - containerPort: 8080
```

## Next Steps

- Learn about [Kubernetes basics](../k8s/README.md)
- Deploy to [Azure Kubernetes Service](../aks/README.md)
- Explore [service mesh patterns](../k8s/service.md)

## Additional Resources

- [Docker Networking](https://docs.docker.com/network/)
- [Docker Compose](https://docs.docker.com/compose/)
- [Azure Container Instances](https://docs.microsoft.com/azure/container-instances/)
- [Microservices Patterns](https://microservices.io/patterns/)

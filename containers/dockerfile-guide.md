# Dockerfile Guide

## What is a Dockerfile?

A Dockerfile is a text file containing instructions for building a container image. Each instruction creates a layer in the final image. The Dockerfile defines everything needed to run your application: the base operating system, dependencies, application code, and runtime configuration.

## Dockerfile Anatomy

### Basic Structure

```dockerfile
# Comment
INSTRUCTION arguments
```

### Example Dockerfile

```dockerfile
# Base image
FROM python:3.11-slim

# Metadata
LABEL maintainer="your-email@example.com"
LABEL version="1.0"

# Set working directory
WORKDIR /app

# Copy files
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Define environment variable
ENV APP_ENV=production

# Run as non-root user
RUN useradd -m appuser
USER appuser

# Command to run
CMD ["python", "app.py"]
```

## Dockerfile Instructions

### FROM - Base Image

The `FROM` instruction specifies the base image for your container. This is always the first instruction (except for ARG before FROM).

```dockerfile
# Use official Python image
FROM python:3.11-slim

# Use specific version
FROM python:3.11.5-slim

# Use Alpine for smaller size
FROM python:3.11-alpine

# Multi-stage build
FROM python:3.11 AS builder
```

**Best Practices:**
- Use official images from trusted sources
- Specify exact versions for reproducibility
- Use slim or alpine variants for smaller images
- Consider distroless images for production

### WORKDIR - Set Working Directory

Sets the working directory for subsequent instructions.

```dockerfile
# Create and set working directory
WORKDIR /app

# All subsequent commands run in /app
COPY . .
RUN pip install -r requirements.txt
```

**Best Practices:**
- Use absolute paths
- Create directory structure early
- Avoid `cd` commands in RUN instructions

### COPY - Copy Files

Copies files from build context to container filesystem.

```dockerfile
# Copy single file
COPY app.py /app/

# Copy directory
COPY src/ /app/src/

# Copy multiple files
COPY app.py requirements.txt /app/

# Copy with wildcard
COPY *.py /app/

# Copy everything
COPY . .
```

**Best Practices:**
- Copy only what's needed
- Use `.dockerignore` to exclude files
- Copy dependency files first for better caching
- Be explicit about source and destination

### ADD - Add Files (Advanced COPY)

Similar to COPY but with additional features:

```dockerfile
# Extract tar archives automatically
ADD archive.tar.gz /app/

# Download from URL
ADD https://example.com/file.txt /app/

# Regular copy (prefer COPY for this)
ADD app.py /app/
```

**Best Practices:**
- Prefer `COPY` unless you need ADD's special features
- Use `RUN wget/curl` for URLs to maintain transparency
- Avoid using ADD for local files

### RUN - Execute Commands

Executes commands during image build.

```dockerfile
# Shell form (runs in shell)
RUN pip install flask

# Exec form (no shell processing)
RUN ["pip", "install", "flask"]

# Multiple commands
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Chain commands to reduce layers
RUN pip install --no-cache-dir \
    flask==2.3.0 \
    gunicorn==21.2.0 \
    && rm -rf /root/.cache
```

**Best Practices:**
- Combine related commands with `&&` to reduce layers
- Clean up in the same layer (apt caches, pip cache)
- Use `--no-cache-dir` with pip
- Sort multi-line arguments alphabetically for readability

### CMD - Default Command

Specifies the default command to run when container starts.

```dockerfile
# Exec form (preferred)
CMD ["python", "app.py"]

# Shell form
CMD python app.py

# Parameters to ENTRYPOINT
CMD ["--port", "8080"]
```

**Best Practices:**
- Use exec form to avoid shell processing
- Can be overridden at runtime
- Only one CMD per Dockerfile (last one wins)

### ENTRYPOINT - Configure Container Executable

Defines the executable that always runs when container starts.

```dockerfile
# Exec form
ENTRYPOINT ["python", "app.py"]

# With CMD for default arguments
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "8080"]

# Shell form
ENTRYPOINT python app.py
```

**ENTRYPOINT vs CMD:**

```dockerfile
# Using CMD only
CMD ["python", "app.py", "--port", "8080"]
# Runtime: docker run myapp
# Runs: python app.py --port 8080
# Override: docker run myapp python other.py

# Using ENTRYPOINT + CMD
ENTRYPOINT ["python", "app.py"]
CMD ["--port", "8080"]
# Runtime: docker run myapp
# Runs: python app.py --port 8080
# Override args: docker run myapp --port 9090
# Runs: python app.py --port 9090
```

### ENV - Environment Variables

Sets environment variables.

```dockerfile
# Single variable
ENV APP_ENV=production

# Multiple variables
ENV APP_ENV=production \
    APP_PORT=8080 \
    APP_DEBUG=false

# Use variables
ENV APP_HOME=/app
WORKDIR $APP_HOME
```

**Best Practices:**
- Use for configuration values
- Document all environment variables
- Set sensible defaults
- Override at runtime with `-e` or `--env-file`

### EXPOSE - Document Ports

Documents which ports the container listens on.

```dockerfile
# Single port
EXPOSE 8080

# Multiple ports
EXPOSE 8080 8443

# With protocol
EXPOSE 8080/tcp
EXPOSE 53/udp
```

**Best Practices:**
- Document all listening ports
- This is documentation only, doesn't publish ports
- Use `-p` flag at runtime to actually publish ports

### VOLUME - Mount Points

Declares mount points for external volumes.

```dockerfile
# Single volume
VOLUME /data

# Multiple volumes
VOLUME ["/data", "/logs"]
```

**Best Practices:**
- Use for persistent data
- Use for data shared between containers
- Data in volumes persists after container removal

### ARG - Build Arguments

Defines build-time variables.

```dockerfile
# Define argument
ARG PYTHON_VERSION=3.11

# Use in FROM
FROM python:${PYTHON_VERSION}-slim

# With default value
ARG APP_ENV=development

# Use in RUN
RUN echo "Building for ${APP_ENV}"
```

**Build with arguments:**
```bash
az acr build --build-arg PYTHON_VERSION=3.10 .
```

**Best Practices:**
- Use for values that change between builds
- Provide default values
- ARG values don't persist in final image (unlike ENV)

### USER - Set User

Switches to specified user for subsequent instructions.

```dockerfile
# Create user and group
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Switch to user
USER appuser

# All subsequent commands run as appuser
CMD ["python", "app.py"]
```

**Best Practices:**
- Never run containers as root in production
- Create user with minimal privileges
- Switch to user before CMD/ENTRYPOINT

### LABEL - Add Metadata

Adds metadata to images.

```dockerfile
LABEL maintainer="your-email@example.com"
LABEL version="1.0.0"
LABEL description="Python echo application"
LABEL org.opencontainers.image.source="https://github.com/user/repo"

# Multiple labels in one instruction
LABEL version="1.0.0" \
      description="Python echo app" \
      maintainer="you@example.com"
```

### HEALTHCHECK - Container Health

Defines how to check if container is healthy.

```dockerfile
# HTTP health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8080/health || exit 1

# Python script health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python health_check.py || exit 1

# Disable health check
HEALTHCHECK NONE
```

## Multi-Stage Builds

Multi-stage builds allow you to use multiple `FROM` statements to create optimized images.

### Why Multi-Stage Builds?

- **Smaller images**: Separate build tools from runtime
- **Security**: Fewer tools in production image
- **Cleaner**: No need to clean up build artifacts
- **Efficient**: Better layer caching

### Example: Python Application

```dockerfile
# Stage 1: Builder
FROM python:3.11 AS builder

WORKDIR /app

# Install dependencies in a virtual environment
COPY requirements.txt .
RUN python -m venv /opt/venv && \
    /opt/venv/bin/pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

# Copy virtual environment from builder
COPY --from=builder /opt/venv /opt/venv

# Set path to use venv
ENV PATH="/opt/venv/bin:$PATH"

WORKDIR /app

# Copy application code
COPY app.py .

# Run as non-root
RUN useradd -m appuser
USER appuser

CMD ["python", "app.py"]
```

### Example: Compile and Run

```dockerfile
# Build stage
FROM python:3.11 AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# Runtime stage
FROM python:3.11-slim

WORKDIR /app

# Install wheels from builder
COPY --from=builder /build/wheels /tmp/wheels
RUN pip install --no-cache-dir --no-index --find-links=/tmp/wheels /tmp/wheels/* && \
    rm -rf /tmp/wheels

COPY . .

USER 1000

CMD ["python", "app.py"]
```

## Best Practices

### 1. Layer Caching

Order instructions from least to most frequently changed:

```dockerfile
# ❌ Bad: Invalidates cache on any code change
FROM python:3.11-slim
COPY . .
RUN pip install -r requirements.txt

# ✅ Good: Dependencies cached separately
FROM python:3.11-slim
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
```

### 2. Minimize Layers

Combine related RUN commands:

```dockerfile
# ❌ Bad: Creates multiple layers
RUN apt-get update
RUN apt-get install -y curl
RUN apt-get clean

# ✅ Good: Single layer
RUN apt-get update && \
    apt-get install -y curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*
```

### 3. Use .dockerignore

Create a `.dockerignore` file:

```
# .dockerignore
.git
.gitignore
.venv
__pycache__
*.pyc
*.pyo
*.pyd
.Python
node_modules
.env
.DS_Store
README.md
.pytest_cache
.coverage
htmlcov
dist
build
*.egg-info
```

### 4. Security

```dockerfile
# ✅ Scan for vulnerabilities
# Run: az acr task credential add --name trivy

# ✅ Run as non-root user
RUN useradd -m -u 1000 appuser
USER appuser

# ✅ Use specific versions
FROM python:3.11.5-slim

# ✅ Don't embed secrets
# Use build args or runtime environment variables

# ✅ Keep base image updated
# Regularly rebuild with updated base images
```

### 5. Image Size Optimization

```dockerfile
# Use slim/alpine variants
FROM python:3.11-slim  # ~120MB vs ~900MB for full image

# Clean up in same layer
RUN pip install --no-cache-dir -r requirements.txt

# Remove unnecessary files
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Use multi-stage builds
FROM builder AS runtime
COPY --from=builder /app/dist /app/dist
```

## Common Patterns

### Python Application

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Security
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s \
  CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

EXPOSE 8080

CMD ["python", "app.py"]
```

### With Build Arguments

```dockerfile
ARG PYTHON_VERSION=3.11
FROM python:${PYTHON_VERSION}-slim

ARG APP_ENV=production
ENV APP_ENV=${APP_ENV}

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

USER 1000

CMD ["python", "app.py"]
```

## Testing Your Dockerfile

```bash
# Build locally (if Docker available)
docker build -t myapp:latest .

# Build with ACR
az acr build --registry myregistry --image myapp:latest .

# Build with arguments
az acr build --build-arg APP_ENV=staging --image myapp:staging .

# Check image size
docker images myapp:latest

# Inspect image layers
docker history myapp:latest

# Scan for vulnerabilities
az acr task credential add --name trivy
```

## Next Steps

- [Flask Echo App Example](examples/flask-echo/README.md)
- [FastAPI Echo App Example](examples/fastapi-echo/README.md)
- [Running Containers Locally](running-containers.md)
- [Azure Container Registry Guide](acr-guide.md)

## Additional Resources

- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [Best Practices](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [Multi-stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Security Scanning](https://docs.docker.com/scout/)

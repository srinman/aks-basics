# Build stage - create wheel packages
FROM python:3.11-slim AS builder

LABEL stage=builder

WORKDIR /build

# Copy requirements file
COPY requirements.txt .

# Create wheel packages (pre-compiled Python packages)
# This is faster to install and doesn't require build tools in final image
RUN pip wheel --no-cache-dir --wheel-dir /build/wheels -r requirements.txt

# Runtime stage - minimal final image
FROM python:3.11-slim

# Set metadata
LABEL maintainer="learner@example.com"
LABEL description="FastAPI Echo API - Multi-stage container demo"
LABEL version="1.0.0"

WORKDIR /app

# Copy wheel packages from builder stage
COPY --from=builder /build/wheels /tmp/wheels

# Install from wheels (no compilation needed)
# --no-index: Don't use PyPI
# --find-links: Look for packages in /tmp/wheels
RUN pip install --no-cache-dir --no-index --find-links=/tmp/wheels /tmp/wheels/* && \
    rm -rf /tmp/wheels

# Copy application code
COPY app.py .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Document the port
EXPOSE 8080

# Set default environment variables
ENV PORT=8080 \
    APP_VERSION=1.0.0

# Health check
# Note: Longer start-period for async app initialization
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "app.py"]

# Use Python slim image for smaller size
FROM python:3.11-slim

# Set metadata
LABEL maintainer="learner@example.com"
LABEL description="Flask Echo API - Container basics demo"
LABEL version="1.0.0"

# Set working directory
WORKDIR /app

# Copy dependency file first for better layer caching
COPY requirements.txt .

# Install dependencies
# --no-cache-dir: Don't cache pip packages (reduces image size)
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY app.py .

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Document the port the app listens on
EXPOSE 8080

# Set default environment variables
ENV PORT=8080 \
    APP_VERSION=1.0.0

# Health check for container orchestration
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "app.py"]

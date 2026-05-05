# Multi-stage build for Hybrid Thesis Recommender
FROM python:3.10-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Final stage
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python packages from builder
COPY --from=builder /root/.local /root/.local

# Make sure scripts in .local are usable
ENV PATH=/root/.local/bin:$PATH

# Copy application code
COPY app/ ./app/
COPY static/ ./static/
COPY config.yaml .
COPY database/ ./database/

# Create data directory for runtime files
RUN mkdir -p data

# Expose port
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.main
ENV PYTHONUNBUFFERED=1
# Skip model download during build - will download on first run
ENV TRANSFORMERS_OFFLINE=0

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:5000/', timeout=5)"

# Run the application
CMD ["python", "-m", "app.main", "serve", "--host", "0.0.0.0", "--port", "5000"]

# Multi-stage build for Analytics Microservice v3
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install system dependencies for matplotlib
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libpng-dev \
    libjpeg-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim

# Install runtime dependencies for matplotlib
RUN apt-get update && apt-get install -y \
    libpng16-16 \
    libjpeg62-turbo \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Copy Python dependencies from builder
COPY --from=builder /root/.local /root/.local

# Set working directory
WORKDIR /app

# Copy application code
COPY . .

# Ensure scripts are on PATH
ENV PATH=/root/.local/bin:$PATH

# Set Python to run in unbuffered mode
ENV PYTHONUNBUFFERED=1

# Set matplotlib backend
ENV MPLBACKEND=Agg

# Expose WebSocket port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8080/health')" || exit 1

# Run the application
CMD ["python", "main.py"]
<<<<<<< HEAD
# ===== Stage 1: Builder =====
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy and install Python dependencies
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# ===== Stage 2: Runtime =====
FROM python:3.11-slim AS runtime

LABEL maintainer="WeatherOps Team"
LABEL version="1.0.0"
LABEL description="WeatherOps - Dashboard Météo avec Alertes"

# Create non-root user for security
RUN groupadd -r weatherops && useradd -r -g weatherops -s /bin/false weatherops

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /root/.local /home/weatherops/.local

# Create data directory with proper permissions
RUN mkdir -p /app/data && chown -R weatherops:weatherops /app

# Copy application code
COPY --chown=weatherops:weatherops . .

# Set Python path to include user packages
ENV PATH=/home/weatherops/.local/bin:$PATH
ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Switch to non-root user
USER weatherops

# Start application
CMD ["python", "-m", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]
=======
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DB_PATH=/app/data/weatherops.db

RUN mkdir -p /app/data

EXPOSE 8000

HEALTHCHECK --interval=20s --timeout=10s --start-period=40s --retries=5 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5)" || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
>>>>>>> 04545d62421a0742ac53ed111b5072899c582a02

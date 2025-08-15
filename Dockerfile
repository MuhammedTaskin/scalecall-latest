# TEKNOFEST 2025 - Local Dockerized System
FROM python:3.10-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Environment variables for local PostgreSQL
ENV DB_HOST=postgres
ENV DB_PORT=5432
ENV DB_NAME=teknofest_telco
ENV DB_USER=postgres
ENV DB_PASSWORD=teknofest2025secret

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python3 -c "import psycopg2; psycopg2.connect(host='$DB_HOST', port=$DB_PORT, database='$DB_NAME', user='$DB_USER', password='$DB_PASSWORD')" || exit 1

# Default command
CMD ["python3", "LOCAL_TELCO_TOOLS.py"]
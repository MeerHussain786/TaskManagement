# ── MULTI-STAGE DOCKER BUILD ───────────────────────────────────────────────

# ── Stage 1: Build Dependencies
FROM python:3.13-slim AS builder

WORKDIR /build

# Install compilation tools needed for libraries like bcrypt
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

# Install dependencies to a local folder to avoid polluting standard path
RUN pip install --no-cache-dir --user -r requirements.txt


# ── Stage 2: Production Runtime
FROM python:3.13-slim AS runner

WORKDIR /app

# Install runtime dependencies (e.g. libpq, curl for healthchecks)
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy installed python dependencies from builder stage
COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

# Copy application source code
COPY main.py .
COPY alembic.ini .
COPY alembic/ ./alembic/
COPY app/ ./app/

# Configure production environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    ENVIRONMENT=production \
    PORT=8000

# Create a non-root group and user for security compliance
RUN groupadd -g 10001 appgroup && \
    useradd -u 10001 -g appgroup -s /bin/sh -m appuser && \
    chown -R appuser:appgroup /app

USER appuser

# Expose standard container port
EXPOSE 8000

# Endpoint health validation check
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/api/v1/health/live || exit 1

# Launch application via uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "2"]

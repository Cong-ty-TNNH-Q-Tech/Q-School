# ══════════════════════════════════════════════════════════
# Q-School AI — Backend Dockerfile (Multi-stage)
# Stages: base → development → production
# ══════════════════════════════════════════════════════════

# ─── Base stage: shared deps ──────────────────────────────
FROM python:3.12-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# System deps (build tools for psycopg2, asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ─── Development stage: hot-reload, full deps ─────────────
FROM base AS development

# Dev-only dependencies (linting, testing)
RUN pip install --no-cache-dir \
    pytest pytest-cov pytest-asyncio \
    flake8 black mypy \
    httpx

# Copy source (overridden by volume mount in docker-compose)
COPY . .

EXPOSE 8000

# Default command (overridden in docker-compose)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]

# ─── Production stage: minimal, secure ────────────────────
FROM base AS production

# Copy only application code (no dev deps)
COPY . .

# Non-root user for security
RUN addgroup --system appgroup && \
    adduser --system --ingroup appgroup appuser && \
    chown -R appuser:appgroup /app
USER appuser

EXPOSE 8000

# Production: gunicorn + uvicorn workers
CMD ["gunicorn", "main:app", \
     "--worker-class", "uvicorn.workers.UvicornWorker", \
     "--workers", "4", \
     "--bind", "0.0.0.0:8000", \
     "--timeout", "120", \
     "--access-logfile", "-"]

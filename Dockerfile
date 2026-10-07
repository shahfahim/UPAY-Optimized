# Stage 1: Build the React frontend
FROM node:22-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci --prefer-offline --no-audit
COPY web/ ./
RUN npm run build

# Stage 2: Build the production FastAPI backend
FROM python:3.11-slim
# This image is the public hackathon demo: seeded users, time travel and reset are on.
# Set HISHAB_DEMO_MODE=0 (and HISHAB_CORS_ORIGINS) for any non-demo deployment.
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HISHAB_WEB_DIST=/app/web/dist \
    HISHAB_DB_PATH=/tmp/hishab.db \
    HISHAB_DEMO_MODE=1

# System dependencies
# LightGBM needs the OpenMP runtime
RUN apt-get update && \
    apt-get install -y --no-install-recommends libgomp1 && \
    rm -rf /var/lib/apt/lists/* && \
    useradd -m -u 1000 user

WORKDIR /app

# Install Python dependencies
COPY backend/pyproject.toml backend/requirements.lock backend/
RUN pip install --no-cache-dir -r backend/requirements.lock && \
    pip install --no-cache-dir uvicorn[standard]

# Copy application source
COPY backend/hishab backend/hishab
RUN pip install --no-cache-dir --no-deps -e ./backend

COPY backend/artifacts backend/artifacts
COPY backend/data/serving backend/data/serving

# Copy frontend static assets
COPY --from=web /web/dist /app/web/dist

USER user
EXPOSE 8000

# Run Uvicorn in production mode (factory pattern)
CMD ["sh", "-c", "uvicorn hishab.api.main:create_app --factory --host 0.0.0.0 --port ${PORT:-8000}"]

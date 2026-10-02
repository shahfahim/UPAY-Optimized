# Hishab — one image: React build + FastAPI API (Hugging Face Spaces, Docker SDK, port 7860)

FROM node:22-slim AS web
WORKDIR /web
COPY web/package.json web/package-lock.json ./
RUN npm ci
COPY web/ ./
RUN npm run build

FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    HISHAB_WEB_DIST=/app/web/dist \
    HISHAB_DB_PATH=/tmp/hishab.db
# LightGBM needs the OpenMP runtime
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*
RUN useradd -m -u 1000 user
WORKDIR /app
COPY backend/pyproject.toml backend/requirements.lock backend/
RUN pip install --no-cache-dir -r backend/requirements.lock
COPY backend/hishab backend/hishab
RUN pip install --no-cache-dir --no-deps -e ./backend
COPY backend/artifacts backend/artifacts
COPY backend/data/serving backend/data/serving
COPY --from=web /web/dist web/dist
USER user
EXPOSE 7860
CMD ["uvicorn", "hishab.api.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "7860"]

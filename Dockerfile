# Multi-stage build for FastAPI + Next.js
FROM node:18-alpine AS frontend-builder

WORKDIR /app/dashboard
COPY dashboard/package*.json ./
RUN npm ci --only=production

COPY dashboard/ ./
RUN npm run build

FROM python:3.12-slim

# Install Node.js for running Next.js
RUN apt-get update && apt-get install -y \
    curl \
    && curl -fsSL https://deb.nodesource.com/setup_18.x | bash - \
    && apt-get install -y nodejs \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app
COPY --from=frontend-builder /app/dashboard ./dashboard

COPY start-backend.sh start-frontend.sh ./
RUN chmod +x start-backend.sh start-frontend.sh

EXPOSE 8000

# Use SERVICE_TYPE env var to determine which service to run
CMD ["sh", "-c", "if [ \"$SERVICE_TYPE\" = \"frontend\" ]; then ./start-frontend.sh; else ./start-backend.sh; fi"]

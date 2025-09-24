FROM python:3.12-slim

WORKDIR /app

ARG DATABASE_URL
ARG API_KEY
ARG FMCSA_WEBKEY

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY app ./app

CMD ["sh", "-c", "python -m uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8080}"]

#!/bin/bash

echo "Starting FastAPI Backend Service"
cd /app
python -m uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT:-8000}

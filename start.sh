#!/bin/bash

# Start the FastAPI backend in the background on port 8000
cd /app
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &

# Start the Next.js frontend on Railway's public port
cd /app/dashboard
npm start -- --port ${PORT:-8080} --hostname 0.0.0.0

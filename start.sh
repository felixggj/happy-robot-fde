#!/bin/bash

# Start the FastAPI backend in the background on port 8000
cd /app
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &

# Wait a moment for the API to start
sleep 2

# Start the Next.js frontend on Railway's assigned port
cd /app/dashboard
echo "Starting Next.js on port ${PORT:-8080}"
npm start -- --port ${PORT:-8080} --hostname 0.0.0.0

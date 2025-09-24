#!/bin/bash

# Start the FastAPI backend in the background
cd /app
python -m uvicorn app.api.main:app --host 0.0.0.0 --port 8000 &

# Start the Next.js frontend
cd /app/dashboard
npm start -- --port $PORT --hostname 0.0.0.0

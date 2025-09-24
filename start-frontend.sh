#!/bin/bash

echo "Starting Next.js Frontend Service"
echo "API URL: $NEXT_PUBLIC_API_URL"
cd /app/dashboard
npm start -- --port ${PORT:-3000} --hostname 0.0.0.0

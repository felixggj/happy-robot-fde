FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["sh", "-c", "PORT=${PORT:-8080} node .next/standalone/server.js"]

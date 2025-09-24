FROM node:18-alpine

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["sh", "-c", "npm start -- --port ${PORT:-8080} --hostname 0.0.0.0"]

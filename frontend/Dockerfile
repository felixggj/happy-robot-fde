FROM node:18-alpine

WORKDIR /app

ARG NEXT_PUBLIC_API_URL
ARG NEXT_PUBLIC_API_KEY

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

CMD ["sh", "-c", "npm start -- --port ${PORT:-8080} --hostname 0.0.0.0"]

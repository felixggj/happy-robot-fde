# HappyRobot Automated Carrier Sales System

Freight brokerage automation platform with AI phone integration, pricing negotiation, and carrier verification.

## Overview

- **Backend**: FastAPI REST API with PostgreSQL database
- **Frontend**: Next.js dashboard with real-time analytics
- **Integration**: HappyRobot AI phone automation
- **Features**: FMCSA verification, dynamic pricing, call tracking

## Tech Stack

**Backend:** FastAPI 0.104.1, SQLAlchemy 2.0.23, PostgreSQL  
**Frontend:** Next.js 14.0.3, React 18, TypeScript, Tailwind CSS  
**Deployment:** Docker containers on Railway

## Project Structure

```
HappyRobot/
├── backend/
│   ├── app/api/
│   │   ├── main.py              # FastAPI application
│   │   ├── models.py            # Pydantic models
│   │   ├── offers.py            # Pricing logic
│   │   ├── fmcsa.py             # Carrier verification
│   │   └── db_models.py         # Database models
│   └── requirements.txt
├── frontend/
│   ├── app/                     # Next.js pages
│   ├── components/              # React components
│   ├── lib/api.ts              # API client
│   └── package.json
```

## Local Development

Prerequisites: Python 3.9+, Node.js 18+

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export API_KEY=your-api-key
python -m uvicorn app.api.main:app --reload --port 8000
```

### Frontend

```bash
cd frontend
npm install
export NEXT_PUBLIC_API_URL=http://localhost:8000
export NEXT_PUBLIC_API_KEY=your-api-key
npm run dev
```

## Railway Deployment

### Backend

1. Create Railway project, link GitHub repo
2. Set root directory to `/backend`
3. Add environment variables:
   ```
   API_KEY=your-production-api-key
   FMCSA_WEBKEY=your-fmcsa-api-key
   ```
4. Deploy with `railway up`

### Frontend

1. Create new Railway project
2. Set root directory to `/frontend`
3. Add environment variables:
   ```
   NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
   NEXT_PUBLIC_API_KEY=your-api-key
   ```
4. Deploy with `railway up`

## API Endpoints

Base URL: `https://backend-fde-production.up.railway.app`  
Authentication: `x-api-key` header required

| Method | Endpoint                     | Description                |
| ------ | ---------------------------- | -------------------------- |
| `GET`  | `/api/health`                | Health check               |
| `POST` | `/api/verify`                | FMCSA carrier verification |
| `GET`  | `/api/loads/search`          | Search available loads     |
| `POST` | `/api/offers/evaluate`       | Evaluate carrier offers    |
| `POST` | `/api/events/call-completed` | Record call session data   |
| `GET`  | `/api/call-sessions`         | Get recent call history    |
| `GET`  | `/api/metrics`               | Get analytics and KPIs     |

## Environment Variables

**Backend:**

```bash
API_KEY=your-secure-api-key
FMCSA_WEBKEY=your-fmcsa-api-key
DATABASE_URL=postgresql://user:pass@host:port/db
```

**Frontend:**

```bash
NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
NEXT_PUBLIC_API_KEY=your-api-key
```

## Live Deployments

- **Backend API**: https://backend-fde-production.up.railway.app
- **Frontend Dashboard**: https://frontend-fde-production.up.railway.app
- **API Documentation**: https://backend-fde-production.up.railway.app/docs

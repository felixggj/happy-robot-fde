# HappyRobot Carrier Sales API

Backend API for automated freight broker carrier sales negotiations.

## Features

- **Carrier Verification**: FMCSA API integration for carrier eligibility checking
- **Load Search**: Intelligent load matching with scoring
- **Price Negotiation**: Automated offer evaluation with floor pricing
- **Call Analytics**: Metrics and reporting for call outcomes
- **HappyRobot Integration**: Webhook endpoints for workflow automation

## Quick Start

### Local Development

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export API_KEY=your-api-key

# Run application
python -m uvicorn app.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker

```bash
# Build and run
docker build -t carrier-sales-api .
docker run -p 8000:8000 -v $(pwd)/app:/app/app -e API_KEY=your-api-key carrier-sales-api
```

### Railway Deployment

1. Connect GitHub repository to Railway
2. Set environment variables:
   - `API_KEY`: Your API key for authentication
   - `FMCSA_WEBKEY`: FMCSA API key (for production)
3. Deploy

## API Endpoints

All endpoints require `x-api-key` header authentication.

### Health Check

- `GET /api/health` → `{"status": "ok"}`

### Carrier Verification

- `POST /api/verify` → Verify carrier eligibility

### Load Search

- `GET /api/loads/search` → Search available loads with filtering

### Offer Evaluation

- `POST /api/offers/evaluate` → Evaluate carrier offers

### Call Completion

- `POST /api/events/call-completed` → Record call data

### Metrics

- `GET /api/metrics` → Get analytics and reporting

## Environment Variables

- `API_KEY`: Required API key for authentication
- `FMCSA_WEBKEY`: FMCSA API key for carrier verification
- `DATABASE_URL`: Database connection string (defaults to SQLite)

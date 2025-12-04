# Events API Deployment Guide

## Prerequisites
- AWS CLI configured with appropriate credentials
- Python 3.11+
- Node.js and npm (for CDK)
- AWS CDK CLI installed (`npm install -g aws-cdk`)

## Deployment Steps

### 1. Install Backend Dependencies
```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 2. Install Infrastructure Dependencies
```bash
cd infrastructure
pip install -r requirements.txt
cd ..
```

### 3. Bootstrap CDK (first time only)
```bash
cd infrastructure
cdk bootstrap
```

### 4. Deploy the Stack
```bash
cdk deploy
```

The deployment will output the API Gateway URL.

## API Endpoints

- `GET /events` - List all events
- `GET /events?status=active` - Filter events by status
- `POST /events` - Create a new event
- `GET /events/{eventId}` - Get a specific event
- `PUT /events/{eventId}` - Update an event
- `DELETE /events/{eventId}` - Delete an event

## Testing

Example POST request:
```bash
curl -X POST https://YOUR-API-URL/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "eventId": "api-test-event-456",
    "title": "API Gateway Test Event",
    "description": "Testing API Gateway integration",
    "date": "2024-12-15",
    "location": "API Test Location",
    "capacity": 200,
    "organizer": "API Test Organizer",
    "status": "active"
  }'
```

## Cleanup
```bash
cd infrastructure
cdk destroy
```

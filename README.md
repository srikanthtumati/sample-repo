# Events API

A serverless REST API for managing events, built with FastAPI and deployed on AWS using Lambda, API Gateway, and DynamoDB.

## Features

- Full CRUD operations for events
- DynamoDB for data persistence
- CORS enabled for web access
- Input validation with Pydantic
- Comprehensive error handling
- Serverless architecture (API Gateway + Lambda)

## Event Properties

- `eventId`: Unique identifier (auto-generated or provided)
- `title`: Event title (1-200 characters)
- `description`: Event description (1-2000 characters)
- `date`: Event date (ISO format: YYYY-MM-DD)
- `location`: Event location (1-500 characters)
- `capacity`: Maximum attendees (must be > 0)
- `organizer`: Event organizer name (1-200 characters)
- `status`: Event status (active, scheduled, ongoing, completed, cancelled)

## Setup

### Prerequisites

- Python 3.11+
- Node.js and npm
- AWS CLI configured with credentials
- AWS CDK CLI: `npm install -g aws-cdk`

### Installation

1. Install backend dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Install infrastructure dependencies:
```bash
pip install -r infrastructure/requirements.txt
```

### Deployment

1. Bootstrap CDK (first time only):
```bash
cd infrastructure
cdk bootstrap
```

2. Deploy the stack:
```bash
cdk deploy
```

3. Note the API URL from the output (e.g., `https://xxxxx.execute-api.us-west-2.amazonaws.com/prod/`)

## API Endpoints

### List Events
```bash
GET /events
GET /events?status=active
```

### Create Event
```bash
POST /events
Content-Type: application/json

{
  "eventId": "optional-custom-id",
  "title": "My Event",
  "description": "Event description",
  "date": "2024-12-15",
  "location": "Event Location",
  "capacity": 100,
  "organizer": "Organizer Name",
  "status": "active"
}
```

### Get Event
```bash
GET /events/{eventId}
```

### Update Event
```bash
PUT /events/{eventId}
Content-Type: application/json

{
  "title": "Updated Title",
  "capacity": 150
}
```

### Delete Event
```bash
DELETE /events/{eventId}
```

## Usage Examples

Replace `YOUR-API-URL` with your actual API Gateway URL.

### Create an event
```bash
curl -X POST https://YOUR-API-URL/prod/events \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Tech Conference 2024",
    "description": "Annual technology conference",
    "date": "2024-12-15",
    "location": "San Francisco, CA",
    "capacity": 500,
    "organizer": "Tech Corp",
    "status": "active"
  }'
```

### List all events
```bash
curl https://YOUR-API-URL/prod/events
```

### Filter events by status
```bash
curl https://YOUR-API-URL/prod/events?status=active
```

### Get a specific event
```bash
curl https://YOUR-API-URL/prod/events/EVENT-ID
```

### Update an event
```bash
curl -X PUT https://YOUR-API-URL/prod/events/EVENT-ID \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Event Title",
    "capacity": 600
  }'
```

### Delete an event
```bash
curl -X DELETE https://YOUR-API-URL/prod/events/EVENT-ID
```

## Architecture

- **API Gateway**: REST API endpoint with CORS support
- **Lambda**: Python 3.11 runtime running FastAPI with Mangum adapter
- **DynamoDB**: NoSQL database with pay-per-request billing
- **CDK**: Infrastructure as Code for deployment

## Development

### Local Testing

Install dependencies and run locally:
```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

Access the API at `http://localhost:8000` and interactive docs at `http://localhost:8000/docs`

### View Logs

```bash
aws logs tail /aws/lambda/ApiStack-EventsApiLambda --follow
```

## Cleanup

To remove all deployed resources:
```bash
cd infrastructure
cdk destroy
```

## License

MIT

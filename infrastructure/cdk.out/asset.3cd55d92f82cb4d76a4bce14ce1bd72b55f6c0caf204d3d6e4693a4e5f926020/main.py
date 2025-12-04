import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field, validator
import boto3
from boto3.dynamodb.conditions import Key
from botocore.exceptions import ClientError

app = FastAPI(title="Events API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# DynamoDB setup
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('EVENTS_TABLE_NAME', 'Events')
table = dynamodb.Table(table_name)


class Event(BaseModel):
    eventId: Optional[str] = None
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=1, max_length=2000)
    date: str = Field(..., description="ISO format date (YYYY-MM-DD)")
    location: str = Field(..., min_length=1, max_length=500)
    capacity: int = Field(..., gt=0, description="Must be greater than 0")
    organizer: str = Field(..., min_length=1, max_length=200)
    status: str = Field(..., description="Event status")

    @validator('status')
    def validate_status(cls, v):
        allowed_statuses = ['active', 'scheduled', 'ongoing', 'completed', 'cancelled']
        if v not in allowed_statuses:
            raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('date')
    def validate_date(cls, v):
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError('Date must be in ISO format (YYYY-MM-DD)')
        return v


class EventUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, min_length=1, max_length=2000)
    date: Optional[str] = None
    location: Optional[str] = Field(None, min_length=1, max_length=500)
    capacity: Optional[int] = Field(None, gt=0)
    organizer: Optional[str] = Field(None, min_length=1, max_length=200)
    status: Optional[str] = None

    @validator('status')
    def validate_status(cls, v):
        if v is not None:
            allowed_statuses = ['active', 'scheduled', 'ongoing', 'completed', 'cancelled']
            if v not in allowed_statuses:
                raise ValueError(f'Status must be one of: {", ".join(allowed_statuses)}')
        return v

    @validator('date')
    def validate_date(cls, v):
        if v is not None:
            try:
                datetime.fromisoformat(v)
            except ValueError:
                raise ValueError('Date must be in ISO format (YYYY-MM-DD)')
        return v


@app.get("/")
def read_root():
    return {"message": "Events API", "version": "1.0.0"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/events", status_code=status.HTTP_201_CREATED)
async def create_event(event: Event):
    """Create a new event"""
    try:
        # Use provided eventId or generate new one
        event_id = event.eventId if event.eventId else str(uuid.uuid4())
        event_data = event.dict()
        event_data['eventId'] = event_id
        event_data['createdAt'] = datetime.utcnow().isoformat()
        event_data['updatedAt'] = datetime.utcnow().isoformat()
        
        table.put_item(Item=event_data)
        return event_data
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create event: {str(e)}"
        )


@app.get("/events")
async def list_events(status: Optional[str] = None):
    """List all events, optionally filtered by status"""
    try:
        if status:
            # Filter by status using scan with filter expression
            response = table.scan(
                FilterExpression=Key('status').eq(status)
            )
        else:
            response = table.scan()
        
        events = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            if status:
                response = table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    FilterExpression=Key('status').eq(status)
                )
            else:
                response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            events.extend(response.get('Items', []))
        
        return {"events": events, "count": len(events)}
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list events: {str(e)}"
        )


@app.get("/events/{event_id}")
async def get_event(event_id: str):
    """Get a specific event by ID"""
    try:
        response = table.get_item(Key={'eventId': event_id})
        
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        return response['Item']
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get event: {str(e)}"
        )


@app.put("/events/{event_id}")
async def update_event(event_id: str, event_update: EventUpdate):
    """Update an existing event"""
    try:
        # Check if event exists
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        # Build update expression
        update_data = event_update.dict(exclude_unset=True)
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        update_data['updatedAt'] = datetime.utcnow().isoformat()
        
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        response = table.update_item(
            Key={'eventId': event_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        return response['Attributes']
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update event: {str(e)}"
        )


@app.delete("/events/{event_id}")
async def delete_event(event_id: str):
    """Delete an event"""
    try:
        # Check if event exists
        response = table.get_item(Key={'eventId': event_id})
        if 'Item' not in response:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Event with ID {event_id} not found"
            )
        
        table.delete_item(Key={'eventId': event_id})
        return {"message": "Event deleted successfully"}
    except ClientError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete event: {str(e)}"
        )


# Lambda handler
from mangum import Mangum
handler = Mangum(app)

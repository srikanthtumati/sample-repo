from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from events.handlers import router as events_router
from users.handlers import router as users_router
from registrations.handlers import router as registrations_router

app = FastAPI(title="Events API", version="1.0.0")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(events_router)
app.include_router(users_router)
app.include_router(registrations_router)


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
                FilterExpression=Attr('status').eq(status)
            )
        else:
            response = table.scan()
        
        events = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            if status:
                response = table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    FilterExpression=Attr('status').eq(status)
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


# User endpoints
@app.post("/users", status_code=status.HTTP_201_CREATED)
async def create_user(user: User):
    """Create a new user"""
    try:
        created_user = user_service.create_user(user.userId, user.name)
        return {
            "userId": created_user.user_id,
            "name": created_user.name
        }
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@app.get("/users/{user_id}")
async def get_user(user_id: str):
    """Get a user by ID"""
    user = user_service.get_user(user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"User {user_id} not found"
        )
    return {
        "userId": user.user_id,
        "name": user.name
    }


# Registration endpoints
@app.post("/events/{event_id}/registrations", status_code=status.HTTP_201_CREATED)
async def register_for_event(event_id: str, request: RegistrationRequest):
    """Register a user for an event"""
    try:
        registration = registration_service.register_user(request.userId, event_id)
        result = {
            "registrationId": registration.registration_id,
            "userId": registration.user_id,
            "eventId": registration.event_id,
            "status": registration.status.value
        }
        if registration.waitlist_position is not None:
            result["waitlistPosition"] = registration.waitlist_position
        return result
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )
    except DuplicateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
    except CapacityError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


@app.get("/events/{event_id}/registrations")
async def get_event_registrations(event_id: str):
    """Get all registrations for an event"""
    registrations = registration_service.get_event_registrations(event_id)
    return {
        "registrations": registrations,
        "count": len(registrations)
    }


@app.delete("/events/{event_id}/registrations/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unregister_from_event(event_id: str, user_id: str):
    """Unregister a user from an event"""
    try:
        registration_service.unregister_user(user_id, event_id)
        return None
    except NotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )


@app.get("/users/{user_id}/registrations")
async def get_user_registrations(user_id: str):
    """Get all active registrations for a user"""
    events = registration_service.get_user_registrations(user_id)
    return {
        "events": events,
        "count": len(events)
    }


# Lambda handler
from mangum import Mangum
handler = Mangum(app)

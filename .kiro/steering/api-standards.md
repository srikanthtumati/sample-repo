---
inclusion: fileMatch
fileMatchPattern: '**/*api*.py|**/*main*.py|**/*routes*.py|**/*endpoints*.py'
---

# API Standards and Conventions

This document defines the REST API standards and conventions for this project.

## HTTP Methods

Use HTTP methods according to their semantic meaning:

- **GET**: Retrieve resources (read-only, idempotent, cacheable)
- **POST**: Create new resources (non-idempotent)
- **PUT**: Update entire resources (idempotent)
- **PATCH**: Partial update of resources (idempotent)
- **DELETE**: Remove resources (idempotent)

## HTTP Status Codes

Use appropriate status codes for all responses:

### Success Codes (2xx)
- **200 OK**: Successful GET, PUT, PATCH, or DELETE
- **201 Created**: Successful POST that creates a resource
- **204 No Content**: Successful request with no response body (typically DELETE)

### Client Error Codes (4xx)
- **400 Bad Request**: Invalid request format or validation error
- **401 Unauthorized**: Authentication required or failed
- **403 Forbidden**: Authenticated but not authorized
- **404 Not Found**: Resource does not exist
- **409 Conflict**: Request conflicts with current state (e.g., duplicate)
- **422 Unprocessable Entity**: Validation error with detailed field errors

### Server Error Codes (5xx)
- **500 Internal Server Error**: Unexpected server error
- **503 Service Unavailable**: Service temporarily unavailable

## JSON Response Format Standards

### Success Response Format

All successful responses should follow this structure:

```json
{
  "data": { ... },
  "metadata": {
    "timestamp": "2024-12-03T10:00:00Z",
    "version": "1.0.0"
  }
}
```

For list endpoints:
```json
{
  "data": [ ... ],
  "count": 10,
  "metadata": {
    "timestamp": "2024-12-03T10:00:00Z",
    "version": "1.0.0"
  }
}
```

### Error Response Format

All error responses must follow this structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "field": "Additional context or field-specific errors"
    }
  },
  "metadata": {
    "timestamp": "2024-12-03T10:00:00Z",
    "requestId": "unique-request-id"
  }
}
```

### Validation Error Format (422)

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Request validation failed",
    "details": [
      {
        "field": "email",
        "message": "Invalid email format",
        "value": "invalid-email"
      }
    ]
  }
}
```

## Naming Conventions

### Endpoints
- Use plural nouns for collections: `/events`, `/users`
- Use kebab-case for multi-word resources: `/event-registrations`
- Use path parameters for specific resources: `/events/{eventId}`
- Use query parameters for filtering: `/events?status=active`

### JSON Fields
- Use camelCase for field names: `eventId`, `createdAt`
- Use ISO 8601 format for dates: `2024-12-03T10:00:00Z`
- Use consistent field names across endpoints

## CORS Configuration

Always configure CORS appropriately:
- Specify allowed origins (avoid `*` in production)
- Include necessary headers: `Content-Type`, `Authorization`
- Support preflight requests (OPTIONS method)

## Error Handling

### Always Handle These Cases
1. Invalid input validation
2. Resource not found
3. Database/external service errors
4. Authentication/authorization failures
5. Rate limiting

### Error Handling Pattern

```python
try:
    # Operation
    result = perform_operation()
    return {"data": result}
except ValidationError as e:
    raise HTTPException(
        status_code=422,
        detail={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "details": e.errors()
            }
        }
    )
except NotFoundError as e:
    raise HTTPException(
        status_code=404,
        detail={
            "error": {
                "code": "NOT_FOUND",
                "message": str(e)
            }
        }
    )
except Exception as e:
    # Log the error
    logger.error(f"Unexpected error: {str(e)}")
    raise HTTPException(
        status_code=500,
        detail={
            "error": {
                "code": "INTERNAL_ERROR",
                "message": "An unexpected error occurred"
            }
        }
    )
```

## Input Validation

- Validate all inputs using Pydantic models or similar
- Provide clear, actionable error messages
- Validate data types, formats, and constraints
- Sanitize inputs to prevent injection attacks

## Pagination

For list endpoints returning large datasets:

```
GET /events?page=1&limit=20
```

Response:
```json
{
  "data": [ ... ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "totalPages": 5
  }
}
```

## Filtering and Sorting

- Use query parameters for filtering: `?status=active&category=tech`
- Use `sort` parameter for sorting: `?sort=createdAt:desc`
- Support multiple sort fields: `?sort=status:asc,date:desc`

## Versioning

- Include API version in URL: `/v1/events`
- Or use Accept header: `Accept: application/vnd.api.v1+json`
- Maintain backward compatibility when possible

## Security Best Practices

1. **Authentication**: Use JWT tokens or API keys
2. **Authorization**: Implement role-based access control
3. **Rate Limiting**: Prevent abuse with rate limits
4. **Input Sanitization**: Validate and sanitize all inputs
5. **HTTPS Only**: Never expose APIs over HTTP in production
6. **Secrets Management**: Never hardcode credentials

## Documentation

- Document all endpoints with OpenAPI/Swagger
- Include request/response examples
- Document error responses
- Keep documentation in sync with implementation

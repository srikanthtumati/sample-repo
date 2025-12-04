"""Event repository for data access"""
from typing import Optional, List, Dict, Any
from boto3.dynamodb.conditions import Attr
from botocore.exceptions import ClientError


class EventRepository:
    """Repository for event data access operations"""
    
    def __init__(self, table):
        """
        Initialize repository with DynamoDB table
        
        Args:
            table: boto3 DynamoDB table resource
        """
        self.table = table
    
    def create(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new event in DynamoDB
        
        Args:
            event_data: Dictionary containing event data
            
        Returns:
            The created event data
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        self.table.put_item(Item=event_data)
        return event_data
    
    def find_by_id(self, event_id: str) -> Optional[Dict[str, Any]]:
        """
        Find an event by ID
        
        Args:
            event_id: The event ID to search for
            
        Returns:
            Event data if found, None otherwise
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        response = self.table.get_item(Key={'eventId': event_id})
        return response.get('Item')
    
    def find_all(self, status_filter: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find all events, optionally filtered by status
        
        Args:
            status_filter: Optional status to filter by
            
        Returns:
            List of event data dictionaries
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        events = []
        
        if status_filter:
            response = self.table.scan(
                FilterExpression=Attr('status').eq(status_filter)
            )
        else:
            response = self.table.scan()
        
        events.extend(response.get('Items', []))
        
        # Handle pagination
        while 'LastEvaluatedKey' in response:
            if status_filter:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey'],
                    FilterExpression=Attr('status').eq(status_filter)
                )
            else:
                response = self.table.scan(
                    ExclusiveStartKey=response['LastEvaluatedKey']
                )
            events.extend(response.get('Items', []))
        
        return events
    
    def update(self, event_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing event
        
        Args:
            event_id: The event ID to update
            update_data: Dictionary of fields to update
            
        Returns:
            The updated event data
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        update_expression = "SET " + ", ".join([f"#{k} = :{k}" for k in update_data.keys()])
        expression_attribute_names = {f"#{k}": k for k in update_data.keys()}
        expression_attribute_values = {f":{k}": v for k, v in update_data.items()}
        
        response = self.table.update_item(
            Key={'eventId': event_id},
            UpdateExpression=update_expression,
            ExpressionAttributeNames=expression_attribute_names,
            ExpressionAttributeValues=expression_attribute_values,
            ReturnValues="ALL_NEW"
        )
        
        return response['Attributes']
    
    def delete(self, event_id: str) -> None:
        """
        Delete an event
        
        Args:
            event_id: The event ID to delete
            
        Raises:
            ClientError: If DynamoDB operation fails
        """
        self.table.delete_item(Key={'eventId': event_id})
    
    def exists(self, event_id: str) -> bool:
        """
        Check if an event exists
        
        Args:
            event_id: The event ID to check
            
        Returns:
            True if event exists, False otherwise
        """
        return self.find_by_id(event_id) is not None

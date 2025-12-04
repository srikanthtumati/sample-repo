"""Quick test script to verify the registration API works"""
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_registration_flow():
    """Test the complete registration flow"""
    print("Testing user registration system...")
    
    # Create an event with waitlist
    print("\n1. Creating event...")
    event_response = client.post("/events", json={
        "eventId": "test-event-1",
        "title": "Test Event",
        "description": "Test event for registration",
        "date": "2024-12-20",
        "location": "Test Location",
        "capacity": 2,
        "organizer": "Test Organizer",
        "status": "active",
        "waitlistEnabled": True
    })
    print(f"   Status: {event_response.status_code}")
    print(f"   Response: {event_response.json()}")
    assert event_response.status_code in [200, 201]
    
    # Create users
    print("\n2. Creating users...")
    for i in range(1, 4):
        user_response = client.post("/users", json={
            "userId": f"test-user-{i}",
            "name": f"Test User {i}"
        })
        print(f"   User {i} - Status: {user_response.status_code}")
        assert user_response.status_code in [200, 201]
    
    # Register first two users (should be ACTIVE)
    print("\n3. Registering first two users (should be ACTIVE)...")
    for i in range(1, 3):
        reg_response = client.post("/events/test-event-1/registrations", json={
            "userId": f"test-user-{i}"
        })
        print(f"   User {i} - Status: {reg_response.status_code}")
        print(f"   Response: {reg_response.json()}")
        assert reg_response.status_code in [200, 201]
        assert reg_response.json()["status"] == "active"
    
    # Register third user (should be WAITLISTED)
    print("\n4. Registering third user (should be WAITLISTED)...")
    reg_response = client.post("/events/test-event-1/registrations", json={
        "userId": "test-user-3"
    })
    print(f"   Status: {reg_response.status_code}")
    print(f"   Response: {reg_response.json()}")
    assert reg_response.status_code in [200, 201]
    assert reg_response.json()["status"] == "waitlisted"
    
    # Get event registrations
    print("\n5. Getting event registrations...")
    event_regs = client.get("/events/test-event-1/registrations")
    print(f"   Status: {event_regs.status_code}")
    print(f"   Count: {event_regs.json()['count']}")
    assert event_regs.status_code == 200
    assert event_regs.json()["count"] == 3
    
    # Get user registrations (should only show active)
    print("\n6. Getting user-1 registrations...")
    user_regs = client.get("/users/test-user-1/registrations")
    print(f"   Status: {user_regs.status_code}")
    print(f"   Count: {user_regs.json()['count']}")
    assert user_regs.status_code == 200
    assert user_regs.json()["count"] == 1
    
    # Unregister user-1 (should promote user-3)
    print("\n7. Unregistering user-1 (should promote user-3)...")
    unreg_response = client.delete("/events/test-event-1/registrations/test-user-1")
    print(f"   Status: {unreg_response.status_code}")
    assert unreg_response.status_code in [200, 204]
    
    # Verify user-3 was promoted
    print("\n8. Verifying user-3 was promoted...")
    event_regs = client.get("/events/test-event-1/registrations")
    registrations = event_regs.json()["registrations"]
    user3_reg = next((r for r in registrations if r["userId"] == "test-user-3"), None)
    print(f"   User-3 status: {user3_reg['status']}")
    assert user3_reg["status"] == "active"
    
    print("\n✅ All tests passed!")

if __name__ == "__main__":
    test_registration_flow()

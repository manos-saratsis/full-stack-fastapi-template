```python
import pytest
from fastapi import status

def test_create_user(client, test_user):
    response = client.post("/api/v1/users/", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["email"] == test_user["email"]
    assert "id" in data
    assert "password" not in data

def test_create_user_duplicate_email(client, test_user):
    # Create first user
    response = client.post("/api/v1/users/", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Try to create user with same email
    response = client.post("/api/v1/users/", json=test_user)
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_get_users(client, test_user):
    # Create a user first
    response = client.post("/api/v1/users/", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Get list of users
    response = client.get("/api/v1/users/")
    assert response.status_code == status.HTTP_200_OK
    users = response.json()
    assert len(users) >= 1
    assert any(user["email"] == test_user["email"] for user in users)

def test_update_user(client, test_user):
    # Create user first
    response = client.post("/api/v1/users/", json=test_user)
    user_id = response.json()["id"]
    
    # Login to get token
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    tokens = response.json()
    
    # Update user
    update_data = {"full_name": "Updated Name"}
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.patch(
        f"/api/v1/users/{user_id}",
        json=update_data,
        headers=headers
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["full_name"] == "Updated Name"
```
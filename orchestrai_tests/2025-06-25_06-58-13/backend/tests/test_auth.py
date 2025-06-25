```python
import pytest
from fastapi import status
from app.core.security import create_access_token

def test_login(client, test_user):
    # First create a user
    response = client.post("/api/v1/users/", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Try logging in
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    assert "access_token" in response.json()

def test_login_invalid_credentials(client):
    login_data = {
        "username": "wrong@example.com",
        "password": "wrongpass"
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, test_user):
    # Create user and get token
    client.post("/api/v1/users/", json=test_user)
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    token = response.json()["access_token"]
    
    # Test getting current user
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    assert response.json()["email"] == test_user["email"]
```
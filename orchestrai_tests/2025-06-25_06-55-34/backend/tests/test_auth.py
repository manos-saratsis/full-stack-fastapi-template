```python
import pytest
from fastapi import status
from jose import jwt

from app.core.config import settings
from app.core.security import create_access_token

def test_login(client, test_user):
    # First create a user
    response = client.post("/api/v1/users/", json=test_user)
    assert response.status_code == status.HTTP_201_CREATED
    
    # Try to login
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    assert response.status_code == status.HTTP_200_OK
    tokens = response.json()
    assert "access_token" in tokens
    assert tokens["token_type"] == "bearer"

def test_login_incorrect_password(client, test_user):
    response = client.post("/api/v1/login/access-token", data={
        "username": test_user["email"],
        "password": "wrong_password"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, test_user):
    # Login first
    login_data = {
        "username": test_user["email"],
        "password": test_user["password"]
    }
    response = client.post("/api/v1/login/access-token", data=login_data)
    tokens = response.json()
    
    # Test getting current user
    headers = {"Authorization": f"Bearer {tokens['access_token']}"}
    response = client.get("/api/v1/users/me", headers=headers)
    assert response.status_code == status.HTTP_200_OK
    user_data = response.json()
    assert user_data["email"] == test_user["email"]
```
```python
from datetime import timedelta
from app.core.security import (
    create_access_token,
    verify_password,
    get_password_hash
)

def test_password_hash():
    password = "test_password"
    hashed = get_password_hash(password)
    assert verify_password(password, hashed)
    assert not verify_password("wrong_password", hashed)

def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data)
    assert isinstance(token, str)
    assert len(token) > 0

    token_with_expire = create_access_token(
        data, expires_delta=timedelta(minutes=15)
    )
    assert isinstance(token_with_expire, str)
    assert len(token_with_expire) > 0
```
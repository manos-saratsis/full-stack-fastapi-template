```python
from app.core.config import settings

def test_settings():
    assert settings.PROJECT_NAME == "Full Stack FastAPI Template"
    assert settings.API_V1_STR == "/api/v1"
    assert isinstance(settings.SECRET_KEY, str)
    assert len(settings.SECRET_KEY) > 0
    assert settings.ACCESS_TOKEN_EXPIRE_MINUTES > 0
```
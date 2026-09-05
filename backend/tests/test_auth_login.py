import pytest
from fastapi.testclient import TestClient
from main import app
from core.config import settings

client = TestClient(app)

def test_admin_login_success():
    response = client.post(
        "/api/auth/login/json",
        json={
            "email": settings.FIRST_SUPERUSER_EMAIL,
            "password": settings.FIRST_SUPERUSER_PASSWORD,
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["user"]["email"] == settings.FIRST_SUPERUSER_EMAIL
    assert data["user"]["is_admin"] is True

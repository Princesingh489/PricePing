import pytest
from unittest.mock import patch, MagicMock
from fastapi.testclient import TestClient
from main import app
from core.config import settings

client = TestClient(app)


def test_google_auth_empty_payload():
    response = client.post("/api/auth/google", json={})
    assert response.status_code == 400
    assert "code" in response.json()["detail"] or "credential" in response.json()["detail"]


def test_google_auth_missing_credentials_on_server():
    with patch.object(settings, "GOOGLE_CLIENT_ID", ""), patch.object(settings, "GOOGLE_CLIENT_SECRET", ""):
        response = client.post(
            "/api/auth/google",
            json={"code": "sample_auth_code", "redirect_uri": "http://localhost:5173/auth/google/callback"}
        )
        assert response.status_code == 500
        assert "not configured" in response.json()["detail"]


def test_google_auth_code_flow_success_new_user():
    # Mock settings
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-google-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-google-client-secret"):

        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {"access_token": "mock-access-token-123"}

        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.status_code = 200
        mock_userinfo_resp.json.return_value = {
            "email": "newgoogleuser@example.com",
            "name": "Google Test User",
            "sub": "1234567890",
        }

        async def mock_post(url, *args, **kwargs):
            return mock_token_resp

        async def mock_get(url, *args, **kwargs):
            return mock_userinfo_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post), \
             patch("httpx.AsyncClient.get", side_effect=mock_get):

            response = client.post(
                "/api/auth/google",
                json={"code": "valid_google_code", "redirect_uri": "http://localhost:5173/auth/google/callback"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["token_type"] == "bearer"
            assert data["user"]["email"] == "newgoogleuser@example.com"
            assert data["user"]["name"] == "Google Test User"


def test_google_auth_code_flow_existing_user():
    # Calling again for same email should successfully log in existing user
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-google-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-google-client-secret"):

        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {"access_token": "mock-access-token-456"}

        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.status_code = 200
        mock_userinfo_resp.json.return_value = {
            "email": "newgoogleuser@example.com",
            "name": "Google Test User",
            "sub": "1234567890",
        }

        async def mock_post(url, *args, **kwargs):
            return mock_token_resp

        async def mock_get(url, *args, **kwargs):
            return mock_userinfo_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post), \
             patch("httpx.AsyncClient.get", side_effect=mock_get):

            response = client.post(
                "/api/auth/google",
                json={"code": "second_google_code", "redirect_uri": "http://localhost:5173/auth/google/callback"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["user"]["email"] == "newgoogleuser@example.com"


def test_google_auth_invalid_code_from_google():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-google-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-google-client-secret"):

        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 400
        mock_token_resp.text = '{"error": "invalid_grant"}'

        async def mock_post(url, *args, **kwargs):
            return mock_token_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post):
            response = client.post(
                "/api/auth/google",
                json={"code": "bad_code", "redirect_uri": "http://localhost:5173/auth/google/callback"}
            )
            assert response.status_code == 400
            assert "Failed to authenticate" in response.json()["detail"]


def test_google_auth_inactive_user_rejected():
    from db.database import SessionLocal
    from db import models
    from core.security import get_password_hash

    db = SessionLocal()
    try:
        inactive_email = "inactivegoogleuser@example.com"
        existing = db.query(models.User).filter(models.User.email == inactive_email).first()
        if not existing:
            user = models.User(
                name="Inactive User",
                email=inactive_email,
                password_hash=get_password_hash("password123"),
                is_active=False,
                is_admin=False,
            )
            db.add(user)
            db.commit()
        else:
            existing.is_active = False
            db.commit()
    finally:
        db.close()

    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-google-client-id"), \
         patch.object(settings, "GOOGLE_CLIENT_SECRET", "mock-google-client-secret"):

        mock_token_resp = MagicMock()
        mock_token_resp.status_code = 200
        mock_token_resp.json.return_value = {"access_token": "mock-access-token-789"}

        mock_userinfo_resp = MagicMock()
        mock_userinfo_resp.status_code = 200
        mock_userinfo_resp.json.return_value = {
            "email": "inactivegoogleuser@example.com",
            "name": "Inactive User",
            "sub": "9876543210",
        }

        async def mock_post(url, *args, **kwargs):
            return mock_token_resp

        async def mock_get(url, *args, **kwargs):
            return mock_userinfo_resp

        with patch("httpx.AsyncClient.post", side_effect=mock_post), \
             patch("httpx.AsyncClient.get", side_effect=mock_get):

            response = client.post(
                "/api/auth/google",
                json={"code": "inactive_user_code", "redirect_uri": "http://localhost:5173/auth/google/callback"}
            )
            assert response.status_code == 400
            assert "Account is inactive" in response.json()["detail"]


def test_google_auth_credential_flow_success():
    with patch.object(settings, "GOOGLE_CLIENT_ID", "mock-google-client-id"):
        mock_tokeninfo_resp = MagicMock()
        mock_tokeninfo_resp.status_code = 200
        mock_tokeninfo_resp.json.return_value = {
            "email": "idtokenuser@example.com",
            "name": "ID Token User",
            "aud": "mock-google-client-id",
        }

        async def mock_get(url, *args, **kwargs):
            return mock_tokeninfo_resp

        with patch("httpx.AsyncClient.get", side_effect=mock_get):
            response = client.post(
                "/api/auth/google",
                json={"credential": "mock_id_token"}
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert data["user"]["email"] == "idtokenuser@example.com"


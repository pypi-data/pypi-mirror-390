import pytest
from fastapi.testclient import TestClient
from app.main import app, SECRET_KEY
import jwt
from datetime import datetime, timedelta

client = TestClient(app)

def create_token(username: str, expired=False):
    payload = {"sub": username}
    if expired:
        payload["exp"] = datetime.utcnow() - timedelta(minutes=1)
    else:
        payload["exp"] = datetime.utcnow() + timedelta(minutes=10)
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")

def test_cloud_database_auth():
    # 1. Sans token
    r = client.get("/cloud_database")
    assert r.status_code == 401
    # 2. Token invalide
    r = client.get("/cloud_database", headers={"Authorization": "Bearer faketoken"})
    assert r.status_code == 401
    # 3. Token expiré
    expired_token = create_token("testuser", expired=True)
    r = client.get("/cloud_database", headers={"Authorization": f"Bearer {expired_token}"})
    assert r.status_code == 401
    # 4. Token valide
    valid_token = create_token("testuser")
    r = client.get("/cloud_database", headers={"Authorization": f"Bearer {valid_token}"})
    assert r.status_code == 200
    assert "Metadidomi Cloud Database" in r.text

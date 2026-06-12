import pytest
from app.models.user import User
from app.database import AsyncSessionLocal

@pytest.mark.asyncio
async def test_github_login_redirect(async_client):
    response = await async_client.get("/auth/github")
    assert response.status_code == 307
    assert "github.com/login/oauth/authorize" in response.headers["location"]

@pytest.mark.asyncio
async def test_logout_blacklists_token(async_client, monkeypatch):
    # Mock user creation
    async with AsyncSessionLocal() as session:
        user = User(github_id="123", username="testuser")
        session.add(user)
        await session.commit()
        await session.refresh(user)

    from app.core.security import create_access_token
    token = create_access_token({"sub": str(user.id), "jti": "mock_jti"})

    # Fetch me should work
    res = await async_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["username"] == "testuser"

    # Logout
    res_logout = await async_client.post("/auth/logout", headers={"Authorization": f"Bearer {token}"})
    assert res_logout.status_code == 200
    
    # Fetch me should fail
    res_failed = await async_client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res_failed.status_code == 401
    assert res_failed.json()["detail"] == "Token blacklisted"

import pytest
from app.models.user import User
from app.models.snippet import Snippet
from app.database import AsyncSessionLocal
from app.core.security import create_access_token

@pytest.fixture
async def authenticated_user():
    async with AsyncSessionLocal() as session:
        user = User(github_id="test_github", username="snippet_tester")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        token = create_access_token({"sub": str(user.id), "plan": "free"})
        return {"user": user, "token": token}

@pytest.mark.asyncio
async def test_create_snippet(async_client, authenticated_user):
    headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
    payload = {
        "title": "My first snippet",
        "code": "print('hello')",
        "language": "python",
        "is_public": True,
        "tags": ["python", "hello"]
    }
    res = await async_client.post("/snippets", json=payload, headers=headers)
    assert res.status_code == 200
    data = res.json()
    assert data["title"] == payload["title"]
    assert "share_id" in data
    assert data["view_count"] == 0

@pytest.mark.asyncio
async def test_free_plan_limit(async_client, authenticated_user):
    headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
    user_id = authenticated_user['user'].id

    # Mock 50 snippets
    async with AsyncSessionLocal() as session:
        user = await session.get(User, user_id)
        user.snippets_count = 50
        await session.commit()
    
    payload = {
        "title": "Overflow snippet",
        "code": "overflow",
        "language": "text",
    }
    res = await async_client.post("/snippets", json=payload, headers=headers)
    assert res.status_code == 403
    assert "Free plan limit exceeded" in res.json()["detail"]

@pytest.mark.asyncio
async def test_get_public_snippet(async_client, authenticated_user):
    headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
    payload = {"title": "Public", "code": "def a(): pass", "language": "python", "is_public": True}
    res_post = await async_client.post("/snippets", json=payload, headers=headers)
    share_id = res_post.json()["share_id"]

    res_get = await async_client.get(f"/s/{share_id}")
    assert res_get.status_code == 200
    assert res_get.json()["title"] == "Public"

@pytest.mark.asyncio
async def test_get_private_snippet_fails(async_client, authenticated_user):
    headers = {"Authorization": f"Bearer {authenticated_user['token']}"}
    payload = {"title": "Private", "code": "def a(): pass", "language": "python", "is_public": False}
    res_post = await async_client.post("/snippets", json=payload, headers=headers)
    share_id = res_post.json()["share_id"]

    res_get = await async_client.get(f"/s/{share_id}")
    assert res_get.status_code == 404

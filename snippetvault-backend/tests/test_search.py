import pytest
import asyncio
from app.models.user import User
from app.database import AsyncSessionLocal
from app.core.security import create_access_token

@pytest.fixture
async def search_user():
    async with AsyncSessionLocal() as session:
        user = User(github_id="search_test", username="search_tester")
        session.add(user)
        await session.commit()
        await session.refresh(user)
        token = create_access_token({"sub": str(user.id), "plan": "pro"})
        return {"user": user, "token": token}

@pytest.mark.asyncio
async def test_search_snippets(async_client, search_user):
    headers = {"Authorization": f"Bearer {search_user['token']}"}
    
    # Create some snippets
    snippets = [
        {"title": "FastAPI intro", "code": "from fastapi import FastAPI", "language": "python"},
        {"title": "React hook", "code": "const [state, setState] = useState()", "language": "javascript", "description": "Basic state"},
        {"title": "Postgres query", "code": "SELECT * FROM users", "language": "sql"}
    ]
    
    for s in snippets:
        await async_client.post("/snippets", json=s, headers=headers)

    # Allow PG to index if needed (sometimes instantaneous in tests)
    await asyncio.sleep(0.1)

    # Search for "FastAPI"
    res1 = await async_client.get("/snippets/search?q=FastAPI", headers=headers)
    assert res1.status_code == 200
    data1 = res1.json()
    assert len(data1) == 1
    assert data1[0]["title"] == "FastAPI intro"

    # Search for "useState"
    res2 = await async_client.get("/snippets/search?q=useState", headers=headers)
    assert len(res2.json()) == 1
    assert res2.json()[0]["title"] == "React hook"

    # Search cache should return same result quickly
    res_cached = await async_client.get("/snippets/search?q=FastAPI", headers=headers)
    assert res_cached.status_code == 200
    assert len(res_cached.json()) == 1

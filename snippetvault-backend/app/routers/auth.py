from fastapi import APIRouter, Depends, HTTPException, status, Query, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import json
from datetime import datetime, timezone

from app.database import get_db
from app.config import settings
from app.schemas.auth import AuthResponse, MessageResponse
from app.schemas.user import UserResponse
from app.models.user import User
from app.services.auth_service import AuthService
from app.services.cache_service import CacheService
from app.core.security import create_access_token, verify_token
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])

@router.get("/github")
async def github_login():
    state = str(uuid.uuid4())
    # Store state in Redis for 5 mins
    await CacheService.set(f"oauth_state:{state}", "1", ttl=300)
    
    url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={settings.GITHUB_CLIENT_ID}"
        f"&scope=read:user user:email"
        f"&redirect_uri={settings.GITHUB_REDIRECT_URI}"
        f"&state={state}"
    )
    return RedirectResponse(url)

@router.get("/github/callback", response_model=AuthResponse)
async def github_callback(code: str, state: str, db: AsyncSession = Depends(get_db)):
    # Verify state
    state_valid = await CacheService.get(f"oauth_state:{state}")
    if not state_valid:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid state parameter")
    await CacheService.delete(f"oauth_state:{state}")

    # Exchange code for token
    access_token = await AuthService.exchange_code_for_token(code)
    
    # Get user profile
    github_user = await AuthService.get_github_user(access_token)
    
    # Upsert user in DB
    result = await db.execute(select(User).where(User.github_id == github_user["github_id"]))
    user = result.scalar_one_or_none()
    
    if not user:
        user = User(**github_user)
        db.add(user)
    else:
        user.username = github_user["username"]
        user.email = github_user["email"]
        user.avatar_url = github_user["avatar_url"]
        user.bio = github_user["bio"]
    
    await db.commit()
    await db.refresh(user)
    
    # Generate JWT
    jti = str(uuid.uuid4())
    jwt_token = create_access_token(data={
        "sub": str(user.id),
        "username": user.username,
        "plan": user.plan,
        "jti": jti
    })
    
    return AuthResponse(
        access_token=jwt_token,
        user=user
    )

@router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.post("/logout", response_model=MessageResponse)
async def logout(request: Request, current_user: User = Depends(get_current_user)):
    auth_header = request.headers.get("Authorization")
    if auth_header:
        token = auth_header.split(" ")[1]
        payload = verify_token(token)
        if payload and "jti" in payload:
            # Blacklist token until expiry
            exp = payload.get("exp")
            now = datetime.now(timezone.utc).timestamp()
            ttl = int(exp - now) if exp else 86400
            if ttl > 0:
                await CacheService.set(f"blacklist:jwt:{payload['jti']}", "1", ttl=ttl)
    
    return {"message": "Logged out successfully"}

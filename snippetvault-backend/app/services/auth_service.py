import httpx
from fastapi import HTTPException, status
from app.config import settings

class AuthService:
    @staticmethod
    async def exchange_code_for_token(code: str) -> str:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://github.com/login/oauth/access_token",
                data={
                    "client_id": settings.GITHUB_CLIENT_ID,
                    "client_secret": settings.GITHUB_CLIENT_SECRET,
                    "code": code,
                    "redirect_uri": settings.GITHUB_REDIRECT_URI,
                },
                headers={"Accept": "application/json"}
            )
            if response.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to exchange token")
            
            data = response.json()
            if "error" in data:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=data["error_description"])
            
            return data["access_token"]

    @staticmethod
    async def get_github_user(access_token: str) -> dict:
        async with httpx.AsyncClient() as client:
            headers = {"Authorization": f"Bearer {access_token}"}
            
            # Get user profile
            user_res = await client.get("https://api.github.com/user", headers=headers)
            if user_res.status_code != 200:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Failed to fetch GitHub profile")
            
            user_data = user_res.json()
            
            # Get user emails (if not public)
            email_res = await client.get("https://api.github.com/user/emails", headers=headers)
            primary_email = None
            if email_res.status_code == 200:
                emails = email_res.json()
                primary_email = next((e["email"] for e in emails if e.get("primary")), None)
                if not primary_email and emails:
                    primary_email = emails[0]["email"]
            
            return {
                "github_id": str(user_data["id"]),
                "username": user_data["login"],
                "email": primary_email or user_data.get("email"),
                "avatar_url": user_data.get("avatar_url"),
                "bio": user_data.get("bio")
            }

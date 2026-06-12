import time
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.services.cache_service import get_redis
from app.core.security import verify_token

class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Determine user limit or IP limit
        is_authenticated = False
        user_id = None
        
        # Check authorization header
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            payload = verify_token(token)
            if payload and "sub" in payload:
                is_authenticated = True
                user_id = payload["sub"]

        path = request.url.path
        
        # Determine keys and limits
        if is_authenticated:
            # Strict limits
            if request.method == "POST" and path == "/snippets":
                limit = 20
                key = f"rl:strict_post:user:{user_id}"
                window = 3600
            else:
                limit = 200
                key = f"rl:user:{user_id}"
                window = 3600
        else:
            ip = request.client.host if request.client else "unknown"
            if request.method == "GET" and path.startswith("/s/"):
                limit = 100
                key = f"rl:strict_get:ip:{ip}"
                window = 3600
            else:
                limit = 30
                key = f"rl:ip:{ip}"
                window = 3600
        
        redis = await get_redis()
        now = time.time()
        
        # Sliding window implementation
        async with redis.pipeline(transaction=True) as pipe:
            pipe.zremrangebyscore(key, 0, now - window)
            pipe.zcard(key)
            pipe.zadd(key, {str(now): now})
            pipe.expire(key, window)
            results = await pipe.execute()
        
        request_count = results[1]
        
        if request_count >= limit:
            return JSONResponse(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                content={"error": "Rate limit exceeded", "retry_after": window},
                headers={
                    "X-RateLimit-Limit": str(limit),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(now + window))
                }
            )

        response = await call_next(request)
        
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(max(0, limit - request_count - 1))
        response.headers["X-RateLimit-Reset"] = str(int(now + window))
        
        return response

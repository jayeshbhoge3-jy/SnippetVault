from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
import json

from app.database import get_db
from app.models.snippet import Snippet
from app.models.user import User
from app.models.star import Star
from app.schemas.snippet import PaginatedSnippetResponse, SnippetResponse
from app.schemas.user import UserStats
from app.core.dependencies import get_current_user
from app.services.cache_service import CacheService

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/{username}/snippets", response_model=PaginatedSnippetResponse)
async def get_user_public_snippets(
    username: str, 
    page: int = Query(1, ge=1), 
    limit: int = Query(12, ge=1, le=50),
    db: AsyncSession = Depends(get_db)
):
    cache_key = f"user_public:{username}:{page}_{limit}"
    cached = await CacheService.get(cache_key)
    if cached:
        return json.loads(cached)
        
    # Find user
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    query = select(Snippet).where(Snippet.user_id == user.id, Snippet.is_public == True).order_by(desc(Snippet.created_at))
    
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    query = query.offset((page - 1) * limit).limit(limit)
    snippets_result = await db.execute(query)
    snippets = list(snippets_result.scalars().all())
    
    response_items = []
    for s in snippets:
        s_dict = {
            "id": str(s.id), "user_id": str(s.user_id), "title": s.title, "code": s.code, "language": s.language,
            "description": s.description, "tags": s.tags, "is_public": s.is_public, "share_id": s.share_id,
            "view_count": s.view_count, "star_count": s.star_count, 
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "is_starred": False
        }
        response_items.append(s_dict)
        
    response = {
        "items": response_items,
        "total": total,
        "page": page,
        "size": limit
    }
    
    await CacheService.set(cache_key, json.dumps(response), ttl=180)
    return response

@router.get("/me/stats", response_model=UserStats)
async def get_user_stats(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cache_key = f"user_stats:{current_user.id}"
    cached = await CacheService.get(cache_key)
    if cached:
        return json.loads(cached)
        
    # Get total snippets
    snippets_result = await db.execute(select(Snippet).where(Snippet.user_id == current_user.id))
    snippets = list(snippets_result.scalars().all())
    
    total_snippets = len(snippets)
    public_snippets = sum(1 for s in snippets if s.is_public)
    private_snippets = total_snippets - public_snippets
    total_views = sum(s.view_count for s in snippets)
    total_stars_received = sum(s.star_count for s in snippets)
    
    # Language breakdown
    lang_counts = {}
    tag_counts = {}
    snippets_this_month = 0
    now = func.now()
    
    for s in snippets:
        lang_counts[s.language] = lang_counts.get(s.language, 0) + 1
        for t in s.tags:
            tag_counts[t] = tag_counts.get(t, 0) + 1
            
    top_languages = sorted(lang_counts, key=lang_counts.get, reverse=True)[:5]
    most_used_tags = sorted(tag_counts, key=tag_counts.get, reverse=True)[:10]
    
    # To get snippets this month, simple naive approach if we just use Python datetime:
    from datetime import datetime, timezone
    current_month = datetime.now(timezone.utc).month
    current_year = datetime.now(timezone.utc).year
    
    snippets_this_month = sum(
        1 for s in snippets 
        if s.created_at and s.created_at.month == current_month and s.created_at.year == current_year
    )
    
    stats = {
        "total_snippets": total_snippets,
        "public_snippets": public_snippets,
        "private_snippets": private_snippets,
        "total_stars_received": total_stars_received,
        "total_views": total_views,
        "top_languages": top_languages,
        "most_used_tags": most_used_tags,
        "snippets_this_month": snippets_this_month
    }
    
    await CacheService.set(cache_key, json.dumps(stats), ttl=300)
    return stats

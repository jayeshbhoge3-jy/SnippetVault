from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc
import json
import hashlib
from nanoid import generate

from app.database import get_db
from app.models.snippet import Snippet
from app.models.user import User
from app.models.star import Star
from app.schemas.snippet import SnippetCreate, SnippetUpdate, SnippetResponse, PaginatedSnippetResponse, SnippetPublicResponse
from app.core.dependencies import get_current_user
from app.services.cache_service import CacheService
from app.services.search_service import SearchService

router = APIRouter(prefix="/snippets", tags=["snippets"])
public_router = APIRouter(prefix="/s", tags=["public snippets"])

@router.get("", response_model=PaginatedSnippetResponse)
async def get_snippets(
    language: str = None,
    tags: str = None,
    search: str = None,
    is_public: bool = None,
    page: int = Query(1, ge=1),
    limit: int = Query(12, ge=1, le=50),
    sort_by: str = Query("created_at", alias="sort"),
    order: str = Query("desc"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    # Cache key generation based on params
    params = f"{language}_{tags}_{search}_{is_public}_{page}_{limit}_{sort_by}_{order}"
    params_hash = hashlib.md5(params.encode()).hexdigest()
    cache_key = f"snippets:{current_user.id}:{params_hash}"
    
    cached = await CacheService.get(cache_key)
    if cached:
        return json.loads(cached)
        
    query = select(Snippet).where(Snippet.user_id == current_user.id)
    
    if language:
        query = query.where(Snippet.language == language)
    if is_public is not None:
        query = query.where(Snippet.is_public == is_public)
    if tags:
        tag_list = tags.split(",")
        query = query.where(Snippet.tags.contains(tag_list))
    if search:
        query = query.where(
            func.to_tsvector('english', Snippet.title + ' ' + func.coalesce(Snippet.description, '') + ' ' + Snippet.code)
            .op('@@')(func.plainto_tsquery('english', search))
        )
        
    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = await db.scalar(count_query)
    
    # Sorting
    sort_col = getattr(Snippet, sort_by, Snippet.created_at)
    if order == "desc":
        query = query.order_by(desc(sort_col))
    else:
        query = query.order_by(asc(sort_col))
        
    # Pagination
    query = query.offset((page - 1) * limit).limit(limit)
    
    # Execute query
    result = await db.execute(query)
    snippets = list(result.scalars().all())

    # Fetch is_starred
    snippet_ids = [s.id for s in snippets]
    starred_query = select(Star.snippet_id).where(Star.user_id == current_user.id, Star.snippet_id.in_(snippet_ids))
    starred_result = await db.execute(starred_query)
    starred_ids = set(starred_result.scalars().all())

    response_items = []
    for s in snippets:
        s_dict = {
            "id": str(s.id),
            "user_id": str(s.user_id),
            "title": s.title,
            "code": s.code,
            "language": s.language,
            "description": s.description,
            "tags": s.tags,
            "is_public": s.is_public,
            "share_id": s.share_id,
            "view_count": s.view_count,
            "star_count": s.star_count,
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "is_starred": s.id in starred_ids
        }
        response_items.append(s_dict)
    
    response = {
        "items": response_items,
        "total": total,
        "page": page,
        "size": limit
    }
    
    # Cache result
    await CacheService.set(cache_key, json.dumps(response), ttl=120)
    
    return response

@router.post("", response_model=SnippetResponse)
async def create_snippet(snippet: SnippetCreate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    if current_user.plan == "free" and current_user.snippets_count >= 50:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Free plan limit exceeded. Please upgrade to Pro.")
        
    share_id = generate(size=12)
    db_snippet = Snippet(
        **snippet.model_dump(),
        user_id=current_user.id,
        share_id=share_id
    )
    db.add(db_snippet)
    current_user.snippets_count += 1
    
    await db.commit()
    await db.refresh(db_snippet)
    
    # Invalidate cache
    await CacheService.delete_pattern(f"snippets:{current_user.id}:*")
    await CacheService.delete_pattern(f"user_public:{current_user.username}:*")
    
    return db_snippet

@router.get("/search", response_model=list[SnippetResponse])
async def search_snippets(q: str = Query(..., min_length=2), current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    cache_key = f"search:{current_user.id}:{q}"
    cached = await CacheService.get(cache_key)
    if cached:
        return json.loads(cached)
        
    snippets = await SearchService.search_snippets(db, str(current_user.id), q)
    
    response_items = []
    for s in snippets:
        s_dict = {
            "id": str(s.id), "user_id": str(s.user_id), "title": s.title, "code": s.code, "language": s.language,
            "description": s.description, "tags": s.tags, "is_public": s.is_public, "share_id": s.share_id,
            "view_count": s.view_count, "star_count": s.star_count, 
            "created_at": s.created_at.isoformat() if s.created_at else None,
            "updated_at": s.updated_at.isoformat() if s.updated_at else None,
            "is_starred": False # Simple mock for search endpoint, can optimize if needed
        }
        response_items.append(s_dict)
        
    await CacheService.set(cache_key, json.dumps(response_items), ttl=60)
    return response_items

@router.get("/{id}", response_model=SnippetResponse)
async def get_snippet(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Snippet).where(Snippet.id == id, Snippet.user_id == current_user.id))
    snippet = result.scalar_one_or_none()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    star_result = await db.execute(select(Star).where(Star.user_id == current_user.id, Star.snippet_id == id))
    is_starred = star_result.scalar_one_or_none() is not None
    
    # We can attach is_starred manually or modify the dict
    snippet_dict = snippet.__dict__
    snippet_dict['is_starred'] = is_starred
    return snippet_dict

@router.put("/{id}", response_model=SnippetResponse)
async def update_snippet(id: str, snippet_update: SnippetUpdate, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Snippet).where(Snippet.id == id, Snippet.user_id == current_user.id))
    db_snippet = result.scalar_one_or_none()
    if not db_snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    update_data = snippet_update.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_snippet, key, value)
        
    db_snippet.updated_at = func.now()
    await db.commit()
    await db.refresh(db_snippet)
    
    # Invalidate cache
    await CacheService.delete_pattern(f"snippets:{current_user.id}:*")
    await CacheService.delete(f"public:{db_snippet.share_id}")
    await CacheService.delete_pattern(f"user_public:{current_user.username}:*")
    
    return db_snippet

@router.delete("/{id}")
async def delete_snippet(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Snippet).where(Snippet.id == id, Snippet.user_id == current_user.id))
    db_snippet = result.scalar_one_or_none()
    if not db_snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    share_id = db_snippet.share_id
    await db.delete(db_snippet)
    current_user.snippets_count -= 1
    await db.commit()
    
    # Invalidate cache
    await CacheService.delete_pattern(f"snippets:{current_user.id}:*")
    await CacheService.delete(f"public:{share_id}")
    await CacheService.delete_pattern(f"user_public:{current_user.username}:*")
    
    return {"message": "Snippet deleted"}

@public_router.get("/{share_id}", response_model=SnippetPublicResponse)
async def get_public_snippet(share_id: str, db: AsyncSession = Depends(get_db)):
    cache_key = f"public:{share_id}"
    cached = await CacheService.get(cache_key)
    
    if cached:
        # Increment view_count asynchronously in DB (lazy approach)
        await db.execute(
            Snippet.__table__.update().where(Snippet.share_id == share_id).values(view_count=Snippet.view_count + 1)
        )
        await db.commit()
        return json.loads(cached)
        
    result = await db.execute(
        select(Snippet, User).join(User, Snippet.user_id == User.id).where(Snippet.share_id == share_id, Snippet.is_public == True)
    )
    row = result.first()
    
    if not row:
        raise HTTPException(status_code=404, detail="Snippet not found or private")
        
    snippet, user = row
    
    # Increment view_count
    snippet.view_count += 1
    await db.commit()
    await db.refresh(snippet)
    
    response_dict = {
        "id": str(snippet.id), "user_id": str(snippet.user_id), "title": snippet.title, "code": snippet.code,
        "language": snippet.language, "description": snippet.description, "tags": snippet.tags,
        "is_public": snippet.is_public, "share_id": snippet.share_id, "view_count": snippet.view_count,
        "star_count": snippet.star_count, "created_at": snippet.created_at.isoformat() if snippet.created_at else None,
        "updated_at": snippet.updated_at.isoformat() if snippet.updated_at else None,
        "author": {
            "username": user.username,
            "avatar_url": user.avatar_url,
            "bio": user.bio
        }
    }
    
    await CacheService.set(cache_key, json.dumps(response_dict), ttl=300)
    
    return response_dict

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.database import get_db
from app.models.snippet import Snippet
from app.models.star import Star
from app.models.user import User
from app.core.dependencies import get_current_user

router = APIRouter(prefix="/snippets/{id}/star", tags=["stars"])

@router.post("")
async def star_snippet(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Snippet).where(Snippet.id == id))
    snippet = result.scalar_one_or_none()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    star = Star(user_id=current_user.id, snippet_id=snippet.id)
    db.add(star)
    
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # Already starred
        return {"starred": True, "star_count": snippet.star_count}
        
    snippet.star_count += 1
    await db.commit()
    return {"starred": True, "star_count": snippet.star_count}

@router.delete("")
async def unstar_snippet(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Snippet).where(Snippet.id == id))
    snippet = result.scalar_one_or_none()
    if not snippet:
        raise HTTPException(status_code=404, detail="Snippet not found")
        
    star_result = await db.execute(select(Star).where(Star.user_id == current_user.id, Star.snippet_id == snippet.id))
    star = star_result.scalar_one_or_none()
    
    if star:
        await db.delete(star)
        if snippet.star_count > 0:
            snippet.star_count -= 1
        await db.commit()
        
    return {"starred": False, "star_count": snippet.star_count}

@router.get("")
async def get_star_status(id: str, current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Star).where(Star.user_id == current_user.id, Star.snippet_id == id))
    star = result.scalar_one_or_none()
    return {"starred": star is not None}

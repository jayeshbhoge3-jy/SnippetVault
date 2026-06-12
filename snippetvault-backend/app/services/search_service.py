from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.snippet import Snippet
from typing import List

class SearchService:
    @staticmethod
    async def search_snippets(db: AsyncSession, user_id: str, query: str, limit: int = 20) -> List[Snippet]:
        # Perform full-text search across title, description, and code
        # We only search within the user's snippets
        
        stmt = (
            select(Snippet)
            .where(Snippet.user_id == user_id)
            .where(
                func.to_tsvector('english', Snippet.title + ' ' + func.coalesce(Snippet.description, '') + ' ' + Snippet.code)
                .op('@@')(func.plainto_tsquery('english', query))
            )
            .limit(limit)
        )
        
        result = await db.execute(stmt)
        return list(result.scalars().all())

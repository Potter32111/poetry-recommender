import logging
from typing import List, Dict, Any

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.poem import Poem
from app.models.user import User
from app.models.memorization import Memorization

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/", response_model=List[Dict[str, Any]])
async def get_recommendations(
    telegram_id: int,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Get personalized poem recommendations for a user based on their memorization history.
    """
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    memo_result = await db.execute(
        select(Poem)
        .join(Memorization, Memorization.poem_id == Poem.id)
        .where(Memorization.user_id == user.id)
    )
    memorized_poems = memo_result.scalars().all()
    memorized_ids = [str(p.id) for p in memorized_poems]
    
    # Exclude memorized IDs from potential recommendations
    base_query = select(Poem)
    if memorized_ids:
        base_query = base_query.where(Poem.id.notin_(memorized_ids))
        
    # Cold start: if no memorized poems, return random ones
    if not memorized_poems:
        logger.info(f"User {telegram_id} has no memorizations. Returning random poems.")
        random_result = await db.execute(base_query.order_by(func.random()).limit(limit))
        return [
            {
                "id": str(p.id),
                "title": p.title,
                "author": p.author,
                "language": p.language,
                "difficulty": p.difficulty,
                "lines_count": p.lines_count,
            } for p in random_result.scalars().all()
        ]

    # Calculate mean embedding
    embeddings = [p.embedding for p in memorized_poems if p.embedding is not None]
    
    if not embeddings:
        logger.info(f"User {telegram_id} memorizations lack embeddings. Returning random poems.")
        fallback_result = await db.execute(base_query.order_by(func.random()).limit(limit))
        return [
            {
                "id": str(p.id),
                "title": p.title,
                "author": p.author,
                "language": p.language,
                "difficulty": p.difficulty,
                "lines_count": p.lines_count,
            } for p in fallback_result.scalars().all()
        ]
        
    dim = len(embeddings[0])
    mean_embedding = [0.0] * dim
    for emb in embeddings:
        for i in range(dim):
            mean_embedding[i] += emb[i]
            
    mean_embedding = [val / len(embeddings) for val in mean_embedding]
    
    # Query database using cosine distance
    rec_result = await db.execute(
        base_query
        .where(Poem.embedding.is_not(None))
        .order_by(Poem.embedding.cosine_distance(mean_embedding))
        .limit(limit)
    )
    recommendations = rec_result.scalars().all()
    
    if not recommendations:
         # Fallback if remaining poems lack embeddings
         fallback_result = await db.execute(base_query.order_by(func.random()).limit(limit))
         recommendations = fallback_result.scalars().all()
         
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "author": p.author,
            "language": p.language,
            "difficulty": p.difficulty,
            "lines_count": p.lines_count,
        } for p in recommendations
    ]

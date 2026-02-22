import logging
from typing import List, Dict, Any
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.poem import Poem
from app.models.user import User
from app.models.memorization import Memorization
from app.services.ml import ml_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/recommendations", tags=["recommendations"])

@router.get("/", response_model=List[Dict[str, Any]])
async def get_recommendations(
    telegram_id: int,
    mood: str | None = None,
    limit: int = 5,
    db: AsyncSession = Depends(get_db)
):
    """
    Get highly personalized poem recommendations using vector similarity.
    Factors considered:
    1. Explicit User Mood (if provided)
    2. Temporal Context (Time of day, Season)
    3. User History (Authors, Themes they are already learning)
    """
    user_result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    user = user_result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    # 1. Gather User History
    memo_result = await db.execute(
        select(Poem)
        .join(Memorization, Memorization.poem_id == Poem.id)
        .where(Memorization.user_id == user.id)
    )
    memorized_poems = memo_result.scalars().all()
    memorized_ids = [str(p.id) for p in memorized_poems]
    
    # 2. Extract History Preferences 
    authors = set(p.author for p in memorized_poems if p.author)
    fav_authors = list(authors)[:3]  # top 3 roughly
    
    # 3. Determine Temporal Context
    now = datetime.now()
    hour = now.hour
    month = now.month
    
    if 5 <= hour < 12: time_of_day = "morning"
    elif 12 <= hour < 17: time_of_day = "afternoon"
    elif 17 <= hour < 22: time_of_day = "evening"
    else: time_of_day = "night"
    
    if month in (12, 1, 2): season = "winter"
    elif month in (3, 4, 5): season = "spring"
    elif month in (6, 7, 8): season = "summer"
    else: season = "autumn"
    
    # 4. Synthesize the Context Prompt
    context_parts = [f"It is a {season} {time_of_day}."]
    if fav_authors:
        context_parts.append(f"The user enjoys poetry by {', '.join(fav_authors)}.")
    if mood:
        context_parts.append(f"The user specifically asked for: '{mood}'.")
    else:
        context_parts.append("The user wants a poem suitable for this moment.")
        
    context_prompt = " ".join(context_parts)
    logger.info(f"Context Prompt generated for {telegram_id}: {context_prompt}")
    
    # 5. Generate Embedding for the Composite Context
    composite_vector = await ml_service.generate_embedding(context_prompt)
    
    # 6. Query PGVector using Cosine Distance
    base_query = select(Poem).where(Poem.embedding.is_not(None))
    if memorized_ids:
        base_query = base_query.where(Poem.id.notin_(memorized_ids))
        
    rec_result = await db.execute(
        base_query
        .order_by(Poem.embedding.cosine_distance(composite_vector))
        .limit(limit)
    )
    recommendations = rec_result.scalars().all()
    
    # Fallback to random if database has no embeddings at all
    if not recommendations:
        logger.warning(f"No embeddings found for recommendations. Falling back to random.")
        fb_query = select(Poem)
        if memorized_ids:
            fb_query = fb_query.where(Poem.id.notin_(memorized_ids))
        fallback_result = await db.execute(fb_query.order_by(func.random()).limit(limit))
        recommendations = fallback_result.scalars().all()
         
    return [
        {
            "id": str(p.id),
            "title": p.title,
            "author": p.author,
            "language": p.language,
            "difficulty": p.difficulty,
            "lines_count": p.lines_count,
            "themes": p.themes,
            "era": p.era
        } for p in recommendations
    ]

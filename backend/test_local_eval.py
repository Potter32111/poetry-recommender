import asyncio
import io
import json
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from app.database import get_db, DATABASE_URL
from app.models.memorization import Memorization
from app.models.poem import Poem
from app.models.user import User

async def run_eval():
    engine = create_async_engine(DATABASE_URL)
    async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
    
    async with async_session() as session:
        # Get the latest memorization attempt that has a voice score
        # Wait, we only save the score history, not the audio itself!
        print("Wait, we don't save the audio in the database...")
        
if __name__ == "__main__":
    asyncio.run(run_eval())

import logging
import asyncio
from typing import List, Optional

from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)

class MLService:
    _instance: Optional['MLService'] = None
    _model: Optional[SentenceTransformer] = None

    def __new__(cls) -> 'MLService':
        if cls._instance is None:
            cls._instance = super(MLService, cls).__new__(cls)
        return cls._instance

    def load_model(self) -> None:
        """Loads the sentence-transformers model if not already loaded."""
        if self._model is None:
            logger.info("Loading sentence-transformers model...")
            # We use a lightweight multilingual model that outputs 384d vectors
            self._model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
            logger.info("Model loaded successfully.")

    async def generate_embedding(self, text: str) -> List[float]:
        """Generates an embedding vector for the given text."""
        if self._model is None:
            # We run the loading in an executor to avoid blocking the event loop
            await asyncio.to_thread(self.load_model)
        
        # Encoding is a CPU bound task, better run it in a thread too
        embedding = await asyncio.to_thread(self._model.encode, text)
        return embedding.tolist()

ml_service = MLService()

"""API client for communicating with the backend."""

import httpx
from app.config import bot_settings


class APIClient:
    """Async HTTP client for the backend API."""

    def __init__(self) -> None:
        self.base_url = bot_settings.backend_url.rstrip("/")

    async def _request(self, method: str, path: str, **kwargs):
        async with httpx.AsyncClient(base_url=self.base_url, timeout=30.0) as client:
            resp = await client.request(method, path, **kwargs)
            resp.raise_for_status()
            return resp.json()

    async def create_user(self, telegram_id: int, username: str | None, first_name: str | None):
        return await self._request("POST", "/api/v1/users/", json={
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
        })

    async def get_user(self, telegram_id: int):
        return await self._request("GET", f"/api/v1/users/{telegram_id}")

    async def update_user(self, telegram_id: int, **kwargs):
        return await self._request("PATCH", f"/api/v1/users/{telegram_id}", json=kwargs)

    async def list_poems(self, language: str | None = None, limit: int = 20):
        params = {"limit": limit}
        if language:
            params["language"] = language
        return await self._request("GET", "/api/v1/poems/", params=params)

    async def get_poem(self, poem_id: str):
        return await self._request("GET", f"/api/v1/poems/{poem_id}")

    async def recommend_poem(self, telegram_id: int):
        return await self._request("POST", f"/api/v1/memorization/recommend/{telegram_id}")

    async def get_pgvector_recommendations(self, telegram_id: int, limit: int = 1):
        params = {"telegram_id": telegram_id, "limit": limit}
        return await self._request("GET", "/api/v1/recommendations/", params=params)

    async def review_poem(self, telegram_id: int, poem_id: str, score: int):
        return await self._request(
            "POST",
            f"/api/v1/memorization/review/{telegram_id}/{poem_id}",
            json={"score": score},
        )

    async def get_progress(self, telegram_id: int):
        return await self._request("GET", f"/api/v1/memorization/progress/{telegram_id}")

    async def get_due_reviews(self, telegram_id: int):
        return await self._request("GET", f"/api/v1/memorization/due/{telegram_id}")

    async def check_voice(self, telegram_id: int, poem_id: str, audio_bytes: bytes):
        """Upload voice audio and get memorization evaluation."""
        async with httpx.AsyncClient(base_url=self.base_url, timeout=60.0) as client:
            resp = await client.post(
                f"/api/v1/memorization/check-voice/{telegram_id}/{poem_id}",
                files={"audio": ("voice.ogg", audio_bytes, "audio/ogg")},
            )
            resp.raise_for_status()
            return resp.json()


api = APIClient()


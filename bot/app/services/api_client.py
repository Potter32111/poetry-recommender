"""API client for communicating with the backend."""

import logging

import httpx
from typing import Any
from app.config import bot_settings

logger = logging.getLogger(__name__)


class APIClient:
    """Async HTTP client for the backend API."""

    def __init__(self) -> None:
        self.base_url = bot_settings.backend_url.rstrip("/")
        self._client: httpx.AsyncClient | None = None
        self._voice_client: httpx.AsyncClient | None = None

    def _get_client(self) -> httpx.AsyncClient:
        """Lazily create the persistent HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(base_url=self.base_url, timeout=30.0)
        return self._client

    def _get_voice_client(self) -> httpx.AsyncClient:
        """Lazily create a separate client with longer timeout for voice."""
        if self._voice_client is None or self._voice_client.is_closed:
            self._voice_client = httpx.AsyncClient(base_url=self.base_url, timeout=60.0)
        return self._voice_client

    async def close(self) -> None:
        """Close persistent HTTP clients for graceful shutdown."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None
        if self._voice_client and not self._voice_client.is_closed:
            await self._voice_client.aclose()
            self._voice_client = None
        logger.info("APIClient connections closed")

    async def _request(self, method: str, path: str, **kwargs) -> Any:
        client = self._get_client()
        resp = await client.request(method, path, **kwargs)
        resp.raise_for_status()
        return resp.json()

    async def create_user(self, telegram_id: int, username: str | None, first_name: str | None) -> dict[str, Any]:
        try:
            user = await self._request("GET", f"/api/v1/users/{telegram_id}")
            return {**user, "_is_new": False}
        except httpx.HTTPStatusError as e:
            if e.response.status_code != 404:
                raise
        result = await self._request("POST", "/api/v1/users/", json={
            "telegram_id": telegram_id,
            "username": username,
            "first_name": first_name,
        })
        return {**result, "_is_new": True}

    async def get_user(self, telegram_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/users/{telegram_id}")

    async def get_leaderboard(self) -> list[dict[str, Any]]:
        """Fetch the top 10 users for the leaderboard."""
        return await self._request("GET", "/api/v1/users/leaderboard")

    async def get_all_users(self) -> list[dict[str, Any]]:
        """Fetch all users (for scheduler)."""
        return await self._request("GET", "/api/v1/users/all")

    async def update_user(self, telegram_id: int, **kwargs) -> dict[str, Any]:
        return await self._request("PATCH", f"/api/v1/users/{telegram_id}", json=kwargs)

    async def list_poems(
        self,
        language: str | None = None,
        limit: int = 20,
        offset: int = 0,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if language:
            params["language"] = language
        return await self._request("GET", "/api/v1/poems/", params=params)

    async def get_poem_count(self) -> dict[str, Any]:
        """Get total poem count."""
        return await self._request("GET", "/api/v1/poems/count")

    async def get_poem(self, poem_id: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/poems/{poem_id}")

    async def parse_poem(self, url: str) -> dict[str, Any]:
        return await self._request("POST", "/api/v1/poems/parse", json={"url": url})

    async def recommend_poem(self, telegram_id: int) -> dict[str, Any]:
        return await self._request("POST", f"/api/v1/memorization/recommend/{telegram_id}")

    async def get_pgvector_recommendations(
        self,
        telegram_id: int,
        mood: str | None = None,
        length: str | None = None,
        era: str | None = None,
        author: str | None = None,
        limit: int = 5,
    ) -> list[dict[str, Any]]:
        """Fetch highly personalized recommendations from the new PGVector endpoint."""
        params: dict[str, Any] = {"telegram_id": telegram_id, "limit": limit}
        if mood:
            params["mood"] = mood
        if length:
            params["length"] = length
        if era:
            params["era"] = era
        if author:
            params["author"] = author
        return await self._request("GET", "/api/v1/recommendations/", params=params)

    async def get_top_authors(self, limit: int = 6) -> list[dict[str, Any]]:
        """Fetch top authors by poem count."""
        return await self._request("GET", "/api/v1/poems/top-authors", params={"limit": limit})

    async def review_poem(self, telegram_id: int, poem_id: str, score: int) -> dict[str, Any]:
        return await self._request(
            "POST",
            f"/api/v1/memorization/review/{telegram_id}/{poem_id}",
            json={"score": score},
        )

    async def get_progress(self, telegram_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/memorization/progress/{telegram_id}")

    async def get_due_reviews(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._request("GET", f"/api/v1/memorization/due/{telegram_id}")
        
    async def get_all_due_reviews(self) -> list[dict[str, Any]]:
        """Fetch all telegram_ids that have poems due for review."""
        return await self._request("GET", "/api/v1/memorization/due/all")

    async def check_voice(self, telegram_id: int, poem_id: str, audio_bytes: bytes) -> dict[str, Any]:
        """Upload voice audio and get memorization evaluation."""
        client = self._get_voice_client()
        resp = await client.post(
            f"/api/v1/memorization/check-voice/{telegram_id}/{poem_id}",
            files={"audio": ("voice.ogg", audio_bytes, "audio/ogg")},
        )
        resp.raise_for_status()
        return resp.json()

    async def transcribe(self, telegram_id: int, audio_bytes: bytes) -> dict[str, Any]:
        """Upload voice audio for transcription only (no SM-2 update)."""
        client = self._get_voice_client()
        resp = await client.post(
            f"/api/v1/memorization/transcribe/{telegram_id}",
            files={"audio": ("voice.ogg", audio_bytes, "audio/ogg")},
        )
        resp.raise_for_status()
        return resp.json()

    async def check_text(
        self, telegram_id: int, poem_id: str, text: str, hints_used: int = 0
    ) -> dict[str, Any]:
        """Submit typed text for memorization evaluation."""
        return await self._request(
            "POST",
            f"/api/v1/memorization/check-text/{telegram_id}/{poem_id}",
            json={"text": text, "hints_used": hints_used},
        )

    async def skip_poem(self, telegram_id: int, poem_id: str) -> dict[str, Any]:
        """Record a skipped poem to prevent immediate re-recommendation."""
        return await self._request(
            "POST",
            "/api/v1/recommendations/skip",
            params={"telegram_id": telegram_id, "poem_id": poem_id},
        )

    async def reset_progress(self, telegram_id: int) -> dict[str, Any]:
        """Delete all user memorization data and reset XP/level/streak."""
        return await self._request("DELETE", f"/api/v1/users/{telegram_id}/progress")

    # ─── Favorites ───────────────────────────────────────────

    async def add_favorite(self, telegram_id: int, poem_id: str) -> dict[str, Any]:
        return await self._request("POST", f"/api/v1/favorites/{telegram_id}/{poem_id}")

    async def remove_favorite(self, telegram_id: int, poem_id: str) -> None:
        client = self._get_client()
        resp = await client.request("DELETE", f"/api/v1/favorites/{telegram_id}/{poem_id}")
        resp.raise_for_status()

    async def list_favorites(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._request("GET", f"/api/v1/favorites/{telegram_id}")

    async def is_favorite(self, telegram_id: int, poem_id: str) -> bool:
        data = await self._request("GET", f"/api/v1/favorites/{telegram_id}/{poem_id}/check")
        return data.get("is_favorite", False)

    # ─── History ─────────────────────────────────────────────

    async def get_history(
        self, telegram_id: int, limit: int = 10, offset: int = 0, status: str | None = None,
    ) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"limit": limit, "offset": offset}
        if status:
            params["status"] = status
        return await self._request(
            "GET", f"/api/v1/memorization/history/{telegram_id}", params=params,
        )

    # ─── Collections ─────────────────────────────────────────

    async def list_collections(self) -> list[dict[str, Any]]:
        return await self._request("GET", "/api/v1/collections/")

    async def get_collection(self, slug: str) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/collections/{slug}")

    # ─── Engagement ──────────────────────────────────────────

    async def get_achievements(self, telegram_id: int) -> list[dict[str, Any]]:
        return await self._request("GET", f"/api/v1/engagement/achievements/{telegram_id}")

    async def get_today_challenge(self, telegram_id: int) -> dict[str, Any]:
        return await self._request("GET", f"/api/v1/engagement/challenges/{telegram_id}/today")

    async def get_poem_tts(self, poem_id: str) -> bytes:
        """Fetch TTS audio bytes for a poem."""
        client = self._get_voice_client()
        resp = await client.post(f"/api/v1/engagement/poems/{poem_id}/tts")
        resp.raise_for_status()
        return resp.content


api = APIClient()


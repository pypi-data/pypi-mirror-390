from __future__ import annotations

import asyncio
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict


class CacheEntry(BaseModel):
    model_config = ConfigDict(extra="ignore")

    expires_at: datetime
    payload: Any

    @property
    def expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.expires_at


class JsonCache:
    def __init__(self, cache_file: Path):
        self._cache_file = cache_file
        self._lock = asyncio.Lock()

    async def read(self, key: str) -> Optional[CacheEntry]:
        async with self._lock:
            data = await self._load()
            raw = data.get(key)
            if not raw:
                return None
            try:
                entry = CacheEntry.model_validate(raw)
            except Exception:
                return None
            return entry

    async def write(self, key: str, payload: Any, ttl: timedelta) -> CacheEntry:
        expires_at = datetime.now(timezone.utc) + ttl
        entry = CacheEntry(expires_at=expires_at, payload=payload)
        async with self._lock:
            data = await self._load()
            data[key] = {
                "expires_at": entry.expires_at.isoformat(),
                "payload": entry.payload,
            }
            await self._dump(data)
        return entry

    async def clear(self, key: Optional[str] = None) -> None:
        async with self._lock:
            if not self._cache_file.exists():
                return
            if key is None:
                try:
                    await asyncio.to_thread(self._cache_file.unlink)
                except FileNotFoundError:
                    pass
                return
            data = await self._load()
            if key in data:
                del data[key]
                await self._dump(data)

    async def _load(self) -> Dict[str, Any]:
        if not self._cache_file.exists():
            if not self._cache_file.parent.exists():
                await asyncio.to_thread(self._cache_file.parent.mkdir, parents=True, exist_ok=True)
            return {}
        try:
            text = await asyncio.to_thread(self._cache_file.read_text)
        except FileNotFoundError:
            return {}
        if not text.strip():
            return {}
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {}

    async def _dump(self, data: Dict[str, Any]) -> None:
        text = json.dumps(data, ensure_ascii=False, indent=2)
        await asyncio.to_thread(self._cache_file.write_text, text)


DEFAULT_TTLS: Dict[str, timedelta] = {
    "courses": timedelta(minutes=15),
    "announcements": timedelta(minutes=10),
    "grades": timedelta(minutes=10),
    "todo": timedelta(minutes=5),
    "content_tree": timedelta(minutes=30),
    "content_verbose": timedelta(minutes=30),
}

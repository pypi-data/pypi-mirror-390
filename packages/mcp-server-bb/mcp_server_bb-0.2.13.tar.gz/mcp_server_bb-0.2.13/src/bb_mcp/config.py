from __future__ import annotations

from pathlib import Path

import os
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    bb_username: str = Field(..., init=False)
    bb_password: str = Field(..., init=False)
    bb_base_url: str = Field(default_factory=lambda: os.getenv("BB_BASE_URL", "https://bb.cuhk.edu.cn"))

    cache_dir: Path = Field(default_factory=lambda: Path(os.getenv("BB_MCP_CACHE_DIR", Path.home() / ".bb_mcp")))
    @property
    def cache_file(self) -> Path:
        return self.cache_dir / "bb_mcp_cache.json"

    def validate_settings(self) -> None:
        if not self.bb_username or not self.bb_password:
            raise ValueError("BB_USERNAME and BB_PASSWORD must be set in environment variables.")

    class Config:
        extra = "ignore"
        env_file = ".env"
        env_file_encoding = "utf-8"


def get_settings() -> Settings:
    settings = Settings()
    return settings

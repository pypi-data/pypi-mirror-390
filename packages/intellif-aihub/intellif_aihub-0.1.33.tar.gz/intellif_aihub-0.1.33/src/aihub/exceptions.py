from __future__ import annotations

from typing import Any, Optional


class SDKError(Exception):
    pass


class APIError(SDKError):
    def __init__(self, message: str, *, status: Optional[int] = None, detail: Any = None) -> None:
        super().__init__(message)
        self.message: str = message
        self.status: Optional[int] = status
        self.detail: Any = detail

    def __str__(self) -> str:
        if self.status == 401:
            return "请检查您的凭证信息，可能已经过期。"
        return f"[HTTP {self.status}] {self.message}" if self.status else self.message

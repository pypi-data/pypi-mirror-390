from __future__ import annotations

from typing import Optional
import httpx


class TigrmailError(Exception):
    """Custom error wrapping HTTP/transport issues with friendly context."""

    def __init__(self, *, error: BaseException, general_message: str = "") -> None:
        tech_message = self._extract_message(error)
        final = (
            f"\n\n  🐅 [Message]:\n"
            f"      {general_message or tech_message}\n\n"
            f"  🐅 [Details]:\n"
            f"      {tech_message}\n"
        )
        super().__init__(final)
        self.generalMessage = general_message or tech_message
        self.techMessage = tech_message

    @staticmethod
    def _extract_message(error: BaseException) -> str:
        # httpx transport error
        if isinstance(error, httpx.HTTPStatusError):
            status = f"[{error.response.status_code}]"
            try:
                data = error.response.json()
                if isinstance(data, dict) and "error" in data and isinstance(data["error"], str):
                    return f"{status} {data['error']}"
            except Exception:
                pass
            return f"{status} {error.response.text.strip() or error.args[0]}"

        if isinstance(error, httpx.RequestError):
            return str(error)

        return str(error)


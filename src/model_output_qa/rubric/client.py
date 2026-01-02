"""Stub client for eval-rubric-api integration."""

from __future__ import annotations

import os
from typing import Any

import httpx

DEFAULT_RUBRIC_BASE_URL = "http://127.0.0.1:8080"


class RubricClient:
    """HTTP client for optional rubric scoring after validation passes."""

    def __init__(self, base_url: str | None = None, *, timeout: float = 10.0) -> None:
        self.base_url = (base_url or os.environ.get("RUBRIC_API_URL", DEFAULT_RUBRIC_BASE_URL)).rstrip("/")
        self.timeout = timeout

    def health(self) -> dict[str, str]:
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.get("/health")
            response.raise_for_status()
            return response.json()

    def score(self, answer: str, rubric: dict[str, str]) -> dict[str, Any]:
        """POST /score on eval-rubric-api (stub-friendly; raises on connection errors)."""
        with httpx.Client(base_url=self.base_url, timeout=self.timeout) as client:
            response = client.post("/score", json={"answer": answer, "rubric": rubric})
            response.raise_for_status()
            return response.json()

    def score_if_available(self, answer: str, rubric: dict[str, str]) -> dict[str, Any] | None:
        """Best-effort score; returns None when the rubric service is unreachable."""
        try:
            return self.score(answer, rubric)
        except (httpx.HTTPError, OSError):
            return None

    def score_batch(
        self,
        items: list[dict[str, Any]],
        *,
        rubric: dict[str, str],
    ) -> list[dict[str, Any] | None]:
        """Score many answers; skips unreachable service per item."""
        results: list[dict[str, Any] | None] = []
        for item in items:
            answer = str(item.get("answer", ""))
            if not answer:
                results.append(None)
                continue
            results.append(self.score_if_available(answer, rubric))
        return results

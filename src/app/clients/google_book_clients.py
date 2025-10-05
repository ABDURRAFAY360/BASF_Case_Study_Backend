from __future__ import annotations

from typing import Any, Dict, List

import httpx


class GoogleBooksClient:
    """
    Minimal async client for Google Books API.
    Refactor note: logic and defaults are unchanged; code is decomposed for clarity.
    """

    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, timeout: int = 10) -> None:
        # Keep the same default timeout and client lifecycle.
        self.client = httpx.AsyncClient(timeout=timeout)

    # -------------------------------------------------------------------------
    # Public API
    # -------------------------------------------------------------------------
    async def search_books(
        self, query: str, max_results: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Fetch books for a query.
        - Raises for non-2xx responses (same as original via raise_for_status()).
        - Returns a list of dicts with keys: title, author, genre.
        """
        params = self._build_search_params(query=query, max_results=max_results)
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()

        data = response.json()
        items = data.get("items", [])
        return self._parse_items(items)

    async def close(self) -> None:
        """Close the underlying HTTP client."""
        await self.client.aclose()

    # -------------------------------------------------------------------------
    # Internal helpers
    # -------------------------------------------------------------------------
    @staticmethod
    def _build_search_params(*, query: str, max_results: int) -> Dict[str, Any]:
        """Keep parameter names and semantics identical to the original."""
        return {"q": query, "maxResults": max_results}

    def _parse_items(self, items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Map raw Google Books items to the minimal shape used by the app.
        (Preserves original defaults and indexing behavior.)
        """
        return [self._parse_item(item) for item in items]

    @staticmethod
    def _parse_item(item: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract title, author(s), and first category exactly like the original:
        - title: "Unknown" fallback
        - author: join with ", " or "Unknown"
        - genre: first element of categories, with ["General"][0] fallback
          Note: if the API returns an empty list for categories, this will raise
          IndexError just like the original code. We intentionally preserve that.
        """
        info = item["volumeInfo"]  # original relied on "volumeInfo" existing
        title = info.get("title", "Unknown")
        author = ", ".join(info.get("authors", ["Unknown"]))
        genre = info.get("categories", ["General"])[0]
        return {"title": title, "author": author, "genre": genre}

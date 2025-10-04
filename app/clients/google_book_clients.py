import httpx
from typing import Any, Dict, List

class GoogleBooksClient:
    BASE_URL = "https://www.googleapis.com/books/v1/volumes"

    def __init__(self, timeout: int = 10):
        self.client = httpx.AsyncClient(timeout=timeout)

    async def search_books(self, query: str, max_results: int = 20) -> List[Dict[str, Any]]:
        """Fetch books from Google Books API."""
        params = {"q": query, "maxResults": max_results}
        response = await self.client.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        items = data.get("items", [])
        return [
            {
                "title": item["volumeInfo"].get("title", "Unknown"),
                "author": ", ".join(item["volumeInfo"].get("authors", ["Unknown"])),
                "genre": item["volumeInfo"].get("categories", ["General"])[0],
            }
            for item in items
        ]

    async def close(self):
        await self.client.aclose()

import pytest
from app.clients.google_book_clients import GoogleBooksClient


@pytest.mark.asyncio
async def test_search_books(monkeypatch):
    async def fake_get(url, params):
        class FakeResponse:
            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "items": [
                        {
                            "volumeInfo": {
                                "title": "Book1",
                                "authors": ["A1"],
                                "categories": ["Tech"],
                            }
                        },
                        {
                            "volumeInfo": {
                                "title": "Book2",
                                "authors": ["A2"],
                                "categories": ["Fiction"],
                            }
                        },
                    ]
                }

        return FakeResponse()

    client = GoogleBooksClient()
    monkeypatch.setattr(client.client, "get", fake_get)

    results = await client.search_books("python", 2)
    await client.close()

    assert len(results) == 2
    assert results[0]["title"] == "Book1"

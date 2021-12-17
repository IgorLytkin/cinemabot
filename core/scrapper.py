from abc import ABC, abstractmethod
from typing import Optional, Any

import aiohttp


class Scrapper(ABC):

    @abstractmethod
    async def get_top_link(self, query: str, cite: Optional[str]) -> Optional[str]:
        pass


class GoogleRestScrapper(Scrapper):
    search_endpoint: str = "https://serpapi.com/search.json"

    def __init__(self, api_key: str):
        self.api_key = api_key

    async def get_top_link(self, query: str, cite: Optional[str]) -> Optional[str]:
        params = {
            'q': f'site:{cite} {query}' if cite else query,
            'api_key': self.api_key
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.search_endpoint, params=params) as response:
                response_json = await response.json()
                return self._get_top_link(response_json)

    @staticmethod
    def _get_top_link(json: dict[str, Any]) -> Optional[str]:
        return json.get('organic_results')[0].get('link')

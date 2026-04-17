import httpx
from typing import Optional, Dict, List
from config import FOOTBALL_DATA_KEY, CACHE_TTL
import time

# Простой in-memory кеш (можно заменить на Redis или базу)
_cache: Dict[str, tuple] = {}  # key -> (data, timestamp)


def _is_cached(key: str) -> bool:
    if key not in _cache:
        return False
    data, timestamp = _cache[key]
    return (time.time() - timestamp) < CACHE_TTL


def _get_from_cache(key: str) -> Optional[Dict]:
    if _is_cached(key):
        return _cache[key][0]
    return None


def _set_cache(key: str, data: Dict):
    _cache[key] = (data, time.time())


class FootballDataClient:
    BASE_URL = "https://api.football-data.org/v4"

    def __init__(self, api_key: str = FOOTBALL_DATA_KEY):
        if not api_key:
            raise ValueError("API key for football-data.org is required")
        self.api_key = api_key
        self.headers = {"X-Auth-Token": api_key}

    async def _request(self, endpoint: str, params: dict = None) -> dict:
        """Выполняет GET-запрос к API с кешированием."""
        cache_key = f"{endpoint}:{str(params)}"
        cached = _get_from_cache(cache_key)
        if cached:
            return cached

        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.BASE_URL}/{endpoint}",
                    headers=self.headers,
                    params=params,
                    timeout=10.0
                )
                response.raise_for_status()
                data = response.json()
                _set_cache(cache_key, data)
                return data
            except httpx.HTTPStatusError as e:
                raise Exception(f"API error: {e.response.status_code} - {e.response.text}")
            except httpx.RequestError as e:
                raise Exception(f"Request failed: {str(e)}")

    async def get_competitions(self) -> list:
        """Получает список доступных соревнований."""
        data = await self._request("competitions")
        return data.get("competitions", [])

    async def get_matches_by_competition(self, competition_id: int, status: str = "SCHEDULED") -> list:
        """Получает матчи для данного соревнования."""
        params = {"status": status}
        data = await self._request(f"competitions/{competition_id}/matches", params=params)
        return data.get("matches", [])

    async def get_team_info(self, team_id: int) -> dict:
        """Получает информацию о команде."""
        data = await self._request(f"teams/{team_id}")
        return data.get("team", {})

    async def get_match_details(self, match_id: int) -> dict:
        """Получает детали конкретного матча."""
        data = await self._request(f"matches/{match_id}")
        return data.get("match", {})


# Экспортируем экземпляр для удобства (если нужен single instance)
# client = FootballDataClient()
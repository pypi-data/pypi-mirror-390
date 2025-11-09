from typing import List, Literal
from urllib.parse import quote

import httpx

from kuryana.base import BASE_KURYANA_API_URL, BaseClient
from kuryana.types.drama import DramaQuery
from kuryana.types.drama_cast import DramaCastQuery
from kuryana.types.drama_episodes import DramaEpisodesQuery
from kuryana.types.drama_reviews import DramaReviewsQuery
from kuryana.types.index import ApiGet
from kuryana.types.list import ListQuery
from kuryana.types.people import PeopleQuery
from kuryana.types.search import SearchResultQuery
from kuryana.types.seasonal_drama import SeasonalDrama, SeasonalDramaQuery
from kuryana.types.user import UserQuery


class Kuryana(BaseClient):
    def __init__(self, base_url: str | None = None) -> None:
        self._retry_count = 3
        self.client = httpx.Client(base_url=base_url or BASE_KURYANA_API_URL)

    def _request(self, endpoint: str, **kwargs) -> httpx.Response:
        response = None
        retry_count = int(kwargs.pop("retry_count", self._retry_count))

        for _ in range(retry_count):
            response = self.client.get(endpoint)
            if response.status_code == 200:
                return response

        if response is None:
            raise httpx.RequestError("Failed to make request after retries.")

        response.raise_for_status()
        return response

    def get(self) -> ApiGet:
        """
        Get API
        """

        response = self._request("/")
        return self._parse_response(response.text, class_type=ApiGet)

    def search(self, query: str) -> SearchResultQuery:
        """
        Search for Drama / People with query
        """

        response = self._request(f"/search/q/{quote(query)}")
        return self._parse_response(response.text, class_type=SearchResultQuery)

    def get_drama(self, slug: str) -> DramaQuery:
        """
        Get Drama by Slug
        """

        response = self._request(f"/id/{quote(slug)}")
        return self._parse_response(response.text, class_type=DramaQuery)

    def get_drama_cast(self, slug: str) -> DramaCastQuery:
        """
        Get Drama Cast by Slug
        """

        response = self._request(f"/id/{quote(slug)}/cast")
        return self._parse_response(response.text, class_type=DramaCastQuery)

    def get_drama_episodes(self, slug: str) -> DramaEpisodesQuery:
        """
        Get Drama Episodes by Slug
        """

        response = self._request(f"/id/{quote(slug)}/episodes")
        return self._parse_response(response.text, class_type=DramaEpisodesQuery)

    def get_drama_reviews(self, slug: str, page: int = 1) -> DramaReviewsQuery:
        """
        Get Drama Reviews by Slug
        """

        if page < 1:
            raise ValueError("Page number must be greater than 0.")

        response = self._request(f"/id/{quote(slug)}/reviews?page={page}")
        return self._parse_response(response.text, class_type=DramaReviewsQuery)

    def get_people(self, slug_id: str) -> PeopleQuery:
        """
        Get People by ID
        """

        response = self._request(f"/people/{quote(slug_id)}")
        return self._parse_response(response.text, class_type=PeopleQuery)

    def get_user(self, user_id: str) -> UserQuery:
        """
        Get User by ID
        """

        response = self._request(f"/dramalist/{quote(user_id)}")
        return self._parse_response(response.text, class_type=UserQuery)

    def get_list(self, list_id: str) -> ListQuery:
        """
        Get Public Lists by ID
        """

        response = self._request(f"/list/{quote(list_id)}")
        return self._parse_response(response.text, class_type=ListQuery)

    def get_seasonal_drama(
        self, season: Literal[1, 2, 3, 4], year: int
    ) -> List[SeasonalDrama]:
        """
        Get Seasonal Drama by Year and Season

        Season: 1 = Winter, 2 = Spring, 3 = Summer, 4 = Fall
        """

        response = self._request(f"/seasonal/{year}/{season}")
        return self._parse_array_response(
            response.text, adapter_type=SeasonalDramaQuery
        )

import pytest

from kuryana import AsyncKuryana

# Real MDL slugs for testing (want real data)
TEST_MDLSlug = "18452-goblin"
TEST_MDLPersonSlug = "274-lee-dong-wook"
TEST_MDLUserSlug = "eggomochi"  # (if you are the user, you can request to remove)
TEST_MDLListId = "1xraljv3"


class TestAsyncKuryanaClient:
    def setup_method(self):
        self.client = AsyncKuryana()

    @pytest.mark.asyncio
    async def test_get_api(
        self,
    ):
        response = await self.client.get()
        assert response is not None
        assert "MDL Scraper API" in response.message

    @pytest.mark.asyncio
    async def test_search(self):
        query = "goblin"
        response = await self.client.search(query)
        assert response is not None
        assert len(response.results.dramas) > 0

    @pytest.mark.asyncio
    async def test_get_dram(self):
        response = await self.client.get_drama(TEST_MDLSlug)
        assert response is not None
        assert response.data.title != ""

    @pytest.mark.asyncio
    async def test_get_drama_cast(self):
        response = await self.client.get_drama_cast(TEST_MDLSlug)
        assert response is not None
        assert len(response.data.casts) > 0

    @pytest.mark.asyncio
    async def test_get_drama_episodes(self):
        response = await self.client.get_drama_episodes(TEST_MDLSlug)
        assert response is not None
        assert len(response.data.episodes) > 0

    @pytest.mark.asyncio
    async def test_get_drama_reviews(self):
        response = await self.client.get_drama_reviews(TEST_MDLSlug)
        assert response is not None
        assert len(response.data.reviews) > 0

    @pytest.mark.asyncio
    async def test_get_people(self):
        response = await self.client.get_people(TEST_MDLPersonSlug)
        assert response is not None
        assert response.data.name != ""

    @pytest.mark.asyncio
    async def test_get_user(self):
        response = await self.client.get_user(TEST_MDLUserSlug)
        assert response is not None
        assert response.data.link != ""

    @pytest.mark.asyncio
    async def test_get_list(self):
        response = await self.client.get_list(TEST_MDLListId)
        assert response is not None
        assert len(response.data.list) > 0

    @pytest.mark.asyncio
    async def test_get_seasonal_dramas(self):
        response = await self.client.get_seasonal_drama(2, 2024)
        assert response is not None
        assert len(response) > 0

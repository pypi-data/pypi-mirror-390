from kuryana import Kuryana

# Real MDL slugs for testing (want real data)
TEST_MDLSlug = "18452-goblin"
TEST_MDLPersonSlug = "274-lee-dong-wook"
TEST_MDLUserSlug = "eggomochi"  # (if you are the user, you can request to remove)
TEST_MDLListId = "1xraljv3"


class TestKuryanaClient:
    def setup_method(self):
        self.client = Kuryana()

    def test_get_api(
        self,
    ):
        response = self.client.get()
        assert response is not None
        assert "MDL Scraper API" in response.message

    def test_search(self):
        query = "goblin"
        response = self.client.search(query)
        assert response is not None
        assert len(response.results.dramas) > 0

    def test_get_dram(self):
        response = self.client.get_drama(TEST_MDLSlug)
        assert response is not None
        assert response.data.title != ""

    def test_get_drama_cast(self):
        response = self.client.get_drama_cast(TEST_MDLSlug)
        assert response is not None
        assert len(response.data.casts) > 0

    def test_get_drama_episodes(self):
        response = self.client.get_drama_episodes(TEST_MDLSlug)
        assert response is not None
        assert len(response.data.episodes) > 0

    def test_get_drama_reviews(self):
        response = self.client.get_drama_reviews(TEST_MDLSlug)
        assert response is not None
        assert len(response.data.reviews) > 0

    def test_get_people(self):
        response = self.client.get_people(TEST_MDLPersonSlug)
        assert response is not None
        assert response.data.name != ""

    def test_get_user(self):
        response = self.client.get_user(TEST_MDLUserSlug)
        assert response is not None
        assert response.data.link != ""

    def test_get_list(self):
        response = self.client.get_list(TEST_MDLListId)
        assert response is not None
        assert len(response.data.list) > 0

    def test_get_seasonal_dramas(self):
        response = self.client.get_seasonal_drama(2, 2024)
        assert response is not None
        assert len(response) > 0

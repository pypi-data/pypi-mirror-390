from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DramaEpisodesEpisode(BaseModel):
    title: str
    image: str
    link: str
    rating: Optional[str] = None
    air_date: Optional[str] = None


class DramaEpisodesData(BaseModel):
    title: str
    episodes: list[DramaEpisodesEpisode]


class DramaEpisodesQuery(BaseModel):
    slug_query: str
    data: DramaEpisodesData
    scrape_date: datetime

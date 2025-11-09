from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class DramaCast(BaseModel):
    name: str
    profile_image: str
    slug: str
    link: str


class DramaDetails(BaseModel):
    country: str
    type: str
    episodes: str
    aired: str
    original_network: str
    duration: str
    score: str
    ranked: str
    popularity: str
    content_rating: str
    watchers: str
    favorites: str


class DramaOthers(BaseModel):
    related_content: List[str]
    native_title: List[str]
    also_known_as: List[str]
    genres: List[str]
    tags: List[str]


class DramaData(BaseModel):
    link: str
    title: str
    complete_title: str
    sub_title: str
    year: Optional[str] = None
    rating: float
    poster: str
    synopsis: str
    casts: List[DramaCast]
    details: DramaDetails
    others: DramaOthers


class DramaQuery(BaseModel):
    slug_query: str
    data: DramaData
    scrape_date: datetime

from typing import List, Optional

from pydantic import BaseModel, TypeAdapter


class SeasonalDrama(BaseModel):
    id: int
    title: str
    episodes: Optional[int] = None
    ranking: int
    popularity: int
    country: str
    content_type: str
    type: str
    synopsis: Optional[str] = None
    released_at: str
    url: str
    genres: str
    thumbnail: str
    cover: str
    rating: float
    timezone: str
    add_status: bool


SeasonalDramaQuery = TypeAdapter(List[SeasonalDrama])

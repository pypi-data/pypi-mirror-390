from datetime import datetime
from typing import List, Optional, Union

from pydantic import BaseModel


class SearchDrama(BaseModel):
    slug: str
    thumb: str
    mdl_id: str
    title: str
    ranking: Optional[str] = None
    type: str
    year: Optional[int] = None
    series: Union[bool, str]


class SearchPerson(BaseModel):
    slug: str
    thumb: str
    name: str
    nationality: str


class SearchResults(BaseModel):
    dramas: List[SearchDrama]
    people: List[SearchPerson]


class SearchResultQuery(BaseModel):
    query: str
    results: SearchResults
    scrape_date: datetime

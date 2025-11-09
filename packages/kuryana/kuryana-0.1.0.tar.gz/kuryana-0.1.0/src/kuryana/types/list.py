from typing import List

from pydantic import BaseModel


class ListDataItem(BaseModel):
    title: str
    image: str
    rank: str
    url: str
    slug: str
    type: str
    year: str
    episodes: int
    short_summary: str


class ListData(BaseModel):
    link: str
    title: str
    description: str
    list: List[ListDataItem]


class ListQuery(BaseModel):
    slug_query: str
    data: ListData
    scrape_date: str

from datetime import datetime
from typing import Dict, List, Optional

from pydantic import BaseModel


class DramaCastRoleClass(BaseModel):
    name: str
    type: str


class DramaCastRole(BaseModel):
    name: str
    profile_image: str
    slug: str
    link: str
    role: Optional[DramaCastRoleClass] = None


class DramaCastData(BaseModel):
    link: str
    title: str
    poster: str
    casts: Dict[str, List[DramaCastRole]]


class DramaCastQuery(BaseModel):
    slug_query: str
    data: DramaCastData
    scrape_date: datetime

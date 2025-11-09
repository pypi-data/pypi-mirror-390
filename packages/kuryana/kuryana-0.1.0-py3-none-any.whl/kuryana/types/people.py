from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field


class PeopleRole(BaseModel):
    name: str
    type: str


class PeopleTitle(BaseModel):
    link: str
    name: str


class PeopleDrama(BaseModel):
    _slug: str
    year: int
    title: PeopleTitle
    rating: float
    role: PeopleRole
    episodes: Optional[int] = None


class PeopleDetails(BaseModel):
    name: str
    native_name: str
    given_name: Optional[str] = None
    also_known_as: str
    nationality: str
    gender: str
    born: str
    age: str


class PeopleWorks(BaseModel):
    Drama: List[PeopleDrama]
    Movie: List[PeopleDrama]
    tv_show: List[PeopleDrama] = Field(alias="TV Show")


class PeopleData(BaseModel):
    link: str
    name: str
    about: str
    profile: str
    works: Union[PeopleWorks, Dict[str, List[PeopleDrama]]]
    details: PeopleDetails


class PeopleQuery(BaseModel):
    slug_query: str
    data: PeopleData
    scrape_date: str

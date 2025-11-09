from datetime import datetime
from typing import Dict, List, Union

from pydantic import BaseModel, Field


class UserDataStats(BaseModel):
    Dramas: str
    TV_Shows: str = Field(alias="TV Shows")
    Episodes: str
    Movies: str
    Days: str


class UserDataListItem(BaseModel):
    name: str
    id: str
    score: str
    episode_seen: str
    episode_total: str


class UserDataListGroup(BaseModel):
    items: List[UserDataListItem]
    stats: Union[UserDataStats, Dict[str, str]]


class UserDataList(BaseModel):
    Completed: UserDataListGroup
    Plan_to_Watch: UserDataListGroup = Field(alias="Plan to Watch")
    On_hold: UserDataListGroup = Field(alias="On-hold")
    Dropped: UserDataListGroup


class UserData(BaseModel):
    link: str
    list: Union[UserDataList, Dict[str, UserDataListGroup]]


class UserQuery(BaseModel):
    slug_query: str
    data: UserData
    scrape_date: datetime

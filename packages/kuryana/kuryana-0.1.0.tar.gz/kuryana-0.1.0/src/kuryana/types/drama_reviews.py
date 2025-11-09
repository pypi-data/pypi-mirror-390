from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DramaReviewsReviewer(BaseModel):
    name: str
    user_link: str
    user_image: str
    info: str


class DramaReviewsReview(BaseModel):
    reviewer: DramaReviewsReviewer
    review: Optional[list[str]] = None
    ratings: Optional[dict[str, float]] = None


class DramaReviewsData(BaseModel):
    link: str
    title: str
    poster: str
    reviews: list[DramaReviewsReview]


class DramaReviewsQuery(BaseModel):
    slug_query: str
    data: DramaReviewsData
    scrape_date: datetime

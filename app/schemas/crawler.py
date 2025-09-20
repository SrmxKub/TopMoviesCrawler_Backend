from pydantic import BaseModel, HttpUrl
from typing import List, Optional

class Cast(BaseModel):
    name: str
    role: Optional[str] = None
    img: Optional[HttpUrl] = None

class MovieBase(BaseModel):
    index: int
    rating: int
    title: str
    year: int
    link: HttpUrl

class MovieDetails(MovieBase):
    genre: Optional[str] = None
    description: Optional[str] = None
    poster_img: Optional[HttpUrl] = None
    cover_img: Optional[HttpUrl] = None
    release_date: Optional[str] = None
    tomato_score: Optional[int] = None
    tomato_reviews: Optional[int] = None
    audience_score: Optional[int] = None
    audience_ratings: Optional[int] = None
    cast: Optional[List[Cast]] = None

class UpdateResponse(BaseModel):
    status: str
    message: str

class SearchResponse(BaseModel):
    status: str
    message: str
    count: int
    movies: List[MovieDetails]

from pydantic import BaseModel, HttpUrl, field_validator
from typing import List, Optional, Any


def validate_url(v: Any):
    if v in (None, "none", "", "null", "None"):
        return None
    return v

class Cast(BaseModel):
    name: str
    role: Optional[str] = None
    img: Optional[HttpUrl] = None
    
    @field_validator("img", mode="before")
    def validate_img(cls, v):
        return validate_url(v)

class MovieBase(BaseModel):
    index: int
    rating: float
    title: str
    year: int
    link: HttpUrl
    
    @field_validator("link", mode="before")
    def validate_link(cls, v):
        return validate_url(v)

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
    cast_crew: Optional[List[Cast]] = None
    
    @field_validator("poster_img", "cover_img", mode="before")
    def validate_images(cls, v):
        return validate_url(v)

class UpdateMoviesResponse(BaseModel):
    movies: List[MovieDetails]

class SearchMoviesResponse(BaseModel):
    count: int
    movies: List[MovieDetails]

class GenreListResponse(BaseModel):
    genres: List[str]
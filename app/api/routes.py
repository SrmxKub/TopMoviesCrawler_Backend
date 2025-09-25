from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.movie import MovieService
from app.services.export import ExportService
from app.schemas.crawler import *
from app.schemas.exceptions import *


# Health Router
health_router = APIRouter(tags=["Health Check"])

@health_router.get("/")
async def health_check():
    """Health check endpoint."""
    return {"message": "Top Movies Crawler API is Running"}



# Movies Router
movies_router = APIRouter(prefix="/movies", tags=["Movies"])
movies_service = MovieService()

# comment update moveis csv
# @movies_router.post("/update", response_model=UpdateMoviesResponse)
# def update_movies():
#     """Trigger update movie database (scraping + save to CSV)."""
#     return movies_service.update_movie_database()

# use this as main crawler endpoint
@movies_router.get("/", response_model=SearchMoviesResponse)
def search_movies(
    name: Optional[str] = None,
    genre: Optional[List[str]] = Query(default=None)
):
    """Search movies live by name or genre."""
    return movies_service.search_movies_live(name=name, genre=genre or [])

@movies_router.get("/{movie_name}", response_model=MovieDetails)
def get_movie_details(movie_name: str):
    return movies_service.get_movie_details(movie_name)

@movies_router.get("/genres", response_model=GenreListResponse)
def get_all_genres():
    """List all available genres in the movie database."""
    return movies_service.get_all_genres()


# Export Router
# export_router = APIRouter(prefix="/movies/export", tags=["Export"])
# export_service = ExportService()

# @export_router.get("/csv")
# def download_csv():
#     """Download the movie database CSV."""
#     return export_service.export_csv()


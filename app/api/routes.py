from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from app.services.movie import MovieService
from app.services.export import ExportService
from app.schemas.crawler import UpdateResponse, SearchResponse


# Health Router
health_router = APIRouter(prefix="/health", tags=["Health Check"])

@health_router.get("/")
async def health_check():
    return {"status": "ok"}



# Movies Router
movies_router = APIRouter(prefix="/movies", tags=["Movies"])
movies_service = MovieService()

@movies_router.post("/update", response_model=UpdateResponse)
def update_movies():
    """Trigger update movie database (scraping + save to CSV)."""
    return movies_service.update_movie_database()

@movies_router.get("/search", response_model=SearchResponse)
def search_movies(
    name: Optional[str] = None,
    genre: Optional[List[str]] = Query(default=None)
):
    """Search movies live by name or genre."""
    return movies_service.search_movies_live(name=name, genre=genre or [])



# Export Router
export_router = APIRouter(prefix="/movies/export", tags=["Export"])
export_service = ExportService()

@export_router.get("/csv")
def download_csv():
    """Download the movie database CSV."""
    try:
        return export_service.export_csv()
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


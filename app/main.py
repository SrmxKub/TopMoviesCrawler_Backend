from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import *

app = FastAPI(title="Top Movies Crawler API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # only for dev
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers
app.include_router(health_router)
app.include_router(movies_router)
# app.include_router(export_router) 

# Global Exception Handlers
@app.exception_handler(NotFoundError)
async def not_found_handler(_: Request, exc: NotFoundError):
    return JSONResponse(
        status_code=404,
        content={
            "detail": str(exc),
            # "endpoint": f"{request.method} {request.url.path}"
        }
    )

@app.exception_handler(ScraperError)
async def scraper_error_handler(_: Request, exc: ScraperError):
    return JSONResponse(
        status_code=500,
        content={
            "detail": str(exc),
            # "endpoint": f"{request.method} {request.url.path}"
        }
    )
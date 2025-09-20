from fastapi import FastAPI
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
app.include_router(export_router) 
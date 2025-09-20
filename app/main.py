from fastapi import FastAPI
from app.api.routes import *

app = FastAPI(title="Top Movies Crawler API")

# Include all routers
app.include_router(health_router)
app.include_router(movies_router)
app.include_router(export_router) 
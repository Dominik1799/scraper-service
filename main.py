import uvicorn
from fastapi import FastAPI
from settings import ROOT_PATH
from routers import scraper_router, request_router
from contextlib import asynccontextmanager
from databases import mongo
import logging

logging.getLogger("httpx").setLevel(logging.WARNING)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    mongo.ensure_initialized_db()
    yield

app = FastAPI(root_path=ROOT_PATH, title="adversea scraper service", lifespan=lifespan)

app.include_router(scraper_router.router)
app.include_router(request_router.router)

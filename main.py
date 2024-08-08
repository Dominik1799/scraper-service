import uvicorn
from fastapi import FastAPI
from settings import ROOT_PATH
from routers import scraper_router

app = FastAPI(root_path=ROOT_PATH, title="adversea scraper service")

app.include_router(scraper_router.router)

@app.get("/")
def root():
    return "Hello from scraper service. Visit /docs"

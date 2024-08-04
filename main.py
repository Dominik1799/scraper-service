from fastapi import FastAPI
from settings import ROOT_PATH
from routers import scraper_router
from fake_useragent import UserAgent

app = FastAPI(root_path=ROOT_PATH, title="adversea scraper service")

app.include_router(scraper_router.router)

@app.get("")
async def root():
    return "Hello from court cases service. Visit /docs"

header = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
}

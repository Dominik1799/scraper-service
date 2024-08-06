import os

from dotenv import load_dotenv

load_dotenv()

ROOT_PATH = str(os.getenv("ROOT_PATH") or "/")
TOR_PROXIES = list(os.getenv("TOR_PROXIES").split(",") or ["http://127.0.0.1:8888", "http://127.0.0.1:8000"])
MAX_PROXY_RETRIES = int(os.getenv("MAX_PROXY_RETRIES") or 2)

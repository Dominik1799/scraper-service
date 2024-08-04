import os

from dotenv import load_dotenv

load_dotenv()

ROOT_PATH = str(os.getenv("ROOT_PATH") or "/")

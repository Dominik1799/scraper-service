# Scraper service

It tries all possible ways to scrape the content from the provided URL.

## How to run

* `python3 -m venv ./venv`
* `source ./venv/bin/activate`
* `pip install -r requirements.txt`
* `fastapi dev main.py`

I suggest visiting `http://localhost:8000/docs` to see the existing routes

## Routes

ATM there is only one route `/scraper/scrape`. It takes `url` parameter only.

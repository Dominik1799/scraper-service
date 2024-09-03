# Scraper service

It tries all possible ways to scrape the content from the provided URL.

## How to run
Have python 3.10 installed and also node 10+ installed. If you dont have node, set env variable SCRAPE_WITH_PYTHON_ONLY to true.


* `python3 -m venv ./venv`
* `source ./venv/bin/activate`
* `pip install -r requirements.txt`
* `python setup_js_dependencies.py` // dont run this if you dont have node
* `fastapi dev main.py`



I suggest visiting `http://localhost:8000/docs` to see the existing routes

## ENV variables

place a .env file into the root dir.

```
REDIS_HOST=localhost
REDIS_PORT=6379

// stored in bitwarden
BING_API_KEY=keyyy

TOR_PROXIES=http://127.0.0.1:8888,http://127.0.0.1:8800

SCRAPE_WITH_PYTHON_ONLY=false // set this to true if you dont have node or have problems with running setup_js_dependencies.py

// pick any located in our bitwarden. 
GOOGLE_SEARCH_API_CREDENTIALS=engineId:Key
// example:
GOOGLE_SEARCH_API_CREDENTIALS=c2d15584f57sd8d08:AIzaSyB5LjL8-zlYpCE19b7TQGLqfn-mrjBobr0
```
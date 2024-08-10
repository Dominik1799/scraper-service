import requests
import random
import logging
import tldextract
from fake_useragent import UserAgent
from settings import TOR_PROXIES, MAX_PROXY_RETRIES, LOG_LEVEL, \
    FAKE_HEADER_SUPPORTED_COUNTRIES, BROWSERS
from random_header_generator import HeaderGenerator
from readabilipy import simple_json_from_html_string

logging.basicConfig(level=LOG_LEVEL)

def scrape_content_from_url(url: str):
    article_data = {
        "plain_text": ""
    }

    response = try_to_get_200_on_request(url)

    if response is not None and response.status_code < 300 and response.status_code >= 200:
        article = simple_json_from_html_string(response.text, use_readability=True, use_is_probably_readable=False)
        
        if article is None or article["plain_text"] is None:
            return article_data
        
        text_parts = [text["text"] for text in article["plain_text"]]
        full_text = " ".join(text_parts)
        article_data["plain_text"] = full_text
        return article_data
    
    return article_data

def try_to_get_200_on_request(url: str, timeout: int = 10):
    ua = UserAgent(
        browsers=BROWSERS,
        os=["windows", "linux", "macos"],
        platforms=["pc"]
    )

    # inspired: https://www.zenrows.com/blog/stealth-web-scraping-in-python-avoid-blocking-like-a-ninja#full-set-of-headers
    # 1. use user agent without proxy
    try:
        response = requests.get(url, timeout=timeout,
                                headers={"User-Agent": ua.random, "Cache-Control": "max-age=0"})
        if response.status_code < 300 and response.status_code >= 200:
            logging.info("Got 2xx without proxy using User-Agent only")
            return response
    except Exception as e:
        logging.error(e)
        logging.info("Failed to get 2xx without proxy using User-Agent only")

    proxies = TOR_PROXIES
    max_proxy_retries = MAX_PROXY_RETRIES if MAX_PROXY_RETRIES <= len(proxies) else len(proxies)

    # 2. use user agent with proxies
    random.shuffle(proxies)
    for i in range(max_proxy_retries):
        try:
            response = requests.get(url, timeout=timeout, 
                                    proxies={"http": proxies[i], "https": proxies[i]}, 
                                    headers={"User-Agent": ua.random, "Cache-Control": "max-age=0"})
            if response.status_code < 300 and response.status_code >= 200:
                logging.info("Got 2xx with proxy using User-Agent")
                return response
        except Exception as e:
            logging.error(e)
            logging.info(f"{i + 1}. attempt - failed to get 2xx with proxy using User-Agent")

    # 3. use complete headers with proxies
    # https://pypi.org/project/random-header-generator/ or https://pypi.org/project/fake-headers/
    random.shuffle(proxies)
    country = get_country_from_url(url)
    generator = HeaderGenerator(user_agents = "scrape") # the latest user agents will be scraped from https://www.useragentstring.com/
    for i in range(max_proxy_retries):
        try:
            headers = generator(
                country     = country, 
                device      = "desktop", 
                browser     = random.choice(BROWSERS),
                httpVersion = 1,
            )

            response = requests.get(url, timeout=timeout,
                                    proxies={"http": proxies[i], "https": proxies[i]},
                                    headers=headers)
            if response.status_code < 300 and response.status_code >= 200:
                logging.info("Got 2xx with proxy using full fake Headers")
                return response
        except Exception as e:
            logging.error(e)
            logging.info(f"{i + 1}. attempt - failed to get 2xx with proxy using full fake Headers")
        
        # use specific country in the first try, then use only us
        country = "us"

    # # wait for a second and retry with a different IP and set of headers. 
    # # This is a way to sometimes trick the Captchas, but IMO it's too pricy on time.
    # time.sleep(1)
    # response = requests.get(url, proxies=proxies, headers=headers)

    # 4. use Selenium, Puppeteer or Playwirght. These slow down the scraping significantly. NOTE: ATM not implemented

    # 5. use Geolocated proxy
  

def get_country_from_url(url: str):
    ext = tldextract.extract(url)
    return ext.suffix if ext.suffix in FAKE_HEADER_SUPPORTED_COUNTRIES else "us"

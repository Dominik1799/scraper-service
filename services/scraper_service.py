import requests
import random
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from settings import TOR_PROXIES, MAX_PROXY_RETRIES
from random_header_generator import HeaderGenerator

def scrape_content_from_url(url: str):
    response = try_to_get_200_on_request(url)

    if response.status_code < 300 and response.status_code >= 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    else:
        return None

def try_to_get_200_on_request(url: str, timeout: int = 10):
    ua = UserAgent(
        browsers=["chrome", "firefox", "safari"],
        operating_systems=["windows", "linux", "macos"],
        platforms=["pc"]
    )

    # inspired: https://www.zenrows.com/blog/stealth-web-scraping-in-python-avoid-blocking-like-a-ninja#full-set-of-headers
    # 1. use user agent without proxy
    response = requests.get(url, timeout=timeout,
                            headers={'User-Agent': ua.random, 'Cache-Control': 'max-age=0'})
    if response.status_code < 300 and response.status_code >= 200:
        return response

    # 2. use user agent with proxies
    proxies = TOR_PROXIES
    random.shuffle(proxies)
    for i in range(MAX_PROXY_RETRIES):
        response = requests.get(url, timeout=timeout, 
                                proxies={"http": proxies[i], "https": proxies[i]}, 
                                headers={'User-Agent': ua.random, 'Cache-Control': 'max-age=0'})
        if response.status_code < 300 and response.status_code >= 200:
            return response

    # 3. use complete headers with proxies
    # https://pypi.org/project/random-header-generator/ or https://pypi.org/project/fake-headers/
    # TODO: check root domain (com, de, sk, etc.) and choose country in the headers
    random.shuffle(proxies)
    generator = HeaderGenerator(user_agents = "scrape") # the latest user agents will be scraped from https://www.useragentstring.com/
    for i in range(MAX_PROXY_RETRIES):
        headers = generator(
            country     = "us", 
            device      = "desktop", 
            browser     = "chrome", # TODO: switch between mozila, safari, and chrome
            httpVersion = 1,
        )

        response = requests.get(url, timeout=timeout,
                                proxies={"http": proxies[i], "https": proxies[i]},
                                headers=headers)
        if response.status_code < 300 and response.status_code >= 200:
            return response

    # # wait for a second and retry with a different IP and set of headers. 
    # # This is a way to sometimes trick the Captchas, but IMO it's too pricy on time.
    # time.sleep(1)
    # response = requests.get(url, proxies=proxies, headers=headers)

    # 4. use Selenium, Puppeteer or Playwirght. These slow down the scraping significantly. NOTE: ATM not implemented

    # 5. use Geolocated proxy

# 3. Complete full headers
# headers_list = [{ 
# 	'authority': 'httpbin.org', 
# 	'cache-control': 'max-age=0', 
# 	'sec-ch-ua': '"Chromium";v="92", " Not A;Brand";v="99", "Google Chrome";v="92"', 
# 	'sec-ch-ua-mobile': '?0', 
# 	'upgrade-insecure-requests': '1', 
# 	'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36', 
# 	'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9', 
# 	'sec-fetch-site': 'none', 
# 	'sec-fetch-mode': 'navigate', 
# 	'sec-fetch-user': '?1', 
# 	'sec-fetch-dest': 'document', 
# 	'accept-language': 'en-US,en;q=0.9', 
# } # , {...} 
# ] 
# headers = random.choice(headers_list) 
# response = requests.get('https://httpbin.org/headers', headers=headers) 

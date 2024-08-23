import requests
import logging
from fake_useragent import UserAgent
import random
import tldextract
from random_header_generator import HeaderGenerator
from settings import TOR_PROXIES, MAX_PROXY_RETRIES, LOG_LEVEL, \
    FAKE_HEADER_SUPPORTED_COUNTRIES, BROWSERS


logger = logging.getLogger(__name__)

def proxy_request(url: str, req_method: str, try_normal_request_first=True, timeout=10, headers={}, **kwargs) -> requests.Response | None:
    ua = UserAgent(
        browsers=BROWSERS,
        os=["windows", "linux", "macos"],
        platforms=["pc"]
    )
    response = None
    if try_normal_request_first:
        headers["User-Agent"] = ua.random
        headers["Cache-Control"] = ua.random
        try:
            response = requests.request(method=req_method, url=url, timeout=timeout, headers=headers, **kwargs)
            if response.status_code >= 200 and response.status_code < 300:
                return response
        except Exception:
            logger.info("Normal request not working for " + url)
            logger.debug("Traceback: ", exc_info=True)


    proxies = TOR_PROXIES
    max_proxy_retries = MAX_PROXY_RETRIES if MAX_PROXY_RETRIES <= len(proxies) else len(proxies)
    random.shuffle(proxies)
    for i in range(max_proxy_retries):
        headers["User-Agent"] = ua.random
        headers["Cache-Control"] = ua.random
        try:
            response = requests.request(method=req_method, url=url, 
                                        proxies={"http": proxies[i], "https": proxies[i]},
                                        timeout=timeout, headers=headers, **kwargs)
            if response.status_code < 300 and response.status_code >= 200:
                logging.info("Got 2xx with proxy using User-Agent")
                return response
        except Exception as e:
            logging.error(e)
            logger.debug("Traceback: ", exc_info=True)
    
    random.shuffle(proxies)
    country = get_country_from_url(url)
    generator = HeaderGenerator(user_agents = "scrape")
    
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
                                    headers=headers, **kwargs)
            if response.status_code < 300 and response.status_code >= 200:
                logging.info("Got 2xx with proxy using full fake Headers")
                return response
        except Exception as e:
            logging.info(f"{i + 1}. attempt - failed to get 2xx with proxy using full fake Headers")
            logger.debug("Traceback: ", exc_info=True)
        # use specific country in the first try, then use only us
        country = "us"
    
        logging.info(f"""Failed to get 2xx from the provided URL with proxy using full fake Headers.
                 The status code {response.status_code} from the last request on {url}""")
    
    return response


def get_country_from_url(url: str):
    ext = tldextract.extract(url)
    return ext.suffix if ext.suffix in FAKE_HEADER_SUPPORTED_COUNTRIES else "us"
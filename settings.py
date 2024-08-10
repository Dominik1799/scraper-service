import os
import logging
from dotenv import load_dotenv

load_dotenv()

DEFAULT_FAKE_HEADERS_SUPPORTED_COUNTRIES="""
ad,ae,af,ag,al,am,ao,ar,as,at,au,az,ba,bb,bd,be,bf,bg,bh,bi,bj,bo,br,bs,bt,bw,by,bz,ca,
cd,ch,cl,cm,cn,co,cr,cu,cy,cz,de,dj,dk,dm,do,dz,ec,ee,eg,er,es,et,fi,fj,fr,ga,gb,gd,ge,
gh,gm,gn,gq,gr,gt,gw,gy,hn,hr,ht,hu,id,ie,il,in,iq,ir,is,it,jm,jo,jp,ke,kg,kh,ki,km,kn,kw,kz,lb,lc,li,lk,lr
"""

BROWSERS = list((os.getenv("BROWSERS") or "chrome,firefox,safari").split(","))
FAKE_HEADER_SUPPORTED_COUNTRIES = dict.fromkeys(list((os.getenv("FAKE_HEADER_SUPPORTED_COUNTRIES") or DEFAULT_FAKE_HEADERS_SUPPORTED_COUNTRIES).split(",")))

ROOT_PATH = str(os.getenv("ROOT_PATH") or "")
TOR_PROXIES = list((os.getenv("TOR_PROXIES") or "http://127.0.0.1:8888,http://127.0.0.1:8800").split(","))
MAX_PROXY_RETRIES = int(os.getenv("MAX_PROXY_RETRIES") or 2)
LOG_LEVEL = int(os.getenv("LOG_LEVEL") or logging.INFO)

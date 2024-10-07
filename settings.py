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

MONGODB_HOST = str(os.getenv("MONGODB_HOST") or "localhost")
MONGODB_PORT = int(os.getenv("MONGODB_PORT") or 27017)
MONGODB_USERNAME = str(os.getenv("MONGODB_USERNAME") or "admin")
MONGODB_PASSWORD = str(os.getenv("MONGODB_PASSWORD") or "admin")
MONGODB_DATABASE = str(os.getenv("MONGODB_DATABASE") or "scraper-service")

MONGODB_TARGET_NAME_CACHE_COLLECTION = "target-name-cache"
MONGODB_URL_DATA_CACHE_COLLECTION = "url-data-cache"

# list of key pairs. One pair looks like this: engineID:APIKey. Each pair is split via , character
GOOGLE_SEARCH_API_CREDENTIALS = os.environ.get("GOOGLE_SEARCH_API_CREDENTIALS") or None
GOOGLE_SEARCH_API_CREDENTIALS = GOOGLE_SEARCH_API_CREDENTIALS.split(",")

BING_API_KEY = os.environ.get("BING_API_KEY") or None

FILE_EXTENSIONS = ["doc", "docx", "ppt", "pptx", "pdf", "xml", "json"]

SOCIAL_MEDIA_WEBSITES = [
    "linkedin.",
    "facebook.",
    "instagram.",
    "twitter.",
    "x.com",
    "youtube.",
    "youtu.be",
    "9gag.com",
    "reddit.com",
    "redd.it",
    "quora.com",
    "tiktok.com",
    "pinterest",
    "vimeo."
]

SCRAPE_WITH_PYTHON_ONLY = os.getenv("ENV_VAR", 'False').lower() in ('true', '1', 't')


TOPIC_SEARCH_KEYWORDS = {
    "basic_check": {
        "en": [],
        "sk": []
    },
    "political_activity": {
        "en": [
            "president",
            "prime minister",
            "minister",
            "member of parliament",
            "mayor",
            "governor",
            "chairman",
            "chairwoman",
            "candidate",
            "municipal council",
            "city council"
        ],
        "sk": [
            "prezident",
            "premiér",
            "minister",
            "poslanec",
            "poslankyňa",
            "starosta",
            "starostka",
            "primátor",
            "guvernér",
            "predseda",
            "predsedkyňa",
            "kandidát",
            "obecné zstupiteľstvo",
            "mestské zastupiteľstvo",
            "mestská rada",
            "obecná rada"
        ]
    },
    "legal_issues": {
        "en": [
            "court",
            "lawsuit",
            "legal case",
            "court case",
            "judge",
            "verdict",
            "sentence",
            "sue",
            "prosecute",
            "prosecuted",
            "defendant",
            "lawyer",
            "attorney",
            "law",
            "accusation",
            "accused",
            "accusations"
        ],
        "sk": [
            "súd",
            "súdny spor",
            "spor",
            "sudca",
            "sudkyňa",
            "rozsudok",
            "zažaloval",
            "zažalovaný",
            "zažalovaná",
            "právnik",
            "právny zástupca",
            "zákon",
            "obžalovaný",
            "obžalovaná",
            "odsúdený",
            "odsúdená",
            "obžalovaní"
        ]
    },
    "corruption": {
        "en": [
            "corruption",
            "fraud",
            "bribe",
            "bribed",
            "nepotism",
            "embezzled",
            "embezzlement"
        ],
        "sk": [
            "korupcia",
            "korupcie",
            "korupčná",
            "podvod",
            "úplatok",
            "rodinkárstvo",
            "úplatky",
            "podplatil",
            "podplatila",
            "nepotizmus",
            "spreneveril",
            "spreneverila",
            "spreneverenie"
        ]
    },
    "financial_crime": {
        "en": [
            "business",
            "sale",
            "purchase",
            "suspicious",
            "leaks",
            "tax",
            "fiscal",
            "pyramid scheme",
            "fraud",
            "scam",
            "theft",
            "steal",
            "stole",
            "corruption",
            "bankruptcy",
            "distrain",
            "distrainment",
            "distraint"
        ],
        "sk": [
            "obchod",
            "predaj",
            "nákup",
            "podozrivý",
            "úniky",
            "dane",
            "daňový",
            "pyramída",
            "pyramídová",
            "podvod",
            "krádež",
            "ukradol",
            "ukradla",
            "korupcia",
            "bankrot",
            "bankrotom",
            "exekúcia",
            "exekúcii",
            "exekúcií",
            "exekúcie"
        ]
    },
    "violent_crime": {
        "en": [
            "crime",
            "murder",
            "assault",
            "robbery",
            "shooting",
            "shoot",
            "kidnapping",
            "violence",
            "violation",
            "gun",
            "weapon",
            "rape",
            "hate crime",
            "brawl",
            "kill",
            "death",
            "shootout"
        ],
        "sk": [
            "zločin",
            "vražda",
            "útok",
            "lúpež",
            "vraždy",
            "smrť",
            "streľba",
            "strieľal",
            "únos",
            "násilie",
            "násilia",
            "zbraň",
            "znásilnil",
            "znásilnila",
            "znásilnenie",
            "nenávisť",
            "bitka",
            "pobil",
            "pobila"
        ]
    },
    "sex_crime": {
        "en": [
            "rape",
            "sex",
            "harassment",
            "harassed",
            "molestation",
            "sexual",
            "meToo",
            "porn",
            "pornography",
            "pornographic",
            "inappropriate"
        ],
        "sk": [
            "znásilnenie",
            "sex",
            "obťažovanie",
            "obťažoval",
            "obťažovala",
            "znásilnil",
            "znásilnila",
            "sexuálne",
            "sexuálny",
            "meToo",
            "porno",
            "pornografia",
            "pornografické",
            "pornografický",
            "nevhodné",
            "nevhodný",
            "nevhodná"
        ]
    }
}
import json
import html2text


def parse_html(html: str) -> str:
    return html2text.html2text(html)
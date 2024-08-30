from readabilipy import simple_json_from_html_string
import json


def parse_html(html: str) -> str | None:
    parsed_data = simple_json_from_html_string(html, use_readability=True, use_is_probably_readable=True)
    if parsed_data == None:
        return None
    text_parts = [text["text"] for text in parsed_data["plain_text"]]
    full_text = " ".join(text_parts)
    return full_text
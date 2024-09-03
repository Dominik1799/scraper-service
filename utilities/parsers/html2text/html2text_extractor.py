import html2text


def extract_text_with_html2text(html: str) -> str:
    return html2text.html2text(html)
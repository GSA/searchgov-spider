import os
import hashlib
import newspaper
from datetime import datetime, timezone
from urllib.parse import urlparse
from typing import Union

ALLOWED_LANGUAGE_CODE = {
    lang: True for lang in [
        "ar", "bg", "bn", "ca", "cs", "da", "de", "el", "en", "es", "et", "fa", "fr",
        "he", "hi", "hr", "ht", "hu", "hy", "id", "it", "ja", "km", "ko", "lt", "lv",
        "mk", "nl", "pl", "ps", "pt", "ro", "ru", "sk", "so", "sq", "sr", "sw", "th",
        "tr", "uk", "ur", "uz", "vi", "zh"
    ]
}

def safe_decode_str(str_value: Union[str, bytes], default_val: str = "") -> str:
    """Safely decodes a string or bytes into UTF-8."""
    try:
        if isinstance(str_value, str):
            return str_value.encode("utf-8").decode("utf-8")
        elif isinstance(str_value, bytes):
            return str_value.decode("utf-8")
    except Exception:
        return default_val
    return default_val

def convert_html(html_content: str, url: str, domain_name: str):
    """Extracts and processes article content from HTML using newspaper3k."""
    article = newspaper.Article(url=url)
    article.download(input_html=html_content)
    article.parse()
    article.nlp()

    title = safe_decode_str(article.title or article.meta_site_name, "")
    description = safe_decode_str(article.meta_description or article.summary, "")
    content = safe_decode_str(article.text or description, "")

    if not content:
        return None

    time_now_str = current_utc_iso()
    path = article.url or url

    basename, extension = get_base_extension(url)
    sha_id = generate_url_sha256(path)

    valid_language = f"_{article.meta_lang}" if article.meta_lang in ALLOWED_LANGUAGE_CODE else ""

    i14y_doc = {
        "audience": None,
        "changed": None,
        "click_count": None,
        "content_type": None,
        "created_at": time_now_str,
        "created": None,
        "_id": sha_id,
        "id": sha_id,
        "thumbnail_url": article.meta_img or article.top_image or None,
        "language": article.meta_lang,
        "mime_type": "text/html",
        "path": path,
        "promote": None,
        "searchgov_custom1": None,
        "searchgov_custom2": None,
        "searchgov_custom3": None,
        "tags": article.tags or article.keywords or article.meta_keywords,
        "updated_at": time_now_str,
        "updated": article.publish_date,
        f"title{valid_language}": title,
        f"description{valid_language}": description,
        f"content{valid_language}": content,
        "basename": basename,
        "extension": extension or None,
        "url_path": get_url_path(url),
        "domain_name": domain_name
    }

    return i14y_doc

def get_url_path(url: str) -> str:
    """Extracts the path from a URL."""
    return urlparse(url).path

def get_base_extension(url: str) -> tuple[str, str]:
    """Extracts the basename and file extension from a URL."""
    basename, extension = os.path.splitext(os.path.basename(urlparse(url).path))
    return basename, extension

def current_utc_iso() -> str:
    """Returns the current UTC timestamp in ISO format."""
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds") + "Z"

def generate_url_sha256(url: str) -> str:
    """Generates a SHA-256 hash for a given URL."""
    return hashlib.sha256(url.encode()).hexdigest()

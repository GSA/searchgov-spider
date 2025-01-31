import os
import hashlib
import newspaper
from datetime import datetime, timezone
from urllib.parse import urlparse

def convert_html(html_content: str, url: str, domain_name: str):
    article = newspaper.article(url=url, input_html=html_content)
    article.nlp()
    description_en = article.meta_description or article.summary
    content_en = article.text_cleaned or article.text or description_en or article.title

    if content_en is None:
        return None

    time_now_str = current_utc_iso()
    path = article.url or url

    basename, extention = get_base_extension(url)
    sha_id = generate_url_sha256(path)

    i14y_doc = {
        "audience": None,
        "changed": None,
        "click_count": None,
        "content_type": None,
        "created_at" : time_now_str,
        "created" : None,
        "_id": sha_id,
        "id" : sha_id,
        "thumbnail_url" : article.meta_img or article.top_img,
        "language" : article.meta_lang or "en",
        "mime_type" : "text/html",
        "path" : path,
        "promote" : None,
        "searchgov_custom1" : None,
        "searchgov_custom2" : None,
        "searchgov_custom3" : None,
        "tags" : article.tags or article.keywords or article.meta_keywords,
        "updated_at" : time_now_str,
        "updated" : None,
        "title_en" : article.title,
        "description_en" : description_en,
        "content_en" : content_en,
        "basename" : basename,
        "extension" : extention,
        "url_path" : get_url_path(url),
        "domain_name" : domain_name
    }

    return i14y_doc


def get_url_path(url: str) -> str:
    parsed_url = urlparse(url)
    return parsed_url.path

def get_base_extension(url: str) -> tuple[str, str]:
    text = os.path.splitext(url)
    basename = text[0].split("/")[-1:]
    extension = text[1]
    return basename, extension

def current_utc_iso() -> str:
    iso_str = datetime.datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    return f"{iso_str}Z"

def generate_url_sha256(url: str) -> str:
    input_bytes = url.encode("utf-8")
    hash_object = hashlib.hashlib()
    hash_object.update(input_bytes)
    hash_hex = hash_object.hexdigest()
    return str(hash_hex)

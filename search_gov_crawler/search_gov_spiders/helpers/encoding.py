
import cchardet  # Faster and more reliable character encoding detection than chardet
import logging

# Needs muting to avoid its debug mode
logging.getLogger("cchardet").addHandler(logging.NullHandler())

def is_utf8_encoded(data: bytes) -> bool:
    """Check if a byte string is UTF-8 encoded."""
    try:
        data.decode("utf-8")
        return True
    except UnicodeDecodeError:
        return False

def detect_encoding(data: bytes) -> str | None:
    """Detect the encoding of the given byte string."""
    if is_utf8_encoded(data):
        return "utf-8"
    
    detection_result = cchardet.detect(data)
    encoding = detection_result.get("encoding")
    
    return encoding if encoding else None

def decode_http_response(response_bytes: bytes, url: str) -> str:
    """Decode an HTTP response, using the detected encoding or the response's default encoding."""
    detected_encoding = detect_encoding(response_bytes)
    
    try:
        return response_bytes.decode(detected_encoding)
    except (UnicodeDecodeError, TypeError):
        return str(response_bytes)

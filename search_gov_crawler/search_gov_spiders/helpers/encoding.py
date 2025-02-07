
import cchardet  # Faster and more reliable character encoding detection than chardet
import logging

# Needs muting to avoid its debug mode
logging.getLogger("cchardet").addHandler(logging.NullHandler())

def detect_encoding(data: bytes) -> str | None:
    """Detect the encoding of the given byte string."""
    detection_result = cchardet.detect(data)
    encoding = detection_result.get("encoding")
    
    return encoding if encoding else None

def decode_http_response(response_bytes: bytes) -> str:
    """Decode an HTTP response, using the detected encoding or the response's default encoding."""
    try:
        decoded_str = response_bytes.decode("utf-8")
        return decoded_str
    except UnicodeDecodeError:
        pass

    detected_encoding = detect_encoding(response_bytes)
    
    try:
        return response_bytes.decode(detected_encoding)
    except (UnicodeDecodeError, TypeError):
        return str(response_bytes)

from search_gov_crawler.search_gov_spiders.helpers.encoding import decode_http_response, detect_encoding

def test_detect_encoding():
    some_str_bytes = "This is UTF-8".encode("utf-8")
    assert detect_encoding(some_str_bytes) == "ASCII" # subset of utf-8
    assert detect_encoding(b"") == None

def test_decode_http_response_utf8():
    response_bytes = b"This is a UTF-8 string"
    decoded_string = decode_http_response(response_bytes)
    assert decoded_string == "This is a UTF-8 string"

def test_decode_http_response_non_utf8():
    response_bytes = b"\xc2\xa0This is not UTF-8"  # Example non-UTF-8
    decoded_string = decode_http_response(response_bytes)
    # Check if it decodes with detected encoding or falls back to string representation
    assert "This is not UTF-8" in decoded_string or repr(response_bytes) == decoded_string  # Allows for either decode or fallback

def test_decode_http_response_empty():
    response_bytes = b""
    decoded_string = decode_http_response(response_bytes)
    assert decoded_string == ""

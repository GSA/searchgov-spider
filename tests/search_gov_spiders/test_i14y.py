from search_gov_crawler.elasticsearch import convert_html_i14y as conversion

def test_convert_html_valid_article():
    html_content = """
    <html lang="en">
    <head>
        <title>Test Article Title</title>
        <meta name="description" content="Test article description.">
        <meta name="keywords" content="test, article, keywords">
        <meta property="og:image" content="https://example.com/image.jpg">
        <meta name="lang" content="en">
    </head>
    <body>
        <h1>Test Article Title</h1>
        <p>This is the main content of the test article.</p>
    </body>
    </html>
    """
    url = "https://example.com/test-article"
    result = conversion.convert_html(html_content, url)

    assert result is not None
    assert result["title_en"] == "Test Article Title"
    assert result["description_en"] == "Test article description."
    assert "This is the main content of the test article." in result["content_en"]
    assert result["thumbnail_url"] == "https://example.com/image.jpg"
    assert result["language"] == "en"
    assert result["path"] == url
    assert result["basename"] == "test-article"
    assert result["extension"] == None
    assert result["domain_name"] == "example.com"
    assert result["url_path"] == "/test-article"
    assert len(result["_id"]) == 64  # SHA256 hash

def test_convert_html_no_content():
    html_content = """
    <html lang="en">
    <head>
        <title>Test Article Title</title>
    </head>
    <body>
    </body>
    </html>
    """
    url = "https://example.com/test-article"
    result = conversion.convert_html(html_content, url)
    assert result is None

def test_convert_html_no_title_or_description():
    html_content = """
    <html lang="en">
    <head>
    </head>
    <body>
        <p>This is the main content of the test article.</p>
    </body>
    </html>
    """
    url = "https://example.com/test-article"
    result = conversion.convert_html(html_content, url)
    assert result is not None
    assert result["title_en"] is None
    assert result["description_en"] is None
    assert "This is the main content of the test article." in result["content_en"]

def test_convert_html_with_meta_site_name():
    html_content = """
    <html lang="en">
    <head>
        <meta property="og:site_name" content="Example Site">
    </head>
    <body>
        <h1>Test Article Title</h1>
        <p>This is the main content.</p>
    </body>
    </html>
    """
    url = "https://example.com/test-article"
    result = conversion.convert_html(html_content, url)
    assert result is not None
    assert result["title_en"] == "Example Site"  # Uses meta_site_name
    assert "This is the main content." in result["content_en"]

def test_convert_html_with_publish_date():
    html_content = """
    <html lang="en">
    <head>
        <meta name="date" content="2024-03-15">
    </head>
    <body>
        <h1>Test Article Title</h1>
        <p>This is the main content.</p>
    </body>
    </html>
    """
    url = "https://example.com/test-article"
    result = conversion.convert_html(html_content, url)
    assert result is not None
    assert result["updated"] is not None # newspaper4k may or may not parse date from meta; this checks for any value.

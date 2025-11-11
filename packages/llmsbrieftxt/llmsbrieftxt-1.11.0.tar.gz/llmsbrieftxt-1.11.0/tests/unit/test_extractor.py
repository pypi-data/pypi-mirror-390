"""Minimal extractor tests - testing our logic, not third-party libraries."""

from llmsbrieftxt.extractor import default_extractor


def test_handles_short_content():
    """Verify handling of short HTML that Trafilatura might reject."""
    # Very short HTML that Trafilatura might reject
    html = "<div><p>Short.</p></div>"

    result = default_extractor(html)

    # Should return empty string or extracted content
    # Trafilatura may or may not extract very short content
    assert isinstance(result, str)


def test_handles_malformed_html():
    """Verify graceful handling of malformed HTML."""
    html = """
    <html>
        <body>
            <div>
                <p>This paragraph is not closed
                <div>Nested div without closing main div
                <h1>Title</h1>
                <p>Some content here</p>
            </div>
        </body>
    """

    result = default_extractor(html)

    # Should extract something without crashing
    assert len(result) > 0
    assert "Title" in result or "content" in result


def test_empty_html():
    """Verify handling of empty HTML."""
    html = "<html><body></body></html>"

    result = default_extractor(html)

    # Should return empty or minimal content without crashing
    assert isinstance(result, str)


def test_basic_extraction():
    """Verify basic HTML to markdown extraction works."""
    html = """
    <html>
        <body>
            <article>
                <h1>Documentation Title</h1>
                <p>This is the main content of the documentation page.</p>
                <h2>Section Heading</h2>
                <p>More content here with details.</p>
            </article>
        </body>
    </html>
    """

    result = default_extractor(html)

    # Should extract main content
    assert "Documentation Title" in result
    assert "main content" in result
    assert "Section Heading" in result
    assert len(result) > 50  # Should have substantial content

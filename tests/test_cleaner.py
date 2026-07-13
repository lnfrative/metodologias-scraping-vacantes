from vacancy_extractor.cleaner import clean_html


def test_removes_noise_tags_and_collapses_whitespace():
    html = """
    <html>
      <head><style>.x{color:red}</style></head>
      <body>
        <nav>Menu</nav>
        <script>console.log('x')</script>
        <main>
          <h1>Backend Developer</h1>
          <p>Se requiere   experiencia   en   Python y AWS.</p>
        </main>
        <footer>Copyright</footer>
      </body>
    </html>
    """
    result = clean_html(html)

    assert "Menu" not in result
    assert "console.log" not in result
    assert "Copyright" not in result
    assert "Backend Developer" in result
    assert "experiencia en Python y AWS." in result


def test_truncates_to_max_chars():
    html = "<p>" + ("a" * 100) + "</p>"
    result = clean_html(html, max_chars=10)
    assert len(result) == 10


def test_empty_html_returns_empty_string():
    assert clean_html("<html><body></body></html>") == ""

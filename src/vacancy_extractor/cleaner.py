"""Limpieza de HTML a texto plano, para reducir tokens enviados al modelo."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup

from . import config

_NOISE_TAGS = ("script", "style", "nav", "footer", "header", "noscript", "svg", "form", "iframe")
_WHITESPACE_RE = re.compile(r"[ \t]+")
_BLANK_LINES_RE = re.compile(r"\n{3,}")


def clean_html(html: str, max_chars: int | None = None) -> str:
    max_chars = max_chars if max_chars is not None else config.MAX_CHARS

    soup = BeautifulSoup(html, "lxml")

    for tag in soup(_NOISE_TAGS):
        tag.decompose()
    for comment in soup.find_all(string=lambda s: s.__class__.__name__ == "Comment"):
        comment.extract()

    text = soup.get_text(separator="\n")
    text = _WHITESPACE_RE.sub(" ", text)
    lines = [line.strip() for line in text.splitlines()]
    text = "\n".join(line for line in lines if line)
    text = _BLANK_LINES_RE.sub("\n\n", text)

    if max_chars and len(text) > max_chars:
        text = text[:max_chars]

    return text.strip()

"""Configuración centralizada del extractor."""

from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")

TAXONOMY_PATH = Path(os.environ.get("TAXONOMY_PATH", PROJECT_ROOT / "taxonomy.json"))
DATASET_PATH = Path(os.environ.get("DATASET_PATH", PROJECT_ROOT / "dataset.json"))

# Tope de caracteres del texto limpio enviado al modelo, como salvaguarda de costos.
MAX_CHARS = int(os.environ.get("MAX_CHARS", "15000"))

HTTP_TIMEOUT_SECONDS = int(os.environ.get("HTTP_TIMEOUT_SECONDS", "15"))
HTTP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

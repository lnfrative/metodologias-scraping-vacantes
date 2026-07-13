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

HTTP_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
)

RENDER_TIMEOUT_MS = int(os.environ.get("RENDER_TIMEOUT_MS", "20000"))
# Espera fija tras domcontentloaded para permitir que el contenido dinámico
# termine de pintarse, sin depender de 'networkidle' (que nunca se cumple en
# portales con tráfico de fondo constante).
RENDER_SETTLE_MS = int(os.environ.get("RENDER_SETTLE_MS", "3000"))

# Headed (con ventana) por defecto: algunos portales con protección
# anti-bot (ej. Cloudflare) bloquean específicamente la huella de Chromium
# en modo headless. Se puede forzar headless=True vía env var si se corre en
# un servidor sin entorno gráfico y el portal no tiene esa protección.
PLAYWRIGHT_HEADLESS = os.environ.get("PLAYWRIGHT_HEADLESS", "false").lower() == "true"

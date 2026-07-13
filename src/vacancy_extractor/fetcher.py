"""Descarga el contenido renderizado de una vacante.

Los portales de empleo son mayoritariamente SPAs (Oracle HCM/Recruiting
Cloud, Workday, LinkedIn, Multitrabajos, etc.) donde el detalle de la vacante
se carga vía JavaScript después de la carga inicial; un simple GET no obtiene
ese contenido. Por eso siempre se renderiza con Playwright/Chromium antes de
limpiar el HTML.

El navegador se lanza en modo headed (con ventana, no headless) por defecto:
algunos portales (ej. Multitrabajos, protegido con Cloudflare) bloquean la
huella específica de Chromium en modo headless devolviendo una página de
verificación en vez del contenido. Un navegador headed normal no dispara ese
bloqueo. Se usa 'domcontentloaded' + una espera corta fija en vez de
'networkidle', ya que muchos portales mantienen tráfico de fondo (anuncios,
analítica) que nunca llega a estar inactivo.
"""

from __future__ import annotations

from . import config
from .cleaner import clean_html


class FetchError(Exception):
    """Error al descargar o renderizar la URL de la vacante."""


def fetch_rendered_html(url: str) -> str:
    """Descarga el HTML tras renderizar JavaScript con un navegador."""
    try:
        from playwright.sync_api import sync_playwright
    except ImportError as exc:  # pragma: no cover - dependencia declarada en pyproject
        raise FetchError(
            "Playwright no está instalado. Ejecuta 'pip install playwright' y "
            "'playwright install chromium'."
        ) from exc

    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=config.PLAYWRIGHT_HEADLESS)
            try:
                page = browser.new_page(
                    user_agent=config.HTTP_USER_AGENT,
                    viewport={"width": 1280, "height": 800},
                    locale="es-EC",
                )
                page.goto(
                    url,
                    wait_until="domcontentloaded",
                    timeout=config.RENDER_TIMEOUT_MS,
                )
                page.wait_for_timeout(config.RENDER_SETTLE_MS)
                html = page.content()
            finally:
                browser.close()
    except Exception as exc:  # noqa: BLE001 - errores diversos de Playwright/red
        raise FetchError(f"No se pudo renderizar {url}: {exc}") from exc

    if not html.strip():
        raise FetchError(f"El renderizado de {url} devolvió contenido vacío")

    return html


def fetch_vacancy_text(url: str) -> str:
    """Obtiene el texto limpio de la vacante a partir del HTML renderizado."""
    html = fetch_rendered_html(url)
    return clean_html(html)

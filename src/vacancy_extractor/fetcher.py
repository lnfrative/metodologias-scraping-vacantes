"""Descarga el HTML crudo de una vacante."""

from __future__ import annotations

import requests

from . import config


class FetchError(Exception):
    """Error al descargar la URL de la vacante."""


def fetch_html(url: str) -> str:
    headers = {"User-Agent": config.HTTP_USER_AGENT}
    try:
        response = requests.get(url, headers=headers, timeout=config.HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
    except requests.RequestException as exc:
        raise FetchError(f"No se pudo descargar {url}: {exc}") from exc

    if not response.text.strip():
        raise FetchError(f"La respuesta de {url} está vacía")

    return response.text

"""Persistencia de dataset.json con deduplicación por URL normalizada."""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from .models import VacancyRecord

_TRACKING_PARAM_PREFIXES = ("utm_", "ref", "src", "gclid", "fbclid")


def normalize_url(url: str) -> str:
    parts = urlsplit(url.strip())
    netloc = parts.netloc.lower()
    path = parts.path.rstrip("/") or "/"
    # Descarta parámetros de tracking pero conserva otros query params relevantes.
    query_pairs = [
        pair
        for pair in parts.query.split("&")
        if pair and not pair.split("=")[0].lower().startswith(_TRACKING_PARAM_PREFIXES)
    ]
    query = "&".join(sorted(query_pairs))
    return urlunsplit((parts.scheme.lower(), netloc, path, query, ""))


def load_dataset(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as f:
        content = f.read().strip()
    if not content:
        return []
    return json.loads(content)


def _write_atomic(path: Path, records: list[dict]) -> None:
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    with open(tmp_path, "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
    os.replace(tmp_path, path)


def upsert_record(path: Path, record: VacancyRecord, force: bool = False) -> bool:
    """Inserta o reemplaza un registro por url_normalizada.

    Retorna True si el registro se escribió, False si se hizo skip por duplicado.
    """
    records = load_dataset(path)
    existing_index = next(
        (i for i, r in enumerate(records) if r.get("url_normalizada") == record.url_normalizada),
        None,
    )

    if existing_index is not None and not force:
        return False

    record_dict = record.to_dict()
    if existing_index is not None:
        records[existing_index] = record_dict
    else:
        records.append(record_dict)

    _write_atomic(path, records)
    return True


def is_duplicate(path: Path, url_normalizada: str) -> bool:
    records = load_dataset(path)
    return any(r.get("url_normalizada") == url_normalizada for r in records)

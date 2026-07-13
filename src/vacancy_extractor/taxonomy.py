"""Carga la taxonomía base y construye el JSON Schema para Structured Outputs."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path

from . import config


class TaxonomyError(Exception):
    """Error al cargar o validar la taxonomía."""


@lru_cache(maxsize=1)
def load_taxonomy(path: Path | None = None) -> dict:
    taxonomy_path = path or config.TAXONOMY_PATH
    try:
        with open(taxonomy_path, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError as exc:
        raise TaxonomyError(f"No se encontró taxonomy.json en {taxonomy_path}") from exc
    except json.JSONDecodeError as exc:
        raise TaxonomyError(f"taxonomy.json no es un JSON válido: {exc}") from exc

    for domain_id, domain in data.items():
        for required_key in ("bloque", "nombre", "sub_items"):
            if required_key not in domain:
                raise TaxonomyError(
                    f"Dominio {domain_id} no tiene el campo requerido '{required_key}'"
                )
    return data


def build_json_schema(taxonomy: dict | None = None) -> dict:
    """Construye un JSON Schema estricto: una clave por dominio, cada una con
    'requerido' (bool) y 'sub_items' (array de strings libre).

    Deliberadamente NO se usa un enum cerrado para sub_items: forzar el
    vocabulario a una lista fija descarta herramientas reales mencionadas en
    la vacante que no estén anticipadas (se perdería información). La
    consistencia terminológica (ej. siempre "PHP", nunca "php") se logra en
    un paso posterior de normalización (ver normalizer.py), no restringiendo
    la generación del modelo.
    """
    taxonomy = taxonomy or load_taxonomy()

    properties = {}
    required = []
    for domain_id, domain in taxonomy.items():
        properties[domain_id] = {
            "type": "object",
            "properties": {
                "requerido": {
                    "type": "boolean",
                    "description": (
                        f"True únicamente si la vacante menciona explícitamente el dominio "
                        f"{domain_id} ({domain['nombre']}). No inferir ni asumir."
                    ),
                },
                "sub_items": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": (
                        "Términos técnicos o competencias específicas mencionadas "
                        "explícitamente en el texto para este dominio, usando el nombre "
                        "propio/oficial de la tecnología (ej. 'PHP', 'AWS', 'Kubernetes'). "
                        "Lista vacía si requerido=false."
                    ),
                },
            },
            "required": ["requerido", "sub_items"],
            "additionalProperties": False,
        }
        required.append(domain_id)

    return {
        "type": "object",
        "properties": properties,
        "required": required,
        "additionalProperties": False,
    }


def canonical_vocabulary(domain_id: str, taxonomy: dict | None = None) -> list[str]:
    """Vocabulario de referencia (no restrictivo) usado en el prompt y en la
    normalización posterior de sub_items."""
    taxonomy = taxonomy or load_taxonomy()
    return list(taxonomy[domain_id]["sub_items"])

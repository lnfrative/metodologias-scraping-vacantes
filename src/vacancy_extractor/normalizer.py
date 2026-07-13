"""Normaliza los sub-ítems extraídos por el modelo para mantener consistencia
terminológica (ej. siempre "PHP", nunca "php"/"Php"), sin restringir el
vocabulario a una lista cerrada: los términos no reconocidos se conservan tal
como los devuelve el modelo (solo se les recorta espacio en blanco) en vez de
descartarlos o encasillarlos en un valor genérico tipo "Otro"."""

from __future__ import annotations

from . import taxonomy as taxonomy_module

# Alias comunes -> forma canónica. Complementa el vocabulario base de taxonomy.json
# para cubrir abreviaturas/variantes frecuentes en vacantes reales.
_KNOWN_ALIASES = {
    "js": "JavaScript",
    "javascript": "JavaScript",
    "ts": "TypeScript",
    "typescript": "TypeScript",
    "k8s": "Kubernetes",
    "postgres": "PostgreSQL",
    "psql": "PostgreSQL",
    "mongo": "MongoDB",
    "aws": "AWS",
    "amazon web services": "AWS",
    "gcp": "GCP",
    "google cloud": "GCP",
    "google cloud platform": "GCP",
    "azure": "Azure",
    "microsoft azure": "Azure",
    "ci/cd": "CI/CD",
    "cicd": "CI/CD",
    "ci-cd": "CI/CD",
    "node": "Node.js",
    "nodejs": "Node.js",
    "node.js": "Node.js",
    "dotnet": ".NET",
    ".net": ".NET",
    "rest api": "REST",
    "restful": "REST",
    "scrum master": "Scrum",
}


def _build_canonical_index(taxonomy: dict) -> dict[str, str]:
    index = dict(_KNOWN_ALIASES)
    for domain in taxonomy.values():
        for item in domain["sub_items"]:
            index.setdefault(item.strip().lower(), item.strip())
    return index


def normalize_sub_items(items: list[str], taxonomy: dict | None = None) -> list[str]:
    """Recorta espacios, colapsa duplicados (case-insensitive) y remapea a la
    forma canónica cuando el término es reconocido. Preserva términos nuevos
    tal cual los reportó el modelo."""
    taxonomy = taxonomy or taxonomy_module.load_taxonomy()
    index = _build_canonical_index(taxonomy)

    seen: set[str] = set()
    normalized: list[str] = []
    for raw in items:
        cleaned = " ".join(raw.strip().split())
        if not cleaned:
            continue
        canonical = index.get(cleaned.lower(), cleaned)
        dedup_key = canonical.lower()
        if dedup_key in seen:
            continue
        seen.add(dedup_key)
        normalized.append(canonical)
    return normalized

"""Clasificación semántica de la vacante contra la taxonomía de 7 dominios,
usando OpenAI Structured Outputs (JSON Schema estricto) para garantizar
consistencia terminológica en los sub-ítems extraídos."""

from __future__ import annotations

import json

from openai import OpenAI

from . import config, taxonomy as taxonomy_module
from .models import DomainResult
from .normalizer import normalize_sub_items

_SYSTEM_PROMPT_TEMPLATE = """Eres un clasificador experto en analizar vacantes de \
empleo tecnológico (Developer, Cloud, DevOps) para Ecuador. Tu tarea es leer el texto \
de una vacante y determinar, para cada uno de los 7 dominios taxonómicos definidos a \
continuación, si la vacante lo exige (requerido=true/false) y qué sub-ítems \
instrumentales específicos menciona.

Reglas estrictas:
- MUY IMPORTANTE: marca requerido=true SOLO si el dominio está mencionado explícita o \
inequívocamente en el texto de la vacante. Nunca infieras ni asumas un dominio que no \
aparece en el texto, aunque parezca "típico" para el cargo. Ante la duda, requerido=false.
- Si requerido=false, sub_items DEBE ser una lista vacía.
- Para sub_items tienes libertad total de extraer cualquier tecnología, herramienta o \
competencia mencionada explícitamente en el texto para ese dominio; no estás limitado a \
una lista fija. No omitas ni descartes una tecnología real solo porque no aparezca en los \
ejemplos de referencia — nunca uses un valor genérico como "Otro": escribe el nombre real \
de la tecnología.
- Usa siempre el nombre propio/oficial de cada tecnología con su capitalización estándar \
(ej. "PHP", "AWS", "Kubernetes", "PostgreSQL"), para que la misma tecnología se reporte \
siempre igual entre distintas vacantes.
- No agregues texto fuera del JSON solicitado.

A continuación, para cada dominio se listan ejemplos de referencia de sub-ítems típicos \
(NO es una lista cerrada, solo una guía de qué tipo de términos y qué capitalización usar):

{domains_description}
"""


def _build_system_prompt(taxonomy: dict) -> str:
    lines = []
    for domain_id, domain in taxonomy.items():
        sub_items = ", ".join(domain["sub_items"])
        lines.append(
            f"- {domain_id} ({domain['nombre']}, {domain['bloque']}): "
            f"{domain['descripcion']} Ejemplos de referencia: [{sub_items}]"
        )
    return _SYSTEM_PROMPT_TEMPLATE.format(domains_description="\n".join(lines))


class ExtractionError(Exception):
    """Error al clasificar la vacante con el modelo de lenguaje."""


def extract_domains(vacancy_text: str, url: str, client: OpenAI | None = None) -> list[DomainResult]:
    if not config.OPENAI_API_KEY:
        raise ExtractionError("OPENAI_API_KEY no está configurada (revisa tu archivo .env)")

    tax = taxonomy_module.load_taxonomy()
    schema = taxonomy_module.build_json_schema(tax)
    client = client or OpenAI(api_key=config.OPENAI_API_KEY)

    system_prompt = _build_system_prompt(tax)
    user_prompt = f"URL de la vacante: {url}\n\nTexto de la vacante:\n{vacancy_text}"

    try:
        response = client.chat.completions.create(
            model=config.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": "clasificacion_taxonomica",
                    "schema": schema,
                    "strict": True,
                },
            },
        )
    except Exception as exc:  # noqa: BLE001 - se relanza como error de dominio
        raise ExtractionError(f"Fallo la llamada a OpenAI: {exc}") from exc

    raw_content = response.choices[0].message.content
    try:
        parsed = json.loads(raw_content)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ExtractionError(f"La respuesta del modelo no es JSON válido: {exc}") from exc

    return _to_domain_results(parsed, tax)


def _to_domain_results(parsed: dict, tax: dict) -> list[DomainResult]:
    """Retorna siempre los 7 dominios de la taxonomía (esquema fijo), con
    requerido=true/false según lo que haya evaluado el modelo. Esto mantiene
    el dataset directamente consumible por pandas (misma forma tabular en
    todas las filas, sin necesidad de reindex/fillna al cargar) y preserva la
    trazabilidad de que el dominio sí fue evaluado y no encontrado, en vez de
    simplemente ausente."""
    results = []
    for domain_id, domain in tax.items():
        entry = parsed.get(domain_id, {"requerido": False, "sub_items": []})
        requerido = bool(entry.get("requerido", False))
        # Si no fue marcado como requerido, no arrastramos sub_items (evita
        # "fugas" donde el modelo llena sub_items de un dominio no mencionado).
        sub_items = normalize_sub_items(entry.get("sub_items", []), tax) if requerido else []
        results.append(
            DomainResult(
                dominio=domain_id,
                nombre=domain["nombre"],
                requerido=requerido,
                sub_items=sub_items,
            )
        )
    return results

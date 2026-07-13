"""CLI: extrae dominios taxonómicos de una vacante de empleo y los persiste en dataset.json."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from . import config, dataset_store
from .extractor import ExtractionError, extract_domains
from .fetcher import FetchError, fetch_vacancy_text
from .models import VacancyRecord


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="vacancy-extractor",
        description="Extrae los dominios y sub-ítems taxonómicos de una vacante de empleo.",
    )
    parser.add_argument("url", help="URL de la vacante a procesar")
    parser.add_argument(
        "--dataset",
        type=Path,
        default=config.DATASET_PATH,
        help="Ruta del archivo dataset.json (default: dataset.json en la raíz del proyecto)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Reprocesa y reemplaza el registro aunque la URL ya exista en el dataset",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Ejecuta el pipeline completo pero no escribe en el dataset; imprime el resultado",
    )
    return parser


def _print_summary(record: VacancyRecord) -> None:
    print(f"\nURL: {record.url}")
    print(f"URL normalizada: {record.url_normalizada}")
    requeridos = [d for d in record.dominios if d.requerido]
    if not requeridos:
        print("  (no se detectó ningún dominio taxonómico en el texto)")
        return
    for domain in requeridos:
        items = ", ".join(domain.sub_items) if domain.sub_items else "(sin sub-ítems)"
        print(f"  [{domain.dominio}] {domain.nombre}: {items}")


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    url_normalizada = dataset_store.normalize_url(args.url)

    if not args.dry_run and not args.force:
        if dataset_store.is_duplicate(args.dataset, url_normalizada):
            print(f"URL ya presente en el dataset, se omite: {url_normalizada}")
            print("(usa --force para reprocesar)")
            return 0

    try:
        text = fetch_vacancy_text(args.url)
        if not text:
            print("Error: el texto limpio quedó vacío tras procesar el HTML.", file=sys.stderr)
            return 1

        domains = extract_domains(text, args.url)
    except FetchError as exc:
        print(f"Error al descargar la vacante: {exc}", file=sys.stderr)
        return 1
    except ExtractionError as exc:
        print(f"Error al extraer dominios con el modelo: {exc}", file=sys.stderr)
        return 1

    record = VacancyRecord.create(url=args.url, url_normalizada=url_normalizada, dominios=domains)

    if args.dry_run:
        print("[dry-run] No se escribió en el dataset.")
        _print_summary(record)
        return 0

    written = dataset_store.upsert_record(args.dataset, record, force=args.force)
    if written:
        print(f"Registro guardado en {args.dataset}")
        _print_summary(record)
    else:
        print(f"URL ya presente en el dataset, se omite: {url_normalizada}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

# Vacancy Extractor

CLI que extrae, a partir de la URL de una vacante de empleo, los dominios taxonómicos y
sub-ítems técnicos que exige (bases de datos, desarrollo de software, arquitectura
distribuida, cloud, DevOps, metodologías ágiles y habilidades blandas), usando OpenAI
Structured Outputs, y los persiste en `dataset.json` sin duplicar por URL.

Este proyecto es parte del avance metodológico del paper *"Análisis de la Brecha de
Empleabilidad para Roles de Developer, Cloud y DevOps"* (Fase 2: Análisis de la Demanda
Laboral).

## Requisitos

- Python >= 3.9
- Una API key de OpenAI

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
playwright install chromium
```

Configura tu API key:

```bash
cp .env.example .env
# edita .env y coloca OPENAI_API_KEY=sk-...
```

## Uso

```bash
python -m vacancy_extractor "<url-de-la-vacante>"
```

Se abrirá brevemente una ventana de Chromium (necesaria para renderizar portales que
cargan el contenido vía JavaScript) y el resultado se guarda en `dataset.json`.

Opciones:

| Flag | Descripción |
|---|---|
| `--dry-run` | Ejecuta todo el pipeline pero no escribe en el dataset; solo imprime el resultado. |
| `--force` | Reprocesa y reemplaza el registro aunque la URL ya exista en el dataset. |
| `--dataset <ruta>` | Usa un archivo de salida distinto a `dataset.json`. |

La deduplicación es automática: si vuelves a correr la misma URL (normalizada, sin
parámetros de tracking) sin `--force`, se omite y no se vuelve a llamar a la API.

## Estructura del proyecto

```
taxonomy.json              # 7 dominios base + vocabulario de referencia (D1–D7)
src/vacancy_extractor/
  fetcher.py                # descarga y renderiza el HTML (Playwright)
  cleaner.py                 # HTML -> texto plano
  extractor.py                # llamada a OpenAI (Structured Outputs)
  normalizer.py                # normaliza términos (ej. "php" -> "PHP")
  dataset_store.py              # persistencia + deduplicación por URL
  cli.py                         # entrypoint del CLI
dataset.json                # salida acumulada (no versionado en git)
```

## Tests

```bash
pytest tests/ -q
```

Los tests cubren limpieza de HTML, taxonomía/schema, normalización y el almacén de
datos. No requieren API key (no llaman a OpenAI).

## Notas

- `taxonomy.json` es editable: agregar/quitar sub-ítems de referencia no rompe nada,
  el modelo tiene libertad de reportar tecnologías no listadas (se normalizan igual).
- El navegador se lanza en modo *headed* (con ventana) por defecto porque algunos
  portales bloquean Chromium en modo headless. Configurable con `PLAYWRIGHT_HEADLESS=true`
  en `.env` si tu entorno no tiene interfaz gráfica y el portal no bloquea headless.

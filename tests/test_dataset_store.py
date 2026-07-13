import json

from vacancy_extractor import dataset_store
from vacancy_extractor.models import DomainResult, VacancyRecord


def _make_record(url: str) -> VacancyRecord:
    url_norm = dataset_store.normalize_url(url)
    domains = [DomainResult(dominio="D1", nombre="Bases de datos", requerido=True, sub_items=["SQL"])]
    return VacancyRecord.create(url=url, url_normalizada=url_norm, dominios=domains)


def test_normalize_url_strips_tracking_params_and_trailing_slash():
    a = dataset_store.normalize_url("https://Example.com/jobs/123/?utm_source=li&ref=abc")
    b = dataset_store.normalize_url("https://example.com/jobs/123")
    assert a == b


def test_upsert_inserts_new_record(tmp_path):
    path = tmp_path / "dataset.json"
    record = _make_record("https://example.com/job/1")

    written = dataset_store.upsert_record(path, record)

    assert written is True
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["url_normalizada"] == record.url_normalizada


def test_upsert_skips_duplicate_without_force(tmp_path):
    path = tmp_path / "dataset.json"
    record = _make_record("https://example.com/job/1")
    dataset_store.upsert_record(path, record)

    written_again = dataset_store.upsert_record(path, record, force=False)

    assert written_again is False
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) == 1


def test_upsert_replaces_duplicate_with_force(tmp_path):
    path = tmp_path / "dataset.json"
    record = _make_record("https://example.com/job/1")
    dataset_store.upsert_record(path, record)

    updated = _make_record("https://example.com/job/1")
    updated.dominios[0].sub_items = ["PostgreSQL"]
    written_again = dataset_store.upsert_record(path, updated, force=True)

    assert written_again is True
    data = json.loads(path.read_text(encoding="utf-8"))
    assert len(data) == 1
    assert data[0]["dominios"][0]["sub_items"] == ["PostgreSQL"]


def test_is_duplicate(tmp_path):
    path = tmp_path / "dataset.json"
    record = _make_record("https://example.com/job/1")
    assert dataset_store.is_duplicate(path, record.url_normalizada) is False

    dataset_store.upsert_record(path, record)

    assert dataset_store.is_duplicate(path, record.url_normalizada) is True

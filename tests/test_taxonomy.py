import json

import pytest

from vacancy_extractor.taxonomy import (
    TaxonomyError,
    build_json_schema,
    canonical_vocabulary,
    load_taxonomy,
)


@pytest.fixture(autouse=True)
def _clear_cache():
    load_taxonomy.cache_clear()
    yield
    load_taxonomy.cache_clear()


def test_load_real_taxonomy_has_seven_domains():
    tax = load_taxonomy()
    assert set(tax.keys()) == {f"D{i}" for i in range(1, 8)}
    for domain in tax.values():
        assert domain["bloque"] in {"Duras", "Blandas"}
        assert isinstance(domain["sub_items"], list)
        assert len(domain["sub_items"]) > 0


def test_build_json_schema_matches_domains():
    tax = load_taxonomy()
    schema = build_json_schema(tax)

    assert schema["type"] == "object"
    assert set(schema["required"]) == set(tax.keys())
    for domain_id in tax:
        prop = schema["properties"][domain_id]
        # sub_items debe ser texto libre (sin enum) para no perder tecnologías
        # reales no anticipadas en el vocabulario de referencia.
        assert "enum" not in prop["properties"]["sub_items"]["items"]
        assert prop["properties"]["sub_items"]["items"]["type"] == "string"
        assert prop["additionalProperties"] is False


def test_canonical_vocabulary_is_reference_only_no_otro_bucket():
    tax = load_taxonomy()
    items = canonical_vocabulary("D2", tax)
    assert "PHP" in items
    assert "Otro" not in items


def test_missing_file_raises(tmp_path):
    with pytest.raises(TaxonomyError):
        load_taxonomy(tmp_path / "does-not-exist.json")


def test_missing_required_field_raises(tmp_path):
    bad_path = tmp_path / "taxonomy.json"
    bad_path.write_text(json.dumps({"D1": {"bloque": "Duras", "nombre": "X"}}), encoding="utf-8")
    with pytest.raises(TaxonomyError):
        load_taxonomy(bad_path)

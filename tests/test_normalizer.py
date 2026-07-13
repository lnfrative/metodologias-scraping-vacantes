from vacancy_extractor.normalizer import normalize_sub_items
from vacancy_extractor.taxonomy import load_taxonomy


def test_known_alias_is_canonicalized():
    result = normalize_sub_items(["php", "AWS", "js"])
    assert result == ["PHP", "AWS", "JavaScript"]


def test_case_insensitive_dedup_keeps_first_occurrence():
    result = normalize_sub_items(["Kubernetes", "kubernetes", "KUBERNETES"])
    assert result == ["Kubernetes"]


def test_unknown_term_is_preserved_not_dropped():
    result = normalize_sub_items(["Symfony", "Deno"])
    assert result == ["Symfony", "Deno"]


def test_whitespace_is_trimmed_and_collapsed():
    result = normalize_sub_items(["  Docker   Compose  "])
    assert result == ["Docker Compose"]


def test_empty_strings_are_ignored():
    result = normalize_sub_items(["", "   ", "Python"])
    assert result == ["Python"]


def test_uses_taxonomy_vocabulary_for_correct_casing():
    tax = load_taxonomy()
    result = normalize_sub_items(["postgresql", "mongodb"], tax)
    assert result == ["PostgreSQL", "MongoDB"]

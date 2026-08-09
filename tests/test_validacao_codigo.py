"""Testes da regra de unicidade de código (funções puras)."""

from collections import Counter

from gerapop.session import encontrar_codigo_duplicado
from gerapop.ui.main import _historico_label


def _record(pop_id: str, codigo: str, nome: str = "Registro de Manobras") -> dict:
    return {
        "id": pop_id,
        "codigo": codigo,
        "nome_pop": nome,
        "created_at": "2026-08-09T10:30:00.000000",
    }


def test_sem_conflito_retorna_none() -> None:
    records = [_record("a1", "POP-OPE-001")]
    assert encontrar_codigo_duplicado("POP-OPE-002", records, set()) is None


def test_conflito_fora_da_permissao() -> None:
    records = [_record("a1", "POP-OPE-001")]
    assert encontrar_codigo_duplicado("POP-OPE-001", records, set()) == records[0]


def test_conflito_permitido_retorna_none() -> None:
    records = [_record("a1", "POP-OPE-001")]
    assert encontrar_codigo_duplicado("POP-OPE-001", records, {"a1"}) is None


def test_codigo_vazio_nunca_bloqueia() -> None:
    records = [_record("a1", "")]
    assert encontrar_codigo_duplicado("", records, set()) is None


def test_retorna_o_mais_recente() -> None:
    antigo = _record("a1", "POP-OPE-001", "Versão antiga")
    novo = _record("b2", "POP-OPE-001", "Versão nova")
    assert encontrar_codigo_duplicado("POP-OPE-001", [novo, antigo], {"a1"}) == novo


def test_historico_label_sem_repeticao() -> None:
    record = _record("a1", "POP-OPE-001")
    label = _historico_label(record, Counter({"POP-OPE-001": 1}))
    assert label == "2026-08-09T10:30:00 — POP-OPE-001 — Registro de Manobras"


def test_historico_label_marca_repeticao() -> None:
    record = _record("a1", "POP-OPE-001")
    label = _historico_label(record, Counter({"POP-OPE-001": 2}))
    assert "POP-OPE-001" in label
    assert "⚠ (2)" in label

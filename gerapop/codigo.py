"""Regras de unicidade de código e rótulos do histórico (módulo puro)."""

from __future__ import annotations

from collections import Counter
from typing import Any


def encontrar_codigo_duplicado(
    codigo: str,
    records: list[dict[str, Any]],
    ids_permitidos: set[str],
) -> dict[str, Any] | None:
    """Retorna o registro mais recente com o mesmo código fora da permissão.

    Espera a lista ordenada por data de criação desc (como `list_pops`
    entrega), de modo que o primeiro conflito é o registro mais recente.
    Código vazio nunca é considerado duplicado.
    """
    if not codigo:
        return None
    for record in records:
        if record["codigo"] == codigo and record["id"] not in ids_permitidos:
            return record
    return None


def historico_label(record: dict[str, Any], contagem_codigos: Counter[str]) -> str:
    """Rótulo de um registro do histórico, com marca de código repetido."""
    codigo = record["codigo"] or "POP"
    label = f"{record['created_at'][:19]} — {codigo} — {record['nome_pop'][:40]}"
    if contagem_codigos[record["codigo"]] > 1:
        label += f" ⚠ ({contagem_codigos[record['codigo']]})"
    return label

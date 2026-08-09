"""Componentes reutilizáveis da interface Streamlit."""

from gerapop.constants import SessionKey
from gerapop.session import remove_item


def remove_at(session_key: SessionKey, index: int) -> None:
    remove_item(session_key, index)

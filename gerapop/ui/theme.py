"""Tema visual — identidade CODEBA (logo, paleta, claro/escuro).

Paleta extraída do logotipo oficial da CODEBA (codeba.gov.br,
codeba-brasil.png): navy #00185A como cor primária, verde #0E963D,
amarelo #F2C804 e índigo #332A83 como cores de apoio.
"""

import os
from pathlib import Path

import streamlit as st

THEME_KEY = "theme"
_THEME_DEFAULT = os.environ.get("GERAPOP_DEFAULT_THEME", "light")

_CSS_FILE = Path(__file__).with_name("theme.css")
_LOGO_LIGHT = Path(__file__).parent.parent / "assets" / "logo-codeba.png"
_LOGO_DARK = Path(__file__).parent.parent / "assets" / "logo-codeba-branca.png"

_VARS = {
    "light": {
        "BG": "#F4F5FA",
        "SURFACE": "#FFFFFF",
        "SIDEBAR": "#FFFFFF",
        "HEADING": "#12162A",
        "TEXT": "#12162A",
        "MUTED": "#5C6483",
        "PRIMARY": "#0F766E",
        "PRIMARY_TEXT": "#FFFFFF",
        "PRIMARY_HOVER": "#0B5E57",
        "ACCENT": "#0F766E",
        "ACCENT_DIM": "rgba(15, 118, 110, 0.12)",
        "BORDER": "#DDE1EE",
        "INPUT_BG": "#EEF0F8",
        "HOVER": "#EEF0F8",
        "SWITCH": "#0F766E",
        "HERO_G1": "#3B3FA6",
        "HERO_G2": "#5A4BC4",
        "DANGER": "#DC2626",
        "DANGER_DIM": "rgba(220, 38, 38, 0.10)",
        "OPTIONAL": "#6B7494",
        "OPTIONAL_DIM": "rgba(107, 116, 148, 0.12)",
    },
    "dark": {
        "BG": "#0A0E1C",
        "SURFACE": "#111834",
        "SIDEBAR": "#111834",
        "HEADING": "#F2F4FA",
        "TEXT": "#F2F4FA",
        "MUTED": "#9AA3C4",
        "PRIMARY": "#2DD4BF",
        "PRIMARY_TEXT": "#06231F",
        "PRIMARY_HOVER": "#3DE0CB",
        "ACCENT": "#2DD4BF",
        "ACCENT_DIM": "rgba(45, 212, 191, 0.14)",
        "BORDER": "#262F52",
        "INPUT_BG": "#161F42",
        "HOVER": "#161F42",
        "SWITCH": "#2DD4BF",
        "HERO_G1": "#2B2F7C",
        "HERO_G2": "#4C3FA0",
        "DANGER": "#E5484D",
        "DANGER_DIM": "rgba(229, 72, 77, 0.15)",
        "OPTIONAL": "#6B7494",
        "OPTIONAL_DIM": "rgba(107, 116, 148, 0.18)",
    },
}


def inject_theme_css(theme: str) -> None:
    """Injeta o CSS do tema com as cores da paleta CODEBA."""
    css = _CSS_FILE.read_text(encoding="utf-8")
    for name, value in _VARS[theme].items():
        css = css.replace(f"__{name}__", value)
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def _render_logo(theme: str) -> None:
    logo = _LOGO_DARK if theme == "dark" else _LOGO_LIGHT
    st.sidebar.image(str(logo), use_container_width=True)


def init_theme() -> None:
    """Aplica a identidade CODEBA: logo na sidebar + CSS do tema."""
    theme = st.session_state.get(THEME_KEY, _THEME_DEFAULT)
    _render_logo(theme)
    inject_theme_css(theme)


def render_theme_toggle() -> None:
    """Toggle claro/escuro — renderizado no rodapé da sidebar, após a navegação."""
    theme = st.session_state.get(THEME_KEY, _THEME_DEFAULT)
    dark = st.sidebar.toggle("Tema escuro", value=theme == "dark", key="theme_toggle")
    active = "dark" if dark else "light"
    if active != theme:
        st.session_state[THEME_KEY] = active
        st.rerun()

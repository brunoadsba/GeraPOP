# Ambiente Frontend — GeraPOP

Resumo da stack de frontend para outra LLM continuar o trabalho.

## App principal (GeraPOP)

- **Framework**: [Streamlit](https://streamlit.io) **1.41.1** (Python 3.11) — sem build step, sem npm, sem JS. UI 100% componentes nativos (`st.columns`, `st.container(border=True)`, `st.button`, `st.download_button`, `st.sidebar.radio`) + **HTML custom** via `st.markdown(unsafe_allow_html=True)`.
- **Tema próprio** (`gerapop/ui/theme.py` + `theme.css`): CSS com placeholders `__VAR__` (`__ACCENT__`, `__BORDER__`, `__SURFACE__`, `__TEXT__`, `__MUTED__`, `__HOVER__`, `__HERO_G1__`, `__HERO_G2__`) substituídos dinamicamente em `init_theme()`. Suporta **light/dark** seguindo a preferência do Streamlit. Classes:
  - `.pop-dash-*` → dashboard: hero em gradiente, 4 KPIs, stepper/timeline de etapas, chips, cards (via `[data-testid="stVerticalBlockBorderWrapper"]`)
  - `.pop-preview-*` → tela de leitura do POP: hero, chips de metadados, banner de aviso, tabelas, passos, regras
- **Navegação**: sidebar radio com 2 páginas — `🏠 Início` (dashboard) e `📝 Formulário`.

## Estrutura da UI (`gerapop/ui/`)

| Arquivo | Papel |
|---|---|
| `main.py` | Orquestração: navegação, formulário, download, histórico |
| `home.py` | Dashboard: hero + KPIs + stepper + cards gerados/pendentes + modelo de referência |
| `form_sections.py` | Formulário guiado com flags OBRIGATÓRIO/OPCIONAL (badges `.pop-flag-*`) |
| `simulacao.py` | Simulação RPA: preenche o formulário campo a campo com captions "Preenchendo: ..." |
| `preview.py` | **Tela de visualização de POPs em modo leitura** (session-state via `SessionKey.PREVIEW`), com baixar .docx/.pdf, editar e voltar |
| `theme.py` / `theme.css` | Tema + estilos custom |

## Visualização de POPs

- Clicar **"Visualizar POP"** no card (home) ou **"Visualizar"** no histórico → renderiza o POP formatado como documento dentro do app (não abre arquivo externo). Estado em `st.session_state[SessionKey.PREVIEW]` = `{"tipo": "fluxo"|"salvo", "ref": ...}`.

## Geração de documentos (saída)

- **DOCX**: python-docx 1.1.2 (`gerapop/services/docx/`)
- **PDF**: reportlab 5.0.0 (`gerapop/services/pdf/`) — nativo, sem LibreOffice
- Downloads .docx/.pdf em 3 pontos: geração, cards da home e histórico. **JSON não é mais baixável** (só storage interno).

## Frontend separado — fluxo-sev (`fluxo-sev/`)

- **HTML/CSS/JS puro, sem framework, sem build**: `index.html` + `style.css` + `app.js` (vanilla JS: `fetch` de JSON estático + modal de visualização do POP ao clicar no card do fluxo). Roda com `python -m http.server`.

## Qualidade

- **Testes de UI**: `streamlit.testing.v1.AppTest` (e2e headless do app inteiro) + pytest — **72 testes** passando. Ruff para lint/format via Makefile. `uv` para dependências.
- Visual QA manual via chromium headless (screenshots) — sem Playwright integrado ao projeto.

## Resumo

Streamlit 1.41.1 + CSS custom com placeholders de tema (light/dark) + HTML inline; docx/pdf via python-docx/reportlab; testes AppTest; sem JS frameworks em nenhum lugar do app principal.

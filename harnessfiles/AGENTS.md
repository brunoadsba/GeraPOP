# AGENTS.md — GeraPOP (CODEBA) · Harness de UX/UI para DeepSeek via OpenCode

## Quem você é
Agente de engenharia frontend focado em Streamlit, atuando exclusivamente sobre o projeto
**GeraPOP** (gerador de POPs para a CODEBA). Seu trabalho é melhorar UX/UI sem quebrar a stack
existente.

## Stack — NÃO MUDAR
- Streamlit 1.41.1, Python 3.11. Sem build step, sem npm, sem framework JS.
- UI = componentes nativos do Streamlit + HTML/CSS custom via `st.markdown(unsafe_allow_html=True)`.
- Tema: `gerapop/ui/theme.py` + `theme.css`, com placeholders `__VAR__` substituídos em
  `init_theme()`. Suporta light/dark seguindo a preferência do Streamlit — qualquer cor nova
  precisa de valor para os dois modos.
- Testes: `streamlit.testing.v1.AppTest` + pytest (72 testes). Lint/format: Ruff via Makefile.
  Deps: uv.
- `fluxo-sev/` é um app HTML/CSS/JS separado, vanilla. Regras deste harness não se aplicam a ele.

## Mapa de arquivos
| Arquivo | Papel |
|---|---|
| gerapop/ui/main.py | navegação, formulário, download, histórico |
| gerapop/ui/home.py | dashboard: hero, KPIs, stepper, cards |
| gerapop/ui/form/ | formulário guiado (widgets, identificacao, conteudo, dinamicas) |
| gerapop/ui/simulacao.py | simulação RPA de preenchimento |
| gerapop/ui/preview.py | tela de leitura do POP |
| gerapop/ui/downloads.py | botões .docx/.pdf reutilizáveis |
| gerapop/ui/historico.py | histórico de POPs + backup zip |
| gerapop/ui/theme.py / theme.css | tokens de tema e estilos |

## Regras inegociáveis
1. Nunca editar mais de um arquivo por iteração de UI, a menos que o `critique.json` peça uma
   mudança acoplada (ex: nova classe CSS + uso dela no componente).
2. Antes de finalizar qualquer edição: `uv run pytest -q` (72 testes verdes) e
   `ruff check --fix .`. Se algo quebrar, reverta a edição — não "conserte" o teste pra passar.
3. Toda cor nova entra como `__VAR__` em `theme.py`, com valor definido para light E dark.
4. Não introduzir framework JS, build step, ou dependências fora de
   python-docx / reportlab / streamlit / requests.
5. Não mexer em `fluxo-sev/` neste harness — é outro frontend, outro dono.
6. Peça confirmação antes de qualquer mudança estrutural (reordenar seções, remover campo,
   mudar fluxo de navegação). Mudanças puramente visuais (cor, espaçamento, tipografia,
   alinhamento, hierarquia) podem ser aplicadas direto.

## Como você recebe trabalho
Você não tem visão. O harness (`harness/ui_loop.py`) tira screenshots do app rodando, manda pra
um modelo com visão (o "crítico" — ex: Gemini), e te entrega um `critique.json` com problemas
priorizados em P0/P1/P2. Você trabalha em cima desse texto + de `design_system.md`, nunca da
imagem diretamente. Corrija só os itens `P0` e `P1` por rodada; deixe `P2` para depois, a menos
que seja trivial e sem risco.

## Formato de saída esperado
Para cada correção: diff mínimo no(s) arquivo(s) indicado(s), mais uma linha de changelog em
`harness/changelog.md` no formato:

```
[YYYY-MM-DD] area · issue_id · o que mudou · arquivo(s)
```

O script já cuida de anexar o changelog automaticamente a partir do `critique.json` — você só
precisa fazer a edição corresponder ao `id` do issue que está corrigindo.

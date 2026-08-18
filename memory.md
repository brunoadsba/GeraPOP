# GeraPOP — Memória de Contexto para LLMs

> Documento de continuidade do projeto. Leia antes de implementar qualquer feature.
> Última atualização: 2026-08-18 (reestruturação de UX/UI concluída: navegação no Sidebar com grupos semânticos "Visão Geral" e "Criação", novas páginas dedicadas `/fluxo` [Esteira do Fluxo SEV com abas de filtro] e `/pops` [Meus POPs / Biblioteca com busca em tempo real e backup], botão de edição instantânea na visualização de POPs, KPIs do dashboard alinhados com a esteira e isolamento estrito dos servidores de teste E2E; 62 pytest + 9 testes E2E Playwright 100% passando).

---

## 1. O que é este projeto

**GeraPOP** é um gerador de **POP** (Procedimento Operacional Padrão) para a **CODEBA** (Companhia de Navegação do Estado da Bahia — contexto portuário).

O usuário preenche um formulário guiado e recebe um arquivo `.docx` formatado, seguindo o modelo `POP_Manobras_CODEBA_v2.docx`.

**Repositório:** https://github.com/brunoadsba/GeraPOP.git  
**Branch principal:** `main`  
**Status atual:** MVP v1 completo (validação por seção, unicidade de código, rascunho persistente, backup zip, export JSON) + export **PDF** (reportlab) + **dashboard home** (KPIs/stepper do fluxo SEV) + **preview do POP** (modo leitura com botão Editar) + **simulação RPA** de preenchimento + **design system v2 sênior** (sidebar com navegação estruturada, `/fluxo` com abas, `/pops` com busca, tema light/dark, glassmorphism, ícones SVG inline, toasts, accordions, progresso de formulário) + **pacote de melhorias visuais v1.1** (sub-cabeçalhos de tela, respostas do sistema, negrito em aspas, cabeçalho de regras, rodapé com página — docx/pdf/fluxo-sev) + **migração de UI para web moderna concluída** (React 19 + TS + Vite 6 no frontend, FastAPI no backend); **62 pytest + 9 testes E2E Playwright 100% passando** (inclui 14 de integração da API); CI do GitHub desativado por pedido do usuário.

---

## 2. Visão de produto (dois projetos conectados)

Existe um pipeline maior documentado em `docs/plano.md`:

```
GeraPOP (Projeto 2)  →  dados estruturados  →  Fluxo Interativo SEV (Projeto 1)
   [este repo]              (pop.json)                 [v1 Desembarque entregue]
```

| Projeto | Nome | Status | Descrição |
|---------|------|--------|-----------|
| 2 | **GeraPOP** | MVP v1 completo | Formulário → `.docx` padronizado + `.json` reutilizável |
| 1 | **Fluxo Interativo SEV** | v1 parcial (só Desembarque) | Fluxogramas clicáveis (Desembarque ✅, Expedição, Recebimento-Exportação, Embarque-Armazenagem) linkando cada nó ao POP |

**Insight central:** o valor do GeraPOP não é só gerar Word — é **forçar estrutura padronizada** e produzir **dados reutilizáveis** para alimentar o Fluxo SEV.

**Ordem de execução (atualizada):**
1. ~~Validar GeraPOP com POP real~~ — feito (modelo OpenPort validado)
2. ~~Construir Fluxo SEV v1 consumindo dados do GeraPOP~~ — feito (Desembarque); **faltam 3 fluxos**
3. **Executar o piloto com a equipe** (`docs/piloto.md`) — gate atual, aguarda o usuário
4. Nuvem, multi-usuário e multi-agente **somente após** validação dos dois MVPs

---

## 3. Stack e restrições técnicas

| Item | Escolha |
|------|---------|
| Linguagem | Python 3.11 (**obrigatório no WSL** — 3.12 quebra `ctypes`) |
| Backend | FastAPI + uvicorn (substituiu o app Streamlit — arquivado em `obsoleto/gerapop-streamlit/`) |
| Frontend | React 19 + TypeScript + Vite 6 + Vanilla CSS (design system CODEBA migrado para `frontend/src/styles/`) |
| Geração doc | python-docx 1.1 |
| Testes | pytest (`tests/` — inclui `test_api_pops.py` com TestClient; E2E AppTest arquivados em `obsoleto/tests-streamlit/`) + Playwright E2E (`frontend/e2e/` — usa Chrome do sistema via `channel: 'chrome'`) |
| Lint/format | ruff (Python) + eslint (frontend) |
| Ambiente | uv + Makefile |
| Deploy v2 (futuro) | FastAPI + frontend estático em Docker + volume (persistente) — ver `docs/deploy.md` (deploy local por enquanto) |
| CI | GitHub Actions (`.github/workflows/ci.yml`) — **desativado** (`disabled_manually`, workflow id `330472653`); reativar com `gh workflow enable 330472653 --repo brunoadsba/GeraPOP` |
| Container | Docker + docker-compose (alternativa ao venv) |

**Persistência (v1.1):** POPs gerados são salvos automaticamente em `data/pops/<id>/` (`pop.json` + `pop.docx`) e listados no app (seção Histórico). Backup = botão "Backup (.zip)" no app ou `python -m gerapop.backup` (gera `data/backups/gerapop_YYYYMMDD_HHMMSS.zip`). `data/` é ignorado pelo git (apenas na raiz). **Exclusão (2026-08-13, migrada em 2026-08-17):** `storage.delete_pop(pop_id)` remove a pasta do POP (validação anti-traversal: o id resolvido precisa estar dentro de `data/pops/`, senão `ValueError`); na UI nova, botão "Excluir" disponível **no histórico (formulário) e nos cards de "POPs salvos no app" (home)**, com confirmação em 2 cliques ("Excluir" → "Sim, excluir"/"Cancelar") via modal no React.

**Rascunho persistente (v1.1):** o formulário salva rascunho a cada alteração — via hook `useDraft` (debounce 2 s → `PUT /api/draft`, `GET /api/draft` no mount, `DELETE /api/draft` após gerar e ao resetar/excluir). Restauração implementada em 2026-08-17: o `FormPage` escuta o evento `gerapop:draft:loaded` e faz `LOAD_POP` (merge com `emptyPop`); não sobrescreve navegação explícita (`novo_pop`/`carregar`/`editar_id`) e aplica o draft apenas uma vez por montagem (ref `aplicadoDraft`). Coberto por teste E2E ("restaura rascunho persistido entre sessões").

**Unicidade de código (v1.1):** a geração é bloqueada se o código já existe no histórico, com exceção para a edição do POP carregado (permissão `{loaded_from_id}`). Ver `gerapop/codigo.py` (`encontrar_codigo_duplicado`, módulo puro) e `POST /api/pops/check-code`; no frontend, debounce de 400 ms no campo código + 409 do servidor como fallback. No Histórico, POPs com códigos repetidos exibem sufixo ` ⚠ (N)` (`historico_label` em `gerapop/codigo.py`).

**Dados JSON (v1.1):** todo POP salvo gera `pop.json` em `data/pops/<id>/` (formato `{"metadata": ..., "pop": ...}`) — consumido pelo Projeto 1 (Fluxo SEV) e incluído no backup zip. **A UI não tem botão de download `.json`** (downloads são `.docx`/`.pdf`). Se o export JSON na UI voltar a ser necessário, reutilizar `get_pop_json_bytes` em `storage.py`.

**Fidelidade ao modelo (v1.1):** o `.docx` segue o modelo `POP_Manobras_CODEBA_v2` (validado em 2026-08-09 com o modelo real OpenPort): numeração plana automática das seções (1..N), aviso ⚠ dentro do Escopo, regras em tabela `R | texto`, consulta em caixa, fontes 18/13pt. **Campos obrigatórios por seção implementados** (G6): cada seção do Procedimento pode declarar campos obrigatórios, renderizados como tabela (Campo/Descrição) no `.docx` e validados no formulário.

**Larguras de tabela (v1.1):** todas as tabelas do `.docx` somam exatamente a largura útil da página (margem a margem). Regras obrigatórias: (1) largura total uniforme em todas as tabelas, calculada de `section.page_width - margins`; (2) passos numerados = coluna de número fixa `PASSO_COL_WIDTH_CM` (1 cm = 567 twips) + descrição preenchendo o restante; (3) `_validar_larguras_tabelas` roda antes de salvar e compensa divergências na última coluna — **mede pela primeira linha sem `gridSpan`** (linhas com sub-cabeçalho mergeado retornam width 0/None e distorceriam a soma; bug corrigido em 2026-08-13 com teste de regressão `test_larguras_validas_com_sub_cabecalho_na_primeira_linha`); (4) regras/restrições numeradas sequencialmente (R1, R2, R3...) em tabela única, nunca "R" repetido. Nota: o XML do .docx armazena larguras em twips (1 twip = 635 EMU), então leituras têm quantização de ±1 twip — os testes usam tolerância `< 635` EMU. Implementação: `services/docx/builder.py` (`_largura_util_emu`, `_larguras_tabela_emu`, `_set_col_widths`, `_validar_larguras_tabelas`) + `services/documento.py` (regras R1..RN em `montar_conteudo`).

**Melhorias visuais (v1.1):** convenções de texto aplicadas na renderização (docx + pdf + fluxo-sev), sem mudar o modelo de dados: (1) passo começando com `Tela ` vira sub-cabeçalho dentro da tabela de passos (docx: célula mergeada com gridSpan + shading `SHADING_SUB`/`COR_SUB`; pdf: SPAN + background; fluxo-sev: `<li class="sub">`); (2) passo começando com `Sistema ` vira resposta do sistema em itálico com "—" na coluna de número (`estilos_linha` da Tabela: ""/sub/sys — sub e sys não consomem numeração); (3) aspas simples **emparelhadas** viram negrito (`_segmentos_bold`/`_segmentos_bold_html`; aspas ímpares = texto literal, ex. `d'água`); (4) tabela de Regras ganhou cabeçalho "Regra | Descrição"; (5) rodapé em todas as páginas com `código · nome` à esquerda e `Versão · Pág. N` à direita (docx: `w:fldSimple PAGE` + tab stop; pdf: `onFirstPage/onLaterPages`). Dados do PS-002 (draft + pop.json salvo) já transformados para as convenções. **Armadilhas conhecidas:** (a) no `montar_conteudo`, o contador de passos usa `passo_numero` — **nunca reutilizar a variável `numero` da closure `titulo()`** (loops não criam escopo em Python; reutilizar reinicia a numeração dos títulos das seções seguintes — bug real corrigido em 2026-08-13); (b) células mergeadas (gridSpan) não têm largura confiável via `cell.width` — sempre pular em medições.

**O que a v1 NÃO faz (proposital):**
- Login / multi-usuário / nuvem — sem auth, qualquer pessoa com a URL pode criar/editar (risco aceito na v1, ver `docs/deploy.md` §Segurança)
- Vínculo integrado GeraPOP → fluxo-sev (hoje é manual: copiar o `.json` exportado para `fluxo-sev/data/pops/`)

---

## 4. Estrutura do código (pós-refatoração clean code)

```
gerapop/
├── app.py                          # Entrada → uvicorn backend.main:app (porta 8000)
├── memory.md                       # Este arquivo
├── guia-usuario.md                 # Guia do usuário final (seção 10 = campos obrigatórios)
├── backend/                        # API FastAPI (substitui a entrada Streamlit)
│   ├── main.py                     # App FastAPI + CORS (localhost:5173) + /api/health
│   ├── schemas.py                  # Modelos Pydantic (PopCreateRequest, PopListItem, Draft...)
│   ├── dependencies.py             # pop_from_request / pop_as_dict
│   └── routers/
│       ├── pops.py                 # CRUD + validate + check-code + fluxo
│       ├── generate.py             # POST /api/generate + docx/pdf (+ preview sem salvar)
│       ├── drafts.py               # Rascunho persistente (GET/PUT/DELETE /api/draft)
│       └── backup.py               # GET /api/backup (zip)
├── frontend/                       # React 19 + TypeScript + Vite 6
│   ├── vite.config.ts              # Proxy /api → http://localhost:8000
│   ├── src/
│   │   ├── main.tsx / App.tsx      # Router (/, /formulario, /preview/:type/:ref)
│   │   ├── api/client.ts           # Fetch wrappers tipados (listPops, generatePop, download...)
│   │   ├── hooks/                  # useTheme, usePopForm (useReducer), useDraft (auto-save)
│   │   ├── components/             # Layout (Sidebar), Dashboard (Hero/Kpi/Stepper/Card),
│   │   │                           #   Form (seções do POP + DynamicList), Simulation, History, ui/
│   │   ├── pages/                  # HomePage, FormPage, PreviewPage
│   │   ├── types/pop.ts            # Interfaces TS espelhando PopData
│   │   └── styles/                 # variables.css (tokens CODEBA light/dark) + global/dashboard/form/preview
│   └── public/                     # logos + favicon (copiados de gerapop/assets/)
├── gerapop/                        # Lógica de domínio (INALTERADA) — sem Streamlit
│   ├── __init__.py                 # Exporta PopData, gerar_docx, gerar_pdf
│   ├── constants.py                # ValidationMessage, estilos docx/pdf, MIME (SessionKey REMOVIDO)
│   ├── codigo.py                   # Unicidade de código + rótulo histórico (módulos puros)
│   ├── fluxo.py                    # carregar fluxo SEV + POP de referência (módulos puros)
│   ├── models.py                   # PopData, TypedDicts, validação, factories
│   ├── storage.py                  # Persistência em disco (pop.json + pop.docx) + backup zip
│   ├── backup.py                   # CLI de backup zip (python -m gerapop.backup)
│   ├── assets/                     # Logos CODEBA (light/dark) usados na sidebar
│   └── services/
│       ├── documento.py            # Modelo neutro de blocos (Titulo/Paragrafo/Aviso/Tabela)
│       ├── docx/
│       │   ├── styles.py           # Formatação de células Word
│       │   └── builder.py          # Renderiza os blocos neutros em .docx
│       └── pdf/
│           └── builder.py          # Renderiza os blocos neutros em PDF (reportlab)
├── tests/
│   ├── conftest.py                 # Fixtures (data dir tmp, pop_minimo/pop_invalido)
│   ├── test_api_pops.py            # Integração da API FastAPI (14 testes)
│   ├── test_docx_builder.py
│   ├── test_validacao_codigo.py    # Unit unicidade + label de histórico (via gerapop.codigo)
│   ├── test_fluxo_sev.py           # Valida dados estáticos do fluxo-sev
│   ├── test_models.py
│   └── test_storage.py
├── obsoleto/
│   ├── ideia-files/                # Protótipo original (versionado)
│   ├── gerapop-streamlit/          # UI Streamlit arquivada (ui/, session_draft.py, session_codigo.py)
│   ├── tests-streamlit/            # E2E AppTest arquivados (test_e2e_app, test_home, ...)
│   └── ambiente-fronend.md, telas-recriadas.html
├── docs/
│   ├── plano.md                    # Roadmap completo
│   ├── piloto.md                   # Roteiro do piloto com a equipe (GATE aguarda usuário)
│   └── deploy.md                   # Opções de hospedagem (Cloud efêmero vs Docker)
├── Makefile
├── pyproject.toml
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### Responsabilidades por camada

| Camada | Arquivo(s) | Responsabilidade |
|--------|-----------|------------------|
| Entrada | `app.py` | Bootstrap FastAPI (uvicorn) |
| API | `backend/` | REST: CRUD, geração docx/pdf, rascunho, backup, fluxo |
| Frontend | `frontend/` | React/TS: dashboard, formulário, preview, histórico, simulação, tema |
| Domínio | `models.py` | `PopData`, validação, normalização |
| Constantes | `constants.py` | Enums, magic strings, config docx |
| Serviço | `services/docx/`, `services/pdf/` | Geração `.docx`/`.pdf` (sem dependência de Streamlit) |
| Persistência | `storage.py`, `backup.py` | Disco + backup zip (CLI) |
| Módulos puros | `codigo.py`, `fluxo.py` | Regras reutilizadas por API e frontend |

**Regra:** lógica de negócio e geração de documento **nunca** devem ficar em `app.py`, `backend/` ou `frontend/` — manter testável sem web.

---

## 5. Modelo de dados do POP

Estrutura baseada em `POP_Manobras_CODEBA_v2.docx`:

1. **Identificação** — Nome, Código*, Versão, Data, Área*, Aviso (opcional)
2. **Objetivo*** 
3. **Escopo e Pré-condições**
4. **Definições** — lista dinâmica (termo + definição)
5. **Procedimento** — seções dinâmicas, cada uma com passos numerados e **campos obrigatórios** (tabela Campo/Descrição no `.docx`)
6. **Regras e Restrições** — lista dinâmica
7. **Consulta e Relatórios** (opcional)
8. **Histórico de Revisões** — revisão, data, descrição, responsável

Campos obrigatórios na validação: **nome, código, área, objetivo**. Código deve ser **único** no histórico (bloqueio com exceção para edição do POP carregado).

Classe principal: `PopData` em `gerapop/models.py`.  
Contrato frontend ↔ backend: schemas Pydantic em `backend/schemas.py` ↔ interfaces TS em `frontend/src/types/pop.ts`.

---

## 6. Como rodar, testar e validar

```bash
# Setup (primeira vez)
make install-dev
cd frontend && npm install

# Desenvolvimento
make run          # backend (http://localhost:8000) + frontend (http://localhost:5173)
make run-backend  # só a API
make run-frontend # só o frontend

# Qualidade
make test         # 62 pytest (storage + docx + pdf + models + unicidade + fluxo-sev + 14 de API)
make lint         # ruff check + format --check (Python) e eslint (frontend)
make format       # auto-format
cd frontend && npm run test:e2e   # 9 testes E2E Playwright (Chrome do sistema)

# Backup
make backup       # zip com todos os POPs + rascunho

# Docker (alternativa)
make docker-run
```

**Notas:**
- **Registro npm corporativo:** `registry.npmjs.org` retorna 403/timeout na rede atual — usar `npm install --registry https://registry.yarnpkg.com`.
- **Problema conhecido:** Python 3.12 no WSL2 causa segfault no Streamlit (`ctypes` corrompido). Sempre usar **Python 3.11** (`.python-version` = `3.11`).

---

## 7. Convenções de desenvolvimento

Seguir estas regras ao continuar o projeto:

1. **KISS / YAGNI** — não adicionar nuvem, auth, framework antes de validação real (piloto)
2. **Arquivos < 200 linhas** — quebrar se ultrapassar
3. **Clean code** — uma responsabilidade por módulo; sem lógica de docx na UI
4. **Testes** — toda lógica de domínio/serviço deve ter teste pytest; suite deve ficar verde antes de push
5. **Commits semânticos** — formato: `tipo(escopo): descrição` (ex: `feat(docx): export JSON`)
6. **Português BR** — comunicação e mensagens de validação em português
7. **Não commitar** `.venv/`, `*.docx`, secrets, `data/` (raiz), `.omo/`
8. **Atualizar este `memory.md`** sempre que o estado do projeto mudar de direção
9. **Arquivos obsoletos vão para `obsoleto/`** (versionado, arquivamento) — não apagar

---

## 8. Estado atual do repositório (2026-08-17)

### Já no GitHub (`main`) — em ordem cronológica
- `feat(gerapop): estrutura inicial do MVP com Streamlit e geração de POP`
- `refactor(gerapop): reorganiza projeto em camadas e adiciona memory.md`
- `feat(ui): campos obrigatórios por seção (G6)` — `62413bd`, `fb874f5`, `fa0e712`, `10601ba`
- `feat(ui): rascunho persistente entre sessões` — `23f6666`
- `feat(backup): zip com todos os POPs` — `6f6ea7d`
- `docs(deploy): opções de hospedagem` — `862067a`
- `docs(piloto): roteiro do piloto com a equipe` — `38898aa`
- `feat(fluxo-sev): diagrama interativo v1 (Desembarque)` — `1ba0927`, `5555604`
- `feat(ui): unicidade de código + marcação ⚠ no histórico` — `339f67a`, `322fd3e`, `d5f73e5`
- `refactor(tests): helpers E2E no conftest` — `472c87d`
- `refactor: simplificações pós-auditoria (templates, bold morto, Counter)` — `4051f82`
- `style: ruff format` — `48f65c2`
- `docs(readme): estrutura e escopo v1 atualizados` — `8f218ea`
- `chore(repo): arquiva protótipo em obsoleto/ e versiona dados do fluxo-sev` — `5598bd8`
- `docs(memory): atualizar estado do projeto` — `7d1d40a`
- `feat(pdf): gerar PDF do POP com reportlab` — `9f6cd84`
- `feat(ui): dashboard, preview, simulacao e design system` — `d2be58d`
- `chore(harness): harness de UX/UI, mockup e docs de frontend` — `9edab35`

> Detalhes da limpeza: `ideia-files/` (protótipo original) movido para `obsoleto/ideia-files/` (pasta versionada de arquivamento — convenção §7.9); `.gitignore` `data/` → `/data/` (só raiz) para que `fluxo-sev/data/` (essencial ao `test_fluxo_sev.py`) fosse versionado; referências a `ideia-files/` removidas de `pyproject.toml` (ruff exclude) e `.ruffignore`; lixo local não versionado removido (`gerapop.egg-info/`, caches).

**Fora do repo (estado local):** CI do GitHub desativado por pedido do usuário (`gh workflow disable 330472653` — reativar com `gh workflow enable 330472653 --repo brunoadsba/GeraPOP`). O workflow roda `ruff` e `pytest` na stack nova (backend/ incluído no lint).

**Em andamento (local, NÃO commitado):** nada — migração concluída, commitada e pushed. Durante a sessão de 2026-08-17:
- **E2E Playwright = 9 testes** (`frontend/e2e/gerapop.spec.ts`): dashboard/KPIs, tema claro/escuro, validação de obrigatórios, gerar POP via card de etapa + baixar `.docx`/`.pdf`, simulação RPA, histórico/backup `.zip`, restauração de rascunho, código duplicado (409) e exclusão com confirmação. `playwright.config.ts` sobe backend (:8000) + frontend (:5173) com data dir isolado `.e2e-data/` (gitignored) e usa o **Chrome do sistema** via `channel: 'chrome'` (download do Chromium bloqueado na rede); scripts `npm run test:e2e`/`test:e2e:headed`; `globalSetup` limpa `.e2e-data/` por execução.
- **Bug do rascunho corrigido** (`FormPage.tsx`): listener de `gerapop:draft:loaded` restaura o form via `LOAD_POP` (merge com `emptyPop()`), guarda `navExplicita` (não sobrescreve `novo_pop`/`carregar`/`editar_id`), ref `aplicadoDraft` (aplica só 1x) e `discard()` no sucesso do gerar e em `onDelCache`.
- **Flakiness de storage corrigida** (`gerapop/storage.py`): `serialize_pop(pop, created_at=None)` + `_proximo_timestamp()` monotônico; `save_pop` usa timestamp estrito crescente — corrige `test_list_pops_ordena_mais_recente_primeiro` que falhava ~1/20 por empate de `created_at` no mesmo microssegundo (20/20 verde depois).
- **Commit + push para `main`** (9 commits, working tree limpo): `1a49bfb` archive Streamlit, `4a754f2` feat backend, `51b0194` refactor módulos puros, `52c4694` fix storage, `55d6222` feat frontend + E2E, `4701f01` gitignore frontend, `da7c1ee` build infra, `8f9848a` docs, `e9fcdaa` docs guia.
- **Guia do usuário atualizado** (`guia-usuario.md`): porta 8501→5173, botão "Carregar modelo" removido (modelo via Início), seção histórico reescrita.
- **Recuperação e réplica do POP-OPE-003:** o `data/` original não existia mais; os dados de teste vieram de `obsoleto/tests-streamlit/test_home.py`, porém o PDF de referência guardado pelo usuário em `teste/POP-OPE-003_TESTE_003.pdf` continha o POP **completo** (objetivo "TESTE DE OBJETIVO", escopo/aviso "TESTE DE ...", área `OPERAÇÕES PORTUÁRIAS`, seção "Acesso ao Sistema OpenPort" com 16 passos + 3 campos obrigatórios, 3 definições, 3 regras, 2 revisões). Reconstruído com o conteúdo exato extraído do PDF e salvo em `data/pops/20260817_141526_714749_14a15a/` (`pop.json` + `pop.docx` regravados); diff do PDF gerado vs referência confirma conteúdo 100% idêntico, mantendo as melhorias visuais atuais (negrito em aspas, regras R1/R2/R3) por decisão do usuário. Opcionalmente, os dados originais podem ser reconstruídos de `teste/POP-OPE-003_TESTE_003.pdf` (decodificar streams ASCII85+Flate) se outra cópia for necessária.

**Histórico recente (base da migração, já em `main` até `e8edbb5`):** melhorias visuais v1.1 (sub-cabeçalhos `Tela `, respostas `Sistema `, negrito em aspas, cabeçalho de regras, rodapé com página, validação de larguras com gridSpan, convenções no guia-usuario), exclusão de POP na home, guia do usuário e referência visual PS-002. A migração está **commitada e pushed** (§8 acima).

**Nota sobre o harness:** `harnessfiles/` contém o loop de crítica visual (screenshot → LLM com visão → correção) e o `changelog.md` acumulado. O `AGENTS.md` dele rege mudanças de UX/UI: cores novas sempre como `__VAR__` com light/dark, testes verdes antes de finalizar, mudanças estruturais exigem confirmação do usuário.

**Próxima ação sugerida:** validar ponta-a-ponta a nova stack (backend + frontend) com a equipe (`docs/piloto.md`) — gate que desbloqueia nuvem e os 3 fluxos SEV restantes.

---

## 9. Roadmap — próximos passos priorizados

### Curto prazo (GeraPOP v1.1) — entregue
- [x] Export JSON junto com `.docx` — habilita Projeto 1 (Fluxo SEV)
- [x] Testar com POP real da CODEBA e ajustar campos/layout — validado contra modelo OpenPort
- [x] Campos obrigatórios por seção (G6)
- [x] Rascunho persistente entre sessões
- [x] Backup zip (app + CLI)
- [x] Unicidade de código com exceção de edição
- [x] Fluxo SEV v1 (Desembarque) com QA Playwright
- [x] Clean code + docs (README, guia-usuario, deploy, piloto)
- [x] Export PDF (reportlab) — mesma estrutura do .docx
- [x] Dashboard home (KPIs, stepper, cards do fluxo SEV)
- [x] Preview do POP em modo leitura (com .docx/.pdf baixáveis)
- [x] Simulação RPA de preenchimento
- [x] Design system: paleta light/dark, componentes custom (hero, KPIs, stepper, badges, tooltips nativos, tabelas, container responsivo)
- [x] Harness de UX/UI (`harnessfiles/`): AGENTS.md + design_system.md + ui_loop.py + changelog
- [x] **Migração de UI:** Streamlit → React 19 + TS + Vite 6 (frontend) + FastAPI (backend) — `backend/`, `frontend/`, `implementation_plan.md` (commitada e pushed em `main`, `e9fcdaa`)
- [x] **E2E Playwright** (9 testes, Chrome do sistema) + **fix rascunho** + **fix flaky storage** + **recuperação do POP-OPE-003** idêntico ao PDF de referência (`teste/POP-OPE-003_TESTE_003.pdf`)

### Gate de negócio (aguarda usuário/equipe)
- [ ] **Piloto com a equipe** — `docs/piloto.md` (roteiro pronto, GATE explícito)

### Médio prazo (GeraPOP v2)
- [ ] Revalidar o app novo (React) ponta-a-ponta com a equipe (piloto) e ajustar Docker/CI da stack nova se necessário
- [ ] Hospedagem da nova stack (FastAPI + frontend estático): Docker + volume ou serviço similar — `docs/deploy.md`
- [ ] Reativar CI (`gh workflow enable 330472653`)
- [ ] Catálogo local de POPs (SQLite) — ideia, não iniciada
- [ ] Vínculo integrado GeraPOP → fluxo-sev (hoje: copiar `.json` manualmente)

### Projeto 1 — Fluxo SEV (parcial)
- [x] Schema de nós, HTML/CSS/JS puro, 1 fluxo (Desembarque) + POP vinculado
- [ ] Mapear 3 fluxos restantes: **Expedição, Recebimento-Exportação, Embarque-Armazenagem** (replicar `fluxo-<nome>.json` + `data-fluxo` no HTML + gerar POPs no GeraPOP)
- [ ] Migrar para TS/framework somente se o uso real justificar (gate do piloto)

---

## 10. Riscos e anti-padrões (NÃO fazer)

| Risco | Mitigação |
|-------|-----------|
| Overengineering | Sem Next.js, multi-agente ou nuvem antes da v1 validada |
| Template engessado | Formulário deve aceitar exceções operacionais |
| Confundir geração com validação | Gerador agiliza escrita, não substitui revisão técnica |
| Python 3.12 no WSL | Usar 3.11 sempre |
| Duplicar código | Manter DRY; extrair para `constants` ou `services` |
| Sem auth (v1) | Qualquer pessoa com a URL pode criar/editar — aceito na v1, documentado em `docs/deploy.md` |
| CI desativado | Reativar antes de nova rodada de desenvolvimento |
| Testes flaky de storage | `save_pop`/`serialize_pop` agora usam timestamps **monotônicos** (`_proximo_timestamp()` em `gerapop/storage.py`) — dois saves no mesmo microssegundo empatavam no `created_at` e quebrava `test_list_pops_ordena_mais_recente_primeiro` (~1/20); corrigido em 2026-08-17, 20/20 verde |
| Perda do `data/` original | `data/` de antes da migração não existe mais e não há backups `.zip`; POPs antigos não são recuperáveis (confirmado com o usuário; POP-OPE-003 era dado de teste). Novo padrão: guardar uma cópia PDF/docx do POP em `teste/` como referência e reconstruir o JSON via extração dos streams (fonte de recuperação futura) |

---

## 11. Referências rápidas

| Recurso | Caminho |
|---------|---------|
| Roadmap completo | `docs/plano.md` |
| Roteiro do piloto | `docs/piloto.md` (GATE aguarda usuário) |
| Opções de hospedagem | `docs/deploy.md` |
| Instruções de uso | `README.md` |
| Guia do usuário final | `guia-usuario.md` |
| Modelo POP | `POP_Manobras_CODEBA_v2.docx` (referência externa, não no repo) |
| Referência do POP teste | `teste/POP-OPE-003_TESTE_003.pdf` (PDF de referência do usuário; fonte para reconstruir `POP-OPE-003`) |
| Protótipo original (arquivado) | `obsoleto/ideia-files/` (não usar) |
| Módulo Fluxo SEV | `fluxo-sev/README.md` + `fluxo-sev/memory/000-fluxo-sev-v1.md` |
| Plano de migração | `implementation_plan.md` (raiz) — Fases 1–6, verificação e arquivamento |
| Config backend/frontend | CORS em `backend/main.py`; proxy `/api` em `frontend/vite.config.ts` |
| Config Streamlit (legado) | `.streamlit/config.toml` (não usado pela stack nova) |
| CI | `.github/workflows/ci.yml` (desativado) |

---

## 12. Prompt de continuidade (copiar para nova sessão)

```
Contexto: Projeto GeraPOP (CODEBA) — gerador de POP com backend FastAPI + frontend
React 19/TS/Vite 6 + python-docx + reportlab.
Leia memory.md e docs/plano.md antes de codar.

Stack: Python 3.11, FastAPI (backend/), React+TS+Vite (frontend/), python-docx,
reportlab, pytest, ruff, eslint.
Arquitetura: gerapop/models (domínio), services/docx + services/pdf (geração),
backend/ (API REST), frontend/ (dashboard, formulário, preview, histórico,
simulação, tema light/dark), fluxo-sev/ (Projeto 1, HTML/CSS/JS puro).
UI Streamlit antiga arquivada em obsoleto/gerapop-streamlit (não usar).

Estado: migração concluída, commitada e pushed (main até e9fcdaa); domínio e geração
intactos; 62 pytest + 9 E2E Playwright OK; ruff/eslint/tsc OK; CI desativado.
Dados: POP-OPE-003 (TESTE 003) recuperado e replicado em data/pops/<id>/ a partir
do PDF de referência em teste/ (conteúdo completo; mantém melhorias visuais atuais).
Próximo passo sugerido: validar ponta-a-ponta da nova stack com a equipe
(docs/piloto.md) — depois os 3 fluxos SEV restantes e a decisão de hospedagem.

NÃO implementar: nuvem, auth, multi-agente, migração de stack adicional sem validação.
```

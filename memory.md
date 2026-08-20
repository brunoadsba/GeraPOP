# GeraPOP — Memória de Contexto para LLMs

> Documento de continuidade do projeto. Leia antes de implementar qualquer feature.
> Última atualização: 2026-08-20 (Branch `ajustes-finos`: Alinhamento da saída DOCX/PDF ao padrão CODEBA a partir dos modelos `teste/POP-COM-001_*.{docx,pdf}` e `teste/POP-OPE-001_*.{docx,pdf}` — matriz de responsabilidades em 2 variantes (Tela / Fluxo), passos com responsável por linha, seções 7 Registros obrigatórios / 8 Critérios de encerramento / 9 Indicadores, header "Página X de Y" a partir da página 2, rodapé "cópia não controlada", fontes Calibri no PDF; biblioteca alimentada com POP-COM-001 e POP-OPE-001 via `scripts/seed_pops.py`; 68 pytest + 9 Playwright E2E 100% passando; eslint/tsc/vite build limpos).

---

## 1. O que é este projeto

**GeraPOP** é um gerador de **POP** (Procedimento Operacional Padrão) para a **CODEBA** (Companhia de Navegação do Estado da Bahia — contexto portuário).

O usuário preenche um formulário guiado e recebe arquivos `.docx` e `.pdf` formatados, seguindo o padrão oficial da CODEBA com logo e metadados no topo.

**Repositório:** https://github.com/brunoadsba/GeraPOP.git  
**Branch principal:** `main` (branch de trabalho atual: `ajustes-finos`)  
**Status atual:** MVP v1 completo (validação por seção, unicidade de código, rascunho persistente, backup zip, export JSON) + export **PDF** (reportlab com logo oficial CODEBA, metadados e revisões no topo em layout de alta densidade) + **dashboard home** (KPIs/stepper do fluxo SEV) + **preview do POP** (modo leitura com botão Editar e downloads) + **simulação RPA** de preenchimento + **design system v2 sênior** (sidebar com navegação estruturada, `/fluxo` com abas, `/pops` com busca, tema light/dark, glassmorphism, ícones SVG inline, toasts, accordions, progresso de formulário em 2 colunas) + **sete de melhorias visuais v1.1** (sub-cabeçalhos de tela, respostas do sistema, negrito em aspas, cabeçalho de regras, rodapé com linha divisória e paginação — docx/pdf/fluxo-sev) + **padrão CODEBA aplicado à saída** (matriz de responsabilidades 2 variantes, passos com responsável por linha, seções 7/8/9, header "Página X de Y" página 2+, rodapé cópia não controlada, fontes Calibri) + **biblioteca alimentada** (`data/pops/` com POP-COM-001 e POP-OPE-001 via `scripts/seed_pops.py`) + **migração de UI para web moderna concluída** (React 19 + TS + Vite 6 no frontend, FastAPI no backend); **68 pytest + 9 testes E2E Playwright 100% passando**; tsc/eslint/build limpos.

---

## 2. Visão de produto (dois projetos conectados)

Existe um pipeline maior documentado em `docs/plano.md`:

```
GeraPOP (Projeto 2)  →  dados estruturados  →  Fluxo Interativo SEV (Projeto 1)
   [este repo]              (pop.json)                 [v1 Desembarque entregue]
```

| Projeto | Nome | Status | Descrição |
|---------|------|--------|-----------|
| 2 | **GeraPOP** | MVP v1 completo | Formulário → `.docx` padronizado + `.pdf` oficial + `.json` reutilizável |
| 1 | **Fluxo Interativo SEV** | v1 parcial (só Desembarque) | Fluxogramas clicáveis (Desembarque ✅, Expedição, Recebimento-Exportação, Embarque-Armazenagem) linkando cada nó ao POP |

**Insight central:** o valor do GeraPOP não é só gerar Word/PDF — é **forçar estrutura padronizada** e produzir **dados reutilizáveis** para alimentar o Fluxo SEV.

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
| Frontend | React 19 + TypeScript + Vite 6 + Vanilla CSS (design system CODEBA em `frontend/src/styles/`) |
| Geração docx | python-docx 1.1 |
| Geração PDF | reportlab 4.x (layout com logo CODEBA, banner, metadados compactos, linha divisória no rodapé) |
| Testes | pytest (`tests/` — 68 testes incluindo API TestClient) + Playwright E2E (`frontend/e2e/` — 9 testes usando Chrome do sistema via `channel: 'chrome'`) |
| Lint/format | ruff (Python) + eslint (frontend) |
| Ambiente | uv + Makefile |
| Deploy v2 (futuro) | FastAPI + frontend estático em Docker + volume (persistente) — ver `docs/deploy.md` (deploy local por enquanto) |
| CI | GitHub Actions (`.github/workflows/ci.yml`) — **desativado** (`disabled_manually`, workflow id `330472653`); reativar com `gh workflow enable 330472653 --repo brunoadsba/GeraPOP` |
| Container | Docker + docker-compose (alternativa ao venv) |

**Persistência (v1.1):** POPs gerados são salvos automaticamente em `data/pops/<id>/` (`pop.json` + `pop.docx`) e listados no app (seção Histórico). Backup = botão "Backup (.zip)" no app ou `python -m gerapop.backup` (gera `data/backups/gerapop_YYYYMMDD_HHMMSS.zip`). `data/` é ignorado pelo git (apenas na raiz). **Exclusão:** `storage.delete_pop(pop_id)` remove a pasta do POP (validação anti-traversal: o id resolvido precisa estar dentro de `data/pops/`, senão `ValueError`); na UI nova, botão "Excluir" disponível **no histórico (formulário) e nos cards de "POPs salvos no app" (home)**, com confirmação em 2 cliques via modal no React.

**Rascunho persistente (v1.1):** o formulário salva rascunho a cada alteração — via hook `useDraft` (debounce 2 s → `PUT /api/draft`, `GET /api/draft` no mount, `DELETE /api/draft` após gerar e ao resetar/excluir). No `FormPage`, escuta o evento `gerapop:draft:loaded` e faz `LOAD_POP` (merge com `emptyPop`); não sobrescreve navegação explícita (`novo_pop`/`carregar`/`editar_id`) e aplica o draft uma única vez por montagem (ref `aplicadoDraft`).

**Unicidade de código (v1.1):** a geração é bloqueada se o código já existe no histórico, com exceção para a edição do POP carregado (permissão `{loaded_from_id}`). Ver `gerapop/codigo.py` (`encontrar_codigo_duplicado`, módulo puro) e `POST /api/pops/check-code`; no frontend, debounce de 400 ms no campo código + 409 do servidor como fallback. No Histórico, POPs com códigos repetidos exibem sufixo ` ⚠ (N)` (`historico_label` em `gerapop/codigo.py`).

**Dados JSON (v1.1):** todo POP salvo gera `pop.json` em `data/pops/<id>/` (formato `{"metadata": ..., "pop": ...}`) — consumido pelo Projeto 1 (Fluxo SEV) e incluído no backup zip.

**Fidelidade ao modelo & Layout de Alta Densidade (v1.1 / branch `ajustes-finos`):**
- **Cabeçalho Oficial CODEBA:** Logo oficial inserida no canto superior esquerdo no PDF (`gerapop/services/pdf/builder.py`) e no frontend (`frontend/public/logo-codeba-topo.png`), alinhada ao título "PROCEDIMENTO OPERACIONAL PADRÃO" e ao nome do POP.
- **Metadados e Revisões no Topo:** Dispostos de forma compacta (Código, Versão, Data, Área Responsável) em tabela no PDF e em 2 colunas equilibradas no formulário e preview da UI.
- **Numeração e Tabelas:** Numeração plana automática das seções (1..N, até 9), aviso ⚠ dentro do Escopo, regras em tabela `R | texto`, consulta em caixa, colunas numéricas de passos (`#`) e regras centralizadas.
- **Rodapé:** Linha divisória fina (`#CBD5E1`) acima do rodapé com código/nome à esquerda e Versão/Página à direita.
- **Larguras de tabela no Word:** todas as tabelas do `.docx` somam a largura útil da página (margem a margem), medindo pela primeira linha sem `gridSpan`.

**Padrão CODEBA na saída (a partir de `teste/POP-COM-001_*` e `teste/POP-OPE-001_*`):**
- **Matriz de Responsabilidades em 2 variantes:** POPs de operação usam `tela/nome_tela/etapa/responsavel` (ex.: Tela 6002/6007); POPs de fluxo de negócios usam `etapa/registro/atividade/responsavel` (matriz fluxo). Detectado em `montar_conteudo` por presença de chave — sem tipo novo de POP.
- **Passos com responsável por linha:** se `Secao.responsaveis` (lista, uma por passo) → tabela `# / Responsável / Passo` sem banner; se `Secao.responsavel` (texto único) → banner de responsável acima da tabela `# / Passo`. Responsável individual por passo sobrepõe o banner.
- **Seções numeradas 7/8/9 (opcionais):** `7. Registros obrigatórios` (tabela Registro/Conteúdo mínimo/Responsável), `8. Critérios de encerramento`, `9. Indicadores de acompanhamento`.
- **Aviso final:** `PopData.aviso_final` renderizado como Aviso; se não iniciar com `■`/`⚠`, recebe o prefixo `■ ATENÇÃO:`.
- **Header/paginação DOCX:** `different_first_page_header_footer` — cabeçalho só na página 2+ com "COD · Nome · Versão · Página X de Y" (fldSimple `PAGE` + `NUMPAGES`); rodapé com tab + "Página X de Y" + aviso "Documento impresso é uma CÓPIA NÃO CONTROLADA…".
- **Header/paginação PDF:** `_NumberedCanvas` (total de páginas conhecido no `save()`) — cabeçalho na página 2+ "COD · Nome · Versão · Página X de Y", rodapé "COD – Nome · Versão   Página X de Y" + aviso de cópia não controlada.
- **Fontes PDF:** Calibri do Windows (`calibri.ttf`, `calibrib.ttf`, `calibrii.ttf`, `calibriz.ttf` registrados no reportlab) com fallback Helvetica (inclusive para o `■`).
- **`titulo_para_header`:** Title Case (conectores minúsculos: a/as/à/às/com/da/de/do/dos/e/em/na/no/nos/para/por) para cabeçalho/rodapé.
- **Célula de número generalizada:** primeira coluna numérica de qualquer tabela com ≥2 colunas (passos, regras, matriz, registros) fica centralizada/negrito.

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
│   │   ├── main.tsx / App.tsx      # Router (/, /fluxo, /pops, /formulario, /preview/:type/:ref)
│   │   ├── api/client.ts           # Fetch wrappers tipados (listPops, generatePop, download...)
│   │   ├── hooks/                  # useTheme, usePopForm (useReducer), useDraft (auto-save)
│   │   ├── components/             # Layout (Sidebar), Dashboard (Hero/Kpi/Stepper/Card),
│   │   │                           #   Form (seções do POP + DynamicList), Simulation, History, ui/
│   │   ├── pages/                  # HomePage, FluxoPage, PopsPage, FormPage, PreviewPage
│   │   ├── types/pop.ts            # Interfaces TS espelhando PopData
│   │   └── styles/                 # variables.css (tokens CODEBA light/dark) + global/dashboard/form/preview
│   └── public/                     # logos (logo-codeba-topo.png, codeba-light/dark) + favicon
├── gerapop/                        # Lógica de domínio — sem dependência de framework web
│   ├── __init__.py                 # Exporta PopData, gerar_docx, gerar_pdf
│   ├── constants.py                # ValidationMessage, estilos docx/pdf, cores, dimensões
│   ├── codigo.py                   # Unicidade de código + rótulo histórico (módulos puros)
│   ├── fluxo.py                    # carregar fluxo SEV + POP de referência (módulos puros)
│   ├── models.py                   # PopData, TypedDicts, validação, factories
│   ├── storage.py                  # Persistência em disco (pop.json + pop.docx) + backup zip
│   ├── backup.py                   # CLI de backup zip (python -m gerapop.backup)
│   ├── assets/                     # Logos CODEBA (light/dark/topo)
│   └── services/
│       ├── documento.py            # Modelo neutro de blocos (Titulo/Paragrafo/Aviso/Tabela)
│       ├── docx/
│       │   ├── styles.py           # Formatação de células Word
│       │   └── builder.py          # Renderiza os blocos neutros em .docx
│       └── pdf/
│           └── builder.py          # Renderiza os blocos neutros em PDF (reportlab com banner/logo)
├── tests/
│   ├── conftest.py                 # Fixtures (data dir tmp, pop_minimo/pop_invalido)
│   ├── test_api_pops.py            # Integração da API FastAPI (14 testes)
│   ├── test_docx_builder.py        # Testes de geração e estrutura Word
│   ├── test_validacao_codigo.py    # Unit unicidade + label de histórico (via gerapop.codigo)
│   ├── test_fluxo_sev.py           # Valida dados estáticos do fluxo-sev
│   ├── test_models.py              # Validação de schema e integridade PopData
│   └── test_storage.py             # Testes de persistência atômica e listagem
├── obsoleto/
│   ├── ideia-files/                # Protótipo original (versionado)
│   ├── gerapop-streamlit/          # UI Streamlit arquivada (ui/, session_draft.py, session_codigo.py)
│   ├── tests-streamlit/            # E2E AppTest arquivados
│   └── ambiente-fronend.md, telas-recriadas.html
├── docs/
│   ├── plano.md                    # Roadmap completo
│   ├── piloto.md                   # Roteiro do piloto com a equipe (GATE aguarda usuário)
│   └── deploy.md                   # Opções de hospedagem (Cloud efêmero vs Docker)
├── Makefile
├── pyproject.toml
├── requirements.txt
├── Dockerfile
├── scripts/
│   └── seed_pops.py               # Alimenta a biblioteca com POP-COM-001/OPE-001 (padrão CODEBA; idempotente)
└── docker-compose.yml
```

---

## 5. Modelo de dados do POP

Estrutura baseada em `POP_Manobras_CODEBA_v2.docx` + padrão CODEBA (`teste/POP-COM-001_*` e `teste/POP-OPE-001_*`):

1. **Identificação** — Nome, Código*, Versão, Data, Área*, Aviso (opcional)
2. **Histórico de Revisões** — revisão, data, descrição, responsável (apresentado no topo e numerado)
3. **Objetivo*** 
4. **Escopo e Pré-condições**
5. **Definições** — lista dinâmica (termo + definição)
6. **Matriz de Responsabilidades** — 2 variantes (Tela: `tela/nome_tela/etapa/responsavel`; Fluxo: `etapa/registro/atividade/responsavel`)
7. **Procedimento** — seções dinâmicas (`Secao`), cada uma com passos numerados, **campos obrigatórios** e responsável (banner `responsavel` ou por linha `responsaveis`)
8. **Regras e Restrições** — lista dinâmica
9. **Consulta e Relatórios** (opcional)
10. **Registros obrigatórios** (opcional) — tabela Registro/Conteúdo mínimo/Responsável
11. **Critérios de encerramento** (opcional)
12. **Indicadores de acompanhamento** (opcional)
13. **Aviso final** (opcional) — prefixo `■ ATENÇÃO:` quando não inicia com `■`/`⚠`

Campos obrigatórios na validação: **nome, código, área, objetivo**. Código deve ser **único** no histórico (bloqueio com exceção para edição do POP carregado).

Classe principal: `PopData` em `gerapop/models.py`: `ItemMatriz` (`registro`/`atividade` + `tela`/`nome_tela`), `Secao` (`responsaveis` paralelo a `passos`), `RegistroObrigatorio`; `PopData.registros_obrigatorios/criterios_encerramento/indicadores/aviso_final`; `from_form` repassa os novos campos.  
Contrato frontend ↔ backend: schemas Pydantic em `backend/schemas.py` ↔ interfaces TS em `frontend/src/types/pop.ts` (novos campos espelhados, mas a UI só edita os campos tradicionais — dados novos entram via API/seed).

---

## 6. Como rodar, testar e validar

```bash
# Setup (primeira vez)
make install-dev
cd frontend && npm install --registry https://registry.yarnpkg.com
```

> **make no Windows:** instalar com `winget install -e --id ezwinports.make` (GNU make 4.4.1). O
> `Makefile` detecta `OS=Windows_NT` e usa `.venv/Scripts/` (python.exe, pytest.exe, ruff.exe);
> `make run` inicia o backend via `Start-Process` (detached) e `make clean` usa PowerShell.
> Em shell novo o PATH já inclui o aliased `make`.

# Desenvolvimento
make run          # backend (http://localhost:8000) + frontend (http://localhost:5173)
make run-backend  # só a API
make run-frontend # só o frontend

# Qualidade
uv run pytest     # 68 pytest (storage + docx + pdf + models + unicidade + fluxo-sev + 14 de API)
make lint         # ruff check + format --check (Python) e eslint (frontend)
make format       # auto-format Python
cd frontend && npm run typecheck  # validação tsc sem erros
cd frontend && npm run build      # validação de build Vite
cd frontend && npm run test:e2e   # 9 testes E2E Playwright (Chrome do sistema em portas 5199/8199)

# Biblioteca de POPs (alimentar data/pops/ com o padrão CODEBA)
.venv/Scripts/python.exe scripts/seed_pops.py   # idempotente (atualiza registro existente pelo codigo)

# Backup
make backup       # zip com todos os POPs + rascunho

# Docker (alternativa)
make docker-run
```

---

## 7. Convenções de desenvolvimento

1. **KISS / YAGNI** — não adicionar nuvem, auth, framework antes de validação real (piloto).
2. **Arquivos < 200 linhas** — quebrar se ultrapassar.
3. **Clean code** — uma responsabilidade por módulo; sem lógica de documento na UI ou API.
4. **Testes** — toda lógica de domínio/serviço deve ter teste pytest; suite verde antes de commit/push.
5. **Commits semânticos** — formato: `tipo(escopo): descrição` (ex: `feat(pdf): layout de alta densidade`).
6. **Português BR** — comunicação e mensagens de validação em português.
7. **Não commitar** `.venv/`, `*.docx`, secrets, `/data/` (raiz), `.omo/`, `.e2e-data/`.
8. **Atualizar este `memory.md`** sempre que o estado do projeto mudar de direção.
9. **Arquivos obsoletos vão para `obsoleto/`** (versionado, arquivamento) — não apagar.

---

## 8. Estado atual do repositório (2026-08-19)

### Commits já integrados no Git
- `feat(gerapop): estrutura inicial do MVP com Streamlit e geração de POP`
- `refactor(gerapop): reorganiza projeto em camadas e adiciona memory.md`
- `feat(ui): campos obrigatórios por seção (G6)`
- `feat(ui): rascunho persistente entre sessões`
- `feat(backup): zip com todos os POPs`
- `docs(deploy): opções de hospedagem`
- `docs(piloto): roteiro do piloto com a equipe`
- `feat(fluxo-sev): diagrama interativo v1 (Desembarque)`
- `feat(ui): unicidade de código + marcação ⚠ no histórico`
- `refactor(tests): helpers E2E no conftest`
- `feat(pdf): gerar PDF do POP com reportlab`
- `feat(ui): dashboard, preview, simulacao e design system`
- `refactor(arch): migração completa para React 19 + TypeScript + Vite 6 + FastAPI`
- `fix(storage/preview): atualiza POP em disco na edição e adiciona botão Visualizar Prévia no formulário`
- `fix(kpi/storage): alinha rótulo do KPI de etapas com POP e garante criação de diretório em escrita atômica`
- `feat(preview): adiciona botão Editar POP na visualização e elimina oscilação de dados`
- `fix(e2e): isola portas e dados dos testes E2E para proteger dados reais em data/`
- `feat(ui): redistribui navegação no Sidebar com visões dedicadas para Fluxo SEV e Biblioteca de POPs`
- `fix(types): declara tipos de node no vite-env e inclui configs no tsconfig` (`4917afe`)
- `feat(pop): evolui modelo e documento com metadados CODEBA` (`0c7958a`)

### Em andamento na branch `ajustes-finos` (Trabalho Atual)
- **Header Oficial CODEBA e Layout de Alta Densidade:**
  - Inclusão da logo oficial CODEBA (`frontend/public/logo-codeba-topo.png` e `gerapop/assets/` / reportlab Image) no topo do PDF e da UI web.
  - Cabeçalho do PDF com banner contendo a logo da CODEBA à esquerda e título "PROCEDIMENTO OPERACIONAL PADRÃO" + Nome do POP centralizados/destacados.
  - Tabela compacta de Metadados (Código, Versão, Data, Área Responsável) no topo do PDF.
  - Seção "Histórico de Revisões" no topo do formulário/preview e como seção numerada no documento gerado com fallback `default_revisao()`.
  - Alinhamento centralizado para colunas numéricas de passos (`#`) e regras (`R`), além de linha separadora fina (`#CBD5E1`) no rodapé do PDF.
- **Frontend & CSS:**
  - Redesenho de `IdentificacaoSection.tsx`, `FormPage.tsx` e `PreviewPage.tsx` com visual de duas colunas no topo, bordas elegantes e badges modernos.
- **Padrão CODEBA / Biblioteca (2026-08-20):**
  - Modelo estendido (`gerapop/models.py` + `backend/schemas.py` + `backend/dependencies.py`): matriz fluxo (`registro`/`atividade`), `Secao.responsaveis` por linha, `RegistroObrigatorio`, `criterios_encerramento`, `indicadores`, `aviso_final` — retrocompatível via `from_form`/`pop_from_request`.
  - `montar_conteudo` (`gerapop/services/documento.py`): matriz em 2 variantes, passos com responsável → tabela `# / Responsável / Passo` (sem banner), seções 7/8/9, aviso final `■`, `titulo_para_header` (Title Case com conectores minúsculos incluindo à/às).
  - Builders DOCX/PDF: header "Página X de Y" (fldSimple PAGE+NUMPAGES no DOCX) a partir da página 2 (`different_first_page_header_footer` DOCX / `_NumberedCanvas` PDF), rodapé "cópia não controlada", células de número generalizadas, fontes Calibri (fallback Helvetica).
  - Biblioteca alimentada: `data/pops/20260820_122120_073271_7e4c3f` (POP-COM-001 Prospecção e Fechamento Comercial de Novas Cargas v01) e `data/pops/20260819_084549_789221_8f80b6` (POP-OPE-001 Programação de Saída v02, telas 6002/6007). Referência: `teste/POP-COM-001_*.{docx,pdf}` e `teste/POP-OPE-001_*.{docx,pdf}`.
  - `scripts/seed_pops.py` idempotente (resolve id por `codigo`; `save_pop` + `gerar_docx`).
  - `pdfplumber` adicionado como dev dependency (`uv add --dev pdfplumber`).
- **Qualidade & Validação:**
  - 68 testes pytest verdes (`uv run pytest`).
  - 9 testes E2E Playwright verdes (`npm run test:e2e`).
  - `tsc`, `eslint` e `npm run build` 100% limpos.

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
- [x] Export PDF (reportlab) com logo CODEBA, banner e metadados de alta densidade
- [x] Dashboard home (KPIs, stepper, cards do fluxo SEV)
- [x] Preview do POP em modo leitura (com .docx/.pdf baixáveis e botão Editar POP)
- [x] Simulação RPA de preenchimento
- [x] Design system: paleta light/dark, componentes custom e navegação estruturada no Sidebar
- [x] Migração de UI: React 19 + TypeScript + Vite 6 + FastAPI
- [x] Suite de testes automatizados: 68 pytest + 9 E2E Playwright isolados

### Gate de negócio (aguarda usuário/equipe)
- [ ] **Piloto com a equipe** — `docs/piloto.md` (roteiro pronto, GATE explícito)

### Médio prazo (GeraPOP v2)
- [ ] Validar o app novo (React) ponta-a-ponta com a equipe no piloto
- [ ] Hospedagem da nova stack (FastAPI + frontend estático em Docker) — `docs/deploy.md`
- [ ] Reativar CI (`gh workflow enable 330472653`)
- [ ] Mapear 3 fluxos restantes no Projeto 1 (Fluxo SEV): **Expedição, Recebimento-Exportação, Embarque-Armazenagem**

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
| Testes flaky de storage | `save_pop`/`serialize_pop` usam timestamps monotônicos (`_proximo_timestamp()`) |
| Perda de POPs de teste | Guardar PDFs de referência em `teste/` para reconstrução se necessário |

---

## 11. Referências rápidas

| Recurso | Caminho |
|---------|---------|
| Roadmap completo | `docs/plano.md` |
| Roteiro do piloto | `docs/piloto.md` (GATE aguarda usuário) |
| Opções de hospedagem | `docs/deploy.md` |
| Instruções de uso | `README.md` |
| Guia do usuário final | `guia-usuario.md` |
| Modelo POP | `POP_Manobras_CODEBA_v2.docx` (referência externa) |
| Referência do padrão CODEBA | `teste/POP-COM-001_*.{docx,pdf}` e `teste/POP-OPE-001_*.{docx,pdf}` (modelos do usuário) |
| Seed da biblioteca | `scripts/seed_pops.py` (alimenta `data/pops/` — idempotente) |
| Logo oficial CODEBA | `frontend/public/logo-codeba-topo.png` e `Logo CODEBA.png` |
| Módulo Fluxo SEV | `fluxo-sev/README.md` + `fluxo-sev/memory/000-fluxo-sev-v1.md` |
| Config backend/frontend | CORS em `backend/main.py`; proxy `/api` em `frontend/vite.config.ts` |
| CI | `.github/workflows/ci.yml` (desativado) |

---

## 12. Prompt de continuidade (copiar para nova sessão)

```
Contexto: Projeto GeraPOP (CODEBA) — gerador de POP com backend FastAPI + frontend
React 19/TS/Vite 6 + python-docx + reportlab (PDF com logo CODEBA e alta densidade).
Leia memory.md e docs/plano.md antes de codar.

Stack: Python 3.11, FastAPI (backend/), React+TS+Vite (frontend/), python-docx,
reportlab, pytest, ruff, eslint.
Arquitetura: gerapop/models (domínio), services/docx + services/pdf (geração),
backend/ (API REST), frontend/ (dashboard, formulário, preview, histórico,
simulação, tema light/dark), fluxo-sev/ (Projeto 1, HTML/CSS/JS puro).

Estado: Branch `ajustes-finos` com saída alinhada ao padrão CODEBA (matriz de
responsabilidades 2 variantes, passos com responsável por linha, seções 7/8/9,
header "Página X de Y" a partir da página 2, rodapé cópia não controlada, fontes
Calibri); biblioteca alimentada com POP-COM-001 e POP-OPE-001 via
scripts/seed_pops.py; 68 pytest + 9 E2E Playwright 100% verdes; tsc/eslint/vite
build limpos.

Próximo passo sugerido: commitar a branch `ajustes-finos`, validar o piloto com a equipe
(docs/piloto.md) e mapear os 3 fluxos SEV restantes.

NÃO implementar: nuvem, auth, multi-agente, frameworks adicionais sem validação do piloto.
```

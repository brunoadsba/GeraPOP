# GeraPOP — Memória de Contexto para LLMs

> Documento de continuidade do projeto. Leia antes de implementar qualquer feature.
> Última atualização: 2026-08-27 (branch `ajustes-finos` `16372d3`: paleta premium leve light editorial (#F8F9FC, slate 900), hero editorial claro com badge e CTAs, sidebar retrátil 250→72px com persistência + drawer mobile 280px e marca C removida (recolhido limpo), empty states premium ilustrados e skeletons com stagger, bug "Novo POP" corrigido (RESET+discard via state novo_pop); biblioteca oficial com 3 POPs — `POP-COM-001`, `POP-OPE-001`, `POP-OPE-002_ANÚNCIO DE NAVIO`; `data/pops/` com 3; 71 pytest + 8 E2E + build Vite 36kB)

---

## 1. O que é este projeto

**GeraPOP** é um gerador de **POP** (Procedimento Operacional Padrão) para a **CODEBA** (Companhia de Navegação do Estado da Bahia — contexto portuário).

O usuário preenche um formulário guiado e recebe arquivos `.docx` e `.pdf` formatados, seguindo o padrão oficial da CODEBA com logo e metadados no topo.

**Repositório:** https://github.com/brunoadsba/GeraPOP.git  
**Branch principal:** `main` (`13681a6`) + `ajustes-finos` (`16372d3`, branch de trabalho atual — 4 commits à frente: redesign premium, paleta light editorial e sidebar retrátil)  
**Status atual:** MVP v1 completo + export **PDF** + **dashboard home enxuto** (KPIs reais, hero editorial claro com badge/CTA, recentes) + **preview** + **design system premium leve** (light #F8F9FC/slate 900, dark #0A0E1C, hero claro com borda, sidebar retrátil 250→72px persistida + drawer mobile 280px com overlay, empty states premium ilustrados e skeletons stagger, foco com glow, `prefers-reduced-motion`) + **bug "Novo POP" corrigido** (navegação com `state novo_pop` + `RESET`/`discard()` — abre vazio, sem rascunho `PROSPECÇÃO...`) + **padrão CODEBA** (matriz 2 variantes, passos com responsável por linha, seções 7/8/9, header "Página X de Y" p2+, rodapé cópia não controlada, Calibri) + **biblioteca interna** (`data/pops/` 3: `POP-COM-001`, `POP-OPE-001`, `POP-OPE-002`) + **biblioteca oficial** (`POP - Procedimento Operacional Padrão/` 3 pastas) + **React 19 + TS + Vite 6**; **71 pytest + 8 E2E + build 36kB** limpos.

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
| Testes | pytest (`tests/` — 68 testes incluindo API TestClient) + Playwright E2E (`frontend/e2e/` — 8 testes usando Chrome do sistema via `channel: 'chrome'`) |
| Lint/format | ruff (Python) + eslint (frontend) |
| Ambiente | uv + Makefile |
| Deploy v2 (futuro) | FastAPI + frontend estático em Docker + volume (persistente) — ver `docs/deploy.md` (deploy local por enquanto) |
| CI | GitHub Actions (`.github/workflows/ci.yml`) — **desativado** (`disabled_manually`, workflow id `330472653`); reativar com `gh workflow enable 330472653 --repo brunoadsba/GeraPOP` |
| Container | Docker + docker-compose (alternativa ao venv) |

**Persistência (v1.1 + biblioteca oficial 2026-08-27):** duas camadas, com papéis distintos:

| Camada | Caminho | Conteúdo | Quem usa |
|--------|---------|----------|----------|
| Histórico do app | `data/pops/<id>/` | `pop.json` + `pop.docx` | API, UI, unicidade de código, backup zip |
| Biblioteca oficial | `POP - Procedimento Operacional Padrão/<CÓDIGO_NOME>/` | `<CÓDIGO_NOME>.docx` + `.pdf` | Arquivo humano / pasta de trabalho CODEBA |

- **Gerar/salvar** (`POST /api/generate` e `scripts/seed_pops.py`) chama `save_pop(..., pdf=...)`, que grava o histórico e chama `exportar_para_biblioteca`. Preview/download (`/preview/docx`, `/preview/pdf`) **não** grava na biblioteca.
- **Nome da pasta:** `{codigo}_{NOME EM MAIÚSCULAS}` (espaços preservados; caracteres inválidos de path removidos). Ex.: `POP-OPE-001_PROGRAMAÇÃO DE SAÍDA`.
- **Mesmo código:** reaproveita a pasta existente; se o nome mudou, a pasta é renomeada e os arquivos sobrescritos.
- **Excluir no app:** `delete_pop` remove `data/pops/<id>/` **e** a pasta da biblioteca daquele código (`remover_da_biblioteca`).
- **Overrides:** `GERAPOP_DATA_DIR` (padrão `data/`); `GERAPOP_LIBRARY_DIR` (padrão: raiz do repo + `POP - Procedimento Operacional Padrão`). Testes isolam as duas via `conftest.py`.
- **Git:** `/data/` ignorado; `*.docx` ignorado; `*:Zone.Identifier` ignorado (ADS do Windows ao copiar arquivos). PDFs da biblioteca oficial podem ser versionados.
- Pastas na biblioteca oficial (2026-08-27): `POP-COM-001_PROSPECÇÃO E FECHAMENTO COMERCIAL DE NOVAS CARGAS`, `POP-OPE-001_PROGRAMAÇÃO DE SAÍDA` e `POP-OPE-002_ANÚNCIO DE NAVIO` (3 pastas, cada com .docx editável + .pdf oficial; .docx ignorado, .pdf versionado). Só são sobrescritas se o app gerar de novo o mesmo código.
- Backup zip continua só sobre `data/` (`python -m gerapop.backup` / `GET /api/backup`). **Exclusão na UI:** histórico e cards da home, confirmação em 2 cliques via modal no React; anti-traversal em `delete_pop`.

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
│       ├── generate.py             # POST /api/generate (salva histórico + biblioteca) + preview sem salvar
│       ├── drafts.py               # Rascunho persistente (GET/PUT/DELETE /api/draft)
│       └── backup.py               # GET /api/backup (zip)
├── frontend/                       # React 19 + TypeScript + Vite 6
│   ├── vite.config.ts              # Proxy /api → http://localhost:8000
│   ├── src/
│   │   ├── main.tsx / App.tsx      # Router (/, /pops, /formulario, /preview/:type/:ref)
│   │   ├── api/client.ts           # Fetch wrappers tipados (listPops, generatePop, download...)
│   │   ├── hooks/                  # useTheme, usePopForm (useReducer), useDraft (auto-save)
│   │   ├── components/             # Layout (Sidebar), Dashboard (KpiGrid/CardGrid),
│   │   │                           #   Form (seções do POP + DynamicList), History, ui/
│   │   ├── pages/                  # HomePage, PopsPage, FormPage, PreviewPage
│   │   ├── types/pop.ts            # Interfaces TS espelhando PopData
│   │   └── styles/                 # variables.css (tokens CODEBA light/dark) + global/dashboard/form/preview
│   └── public/                     # logos (logo-codeba-topo.png, codeba-light/dark) + favicon
├── gerapop/                        # Lógica de domínio — sem dependência de framework web
│   ├── __init__.py                 # Exporta PopData, gerar_docx, gerar_pdf
│   ├── constants.py                # ValidationMessage, estilos docx/pdf, cores, dimensões
│   ├── codigo.py                   # Unicidade de código + rótulo histórico (módulos puros)
│   ├── fluxo.py                    # carregar fluxo SEV + POP de referência (módulos puros)
│   ├── models.py                   # PopData, TypedDicts, validação, factories
│   ├── storage.py                  # data/pops (json+docx) + export oficial (docx+pdf) + backup zip
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
│   ├── conftest.py                 # Fixtures (GERAPOP_DATA_DIR + GERAPOP_LIBRARY_DIR tmp, pop_minimo)
│   ├── test_api_pops.py            # Integração da API FastAPI (14 testes)
│   ├── test_docx_builder.py        # Testes de geração e estrutura Word
│   ├── test_validacao_codigo.py    # Unit unicidade + label de histórico (via gerapop.codigo)
│   ├── test_fluxo_sev.py           # Valida dados estáticos do fluxo-sev
│   ├── test_models.py              # Validação de schema e integridade PopData
│   └── test_storage.py             # Persistência, listagem, export/exclusão da biblioteca oficial
├── POP - Procedimento Operacional Padrão/  # Biblioteca humana: uma pasta por POP (docx + pdf)
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
> O instalador já adiciona o diretório `bin` do pacote ao **User PATH** (não é preciso mexer);
> apenas abra um **terminal novo** para o `make` resolver.
>
> **Servidores persistentes fora da sessão de tooling:** processos iniciados dentro de uma
> chamada de ferramenta (ex.: `Start-Process`) morrem com o fim dela (job object). Para manter
> backend + frontend vivos, iniciar a árvore via WMI:
> `Invoke-CimMethod -ClassName Win32_Process -MethodName Create -Arguments @{ CommandLine = 'cmd.exe /c "C:\Users\BRUNO~1.SAN\AppData\Local\Temp\opencode\start_gerapop.cmd"' }`
> (o `.cmd` roda `make run` e loga em `%TEMP%\opencode\gerapop_servers.log`).

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
cd frontend && npm run test:e2e   # 8 testes E2E Playwright (Chrome do sistema em portas 5199/8199)

# Biblioteca de POPs (data/pops/ + pasta oficial na raiz)
.venv/bin/python scripts/seed_pops.py   # WSL; no Windows: .venv/Scripts/python.exe
# idempotente (atualiza pelo codigo; também exporta .docx/.pdf para a pasta oficial)

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
7. **Não commitar** `.venv/`, `*.docx`, secrets, `/data/` (raiz), `.omo/`, `.e2e-data/`, `*:Zone.Identifier`.
8. **Atualizar este `memory.md`** sempre que o estado do projeto mudar de direção.
9. **Arquivos obsoletos vão para `obsoleto/`** (versionado, arquivamento) — não apagar.

---

## 8. Estado atual do repositório (2026-08-27)

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
- `feat(pop): aplica padrão CODEBA na saída e alimenta biblioteca com seed idempotente` (`859ef60`)
- `build(make): compatibiliza Makefile com Windows` (`fc26538`)
- `docs(memory): registra make no Windows e servidores persistentes via WMI` (`2b5b1bf`) — HEAD de `origin/main`

### Trabalho local em `main` (2026-08-27, ainda não commitado)

- **Biblioteca oficial em pasta humana:** geração grava `.docx` e `.pdf` em `POP - Procedimento Operacional Padrão/<CÓDIGO_NOME>/` (`exportar_para_biblioteca` em `gerapop/storage.py`; `POST /api/generate` passa `pdf=gerar_pdf(...)`; seed idempotente também). Preview não exporta.
- Regenerar o mesmo código sobrescreve; mudança de nome renomeia a pasta; `delete_pop` limpa histórico e pasta oficial.
- Testes em `tests/test_storage.py` (export, rename, delete) isolados com `GERAPOP_LIBRARY_DIR`.
- Biblioteca oficial com 3 POPs (2026-08-27): `POP-COM-001`, `POP-OPE-001`, `POP-OPE-002_ANÚNCIO DE NAVIO` (seed + restauração do OPE-002 em `data/pops/` para o frontend).

### Já integrado (antes `ajustes-finos`, agora em `main`)
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
  - `scripts/seed_pops.py` idempotente (resolve id por `codigo`; `save_pop` + `gerar_docx` + `gerar_pdf` → pasta oficial).
  - `pdfplumber` adicionado como dev dependency (`uv add --dev pdfplumber`).
- **Qualidade & Validação:**
  - 68 testes pytest verdes (`uv run pytest`).
  - 8 testes E2E Playwright verdes (`npm run test:e2e`).
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
- [x] Design system: paleta light/dark, componentes custom e navegação estruturada no Sidebar
- [x] Migração de UI: React 19 + TypeScript + Vite 6 + FastAPI
- [x] Suite de testes automatizados: 71 pytest + 8 E2E Playwright isolados
- [x] Cópia oficial de cada POP gerado em `POP - Procedimento Operacional Padrão/<CÓDIGO_NOME>/` (docx + pdf)

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
| Excluir no app apaga a pasta oficial | `delete_pop` remove `POP - Procedimento Operacional Padrão/<CÓDIGO_*>`; confirmar antes de excluir POPs já publicados |

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
| Seed da biblioteca | `scripts/seed_pops.py` (alimenta `data/pops/` **e** a pasta oficial — idempotente) |
| Biblioteca oficial (humana) | `POP - Procedimento Operacional Padrão/<CÓDIGO_NOME>/` (`.docx` + `.pdf`) |
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

Stack: Python 3.11, FastAPI (backend/), React+TS+Vite (frontend/ premium leve), python-docx,
reportlab, pytest, ruff, eslint.
Arquitetura: gerapop/models (domínio), services/docx + services/pdf (geração),
backend/ (API REST), frontend/ (dashboard enxuto com hero editorial claro, sidebar retrátil 250→72px + drawer mobile, empty premium + skeletons, sem /fluxo/sem simulação), fluxo-sev/ (Projeto 1 externo).

Estado: `ajustes-finos` `16372d3` (4 à frente de `main` `13681a6`): paleta light #F8F9FC/slate 900, hero claro, sidebar recolhível com persistência e sem marca C, empty/skeleton premium, bug Novo POP corrigido (RESET+discard). Saída CODEBA (matriz 2 variantes, passos com responsável por linha, seções 7/8/9, header "Página X de Y" p2+, Calibri). Histórico `data/pops/` 3 + biblioteca humana 3 (docx editável + pdf oficial); 71 pytest + 8 E2E + build 36kB limpos.

Próximo passo sugerido: piloto com equipe (docs/piloto.md) ou merge `ajustes-finos` → `main` se aprovado; 3 fluxos SEV restantes.

NÃO implementar: nuvem, auth, multi-agente, frameworks adicionais sem validação do piloto.
```

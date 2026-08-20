# GeraPOP — CODEBA

Gerador de POP (Procedimento Operacional Padrão) com formulário guiado e exportação `.docx`/`.pdf` formatadas — **backend FastAPI + frontend React (TypeScript/Vite)**.

## Pré-requisitos

- Python 3.11 (recomendado — Python 3.12 no WSL pode falhar com `ctypes`)
- [uv](https://docs.astral.sh/uv/) ou Make
- Node.js 20+ e npm (para o frontend)

## Início rápido

```bash
make install-dev
cd frontend && npm install
make run
```

- Frontend: http://localhost:5173
- API: http://localhost:8000 (docs em `/docs`)

> **Nota (rede corporativa):** se `registry.npmjs.org` estiver bloqueado, use `npm install --registry https://registry.yarnpkg.com`.

## Alternativa via Docker

```bash
make docker-run
```

## Comandos

| Comando | Descrição |
|---------|-----------|
| `make install` | Cria `.venv` e instala dependências |
| `make install-dev` | Instala dependências + pytest e ruff |
| `make run-backend` | Sobe a API FastAPI (http://localhost:8000) |
| `make run-frontend` | Sobe o frontend React (http://localhost:5173) |
| `make run` | Sobe backend + frontend em paralelo |
| `make test` | Roda testes automatizados (pytest) |
| `make lint` | Verifica estilo e imports (ruff + eslint) |
| `make format` | Formata o código (ruff) |
| `make docker-run` | Sobe via Docker Compose |

## Testes E2E (Playwright)

Testes de ponta a ponta no `frontend/e2e/` cobrem dashboard, formulário → geração → download `.docx`/`.pdf`, validação, código duplicado, histórico/backup `.zip`, exclusão com confirmação, simulação RPA e tema claro/escuro.

```bash
cd frontend
npm install --registry https://registry.yarnpkg.com   # se o npmjs estiver bloqueado
npx playwright install chromium                        # (o Channel Chrome do sistema também funciona)
npm run test:e2e          # headless (sobe backend 8000 + frontend 5173 automaticamente)
npm run test:e2e:headed   # com navegador visível
```

> Usos do config: usa o Chrome instalado via `channel: 'chrome'` (sem Chromium baixado), backend com data dir isolado em `.e2e-data/` (gitignored) e `fullyParallel: false` + `workers: 1` para sequência determinística.

## Estrutura

```
backend/                       # API FastAPI
├── main.py                    # App + CORS + /api/health
├── schemas.py                 # Modelos Pydantic
├── dependencies.py            # Conversões PopData ↔ schema
└── routers/                   # pops, generate, drafts, backup
frontend/                      # React 19 + TypeScript + Vite
├── src/
│   ├── pages/                 # HomePage, FormPage, PreviewPage
│   ├── components/            # Layout, Dashboard, Form, History, Simulation, ui
│   ├── hooks/                 # useTheme, usePopForm, useDraft
│   ├── api/client.ts          # Fetch wrappers tipados
│   ├── types/pop.ts           # Interfaces TS (PopData)
│   └── styles/                # Design system CODEBA (light/dark)
gerapop/                       # Lógica de domínio
├── models.py                  # Domínio e validação (matriz fluxo, responsáveis, seções 7/8/9)
├── codigo.py                  # Unicidade de código + rótulo histórico (puro)
├── fluxo.py                   # Leitura do fluxo SEV (puro)
├── storage.py                 # Histórico em disco (pop.json + pop.docx)
├── backup.py                  # CLI de backup (python -m gerapop.backup)
└── services/
    ├── documento.py           # Modelo neutro de blocos (docx/pdf) + título para header
    ├── docx/                  # Geração do .docx (header página 2+, rodapé cópia não controlada)
    └── pdf/                   # Geração do .pdf (Calibri, _NumberedCanvas, página X de Y)
scripts/
└── seed_pops.py               # Alimenta data/pops/ com o padrão CODEBA (idempotente)
obsoleto/
├── gerapop-streamlit/         # UI Streamlit antiga (arquivada)
└── tests-streamlit/           # Testes E2E AppTest (arquivados)
fluxo-sev/                     # Diagrama interativo do fluxo SEV
tests/                         # pytest (68 testes)
```

## O que a v1 faz

- UI moderna e sênior (React 19 + TypeScript + Vite 6 + Vanilla CSS) com tema light/dark, glassmorphism (`backdrop-filter`), fonte Inter via Google Fonts e animações fluídas
- Biblioteca de ícones vetoriais SVG inline (`Icons.tsx`), sistema de notificações flutuantes Toast (`Toast.tsx`) e modais com confirmação e backdrop blur
- Formulário com seções colapsáveis em sanfona (`Accordion.tsx`), selos informativos (*badges*) e barra de progresso de preenchimento em tempo real
- Dashboard do fluxo SEV com KPIs animados em estilo *count-up*, stepper com linha conectora visual e ação rápida "Novo POP" no Hero
- Preview do POP em modo leitura com numeração destacada, passos especiais (sub-cabeçalhos de tela e respostas do sistema) e tabelas zebradas
- Simulação RPA de preenchimento automático para demonstração prática
- Validação mínima (nome, código, área e objetivo) e unicidade de código (bloqueio de duplicidade com exceção para edição)
- Gera `.docx` seguindo a estrutura do modelo `POP_Manobras_CODEBA_v2` (numeração automática das seções, aviso ⚠ no escopo, regras em tabela, fontes do modelo) — validado contra o modelo real OpenPort
- Export `.pdf` (reportlab) com a mesma estrutura do `.docx`
- Dados estruturados: cada POP salvo guarda `pop.json` (`{"metadata", "pop"}`) em `data/pops/<id>/`, usado para reutilização e backup — downloads na UI são `.docx`/`.pdf`
- Histórico de POPs gerados em `data/pops/` (JSON + .docx) com re-download e "carregar para editar" (persistente via volume no Docker)
- Rascunho do formulário persistido entre sessões (`/api/draft`)
- Backup dos POPs em `.zip` (botão no histórico + `python -m gerapop.backup`)
- **Padrão CODEBA na saída DOCX/PDF:** matriz de responsabilidades em 2 variantes (Tela / Fluxo de negócios), passos com responsável por linha (`# / Responsável / Passo`) ou banner de responsável, seções numeradas 7 Registros obrigatórios / 8 Critérios de encerramento / 9 Indicadores de acompanhamento, aviso final com `■`, header "Página X de Y" a partir da página 2 e rodapé com aviso de cópia não controlada (PDF usa fonte Calibri com fallback)

## Biblioteca de POPs (padrão CODEBA)

A biblioteca (`data/pops/`) é alimentada a partir dos modelos de referência em `teste/` via seed idempotente:

```bash
.venv/Scripts/python.exe scripts/seed_pops.py
```

Contém hoje:
- **POP-COM-001** — Prospecção e Fechamento Comercial de Novas Cargas (v01, matriz fluxo, 8 etapas)
- **POP-OPE-001** — Programação de Saída (v02, telas 6002/6007, responsabilidades segregadas)

Os arquivos `teste/POP-COM-001_*.{docx,pdf}` e `teste/POP-OPE-001_*.{docx,pdf}` são os modelos de referência do padrão (não versionados).

## O que a v1 não faz (proposital)

- Multi-usuário / login / nuvem

## Sem Make

```bash
uv venv --python 3.11 .venv
uv pip install -r requirements.txt -r requirements-dev.txt
uv pip install -e .

# Backend
.venv/Scripts/python.exe -m uvicorn backend.main:app --reload --port 8000
# Frontend (outro terminal)
cd frontend && npm install && npm run dev
```

## Documentação

Ver [docs/plano.md](docs/plano.md) para visão completa do pipeline GeraPOP + Fluxo Interativo SEV.

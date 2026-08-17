# Plano de Migração: Streamlit → Frontend Moderno (React/TS + FastAPI)

> **Meta:** Substituir a camada UI do GeraPOP (Streamlit) por uma interface web moderna em **React + TypeScript + Vite** consumindo uma **API REST (FastAPI)**, mantendo 100% da lógica de domínio e geração de documentos em Python.

---

## User Review Required

> [!IMPORTANT]
> **Decisão de Timing:** Este plano pode ser executado a qualquer momento, mas o [memory.md](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/memory.md) recomenda **aguardar o piloto** com a equipe antes de migrar. Se quiser prosseguir agora, confirme.

> [!WARNING]
> **Escopo:** A migração substitui toda a pasta `gerapop/ui/` e os módulos de sessão Streamlit (`session_draft.py`, `session_codigo.py`). A lógica de domínio (`models.py`, `services/`, `storage.py`, `backup.py`, `constants.py`) permanece **intacta**.

> [!IMPORTANT]
> **Stack escolhida:** React 19 + TypeScript + Vite 6 + Vanilla CSS (design system migrado do tema CODEBA existente) no frontend; FastAPI no backend. Se preferir outra combinação (ex: Vue, Next.js, Svelte), informe antes de aprovar.

---

## Open Questions

1. **Autenticação:** Aproveitar a migração para adicionar login básico (ex: senha única por equipe) ou manter sem auth como na v1?
2. **Deploy:** A nova versão rodará local (como hoje) ou já preparamos para Docker em produção?
3. **Módulo Fluxo SEV:** Integrar o [fluxo-sev/](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/fluxo-sev/) (hoje é HTML/JS puro separado) como uma rota dentro do novo frontend, ou mantê-lo isolado?

---

## Arquitetura Proposta

```
GeraPOP/
├── backend/                      # FastAPI — expõe a lógica Python existente como API
│   ├── main.py                   # App FastAPI + CORS + rotas
│   ├── routers/
│   │   ├── pops.py               # CRUD de POPs (list, get, create, update, delete)
│   │   ├── generate.py           # Gerar .docx / .pdf / .json (download)
│   │   ├── drafts.py             # Rascunho persistente (save, load, clear)
│   │   └── backup.py             # Backup zip
│   ├── schemas.py                # Pydantic models (request/response)
│   └── dependencies.py           # Helpers (storage dir, etc.)
│
├── frontend/                     # React + TypeScript + Vite
│   ├── index.html
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── package.json
│   ├── src/
│   │   ├── main.tsx              # Entry point
│   │   ├── App.tsx               # Router + Layout
│   │   ├── api/                  # Fetch wrappers para o backend
│   │   │   └── client.ts         # Funções tipadas: listPops(), generateDocx(), etc.
│   │   ├── hooks/                # Custom hooks
│   │   │   ├── useDraft.ts       # Auto-save do rascunho (debounce)
│   │   │   ├── usePopForm.ts     # Estado do formulário (useReducer)
│   │   │   └── useTheme.ts       # Toggle light/dark
│   │   ├── components/           # Componentes reutilizáveis
│   │   │   ├── Layout/           # Sidebar, Header, Footer
│   │   │   ├── Form/             # Campos do formulário POP
│   │   │   │   ├── IdentificacaoSection.tsx
│   │   │   │   ├── ObjetivoEscopoSection.tsx
│   │   │   │   ├── DefinicoesSection.tsx
│   │   │   │   ├── ProcedimentoSection.tsx
│   │   │   │   ├── RegrasSection.tsx
│   │   │   │   ├── ConsultaSection.tsx
│   │   │   │   ├── RevisoesSection.tsx
│   │   │   │   └── DynamicList.tsx    # Componente genérico add/remove
│   │   │   ├── Dashboard/        # Hero, KPIs, Stepper, Cards
│   │   │   ├── Preview/          # Visualização do POP em modo leitura
│   │   │   ├── History/          # Histórico de POPs salvos
│   │   │   ├── Simulation/       # Simulação RPA
│   │   │   └── ui/               # Primitivos (Button, Input, Badge, Card, etc.)
│   │   ├── pages/
│   │   │   ├── HomePage.tsx      # Dashboard + cards do fluxo SEV
│   │   │   ├── FormPage.tsx      # Formulário de criação/edição
│   │   │   └── PreviewPage.tsx   # Preview de um POP
│   │   ├── types/
│   │   │   └── pop.ts            # Interfaces TypeScript espelhando PopData
│   │   └── styles/
│   │       ├── variables.css     # Design tokens (paleta CODEBA light/dark)
│   │       ├── global.css        # Reset + base styles
│   │       └── components/       # CSS por componente
│
├── gerapop/                      # Lógica de domínio (INALTERADA)
│   ├── models.py                 # PopData, validação, factories
│   ├── constants.py              # SessionKey → removido; demais constantes mantidas
│   ├── storage.py                # Persistência em disco
│   ├── backup.py                 # CLI de backup
│   └── services/
│       ├── documento.py          # Modelo neutro de blocos
│       ├── docx/builder.py       # Renderizador .docx
│       └── pdf/builder.py        # Renderizador .pdf
│
├── tests/                        # Testes existentes + novos testes de API
└── app.py                        # Substituído por backend/main.py (ou removido)
```

---

## Proposed Changes

### Componente 1 — Backend FastAPI

> Expor toda a lógica Python existente como endpoints REST, sem reescrever nada de domínio.

#### [NEW] [main.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/backend/main.py)

App FastAPI com CORS configurado para `localhost:5173` (Vite dev server). Inclui:
- Montagem dos routers
- Middleware CORS
- Lifespan handler (nenhuma inicialização necessária por enquanto)

#### [NEW] [schemas.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/backend/schemas.py)

Modelos Pydantic V2 espelhando os TypedDicts e o `PopData`:

```python
class DefinicaoSchema(BaseModel):
    termo: str
    definicao: str

class CampoProcedimentoSchema(BaseModel):
    campo: str
    descricao: str

class SecaoSchema(BaseModel):
    titulo: str
    passos: list[str]
    campos: list[CampoProcedimentoSchema] = []

class RevisaoSchema(BaseModel):
    revisao: str
    data: str
    descricao: str
    responsavel: str

class PopCreateRequest(BaseModel):
    nome_pop: str
    codigo: str
    versao: str = "01"
    data: str
    area: str
    aviso: str = ""
    objetivo: str
    escopo: str = ""
    definicoes: list[DefinicaoSchema] = []
    secoes: list[SecaoSchema] = []
    regras: list[str] = []
    consulta: str = ""
    revisoes: list[RevisaoSchema] = []

class PopListItem(BaseModel):
    id: str
    created_at: str
    status: str
    codigo: str
    nome_pop: str
    filename: str

class ValidationErrorResponse(BaseModel):
    errors: list[str]

class DraftPayload(BaseModel):
    form: dict
    loaded_from_id: str | None = None
```

#### [NEW] [routers/pops.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/backend/routers/pops.py)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/pops` | GET | Lista POPs salvos (reutiliza `storage.list_pops()`) |
| `/api/pops/{pop_id}` | GET | Retorna dados de um POP (reutiliza `storage.get_pop()`) |
| `/api/pops/{pop_id}` | DELETE | Exclui um POP (reutiliza `storage.delete_pop()`) |
| `/api/pops/validate` | POST | Valida `PopCreateRequest` → retorna erros ou `200 OK` |
| `/api/pops/check-code` | POST | Verifica unicidade de código (`encontrar_codigo_duplicado()`) |
| `/api/pops/fluxo` | GET | Lista dados do fluxo SEV (`carregar_fluxo()`) |
| `/api/pops/fluxo/{pop_ref}` | GET | Retorna POP do fluxo (`carregar_pop_fluxo()`) |

#### [NEW] [routers/generate.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/backend/routers/generate.py)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/generate` | POST | Recebe `PopCreateRequest`, valida, salva, retorna `{ pop_id, filename }` |
| `/api/generate/{pop_id}/docx` | GET | Retorna `.docx` como `StreamingResponse` (reutiliza `gerar_docx()`) |
| `/api/generate/{pop_id}/pdf` | GET | Retorna `.pdf` como `StreamingResponse` (reutiliza `gerar_pdf()`) |
| `/api/generate/preview/docx` | POST | Gera `.docx` sem salvar (para preview de download) |
| `/api/generate/preview/pdf` | POST | Gera `.pdf` sem salvar |

#### [NEW] [routers/drafts.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/backend/routers/drafts.py)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/draft` | GET | Retorna o rascunho salvo (`storage.get_draft()`) |
| `/api/draft` | PUT | Salva o rascunho (`storage.save_draft()`) |
| `/api/draft` | DELETE | Limpa o rascunho (`storage.clear_draft()`) |

#### [NEW] [routers/backup.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/backend/routers/backup.py)

| Endpoint | Método | Descrição |
|----------|--------|-----------|
| `/api/backup` | GET | Retorna o zip de backup (`storage.gerar_backup_zip()`) |

---

### Componente 2 — Tipos TypeScript (Contrato Frontend ↔ Backend)

#### [NEW] [types/pop.ts](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/frontend/src/types/pop.ts)

Espelha os schemas Pydantic:

```typescript
export interface Definicao {
  termo: string;
  definicao: string;
}

export interface CampoProcedimento {
  campo: string;
  descricao: string;
}

export interface Secao {
  titulo: string;
  passos: string[];
  campos: CampoProcedimento[];
}

export interface Revisao {
  revisao: string;
  data: string;
  descricao: string;
  responsavel: string;
}

export interface PopData {
  nome_pop: string;
  codigo: string;
  versao: string;
  data: string;
  area: string;
  aviso: string;
  objetivo: string;
  escopo: string;
  definicoes: Definicao[];
  secoes: Secao[];
  regras: string[];
  consulta: string;
  revisoes: Revisao[];
}

export interface PopListItem {
  id: string;
  created_at: string;
  status: string;
  codigo: string;
  nome_pop: string;
  filename: string;
}

export interface FluxoNo {
  id: string;
  rotulo: string;
  etapa: number;
  descricao: string;
  pop_ref?: string;
}

export interface Fluxo {
  titulo: string;
  descricao: string;
  nos: FluxoNo[];
}
```

---

### Componente 3 — API Client (Frontend)

#### [NEW] [api/client.ts](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/frontend/src/api/client.ts)

Funções tipadas que encapsulam `fetch()`:

```typescript
const BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export async function listPops(): Promise<PopListItem[]> { ... }
export async function getPop(id: string): Promise<PopData> { ... }
export async function deletePop(id: string): Promise<void> { ... }
export async function generatePop(data: PopData): Promise<{ pop_id: string; filename: string }> { ... }
export async function downloadDocx(popId: string): Promise<Blob> { ... }
export async function downloadPdf(popId: string): Promise<Blob> { ... }
export async function previewDocx(data: PopData): Promise<Blob> { ... }
export async function previewPdf(data: PopData): Promise<Blob> { ... }
export async function validatePop(data: PopData): Promise<string[]> { ... }
export async function checkCode(codigo: string, allowedIds?: string[]): Promise<PopListItem | null> { ... }
export async function getDraft(): Promise<DraftPayload | null> { ... }
export async function saveDraft(payload: DraftPayload): Promise<void> { ... }
export async function clearDraft(): Promise<void> { ... }
export async function downloadBackup(): Promise<Blob> { ... }
export async function getFluxo(): Promise<Fluxo | null> { ... }
export async function getFluxoPop(ref: string): Promise<PopData | null> { ... }
```

---

### Componente 4 — Design System CSS (Migração do Tema CODEBA)

#### [NEW] [styles/variables.css](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/frontend/src/styles/variables.css)

Migra a paleta de [theme.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/theme.py) para CSS custom properties nativas:

```css
:root[data-theme="light"] {
  --bg: #F4F5FA;
  --surface: #FFFFFF;
  --heading: #12162A;
  --text: #12162A;
  --muted: #5C6483;
  --primary: #0F766E;
  --primary-text: #FFFFFF;
  --primary-hover: #0B5E57;
  --accent: #0F766E;
  --accent-dim: rgba(15, 118, 110, 0.12);
  --border: #DDE1EE;
  --input-bg: #EEF0F8;
  --hover: #EEF0F8;
  --hero-g1: #3B3FA6;
  --hero-g2: #5A4BC4;
  --danger: #DC2626;
  --danger-dim: rgba(220, 38, 38, 0.10);
  /* ... demais tokens ... */
}

:root[data-theme="dark"] {
  --bg: #0A0E1C;
  --surface: #111834;
  --heading: #F2F4FA;
  --text: #F2F4FA;
  --muted: #9AA3C4;
  --primary: #2DD4BF;
  /* ... demais tokens ... */
}
```

#### [NEW] [styles/global.css](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/frontend/src/styles/global.css)

Migra os 616 linhas de [theme.css](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/theme.css) convertendo os placeholders `__VAR__` em `var(--var)`.

Inclui:
- Reset moderno (box-sizing, margin, font)
- Google Font: Inter (substituindo "Segoe UI" do Streamlit)
- Scrollbar custom, focus ring, selection highlight
- Todos os componentes visuais: hero, KPIs, stepper, chips, badges, preview, cards

---

### Componente 5 — Páginas e Componentes React

#### [NEW] `pages/HomePage.tsx`

Replica o dashboard de [home.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/home.py):
- **Hero** com gradiente índigo→roxo, título do fluxo e descrição
- **KPIs** (4 cards: Etapas, POPs gerados, Pendentes, % Concluído)
- **Stepper** das etapas do fluxo (done/current/pending)
- **Modelo de referência** (card com botões Download .docx e Ver no formulário)
- **Cards de etapas com POP** (Visualizar, Download .docx/.pdf, Editar)
- **Cards de etapas pendentes** (botão "Criar POP")
- **Cards de POPs salvos** (Visualizar, Download, Editar, Excluir com confirmação em 2 cliques)

#### [NEW] `pages/FormPage.tsx`

Replica o formulário de [main.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/main.py) + [form/](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/form/):
- Seção **Identificação**: Nome*, Código*, Versão, Data, Área*, Aviso
- Seção **Objetivo***: textarea
- Seção **Escopo**: textarea
- Seção **Definições**: lista dinâmica (termo + definição) com +/−
- Seção **Procedimento**: seções dinâmicas com título, passos (lista +/−), campos obrigatórios (lista +/−)
- Seção **Regras e Restrições**: lista dinâmica com +/−
- Seção **Consulta**: textarea
- Seção **Histórico de Revisões**: lista dinâmica (revisão, data, descrição, responsável) com +/−
- Botão **"Gerar POP"** com validação client-side + server-side
- **Simulação RPA**: barra de progresso + preenchimento campo a campo com animação
- **Histórico** (expander com selectbox, download, editar, excluir, backup)
- **Auto-save de rascunho** via `useDraft` hook (debounce 2s → `PUT /api/draft`)
- **Restauração de rascunho** no mount da página

#### [NEW] `pages/PreviewPage.tsx`

Replica [preview.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/preview.py):
- Hero com nome, código, versão, data, área em chips
- Seções formatadas (Objetivo, Escopo, Definições em tabela, Procedimento com passos, Campos, Regras, Consulta, Revisões)
- Botões Voltar, Download .docx/.pdf, Editar

#### [NEW] `components/Form/DynamicList.tsx`

Componente genérico para listas dinâmicas com:
- Botão "+ Adicionar" que insere um template vazio
- Botão "Remover" por item (desabilitado quando há 1 item)
- Animação de entrada/saída (CSS transitions)
- Props tipadas para template factory e renderização do item

#### [NEW] `components/Dashboard/Hero.tsx`, `KpiGrid.tsx`, `Stepper.tsx`, `CardGrid.tsx`

Componentes reutilizáveis extraídos da lógica de [home.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/home.py).

#### [NEW] `components/ui/Button.tsx`, `Input.tsx`, `Badge.tsx`, `Card.tsx`, `Modal.tsx`

Primitivos UI genéricos com variantes (primary, danger, ghost) e suporte a estados (hover, focus, disabled, loading).

#### [NEW] `components/Layout/Sidebar.tsx`, `Header.tsx`

- **Sidebar**: Logo CODEBA (light/dark), navegação (🏠 Início, 📝 Formulário), toggle de tema
- **Header**: Transparente (como no Streamlit atual), sem menu hamburger

#### [NEW] `hooks/usePopForm.ts`

`useReducer` com actions tipadas:
```typescript
type Action =
  | { type: 'SET_FIELD'; field: keyof PopData; value: string }
  | { type: 'SET_DEFINICOES'; definicoes: Definicao[] }
  | { type: 'ADD_DEFINICAO' }
  | { type: 'REMOVE_DEFINICAO'; index: number }
  | { type: 'SET_SECOES'; secoes: Secao[] }
  | { type: 'ADD_SECAO' }
  | { type: 'REMOVE_SECAO'; index: number }
  | { type: 'ADD_PASSO'; secaoIndex: number }
  | { type: 'REMOVE_PASSO'; secaoIndex: number; passoIndex: number }
  | { type: 'ADD_CAMPO'; secaoIndex: number }
  | { type: 'REMOVE_CAMPO'; secaoIndex: number; campoIndex: number }
  | { type: 'SET_REGRAS'; regras: string[] }
  | { type: 'ADD_REGRA' }
  | { type: 'REMOVE_REGRA'; index: number }
  | { type: 'SET_REVISOES'; revisoes: Revisao[] }
  | { type: 'ADD_REVISAO' }
  | { type: 'REMOVE_REVISAO'; index: number }
  | { type: 'LOAD_POP'; pop: PopData }
  | { type: 'RESET' };
```

#### [NEW] `hooks/useDraft.ts`

- `useEffect` no mount → `GET /api/draft` → preenche form se existir
- `useEffect` com debounce 2s → `PUT /api/draft` a cada mudança do form state
- `clearDraft()` ao salvar/gerar com sucesso

#### [NEW] `hooks/useTheme.ts`

- Lê preferência de `localStorage` ou `prefers-color-scheme`
- Seta `data-theme` no `<html>`
- Persiste no `localStorage`

---

### Componente 6 — Módulos Python a Remover/Adaptar

#### [DELETE] [session_draft.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/session_draft.py)

> Estado de sessão Streamlit. Substituído por `hooks/usePopForm.ts` + `hooks/useDraft.ts` no frontend e `routers/drafts.py` no backend.

#### [DELETE] [session_codigo.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/session_codigo.py)

> Verificação de unicidade. A função `encontrar_codigo_duplicado()` é promovida para um módulo puro (sem dependência de `st.session_state`) e exposta via endpoint.

#### [DELETE] [ui/](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/) (toda a pasta)

> Substituída pelo frontend React.

#### [MODIFY] [constants.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/constants.py)

- **Remover**: `SessionKey` (enum exclusiva do Streamlit)
- **Manter**: `DOCX_MIME`, `PDF_MIME`, `DATE_FORMAT`, `DEFAULT_VERSAO`, constantes de estilo docx, `ValidationMessage`

#### [MODIFY] [__init__.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/__init__.py)

- Adicionar `gerar_pdf` ao `__all__`
- Manter exports atuais

#### [MODIFY] [app.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/app.py)

- Substituir conteúdo por: `uvicorn backend.main:app` ou remover em favor de `backend/main.py`

---

### Componente 7 — Mapeamento UI Streamlit → React

Referência precisa de cada funcionalidade e onde ela está no código atual:

| Funcionalidade | Streamlit Atual | React Equivalente |
|---|---|---|
| **Navegação sidebar** | `st.sidebar.radio` em [main.py:173](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/main.py#L173) | `react-router-dom` com `<NavLink>` em `Sidebar.tsx` |
| **Toggle tema** | `st.sidebar.toggle` em [theme.py:93](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/theme.py#L93) | `useTheme` hook + `<button>` em `Sidebar.tsx` |
| **Logo CODEBA** | `st.sidebar.image` em [theme.py:80](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/theme.py#L80) | `<img>` em `Sidebar.tsx` com src dinâmico |
| **Dashboard Hero** | `st.markdown(unsafe_allow_html)` em [home.py:106-116](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/home.py#L106-L116) | `<Hero>` component com JSX nativo |
| **KPIs** | HTML string injetada em [home.py:100-104](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/home.py#L100-L104) | `<KpiGrid>` com CSS Grid |
| **Stepper** | HTML string injetada em [home.py:119-144](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/home.py#L119-L144) | `<Stepper>` component com Flexbox |
| **Cards (grade 2 colunas)** | `st.columns(2)` em [home.py:153-168](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/home.py#L153-L168) | CSS Grid `grid-template-columns: repeat(2, 1fr)` |
| **Formulário Identificação** | `st.text_input` em [identificacao.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/form/identificacao.py) | `<IdentificacaoSection>` com `<input>` controlados |
| **Listas dinâmicas (+/−)** | `st.button` + `add_item`/`remove_at` em [dinamicas.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/form/dinamicas.py) | `<DynamicList>` genérico com dispatch de actions |
| **Validação de campos** | `pop.validate()` + `st.error` em [conteudo.py:88-103](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/form/conteudo.py#L88-L103) | Validação client-side instantânea + `POST /api/pops/validate` |
| **Unicidade de código** | `verificar_codigo_duplicado()` em [session_codigo.py:46-58](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/session_codigo.py#L46-L58) | `POST /api/pops/check-code` com debounce no `onChange` |
| **Download .docx/.pdf** | `st.download_button` em [downloads.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/downloads.py) | `<a download>` com `URL.createObjectURL(blob)` |
| **Simulação RPA** | `time.sleep` + `st.rerun` em [simulacao.py:205-208](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/simulacao.py#L205-L208) | `requestAnimationFrame` + `setTimeout` com dispatch sequencial |
| **Preview POP** | HTML injetado em [preview.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/preview.py) | `<PreviewPage>` com JSX semântico (sem `dangerouslySetInnerHTML`) |
| **Histórico** | `st.expander` + `st.selectbox` em [historico.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/historico.py) | `<History>` com `<select>` ou dropdown custom |
| **Exclusão com confirmação** | 2 cliques (`st.button` → `st.rerun`) em [exclusao.py](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/exclusao.py) | `<ConfirmDialog>` modal com animação de entrada |
| **Rascunho auto-save** | `on_change=salvar_rascunho` em todos os campos em [session_draft.py:206-216](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/session_draft.py#L206-L216) | `useDraft` hook com debounce 2s |
| **Backup zip** | `st.download_button` em [historico.py:85-90](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/gerapop/ui/historico.py#L85-L90) | `GET /api/backup` → download blob |

---

### Componente 8 — Testes

#### [NEW] `tests/test_api_pops.py`

Testes de integração para os endpoints do FastAPI usando `TestClient`:
- CRUD completo de POPs
- Validação de campos obrigatórios
- Verificação de unicidade de código
- Geração e download de .docx/.pdf
- Rascunho (save/load/clear)
- Backup zip
- Exclusão com validação anti-traversal

#### [MODIFY] Testes existentes

- Os testes de domínio (`test_models.py`, `test_docx_builder.py`, `test_storage.py`, `test_validacao_codigo.py`, `test_fluxo_sev.py`) **permanecem inalterados** — não dependem de Streamlit
- Os testes E2E (`test_e2e_app.py`, `test_e2e_codigo_duplicado.py`, `test_home.py`, `test_simulacao.py`) que usam `AppTest` do Streamlit devem ser **reescritos** como testes de API ou removidos

---

### Componente 9 — Configuração de Dev

#### [NEW] `frontend/package.json`

```json
{
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview"
  }
}
```

#### [NEW] `frontend/vite.config.ts`

Proxy de API para o backend:
```typescript
export default defineConfig({
  server: {
    proxy: {
      '/api': 'http://localhost:8000'
    }
  }
})
```

#### [MODIFY] [Makefile](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/Makefile)

Novos targets:
```makefile
run-backend:     # uvicorn backend.main:app --reload
run-frontend:    # cd frontend && npm run dev
run:             # Inicia backend + frontend em paralelo
```

#### [MODIFY] [pyproject.toml](file:///c:/Users/bruno.santos/Downloads/Projetos/GeraPOP/pyproject.toml)

Adicionar `fastapi` e `uvicorn` às dependências:
```toml
dependencies = [
    "python-docx>=1.1.2,<2",
    "reportlab>=5.0.0,<6",
    "fastapi>=0.115.0,<1",
    "uvicorn[standard]>=0.34.0,<1",
]
```

Remover `streamlit` das dependências (ou manter como opcional para compatibilidade transitória).

---

## Melhorias de UX/UI que a Migração Habilita

Além de replicar 1:1 as funcionalidades atuais, a nova stack permite:

| Melhoria | Descrição | Impossível no Streamlit? |
|----------|-----------|------------------------|
| **Drag-and-drop** nos passos | Reordenar passos e seções arrastando | ✅ Sim |
| **Validação instantânea** | Erros inline sem re-render da página inteira | ✅ Sim |
| **Animações fluidas** | Transições de página, entrada de cards, skeleton loading | ✅ Parcialmente |
| **Simulação sem refresh** | Preenchimento suave sem `st.rerun()` + `time.sleep()` | ✅ Sim |
| **Formulário multi-step wizard** | Barra de progresso real com navegação entre seções | ⚠️ Difícil |
| **Preview live** | Pré-visualização do documento ao lado do formulário (split view) | ✅ Sim |
| **Atalhos de teclado** | `Ctrl+S` para salvar rascunho, `Ctrl+Enter` para gerar | ✅ Sim |
| **Editor de texto rico** | Bold, listas, links nos campos de texto | ✅ Sim |

---

## Verification Plan

### Automated Tests
```bash
# Backend — testes de API
uv run pytest tests/test_api_pops.py tests/test_models.py tests/test_docx_builder.py tests/test_storage.py tests/test_validacao_codigo.py tests/test_fluxo_sev.py -q

# Frontend — typecheck
cd frontend && npx tsc --noEmit

# Lint
uv run ruff check backend/ gerapop/
cd frontend && npx eslint src/
```

### Manual Verification
1. Iniciar backend (`make run-backend`) e frontend (`make run-frontend`)
2. Navegar pelo dashboard — verificar Hero, KPIs, Stepper, Cards
3. Criar um POP completo no formulário → gerar .docx e .pdf → verificar conteúdo
4. Testar simulação RPA (preenchimento automático)
5. Editar POP do histórico → re-gerar → verificar unicidade de código
6. Excluir POP (confirmação em 2 cliques)
7. Toggle tema light/dark
8. Verificar rascunho: preencher parcialmente, fechar, reabrir → dados restaurados
9. Download de backup .zip
10. Comparar visualmente com a interface Streamlit atual

---

## Ordem de Implementação Sugerida para LLMs

> [!TIP]
> Para qualquer LLM executar este plano, siga esta sequência. Cada fase é auto-contida e testável.

### Fase 1 — Backend FastAPI (sem frontend)
1. Criar `backend/schemas.py` (modelos Pydantic)
2. Criar `backend/main.py` (app + CORS)
3. Criar `backend/routers/pops.py` (CRUD)
4. Criar `backend/routers/generate.py` (geração .docx/.pdf)
5. Criar `backend/routers/drafts.py` (rascunho)
6. Criar `backend/routers/backup.py` (backup)
7. Adaptar `constants.py` (extrair `encontrar_codigo_duplicado` do `session_codigo.py`)
8. Escrever `tests/test_api_pops.py`
9. ✅ Verificar: todos os endpoints respondem corretamente via `curl` ou `TestClient`

### Fase 2 — Frontend Foundation
1. `npx -y create-vite@latest ./frontend -- --template react-ts`
2. Configurar proxy em `vite.config.ts`
3. Criar `styles/variables.css` + `styles/global.css` (migrar paleta CODEBA)
4. Criar componentes primitivos (`Button`, `Input`, `Badge`, `Card`)
5. Criar `Layout/Sidebar.tsx` + roteamento com `react-router-dom`
6. Criar `hooks/useTheme.ts`
7. ✅ Verificar: app renderiza com sidebar, navegação e tema funcionando

### Fase 3 — Dashboard (Home)
1. Criar `api/client.ts` (funções de fetch)
2. Criar `components/Dashboard/Hero.tsx`, `KpiGrid.tsx`, `Stepper.tsx`, `CardGrid.tsx`
3. Montar `pages/HomePage.tsx`
4. ✅ Verificar: dashboard exibe dados do fluxo SEV, KPIs corretos, cards clicáveis

### Fase 4 — Formulário
1. Criar `hooks/usePopForm.ts` (useReducer)
2. Criar `hooks/useDraft.ts` (auto-save)
3. Criar todas as seções do formulário (`IdentificacaoSection.tsx`, etc.)
4. Criar `DynamicList.tsx` genérico
5. Montar `pages/FormPage.tsx`
6. ✅ Verificar: formulário preenche, valida, gera POP, salva rascunho

### Fase 5 — Preview + Histórico + Simulação
1. Criar `pages/PreviewPage.tsx`
2. Criar `components/History/`
3. Criar `components/Simulation/`
4. ✅ Verificar: preview renderiza, histórico lista, simulação anima

### Fase 6 — Polish
1. Micro-animações (transições de página, hover effects, skeleton loading)
2. Responsividade (mobile-friendly)
3. Acessibilidade (ARIA labels, keyboard navigation, focus management)
4. SEO (meta tags, títulos por página)
5. ✅ Teste visual final comparando com a interface Streamlit

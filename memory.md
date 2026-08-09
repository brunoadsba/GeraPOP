# GeraPOP — Memória de Contexto para LLMs

> Documento de continuidade do projeto. Leia antes de implementar qualquer feature.
> Última atualização: 2026-08-09 (sessão de limpeza + unicidade de código + clean code)

---

## 1. O que é este projeto

**GeraPOP** é um gerador de **POP** (Procedimento Operacional Padrão) para a **CODEBA** (Companhia de Navegação do Estado da Bahia — contexto portuário).

O usuário preenche um formulário guiado e recebe um arquivo `.docx` formatado, seguindo o modelo `POP_Manobras_CODEBA_v2.docx`.

**Repositório:** https://github.com/brunoadsba/GeraPOP.git  
**Branch principal:** `main`  
**Status atual:** MVP v1 completo (validação por seção, unicidade de código, rascunho persistente, backup zip, export JSON) + Fluxo SEV v1 entregue (fluxo Desembarque); **54 testes passando**; CI do GitHub desativado por pedido do usuário.

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
| UI | Streamlit 1.41 |
| Geração doc | python-docx 1.1 |
| Testes | pytest |
| Lint/format | ruff |
| Ambiente | uv + Makefile |
| Deploy v2 (futuro) | Streamlit Community Cloud (efêmero) ou Docker + volume (persistente) — ver `docs/deploy.md` |
| CI | GitHub Actions (`.github/workflows/ci.yml`) — **desativado** (`disabled_manually`, workflow id `330472653`); reativar com `gh workflow enable 330472653 --repo brunoadsba/GeraPOP` |
| Container | Docker + docker-compose (alternativa ao venv) |

**Persistência (v1.1):** POPs gerados são salvos automaticamente em `data/pops/<id>/` (`pop.json` + `pop.docx`) e listados no app (seção Histórico). Backup = botão "Backup (.zip)" no app ou `python -m gerapop.backup` (gera `data/backups/gerapop_YYYYMMDD_HHMMSS.zip`). `data/` é ignorado pelo git (apenas na raiz).

**Rascunho persistente (v1.1):** o formulário salva rascunho a cada alteração (`session.py`); ao voltar, o usuário escolhe continuar o rascunho ou recomeçar. O rascunho é restaurado se o `pop_id` de origem ainda existir no histórico.

**Unicidade de código (v1.1):** a geração é bloqueada se o código já existe no histórico, com exceção para a edição do POP carregado (permissão `{loaded_from_id} ∪ {SAVED_POP_ID}`). Ver `SessionKey.LOADED_FROM_ID`, `session.encontrar_codigo_duplicado`, `verificar_codigo_duplicado`. No Histórico, POPs com códigos repetidos exibem sufixo ` ⚠ (N)`.

**Export JSON (v1.1):** todo POP gerado pode ser baixado como `.json` (formato `{"metadata": ..., "pop": ...}`, igual ao `pop.json` do storage) — tanto na tela de geração quanto no Histórico. Habilita o Projeto 1 (Fluxo SEV).

**Fidelidade ao modelo (v1.1):** o `.docx` segue o modelo `POP_Manobras_CODEBA_v2` (validado em 2026-08-09 com o modelo real OpenPort): numeração plana automática das seções (1..N), aviso ⚠ dentro do Escopo, regras em tabela `R | texto`, consulta em caixa, fontes 18/13pt. **Campos obrigatórios por seção implementados** (G6): cada seção do Procedimento pode declarar campos obrigatórios, renderizados como tabela (Campo/Descrição) no `.docx` e validados no formulário.

**O que a v1 NÃO faz (proposital):**
- Login / multi-usuário / nuvem — sem auth, qualquer pessoa com a URL pode criar/editar (risco aceito na v1, ver `docs/deploy.md` §Segurança)
- Vínculo integrado GeraPOP → fluxo-sev (hoje é manual: copiar o `.json` exportado para `fluxo-sev/data/pops/`)

---

## 4. Estrutura do código (pós-refatoração clean code)

```
gerapop/
├── app.py                          # Entrada Streamlit (3 linhas → chama gerapop.ui.run)
├── memory.md                       # Este arquivo
├── guia-usuario.md                 # Guia do usuário final (seção 10 = campos obrigatórios)
├── gerapop/
│   ├── __init__.py                 # Exporta PopData, gerar_docx
│   ├── constants.py                # SessionKey, ValidationMessage, estilos docx, MIME
│   ├── models.py                   # PopData, TypedDicts, validação, factories
│   ├── session.py                  # Estado Streamlit (listas dinâmicas, rascunho, unicidade)
│   ├── storage.py                  # Persistência em disco (pop.json + pop.docx)
│   ├── backup.py                   # CLI de backup zip (python -m gerapop.backup)
│   ├── services/
│   │   └── docx/
│   │       ├── styles.py           # Formatação de células Word
│   │       └── builder.py          # Montagem do documento por seções
│   └── ui/
│       ├── main.py                 # Orquestração (configure → form → histórico → download)
│       └── form_sections.py        # Uma função por seção do formulário
├── fluxo-sev/                      # Projeto 1 — diagrama interativo (HTML/CSS/JS puro)
│   ├── index.html, app.js, style.css
│   ├── schema/                     # fluxo.schema.json + pop.schema.json
│   ├── data/                       # VERSIONADO (fluxo-desembarque.json + pops/pop-desembarque.json)
│   └── memory/000-fluxo-sev-v1.md  # Decisões do módulo
├── tests/
│   ├── conftest.py                 # Helpers E2E compartilhados (APP_PATH, _gerar_pop, downloads)
│   ├── test_docx_builder.py
│   ├── test_e2e_app.py             # E2E via AppTest
│   ├── test_e2e_codigo_duplicado.py# E2E unicidade de código
│   ├── test_validacao_codigo.py    # Unit unicidade + label de histórico
│   ├── test_fluxo_sev.py           # Valida dados estáticos do fluxo-sev
│   ├── test_models.py
│   └── test_storage.py
├── docs/
│   ├── plano.md                    # Roadmap completo
│   ├── piloto.md                   # Roteiro do piloto com a equipe (GATE aguarda usuário)
│   └── deploy.md                   # Opções de hospedagem (Cloud efêmero vs Docker)
├── obsoleto/                       # Arquivamento versionado (ex.: ideia-files/)
├── Makefile
├── pyproject.toml
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```

### Responsabilidades por camada

| Camada | Arquivo(s) | Responsabilidade |
|--------|-----------|------------------|
| Entrada | `app.py` | Bootstrap Streamlit |
| Domínio | `models.py` | `PopData`, validação, normalização |
| Constantes | `constants.py` | Enums, magic strings, config docx |
| Sessão | `session.py` | `st.session_state`, listas dinâmicas, rascunho, unicidade |
| Serviço | `services/docx/` | Geração `.docx` (sem dependência de Streamlit) |
| Persistência | `storage.py`, `backup.py` | Disco + backup zip (CLI) |
| UI | `ui/` | Formulário, histórico e download (depende de Streamlit) |

**Regra:** lógica de negócio e geração de documento **nunca** devem ficar em `app.py` ou `ui/` — manter testável sem Streamlit.

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
Chaves de sessão: enum `SessionKey` em `gerapop/constants.py`.

---

## 6. Como rodar, testar e validar

```bash
# Setup (primeira vez)
make install-dev

# Desenvolvimento
make run          # http://localhost:8501

# Qualidade
make test         # 54 testes (storage + docx + models + e2e + unicidade + fluxo-sev)
make lint         # ruff check + format --check
make format       # auto-format

# Backup
make backup       # zip com todos os POPs + rascunho

# Docker (alternativa)
make docker-run
```

**Problema conhecido:** Python 3.12 no WSL2 causa segfault no Streamlit (`ctypes` corrompido). Sempre usar **Python 3.11** (`.python-version` = `3.11`).

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

## 8. Estado atual do repositório (2026-08-09)

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

> Detalhes da limpeza: `ideia-files/` (protótipo original) movido para `obsoleto/ideia-files/` (pasta versionada de arquivamento — convenção §7.9); `.gitignore` `data/` → `/data/` (só raiz) para que `fluxo-sev/data/` (essencial ao `test_fluxo_sev.py`) fosse versionado; referências a `ideia-files/` removidas de `pyproject.toml` (ruff exclude) e `.ruffignore`; lixo local não versionado removido (`gerapop.egg-info/`, caches).

**Fora do repo (estado local):** CI do GitHub desativado por pedido do usuário (`gh workflow disable 330472653` — reativar com `gh workflow enable 330472653 --repo brunoadsba/GeraPOP`).

**Próxima ação sugerida:** executar o piloto com a equipe (`docs/piloto.md`) — gate que desbloqueia nuvem e os 3 fluxos SEV restantes.

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

### Gate de negócio (aguarda usuário/equipe)
- [ ] **Piloto com a equipe** — `docs/piloto.md` (roteiro pronto, GATE explícito)

### Médio prazo (GeraPOP v2)
- [ ] Hospedagem: Streamlit Community Cloud (efêmero) ou Docker + volume (persistente) — `docs/deploy.md`
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
| Protótipo original (arquivado) | `obsoleto/ideia-files/` (não usar) |
| Módulo Fluxo SEV | `fluxo-sev/README.md` + `fluxo-sev/memory/000-fluxo-sev-v1.md` |
| Config Streamlit | `.streamlit/config.toml` |
| CI | `.github/workflows/ci.yml` (desativado) |

---

## 12. Prompt de continuidade (copiar para nova sessão)

```
Contexto: Projeto GeraPOP (CODEBA) — gerador de POP em Streamlit + python-docx.
Leia memory.md e docs/plano.md antes de codar.

Stack: Python 3.11, Streamlit, python-docx, pytest, ruff.
Arquitetura: gerapop/models (domínio), services/docx (geração), ui/ (formulário),
storage/backup (persistência), fluxo-sev/ (Projeto 1, HTML/CSS/JS puro).

Estado: MVP v1 completo (validação por seção, unicidade de código, rascunho,
backup zip, export JSON) + Fluxo SEV v1 Desembarque (54 testes OK). CI desativado.
Próximo passo sugerido: piloto com a equipe (docs/piloto.md) — depois os 3 fluxos
SEV restantes e a decisão de hospedagem (docs/deploy.md).

NÃO implementar: nuvem, auth, multi-agente, migração de stack antes do piloto.
```

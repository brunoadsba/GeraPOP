# GeraPOP — Memória de Contexto para LLMs

> Documento de continuidade do projeto. Leia antes de implementar qualquer feature.
> Última atualização: 2026-08-09

---

## 1. O que é este projeto

**GeraPOP** é um gerador de **POP** (Procedimento Operacional Padrão) para a **CODEBA** (Companhia de Navegação do Estado da Bahia — contexto portuário).

O usuário preenche um formulário guiado e recebe um arquivo `.docx` formatado, seguindo o modelo `POP_Manobras_CODEBA_v2.docx`.

**Repositório:** https://github.com/brunoadsba/GeraPOP.git  
**Branch principal:** `main`  
**Status atual:** MVP v1 funcional; refatoração clean code **commitada e no GitHub** (`main`).

---

## 2. Visão de produto (dois projetos conectados)

Existe um pipeline maior documentado em `docs/plano.md`:

```
GeraPOP (Projeto 2)  →  dados estruturados  →  Fluxo Interativo SEV (Projeto 1)
   [este repo]                                      [ainda não iniciado]
```

| Projeto | Nome | Status | Descrição |
|---------|------|--------|-----------|
| 2 | **GeraPOP** | MVP entregue | Formulário → `.docx` padronizado |
| 1 | **Fluxo Interativo SEV** | Ideia validada, não iniciada | Fluxogramas clicáveis (Desembarque, Expedição, Recebimento-Exportação, Embarque-Armazenagem) linkando cada nó ao POP |

**Insight central:** o valor do GeraPOP não é só gerar Word — é **forçar estrutura padronizada** e produzir **dados reutilizáveis** para alimentar o Fluxo SEV.

**Ordem de execução obrigatória:**
1. Validar GeraPOP com POP real (Projeto 2)
2. Só então construir Fluxo SEV consumindo dados do GeraPOP (Projeto 1)
3. Nuvem, multi-usuário e multi-agente **somente após** validação dos dois MVPs

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
| Deploy v2 (futuro) | Streamlit Community Cloud |
| CI | GitHub Actions (`.github/workflows/ci.yml`) |
| Container | Docker + docker-compose (alternativa ao venv) |

**O que a v1 NÃO faz (proposital):**
- Persistência entre sessões
- Login / multi-usuário
- Nuvem
- Export JSON (próximo passo sugerido, ainda não implementado)

---

## 4. Estrutura do código (pós-refatoração clean code)

```
gerapop/
├── app.py                          # Entrada Streamlit (3 linhas → chama gerapop.ui.run)
├── memory.md                       # Este arquivo
├── gerapop/
│   ├── __init__.py                 # Exporta PopData, gerar_docx
│   ├── constants.py                # SessionKey, ValidationMessage, estilos docx, MIME
│   ├── models.py                   # PopData, TypedDicts, validação, factories
│   ├── session.py                  # Estado Streamlit (listas dinâmicas)
│   ├── services/
│   │   └── docx/
│   │       ├── styles.py           # Formatação de células Word
│   │       └── builder.py          # Montagem do documento por seções
│   └── ui/
│       ├── main.py                 # Orquestração (configure → form → download)
│       ├── form_sections.py        # Uma função por seção do formulário
│       └── components.py           # Helpers (remove_at)
├── tests/
│   ├── conftest.py                 # Fixtures pop_minimo, pop_invalido
│   ├── test_docx_builder.py
│   └── test_models.py
├── docs/plano.md                   # Roadmap completo
├── ideia-files/                    # Protótipo original (referência, não usar)
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
| Sessão | `session.py` | `st.session_state`, listas dinâmicas |
| Serviço | `services/docx/` | Geração `.docx` (sem dependência de Streamlit) |
| UI | `ui/` | Formulário e download (depende de Streamlit) |

**Regra:** lógica de negócio e geração de documento **nunca** devem ficar em `app.py` ou `ui/` — manter testável sem Streamlit.

---

## 5. Modelo de dados do POP

Estrutura baseada em `POP_Manobras_CODEBA_v2.docx`:

1. **Identificação** — Nome, Código*, Versão, Data, Área*, Aviso (opcional)
2. **Objetivo*** 
3. **Escopo e Pré-condições**
4. **Definições** — lista dinâmica (termo + definição)
5. **Procedimento** — seções dinâmicas, cada uma com passos numerados
6. **Regras e Restrições** — lista dinâmica
7. **Consulta e Relatórios** (opcional)
8. **Histórico de Revisões** — revisão, data, descrição, responsável

Campos obrigatórios na validação: **nome, código, área, objetivo**.

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
make test         # 7 testes (docx + models)
make lint         # ruff check + format --check
make format       # auto-format

# Docker (alternativa)
make docker-run
```

**Problema conhecido:** Python 3.12 no WSL2 causa segfault no Streamlit (`ctypes` corrompido). Sempre usar **Python 3.11** (`.python-version` = `3.11`).

---

## 7. Convenções de desenvolvimento

Seguir estas regras ao continuar o projeto:

1. **KISS / YAGNI** — não adicionar nuvem, auth, JSON export ou framework antes de validação real
2. **Arquivos < 200 linhas** — quebrar se ultrapassar
3. **Clean code** — uma responsabilidade por módulo; sem lógica de docx na UI
4. **Testes** — toda lógica de domínio/serviço deve ter teste pytest
5. **Commits semânticos** — formato: `tipo(escopo): descrição` (ex: `feat(docx): export JSON`)
6. **Português BR** — comunicação e mensagens de validação em português
7. **Não commitar** `.venv/`, `*.docx`, secrets
8. **Não reescrever** protótipo de `ideia-files/` — código ativo está na raiz

---

## 8. Estado atual do repositório (2026-08-09)

### Já no GitHub (`main`)
- `feat(gerapop): estrutura inicial do MVP com Streamlit e geração de POP`
- `refactor(gerapop): reorganiza projeto em camadas e adiciona memory.md` — **commit + push concluídos**
- Refatoração clean code completa no `main`:
  - Separação em `constants`, `services/docx/`, `ui/`
  - Remoção de `gerapop/docx_builder.py` monolítico
  - Remoção de duplicatas em `ideia-files/`
  - Novos testes (`test_models.py`, `conftest.py`) — **7 testes passando**
  - README atualizado com nova estrutura

**Próxima ação sugerida:** implementar export JSON (habilita o Projeto 1 — Fluxo SEV), ou testar com POP real da CODEBA.

---

## 9. Roadmap — próximos passos priorizados

### Curto prazo (GeraPOP v1.1)
- [ ] **Export JSON** junto com `.docx` — habilita Projeto 1 (Fluxo SEV)
- [ ] Testar com POP real da CODEBA e ajustar campos/layout
- [x] Commit + push da refatoração clean code

### Médio prazo (GeraPOP v2)
- [ ] Hospedagem Streamlit Community Cloud (após validação interna)
- [ ] Catálogo local de POPs (SQLite ou pasta)

### Longo prazo (Projeto 1 — Fluxo SEV)
- [ ] Schema JSON de nós: `{ id, label, pop_codigo, posicao }`
- [ ] HTML/CSS/JS puro, sem build step
- [ ] Mapear 4 fluxogramas estáticos → POPs gerados
- [ ] Piloto com 1 fluxo (Desembarque)

---

## 10. Riscos e anti-padrões (NÃO fazer)

| Risco | Mitigação |
|-------|-----------|
| Overengineering | Sem Next.js, multi-agente ou nuvem antes da v1 validada |
| Template engessado | Formulário deve aceitar exceções operacionais |
| Confundir geração com validação | Gerador agiliza escrita, não substitui revisão técnica |
| Python 3.12 no WSL | Usar 3.11 sempre |
| Duplicar código | Manter DRY; extrair para `constants` ou `services` |

---

## 11. Referências rápidas

| Recurso | Caminho |
|---------|---------|
| Roadmap completo | `docs/plano.md` |
| Instruções de uso | `README.md` |
| Modelo POP | `POP_Manobras_CODEBA_v2.docx` (referência externa, não no repo) |
| Protótipo original | `ideia-files/` (arquivado, não usar) |
| Config Streamlit | `.streamlit/config.toml` |
| CI | `.github/workflows/ci.yml` |

---

## 12. Prompt de continuidade (copiar para nova sessão)

```
Contexto: Projeto GeraPOP (CODEBA) — gerador de POP em Streamlit + python-docx.
Leia memory.md e docs/plano.md antes de codar.

Stack: Python 3.11, Streamlit, python-docx, pytest, ruff.
Arquitetura: gerapop/models (domínio), services/docx (geração), ui/ (formulário).

Estado: MVP v1 funcional. Refatoração clean code commitada e pushada (7 testes OK).
Próximo passo sugerido: export JSON ou validação com POP real.

NÃO implementar: nuvem, auth, multi-agente, migração de stack.
```

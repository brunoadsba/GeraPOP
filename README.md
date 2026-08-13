# GeraPOP — CODEBA

Gerador de POP (Procedimento Operacional Padrão) com formulário guiado e exportação `.docx` formatada.

## Pré-requisitos

- Python 3.11 (recomendado — Python 3.12 no WSL pode falhar com `ctypes`)
- [uv](https://docs.astral.sh/uv/) ou Make

## Início rápido

```bash
make install-dev
make run
```

Abra [http://localhost:8501](http://localhost:8501), preencha o formulário e clique em **Gerar POP (.docx)**.

## Alternativa via Docker

```bash
make docker-run
```

## Comandos

| Comando | Descrição |
|---------|-----------|
| `make install` | Cria `.venv` e instala dependências |
| `make install-dev` | Instala dependências + pytest e ruff |
| `make run` | Sobe o Streamlit |
| `make test` | Roda testes automatizados |
| `make lint` | Verifica estilo e imports |
| `make format` | Formata o código |
| `make docker-run` | Sobe via Docker Compose |

## Estrutura

```
gerapop/
├── app.py                      # Entrada Streamlit (3 linhas)
├── gerapop/
│   ├── constants.py            # Constantes e enums
│   ├── models.py               # Domínio e validação
│   ├── session_codigo.py       # Unicidade de código + estado de edição
│   ├── session_draft.py        # Estado da sessão Streamlit + rascunho
│   ├── storage.py              # Histórico em disco (pop.json + pop.docx)
│   ├── backup.py               # CLI de backup (python -m gerapop.backup)
│   ├── services/
│   │   ├── documento.py        # Modelo neutro de blocos (docx/pdf)
│   │   ├── docx/               # Geração do .docx
│   │   └── pdf/                # Geração do .pdf
│   └── ui/
│       ├── main.py             # Orquestração da interface
│       ├── home.py             # Dashboard (KPIs, stepper, cards)
│       ├── downloads.py        # Botões .docx/.pdf reutilizáveis
│       ├── historico.py        # Histórico + backup zip
│       ├── preview.py          # Tela de leitura do POP
│       └── form/               # Seções do formulário
├── fluxo-sev/                  # Diagrama interativo do fluxo SEV
├── tests/
├── docs/plano.md
├── guia-usuario.md
├── requirements.txt
├── pyproject.toml
└── Makefile
```

## O que a v1 faz

- Formulário com cabeçalho, objetivo, escopo, definições, procedimento (seções/passos dinâmicos com campos obrigatórios), regras, consulta e histórico de revisões
- Validação mínima (nome, código, área e objetivo) e unicidade de código (bloqueio de duplicidade com exceção para edição)
- Gera `.docx` seguindo a estrutura do modelo `POP_Manobras_CODEBA_v2` (numeração automática das seções, aviso ⚠ no escopo, regras em tabela, fontes do modelo) — validado contra o modelo real OpenPort
- Export `.pdf` (reportlab) com a mesma estrutura do `.docx`
- Dados estruturados: cada POP salvo guarda `pop.json` (`{"metadata", "pop"}`) em `data/pops/<id>/`, usado para reutilização e backup — downloads na UI são `.docx`/`.pdf`
- Histórico de POPs gerados em `data/pops/` (JSON + .docx) com re-download e "carregar para editar" (persistente via volume no Docker)
- Rascunho do formulário persistido entre sessões
- Backup dos POPs em `.zip` (botão no histórico + `python -m gerapop.backup`)

## O que a v1 não faz (proposital)

- Multi-usuário / login / nuvem

## Sem Make

```bash
uv venv --python 3.11 .venv
source .venv/bin/activate
uv pip install -r requirements.txt -r requirements-dev.txt
uv pip install -e .
streamlit run app.py --server.headless true
```

## Documentação

Ver [docs/plano.md](docs/plano.md) para visão completa do pipeline GeraPOP + Fluxo Interativo SEV.

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
│   ├── session.py              # Estado da sessão Streamlit
│   ├── storage.py              # Histórico em disco (pop.json + pop.docx)
│   ├── services/
│   │   └── docx/               # Geração do .docx
│   └── ui/
│       ├── main.py             # Orquestração da interface
│       └── form_sections.py    # Seções do formulário
├── tests/
├── docs/plano.md
├── requirements.txt
├── pyproject.toml
└── Makefile
```

## O que a v1 faz

- Formulário com cabeçalho, objetivo, escopo, definições, procedimento (seções/passos dinâmicos), regras, consulta e histórico de revisões
- Validação mínima (nome, código, área e objetivo)
- Gera `.docx` seguindo a estrutura do modelo `POP_Manobras_CODEBA_v2` (numeração automática das seções, aviso ⚠ no escopo, regras em tabela, fontes do modelo) — validado contra o modelo real OpenPort
- Export `.json` do POP (`{"metadata", "pop"}`) junto com o `.docx` — na geração e no histórico
- Histórico de POPs gerados em `data/pops/` (JSON + .docx) com re-download e "carregar para editar" (persistente via volume no Docker)

## O que a v1 não faz (proposital)

- Rascunho do formulário persistido entre sessões
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

# SEV — Fluxo Interativo (Projeto 1)

Diagrama clicável dos fluxos operacionais da CODEBA. Cada caixa do processo
abre o POP relacionado, gerado pelo **GeraPOP** (Projeto 2).

v1: **HTML/CSS/JS puro, sem build step**, rodando localmente (sem framework).

## Como rodar

O app carrega os dados via `fetch`, então precisa de um servidor HTTP (abrir o
`index.html` direto do navegador — `file://` — bloqueia o fetch):

```bash
cd fluxo-sev
python -m http.server 8000
# abra http://localhost:8000
```

Sem Makefile: é estático, nenhuma instalação é necessária.

## Estrutura

```
fluxo-sev/
├── index.html                  # página do diagrama
├── style.css                   # estilos (tema portuário)
├── app.js                      # lógica pura (fetch + render + modal)
├── schema/
│   ├── fluxo.schema.json       # schema de um fluxo (nós + links)
│   └── pop.schema.json         # schema do pop.json do GeraPOP
├── data/
│   ├── fluxo-desembarque.json  # fluxo Desembarque (etapas e nós)
│   └── pops/
│       └── pop-desembarque.json# POP gerado pelo GeraPOP (formato oficial)
└── memory/                     # decisões do módulo
```

## Adicionar um POP vinculado

1. Gere o POP no GeraPOP e exporte o `.json` (mesmo conteúdo do botão
   "Baixar POP (.json)").
2. Salve em `fluxo-sev/data/pops/<nome>.json` (ex.: `pop-expedicao.json`).
3. No fluxo, aponte o nó desejado: `"pop_ref": "<nome>"` (sem extensão).

O nó passa a exibir "Ver POP" e o clique abre o POP formatado (cabeçalho,
objetivo, escopo, definições, seções com passos e campos obrigatórios, regras,
consulta, revisões).

Nós com `"pop_ref": null` exibem "POP não gerado" e informam como vincular.

## Adicionar um novo fluxo

1. Crie `fluxo-sev/data/fluxo-<nome>.json` seguindo
   `schema/fluxo.schema.json` (etapas numeradas, nós com `id` único).
2. Aponte o `index.html` para ele: `<html data-fluxo="data/fluxo-<nome>.json">`.
3. Valide contra o schema (ou com o teste `tests/test_fluxo_sev.py`).

## Testes

`tests/test_fluxo_sev.py` valida os dados estáticos: o `pop.json` deve ser
compatível com o `PopData` do GeraPOP e os fluxos devem referenciar só POPs
existentes.

## Limitações v1

- Layout em colunas por etapa (sem canvas/SVG de setas livres).
- 1 fluxo por página (troca via `data-fluxo` no HTML).
- Sem busca, sem multiusuário — estático e local.

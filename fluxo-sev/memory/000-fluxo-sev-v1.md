# Memory — SEV Fluxo Interativo (fluxo-sev/)

Decisões e contexto do módulo. Sempre atualizar quando algo mudar de direção.

## 2026-08-09 — v1: diagrama clicável estático

**Decisão:** HTML/CSS/JS puro, sem build step, sem framework, rodando de um
servidor HTTP simples. Motivo (do docs/plano.md): validar a ideia antes de
adicionar TS/framework numa v2; TS só entra se a v1 provar valor.

**Formato dos dados:** os nós referenciam POPs por `pop_ref` (nome do arquivo
sem extensão em `data/pops/`). O `pop.json` usa **exatamente** o formato do
GeraPOP (`metadata` + `pop` de `serialize_pop`) — o mesmo arquivo exportado
pelo botão "Baixar POP (.json)". Isso garante que o Projeto 1 consome o output
do Projeto 2 sem transformação.

**Por que fetch + http.server e não file://:** `fetch` é bloqueado em `file://`.
v1 assume um `python -m http.server`; sem dependência nenhuma além do Python
que já existe no projeto.

**Layout:** colunas por etapa (sem canvas/SVG). Cada nó é um `<button>` com
`data-no-id` — acessível por teclado e por testes de acessibilidade (snapshot
ARIA). Modal com `role="dialog"`, fecha por botão, backdrop ou `Esc`.

**Campos obrigatórios por seção:** renderizados como tabela (Campo /
Descrição) no modal — espelha a sub-tabela do `.docx` do GeraPOP.

**Compatibilidade:** nós com `pop_ref: null` são válidos e exibem estado
"POP não gerado" com instrução de vínculo — o fluxo não quebra quando um POP
ainda não existe.

**Validação por teste:** `tests/test_fluxo_sev.py` garante que o pop.json é
carregável pelo `PopData` do GeraPOP (fidelidade do formato) e que todo
`pop_ref` aponta para arquivo existente.

**QA v1 (Playwright, 2026-08-09):** renderização de 7 etapas/cards corretos;
modal do nó com POP exibiu o conteúdo completo (cabeçalho, aviso, objetivo,
escopo, definições, seções + campos, regras, consulta, revisões); nó sem POP
exibiu a mensagem de vínculo; `Esc` fecha; console sem erros. Evidência:
snapshot ARIA + screenshot arquivado em /tmp/opencode/.

## Próximos passos (não decididos ainda)

- Outros fluxos: Expedição, Recebimento-Exportação, Embarque-Armazenagem
  (replicar `fluxo-<nome>.json` + `data-fluxo` no HTML).
- Migrar para TS/framework somente se o uso real justificar (gate do piloto).
- Sinalizar visualmente nós sem POP já implementado; falta o fluxo de
  "adicionar POP" integrado ao GeraPOP (hoje é manual: copiar o json).

## Melhorias de renderização de passos (2026-08-13)

O modal de POP agora aplica as convenções de texto do GeraPOP (paridade com
docx/pdf): passo iniciando com `Tela ` vira sub-cabeçalho (`li.sub`, fundo
azul-claro, sem número); passo iniciando com `Sistema ` vira resposta do
sistema (`li.sys`, itálico, sem número); aspas simples emparelhadas viram
negrito (`<b>`). Ver `app.js::renderPasso` e classes `.pop-passos li.sub/sys`
no `style.css`.

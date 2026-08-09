# Plano — Ferramentas de Fluxo e Documentação Operacional (CODEBA)

## Visão geral

Dois projetos que nasceram separados, mas se conectam num único pipeline:

```
Gerador de POP  →  dados estruturados do procedimento  →  Fluxo interativo (SEV)
   (Projeto 2)                                                (Projeto 1)
```

O Gerador de POP produz o conteúdo padronizado. O Fluxo Interativo consome
esse conteúdo, linkando cada etapa do processo ao POP correspondente.

---

## Projeto 1 — Fluxo Interativo (SEV) + POPs

**Objetivo:** transformar os fluxogramas estáticos (Desembarque, Expedição,
Recebimento-Exportação, Embarque-Armazenagem) em um diagrama clicável, onde
cada caixa do processo abre o POP relacionado.

**Status:** ideia validada, ainda não iniciada.

**Decisões tomadas:**
- Stack v1: HTML/CSS/JS puro, sem build step, rodando localmente (abrir o
  arquivo no navegador).
- Sem multi-agentes por enquanto — escopo cortado por ser prematuro.
- TS + framework só entram numa v2, se a v1 provar valor.
- Fonte dos dados de cada nó: os POPs gerados pelo Projeto 2.

**Próximo passo:** montar o JSON/estrutura de dados mapeando cada caixa dos
4 fluxos aos respectivos POPs.

---

## Projeto 2 — GeraPOP

**Objetivo:** formulário guiado que gera o documento de POP já formatado,
eliminando a fricção de montar o Word manualmente a cada novo procedimento.

**Status:** MVP local funcionando (v1 entregue).

**Modelo de referência:** `POP_Manobras_CODEBA_v2.docx` — estrutura usada
como base: cabeçalho (Código/Versão/Data/Área), Objetivo, Escopo, Definições,
Procedimento (seções com passos numerados), Regras e Restrições, Consulta e
Relatórios, Histórico de Revisões.

**Decisões tomadas:**
- v1 = single-use, 100% local (Streamlit + python-docx), sem login, sem
  persistência entre sessões.
- v2 (só se a v1 rodar bem no uso real) = hospedagem em nuvem (Streamlit
  Community Cloud) para acesso do setor inteiro.
- Motivo de usar Streamlit: reaproveita conhecimento já existente do
  [[Argus MVP]] e evita stack nova desnecessária.
- O ganho real do gerador não é a geração do arquivo em si (é um merge
  simples), e sim forçar estrutura padronizada e gerar dados reutilizáveis
  (que alimentam o Projeto 1).

**Nome do projeto:** GeraPOP

**Entregue:**
- `app.py` — formulário completo com seções dinâmicas (definições, passos,
  regras, revisões) e geração de `.docx`.
- `requirements.txt`, `README.md`.

**Próximo passo:** você testar localmente com um POP real e reportar ajustes
(campos, layout, usabilidade das listas dinâmicas) antes de cogitar nuvem.

---

## Ordem de execução recomendada

1. Validar o Gerador de POP (Projeto 2) com uso real — é a base de dados do
   Projeto 1.
2. Só depois montar o Fluxo Interativo (Projeto 1), já consumindo POPs
   gerados pela ferramenta.
3. Reavaliar nuvem/multi-usuário e qualquer ideia de multi-agente somente
   depois que os dois MVPs estiverem validados em uso — não antes.

---

## Riscos identificados a evitar

- **Overengineering prematuro:** multi-agente, stack pesado ou nuvem antes
  de validar a v1 local.
- **Template engessado:** o formulário do POP precisa aceitar exceções e
  nuances operacionais, não travar em campos rígidos demais.
- **Confundir geração com validação:** o gerador agiliza a escrita, não
  substitui a revisão técnica do conteúdo do POP.

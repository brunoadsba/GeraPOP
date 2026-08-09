# Piloto do GeraPOP — roteiro com a equipe

O objetivo do piloto é **validar o GeraPOP com uso real** antes de decidir por
nuvem/multi-usuário e antes de alimentar o Fluxo Interativo (Projeto 1) com os
dados gerados. Um piloto bem-feito responde a duas perguntas:

1. O formulário cobre os POPs reais do setor sem travar em campos rígidos?
2. O `.docx` gerado é aceitável como documento oficial (estrutura e formatação)?

> GATE: este roteiro é o plano de execução com a equipe. A execução em si
> (agendar sessões, rodar com POPs reais) aguarda o usuário.

---

## Duração e participantes

- **Duração sugerida:** 2–4 semanas.
- **Participantes:** 1–2 redatores de POP do setor operacional + 1 responsável
  pela revisão técnica (validação do conteúdo).

## Como rodar o piloto

```
make install-dev
make run
```

Abra http://localhost:8501 — ou, se o objetivo já for avaliar o acesso do
setor, publique via [deploy.md](deploy.md) (Opção A, Cloud).

---

## Roteiro passo a passo

**Fase 1 — Preparação (antes da 1ª sessão)**
- [ ] Selecionar 3 POPs reais existentes para recriar no GeraPOP (variando em
      tamanho: 1 simples, 1 médio, 1 com muitas seções/regras).
- [ ] Rodar `make test` e `make lint` — confirmar que a base está verde.
- [ ] Gerar um POP de teste e conferir o `.docx` no Word (fonte, tabelas,
      numeração, margens).

**Fase 2 — Sessão de demonstração (1–2h com a equipe)**
- [ ] Demonstrar o fluxo completo: preencher → gerar → baixar `.docx` e `.json`
      → ver no histórico → carregar para editar → backup zip.
- [ ] Recriar **um** POP real diante da equipe, em conjunto, anotando em tempo
      real os atritos (campos faltando, ordem, nomes, etc.).

**Fase 3 — Uso real (semanas 2–4)**
- [ ] Cada participante recria **pelo menos 1 POP real** sozinho.
- [ ] Registrar cada ajuste/incômodo num único lugar (planilha ou issue).

**Fase 4 — Revisão e decisão**
- [ ] Reunir feedback e classificar: *bloqueante* vs *desejável*.
- [ ] Decidir o destino do piloto (ver Critérios de saída).

---

## Checklist de validação do formulário

Para cada POP recriado, marcar:

- [ ] Todos os campos do POP original couberam no formulário **sem forçar**.
- [ ] Seções e passos dinâmicos atenderam estruturas com 1 ou N seções.
- [ ] Campos obrigatórios por seção (quando aplicável) cobriram o caso real.
- [ ] Listas (definições, regras, revisões) permitiram o que o POP precisava.
- [ ] O rascunho sobreviveu a fechar e reabrir o navegador (quando local).
- [ ] O `.docx` saiu pronto para uso no Word **sem retrabalho de formatação**.
- [ ] O `.json` gerado tem o conteúdo esperado (conferir num visualizador).

## Checklist de validação do processo

- [ ] Tempo para criar um POP novo ficou menor que montar no Word.
- [ ] A equipe entendeu o que a ferramenta faz e o que **não** faz (gera o
      documento, não substitui a revisão técnica do conteúdo).
- [ ] O histórico + backup zip foi suficiente para guardar os POPs (ou já ficou
      evidente a necessidade de persistência — ver deploy.md).

---

## Critérios de saída

| Resultado | Decisão |
|-----------|---------|
| ≥ 2 POPs reais recriados sem bloqueantes e `.docx` aceito | **Piloto aprovado** → avaliar Cloud (deploy.md) e iniciar o Fluxo Interativo (Projeto 1) |
| Bloqueantes de campos/formatação | **Ajustar o GeraPOP** (o formulário é o que precisa aceitar exceções — risco "template engessado") e repetir o piloto |
| Equipe não adotou / tempo não melhorou | **Não escalar**: manter uso individual e reavaliar em outro momento |

---

## Registro de feedback

Modelo de entrada (uma linha por item):

```
| POP | O que aconteceu | Esperado | Bloqueante? | Sugestão |
|-----|-----------------|----------|-------------|----------|
```

Os ajustes priorizados vão para o backlog do GeraPOP; nada do piloto deve
"quebrar" um POP já gerado — o `.docx` final é sempre o artefato de verdade.

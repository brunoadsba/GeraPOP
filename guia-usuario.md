# Guia do Usuário — GeraPOP

Este guia explica, em linguagem simples, como usar o **GeraPOP**: a ferramenta
que ajuda a criar POPs (Procedimento Operacional Padrão) preenchendo um
formulário no computador. No final, ela gera o documento pronto, bonito e
formatado — sem precisar montar nada no Word.

Se você nunca usou a ferramenta, siga este guia do começo ao fim. Leva poucos
minutos.

---

## 1. O que é um POP?

Um POP é um documento que explica **como fazer uma tarefa**, passo a passo.
Por exemplo: "Como registrar uma manobra no sistema" ou "Como fazer a
inspeção inicial de um navio".

O GeraPOP transforma o que você digita num documento pronto para usar.

---

## 2. Como abrir o GeraPOP

**Se a ferramenta está instalada no seu computador:**

1. Peça para alguém do setor de tecnologia abrir o programa.
2. O GeraPOP abre no seu navegador de internet (Chrome, Edge, etc.), em um
   endereço parecido com: `http://localhost:8501`.

**Se a ferramenta está publicada na internet:**

1. Clique no link que o setor enviou.
2. O GeraPOP abre no navegador.

> Pronto. Você não precisa instalar nada nem digitar senha.

---

## 3. Conhecendo a tela

A tela é um **formulário com várias partes**, uma embaixo da outra. Basta ir
preenchendo de cima para baixo.

Os campos marcados com **\*** (asterisco) são **obrigatórios** — sem eles, o
documento não é gerado. Os demais são opcionais: preencha se fizer sentido
para o seu POP.

Ao terminar, clique no botão verde **"Gerar POP (.docx)"** (no final do
formulário) e o documento é criado na hora.

---

## 4. Passo a passo para criar um POP

### 4.1 Dados principais (parte de cima)

Preencha:

- **Nome do POP \*** — o título do documento. Ex.: "Manobra de Atracação de Navio".
- **Código \*** — o código do procedimento. Ex.: `POP-OPE-001`.
- **Versão** — número da versão. Normalmente começa em `01` (não precisa mudar).
- **Data** — data do documento. Já vem com a data de hoje.
- **Área \*** — o setor responsável. Ex.: "Operações Portuárias".
- **Aviso (opcional)** — um alerta importante que deve aparecer em destaque no
  documento. Ex.: "Somente executar com autorização da coordenação."

### 4.2 Objetivo e escopo

- **Objetivo \*** — para que serve o procedimento, em uma ou duas frases.
  Ex.: "Padronizar o registro de manobras no sistema."
- **Escopo** — para quem vale o procedimento. Ex.: "Aplica-se à equipe de
  operações portuárias."

### 4.3 Definições (opcional)

Aqui você explica **termos técnicos** que aparecem no documento, para quem lê
entender. Ex.: "TOS — Terminal Operating System".

- Digite o **termo** e a **definição**.
- Para acrescentar outro termo, clique em **"+ Adicionar termo"**.
- Para apagar, clique em **"Remover"** ao lado do termo (só é possível apagar
  quando há mais de um).

### 4.4 Procedimento — seções e passos (a parte principal)

O procedimento é dividido em **seções**, e cada seção tem **passos numerados**.

Por exemplo, a seção "Preparação da manobra" pode ter os passos:

1. Confirmar o horário de chegada do navio.
2. Designar o berço de atracação.
3. Confirmar a disponibilidade do prático.

Como fazer:

1. No campo **"Título da seção"**, digite o nome da seção.
2. No campo **"Passo"**, digite o primeiro passo.
3. Clique em **"+ Adicionar passo"** para acrescentar mais passos (eles são
   numerados automaticamente no documento final).
4. Para apagar um passo, clique em **"Remover"** ao lado dele.
5. Para criar **outra seção**, clique em **"+ Adicionar seção"** no final.
6. Para apagar uma seção inteira, clique em **"Remover seção"** (só é possível
   quando há mais de uma seção).

> Dica: divida o procedimento em seções curtas. Fica mais fácil de ler e de
> seguir.

### 4.5 Campos obrigatórios por seção (opcional)

Se a seção precisa de **informações que devem ser anotadas** durante a
execução (ex.: data e hora, berço, nome do prático), você pode listá-las aqui.
Elas viram uma tabela **"Campos obrigatórios"** no documento.

1. Clique em **"+ Adicionar campo"**.
2. Digite o **nome do campo** (ex.: "Berço") e a **descrição ou instrução**
   (ex.: "Número do berço designado para a atracação.").

### 4.6 Regras e Restrições (opcional)

Liste o que **não pode ser feito** ou o que é obrigatório cumprir.
Ex.: "Não iniciar a manobra sem prático credenciado a bordo."

- Digite a regra e clique em **"+ Adicionar regra"** para incluir outras.

### 4.7 Consulta (opcional)

Se o POP estiver disponível em algum sistema ou menu, informe o caminho.
Ex.: "Menu > Operações > Manobras".

### 4.8 Histórico de revisões (opcional)

Registre as **versões** do documento:

- **Revisão** — número da revisão (ex.: `01`).
- **Data** — data da revisão.
- **Descrição** — o que mudou (ex.: "Emissão inicial").
- **Responsável** — quem fez a revisão.

Use **"+ Adicionar revisão"** para incluir outra.

---

## 5. Gerando e baixando o POP

1. Preencha tudo e clique em **"Gerar POP (.docx)"**.
2. Se faltar algum campo obrigatório, a ferramenta avisa o que falta — basta
   preencher e tentar de novo.
3. Quando der certo, aparece a mensagem **"POP gerado com sucesso."** e dois
   botões:
   - **"Baixar POP (.docx)"** — o documento do Word, pronto para usar.
   - **"Baixar POP (.json)"** — uma cópia digital dos dados, usada por outros
     sistemas. Não se preocupe com ela: baixe junto por segurança.

O arquivo baixado vai para a pasta de downloads do seu computador (ou para o
local que o navegador escolher).

> Dica: se você mudar alguma coisa no formulário **depois** de gerar o POP, os
> botões de download somem (porque o documento antigo já não corresponde ao
> formulário). Clique em **"Gerar POP (.docx)"** de novo para gerar a versão
> nova.

---

## 6. Histórico de POPs gerados

Os POPs gerados ficam guardados na própria ferramenta.

1. No final da página, abra **"Histórico de POPs gerados"**.
2. Escolha o POP na lista (ela mostra a data, o código e o nome).
3. Você pode:
   - **"Baixar .docx"** — baixar o documento de novo.
   - **"Baixar .json"** — baixar os dados de novo.
   - **"Carregar para editar"** — trazer esse POP de volta para o formulário
     para fazer alterações. Depois de editar, gere o POP novamente.

---

## 7. O rascunho automático

O GeraPOP **guarda o que você digitou automaticamente**. Se você fechar a
página sem querer, ou abrir a ferramenta de novo no mesmo computador, o
formulário volta preenchido como estava. Nada se perde.

---

## 8. Fazendo backup (cópia de segurança)

Se a ferramenta estiver instalada no seu computador (uso local), alguém do
setor pode fazer uma cópia de todos os POPs com o comando `make backup`.

Dentro do histórico, há também o botão **"Baixar backup (.zip)"**: ele gera
um arquivo com todos os POPs guardados, para você salvar num lugar seguro
(pen drive, pasta da rede, etc.).

> Importante: se a ferramenta estiver publicada na internet (nuvem), os POPs
> guardados podem ser **apagados quando o serviço reiniciar**. Por isso, baixe
> os POPs importantes (ou o backup) e guarde fora da ferramenta.

---

## 9. Dicas rápidas

- Preencha os campos com **\*** primeiro — sem eles, não gera.
- Use frases curtas nos passos: cada passo é uma ação.
- Revise o documento gerado antes de compartilhar: a ferramenta ajuda a
  escrever, mas a **revisão técnica do conteúdo é sua**.
- O gerador cria a estrutura; quem conhece a tarefa é quem garante que o
  conteúdo está correto.

---

## 10. Problemas comuns e como resolver

| O que aconteceu | O que fazer |
|-----------------|-------------|
| Clico em "Gerar POP (.docx)" e aparece "código já é usado" | Esse código já pertence a outro POP salvo. Escolha um código diferente ou carregue o POP existente no histórico ("Carregar para editar") e gere a partir dele. |
| Clico em "Gerar POP (.docx)" e nada acontece | Verifique se os campos com \* estão preenchidos. A mensagem de erro diz qual falta. |
| Não encontro os botões de baixar o POP | Eles só aparecem depois de clicar em "Gerar POP (.docx)" com sucesso. Se você editou o formulário, gere de novo. |
| O histórico está vazio | Os POPs só aparecem no histórico **depois** de gerados. Gere um POP primeiro. |
| O formulário voltou preenchido quando reabri | Isso é o rascunho automático funcionando. Se quiser começar do zero, apague o conteúdo manualmente. |
| Não sei se um campo é obrigatório | Todo campo com \* é obrigatório. O resto é opcional. |
| Preciso de ajuda ou algo não funciona | Fale com o responsável pelo setor de tecnologia — informe o que você estava fazendo e o que apareceu na tela. |

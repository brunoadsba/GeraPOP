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
   endereço parecido com: `http://localhost:5173`.

**Se a ferramenta está publicada na internet:**

1. Clique no link que o setor enviou.
2. O GeraPOP abre no navegador.

> Pronto. Você não precisa instalar nada nem digitar senha.

---

## 3. Conhecendo a tela

O GeraPOP tem **duas telas**, trocadas pelo menu lateral (barra à esquerda):

- **🏠 Início** — o painel do Fluxo SEV (veja a seção 4).
- **📝 Formulário** — onde você cria e edita POPs (veja a seção 5).

Na barra lateral também há o botão de **tema claro/escuro**: use o que for
mais confortável para você.

Na tela do Formulário, os campos marcados com **\*** (asterisco) são
**obrigatórios** — sem eles, o documento não é gerado. Os demais são
opcionais: preencha se fizer sentido para o seu POP.

Ao terminar, clique no botão verde **"Gerar POP (.docx)"** (no final do
formulário) e o documento é criado na hora.

---

## 4. A página Início (o painel do Fluxo SEV)

A página Início acompanha o **Fluxo SEV** (Desembarque): a sequência de
etapas do processo e os POPs de cada etapa. Ela mostra:

- **Indicadores no topo** — total de etapas, POPs já gerados, POPs pendentes
  e o percentual de conclusão.
- **A sequência de passos do fluxo** — cada etapa aparece como um passo;
  as etapas concluídas ficam marcadas com ✓.
- **Modelo de referência** — um POP de exemplo, já preenchido e validado.
  Você pode baixar o `.docx` dele ou clicar em **"Ver modelo no formulário"**
  para vê-lo na tela de edição (atenção: isso substitui o que estiver no
  formulário).
- **Cards de POPs gerados** — para cada etapa com POP pronto: **"Visualizar
  POP"** (abre o documento em modo de leitura, sem baixar), baixar `.docx` /
  `.pdf` e **"Editar POP"** (abre o POP no formulário para alterações).
- **Cards de POPs pendentes** — etapas que ainda não têm POP, com o botão
  **"Criar POP"** para começar (o nome e a descrição da etapa já entram
  preenchidos no formulário).

> **Visualizar POP** abre o documento em modo de leitura, com botões para
> baixar `.docx`/`.pdf` e voltar. Use para conferir um POP sem abrir o Word.

---

## 5. Passo a passo para criar um POP

Vá para **📝 Formulário** no menu lateral.

No topo do formulário você encontra:

- **Simulação de preenchimento (RPA)** — um painel com o botão **"▶ Iniciar
  simulação"**: um robô preenche o formulário automaticamente, campo a
  campo, mostrando na prática como cada campo deve ser preenchido. Serve
  como demonstração; você pode parar a simulação a qualquer momento e editar
  à vontade.

> Se quiser ver um POP de exemplo preenchido (o **modelo de referência**),
> abra **🏠 Início** e clique em **"Ver modelo no formulário"** no card do
> modelo — atenção: isso substitui o que estiver no formulário.

### 5.1 Dados principais (parte de cima)

Preencha:

- **Nome do POP \*** — o título do documento. Ex.: "Manobra de Atracação de Navio".
- **Código \*** — o código do procedimento. Ex.: `POP-OPE-001`.
- **Versão** — número da versão. Normalmente começa em `01` (não precisa mudar).
- **Data** — data do documento. Já vem com a data de hoje.
- **Área \*** — o setor responsável. Ex.: "Operações Portuárias".
- **Aviso (opcional)** — um alerta importante que deve aparecer em destaque no
  documento. Ex.: "Somente executar com autorização da coordenação."

### 5.2 Objetivo e escopo

- **Objetivo \*** — para que serve o procedimento, em uma ou duas frases.
  Ex.: "Padronizar o registro de manobras no sistema."
- **Escopo** — para quem vale o procedimento. Ex.: "Aplica-se à equipe de
  operações portuárias."

### 5.3 Definições (opcional)

Aqui você explica **termos técnicos** que aparecem no documento, para quem lê
entender. Ex.: "TOS — Terminal Operating System".

- Digite o **termo** e a **definição**.
- Para acrescentar outro termo, clique em **"+ Adicionar termo"**.
- Para apagar, clique em **"Remover"** ao lado do termo (só é possível apagar
  quando há mais de um).

### 5.4 Procedimento — seções e passos (a parte principal)

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

#### Passos especiais (sub-cabeçalho de tela e resposta do sistema)

Dois formatos de passo recebem destaque visual no documento:

- **Comece o passo com `Tela `** (ex.: `Tela 6002 – Programação de Saída`) para
  criar um **sub-cabeçalho** dentro da tabela de passos — ele agrupa os passos
  daquela tela, sem número, com fundo azul-claro.
- **Comece o passo com `Sistema `** (ex.: `Sistema exibe: "Deseja liberar a
  programação de saída?" Clique no botão 'Ok'.`) para marcar uma **resposta do
  sistema** (mensagem/pop-up) — ela sai em itálico, sem número, com traço na
  coluna de número.

Esses passos especiais **não consomem numeração** — os passos normais seguem
numerados em sequência.

> Dica: use **aspas simples** ao redor de nomes de botões (ex.: `'Novo'`,
> `'Gravar'`) — eles saem em **negrito** no documento, facilitando a leitura
> rápida durante a operação. Aspas simples desemparelhadas (ex.: `d'água`) são
> tratadas como texto normal.

### 5.5 Campos obrigatórios por seção (opcional)

Se a seção precisa de **informações que devem ser anotadas** durante a
execução (ex.: data e hora, berço, nome do prático), você pode listá-las aqui.
Elas viram uma tabela **"Campos obrigatórios"** no documento.

1. Clique em **"+ Adicionar campo"**.
2. Digite o **nome do campo** (ex.: "Berço") e a **descrição ou instrução**
   (ex.: "Número do berço designado para a atracação.").

### 5.6 Regras e Restrições (opcional)

Liste o que **não pode ser feito** ou o que é obrigatório cumprir.
Ex.: "Não iniciar a manobra sem prático credenciado a bordo."

- Digite a regra e clique em **"+ Adicionar regra"** para incluir outras.

### 5.7 Consulta (opcional)

Se o POP estiver disponível em algum sistema ou menu, informe o caminho.
Ex.: "Menu > Operações > Manobras".

### 5.8 Histórico de revisões (opcional)

Registre as **versões** do documento:

- **Revisão** — número da revisão (ex.: `01`).
- **Data** — data da revisão.
- **Descrição** — o que mudou (ex.: "Emissão inicial").
- **Responsável** — quem fez a revisão.

Use **"+ Adicionar revisão"** para incluir outra.

---

## 6. Gerando e baixando o POP

1. Preencha tudo e clique em **"Gerar POP (.docx)"**.
2. Se faltar algum campo obrigatório, a ferramenta avisa o que falta — basta
   preencher e tentar de novo.
3. Quando der certo, aparece a mensagem **"POP gerado com sucesso."** e dois
   botões:
   - **"Baixar POP (.docx)"** — o documento do Word, pronto para usar.
   - **"Baixar POP (.pdf)"** — o mesmo documento em PDF.

O arquivo baixado vai para a pasta de downloads do seu computador (ou para o
local que o navegador escolher).

> Dica: se você mudar alguma coisa no formulário **depois** de gerar o POP, os
> botões de download somem (porque o documento antigo já não corresponde ao
> formulário). Clique em **"Gerar POP (.docx)"** de novo para gerar a versão
> nova.

---

## 7. Histórico de POPs gerados

Os POPs gerados ficam guardados na própria ferramenta.

1. No final da página do Formulário, use **"Histórico de POPs gerados"**.
2. Escolha o POP na lista (ela mostra a data, o código e o nome).
3. Você pode:
   - **"Visualizar"** — abrir o POP em modo de leitura (sem baixar).
   - **"Baixar .docx"** — baixar o documento de novo.
   - **"Baixar .pdf"** — baixar a versão em PDF de novo.
   - **"Carregar para editar"** — trazer esse POP de volta para o formulário
     para fazer alterações. Depois de editar, gere o POP novamente.

---

## 8. O rascunho automático

O GeraPOP **guarda o que você digitou automaticamente**. Se você fechar a
página sem querer, ou abrir a ferramenta de novo no mesmo computador, o
formulário volta preenchido como estava. Nada se perde.

---

## 9. Fazendo backup (cópia de segurança)

Se a ferramenta estiver instalada no seu computador (uso local), alguém do
setor pode fazer uma cópia de todos os POPs com o comando `make backup`.

Dentro do histórico, há também o botão **"Baixar backup (.zip)"**: ele gera
um arquivo com todos os POPs guardados, para você salvar num lugar seguro
(pen drive, pasta da rede, etc.).

> Importante: se a ferramenta estiver publicada na internet (nuvem), os POPs
> guardados podem ser **apagados quando o serviço reiniciar**. Por isso, baixe
> os POPs importantes (ou o backup) e guarde fora da ferramenta.

---

## 10. Dicas rápidas

- Preencha os campos com **\*** primeiro — sem eles, não gera.
- Use frases curtas nos passos: cada passo é uma ação.
- Revise o documento gerado antes de compartilhar: a ferramenta ajuda a
  escrever, mas a **revisão técnica do conteúdo é sua**.
- Use **"Visualizar"** (no histórico ou no painel Início) para conferir o POP
  antes de baixar ou editar.
- O gerador cria a estrutura; quem conhece a tarefa é quem garante que o
  conteúdo está correto.

---

## 11. Problemas comuns e como resolver

| O que aconteceu | O que fazer |
|-----------------|-------------|
| Clico em "Gerar POP (.docx)" e aparece "código já é usado" | Esse código já pertence a outro POP salvo. Escolha um código diferente ou carregue o POP existente no histórico ("Carregar para editar") e gere a partir dele. |
| Clico em "Gerar POP (.docx)" e nada acontece | Verifique se os campos com \* estão preenchidos. A mensagem de erro diz qual falta. |
| Não encontro os botões de baixar o POP | Eles só aparecem depois de clicar em "Gerar POP (.docx)" com sucesso. Se você editou o formulário, gere de novo. |
| O histórico está vazio | Os POPs só aparecem no histórico **depois** de gerados. Gere um POP primeiro. |
| O formulário voltou preenchido quando reabri | Isso é o rascunho automático funcionando. Se quiser começar do zero, apague o conteúdo manualmente. |
| Não sei se um campo é obrigatório | Todo campo com \* é obrigatório. O resto é opcional. |
| Quero só dar uma olhada no POP, sem baixar | Use o botão "Visualizar" (histórico ou painel Início). |
| Preciso de ajuda ou algo não funciona | Fale com o responsável pelo setor de tecnologia — informe o que você estava fazendo e o que apareceu na tela. |
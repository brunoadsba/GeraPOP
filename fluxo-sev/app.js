"use strict";

// SEV — Fluxo Interativo (v1, sem build)
// Lê o fluxo e os POPs como JSON estático e renderiza o diagrama clicável.
// Requer um servidor HTTP simples (fetch não funciona via file://):
//   python -m http.server 8000   (dentro da pasta fluxo-sev)

const FLUXO_ARQUIVO = document.documentElement.dataset.fluxo || "data/fluxo-desembarque.json";
const POPS_DIR = document.documentElement.dataset.pops || "data/pops";

const diagrama = document.getElementById("diagrama");
const erro = document.getElementById("erro");
const fluxoTitulo = document.getElementById("fluxo-titulo");
const fluxoId = document.getElementById("fluxo-id");
const modal = document.getElementById("modal");
const modalConteudo = document.getElementById("modal-conteudo");

const popCache = new Map();

function criarEl(tag, classe, texto) {
  const el = document.createElement(tag);
  if (classe) el.className = classe;
  if (texto !== undefined) el.textContent = texto;
  return el;
}

async function carregarJson(url) {
  const resposta = await fetch(url);
  if (!resposta.ok) {
    throw new Error(`HTTP ${resposta.status} em ${url}`);
  }
  return resposta.json();
}

async function carregarPop(popRef) {
  if (!popCache.has(popRef)) {
    popCache.set(popRef, await carregarJson(`${POPS_DIR}/${popRef}.json`));
  }
  return popCache.get(popRef);
}

function renderizarDiagrama(fluxo) {
  const etapas = new Map();
  for (const no of fluxo.nos) {
    if (!etapas.has(no.etapa)) etapas.set(no.etapa, []);
    etapas.get(no.etapa).push(no);
  }

  diagrama.replaceChildren();
  for (const [numero, nos] of etapas) {
    const coluna = criarEl("section", "etapa");
    coluna.appendChild(criarEl("h2", null, `Etapa ${numero}`));
    for (const no of nos) coluna.appendChild(criarCard(no));
    diagrama.appendChild(coluna);
  }
}

function criarCard(no) {
  const card = criarEl("button", "card" + (no.pop_ref ? "" : " card-sem-pop"));
  card.setAttribute("data-no-id", no.id);
  card.type = "button";
  card.appendChild(criarEl("strong", null, no.rotulo));
  if (no.descricao) {
    card.appendChild(criarEl("span", "card-descricao", no.descricao));
  }
  card.appendChild(
    criarEl("small", "card-badge", no.pop_ref ? "Ver POP" : "POP não gerado")
  );
  card.addEventListener("click", () => abrirNo(no));
  return card;
}

async function abrirNo(no) {
  if (!no.pop_ref) {
    mostrarSemPop(no);
    return;
  }
  try {
    mostrarPop(await carregarPop(no.pop_ref));
  } catch (e) {
    mostrarErro(`Não foi possível carregar o POP de "${no.rotulo}": ${e.message}`);
  }
}

function abrirModal() {
  modal.hidden = false;
  modalConteudo.scrollTop = 0;
}

function fecharModal() {
  modal.hidden = true;
}

function mostrarErro(mensagem) {
  modalConteudo.replaceChildren(criarEl("p", "pop-sem-pop", mensagem));
  abrirModal();
}

function mostrarSemPop(no) {
  modalConteudo.replaceChildren(
    criarEl("h2", null, no.rotulo),
    criarEl(
      "p",
      "pop-sem-pop",
      "Este nó ainda não possui um POP vinculado. Gere o POP no GeraPOP e adicione o arquivo em data/pops/ para vinculá-lo."
    )
  );
  abrirModal();
}

function mostrarPop(payload) {
  const pop = payload.pop;
  const conteudo = document.createDocumentFragment();

  const cabecalho = criarEl("div", "pop-cabecalho");
  cabecalho.appendChild(criarEl("h2", null, pop.nome_pop));
  cabecalho.appendChild(
    criarEl(
      "p",
      "pop-meta",
      `${pop.codigo} · Versão ${pop.versao} · ${pop.data} · ${pop.area}`
    )
  );
  conteudo.appendChild(cabecalho);

  if (pop.aviso) conteudo.appendChild(criarEl("p", "pop-aviso", `⚠ ${pop.aviso}`));

  conteudo.appendChild(blocoCom("Objetivo", criarEl("p", null, pop.objetivo)));
  conteudo.appendChild(blocoCom("Escopo", criarEl("p", null, pop.escopo)));

  if (pop.definicoes && pop.definicoes.length) {
    const lista = criarEl("ul");
    for (const def of pop.definicoes) {
      if (def.termo) lista.appendChild(criarEl("li", null, `${def.termo}: ${def.definicao}`));
    }
    conteudo.appendChild(blocoCom("Definições", lista));
  }

  for (const secao of pop.secoes || []) {
    const secaoEl = document.createDocumentFragment();
    const passos = criarEl("ol", "pop-passos");
    for (const passo of secao.passos || []) {
      if (passo.trim()) passos.appendChild(criarEl("li", null, passo));
    }
    secaoEl.appendChild(passos);

    const campos = (secao.campos || []).filter((item) => item.campo.trim());
    if (campos.length) {
      secaoEl.appendChild(tabelaCampos(campos));
    }
    conteudo.appendChild(blocoCom(secao.titulo || "Procedimento", secaoEl));
  }

  if (pop.regras && pop.regras.length) {
    const lista = criarEl("ul");
    for (const regra of pop.regras) {
      if (regra.trim()) lista.appendChild(criarEl("li", null, regra));
    }
    conteudo.appendChild(blocoCom("Regras e Restrições", lista));
  }

  if (pop.consulta) {
    conteudo.appendChild(blocoCom("Consulta", criarEl("p", null, pop.consulta)));
  }

  if (pop.revisoes && pop.revisoes.length) {
    const lista = criarEl("ul");
    for (const rev of pop.revisoes) {
      if (rev.revisao) {
        lista.appendChild(
          criarEl("li", null, `Rev. ${rev.revisao} (${rev.data}) — ${rev.descricao} — ${rev.responsavel}`)
        );
      }
    }
    conteudo.appendChild(blocoCom("Histórico de Revisões", lista));
  }

  modalConteudo.replaceChildren(conteudo);
  abrirModal();
}

function blocoCom(titulo, corpo) {
  const bloco = criarEl("div", "pop-bloco");
  bloco.appendChild(criarEl("h3", null, titulo));
  bloco.appendChild(corpo);
  return bloco;
}

function tabelaCampos(campos) {
  const tabela = criarEl("table", "pop-campos");
  const cabecalho = criarEl("tr");
  cabecalho.appendChild(criarEl("th", null, "Campo"));
  cabecalho.appendChild(criarEl("th", null, "Descrição / Instruções"));
  tabela.appendChild(cabecalho);
  for (const item of campos) {
    const linha = criarEl("tr");
    linha.appendChild(criarEl("td", null, item.campo));
    linha.appendChild(criarEl("td", null, item.descricao));
    tabela.appendChild(linha);
  }
  return tabela;
}

modal.querySelectorAll("[data-fechar]").forEach((el) => el.addEventListener("click", fecharModal));
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !modal.hidden) fecharModal();
});

async function iniciar() {
  try {
    const fluxo = await carregarJson(FLUXO_ARQUIVO);
    fluxoTitulo.textContent = fluxo.titulo;
    fluxoId.textContent = fluxo.fluxo_id;
    document.title = `${fluxo.titulo} — SEV`;
    renderizarDiagrama(fluxo);
  } catch (e) {
    erro.hidden = false;
    erro.textContent =
      `Não foi possível carregar o fluxo (${FLUXO_ARQUIVO}): ${e.message}. ` +
      "Se você abriu o index.html direto do navegador (file://), o fetch é bloqueado. " +
      "Rode um servidor local na pasta fluxo-sev: python -m http.server 8000 e acesse http://localhost:8000.";
  }
}

iniciar();

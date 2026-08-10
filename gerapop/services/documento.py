"""Modelo neutro do documento POP.

Descreve o conteúdo de um POP como uma lista de blocos (títulos, parágrafos,
avisos e tabelas) independente do formato de saída. Os builders de .docx e
.pdf consomem a mesma lista, garantindo numeração, ordem e conteúdo idênticos
nos dois formatos — a lógica condicional (o que entra, o que é filtrado) vive
aqui, uma única vez.
"""

from __future__ import annotations

from dataclasses import dataclass

from gerapop.constants import AVISO_PREFIX, PASSO_COL_WIDTH_CM
from gerapop.models import PopData


@dataclass(frozen=True)
class Titulo:
    numero: int
    texto: str


@dataclass(frozen=True)
class Paragrafo:
    texto: str
    bold: bool = False


@dataclass(frozen=True)
class Aviso:
    texto: str


@dataclass(frozen=True)
class Tabela:
    cabecalho: tuple[str, ...] | None
    linhas: tuple[tuple[str, ...], ...]
    # Larguras (cm) por coluna; None = preencher o restante da página (PDF).
    larguras_cm: tuple[float | None, ...] | None = None
    # Largura explícita da coluna 0 no .docx (as demais são automáticas).
    largura_col0_docx_cm: float | None = None
    # O .docx não imprime cabeçalho em algumas tabelas (ex.: passos).
    com_cabecalho_docx: bool = True
    # O .pdf destaca a primeira célula de cada linha (ex.: rótulo "R").
    primeira_celula_bold: bool = False


Bloco = Titulo | Paragrafo | Aviso | Tabela


def montar_conteudo(pop: PopData) -> list[Bloco]:
    """Blocos do documento na ordem de apresentação, com numeração automática."""
    blocos: list[Bloco] = []
    numero = 0

    def titulo(texto: str) -> None:
        nonlocal numero
        numero += 1
        blocos.append(Titulo(numero, texto))

    titulo("Objetivo")
    blocos.append(Paragrafo(pop.objetivo))

    titulo("Escopo e Pré-condições")
    blocos.append(Paragrafo(pop.escopo))
    if pop.aviso:
        blocos.append(Aviso(f"{AVISO_PREFIX}{pop.aviso}"))

    if any(item["termo"].strip() for item in pop.definicoes):
        titulo("Definições")
        linhas = tuple(
            (item["termo"], item["definicao"]) for item in pop.definicoes if item["termo"].strip()
        )
        blocos.append(Tabela(("Termo", "Definição"), linhas, larguras_cm=(4.5, None)))

    for secao in pop.secoes:
        if not secao["titulo"].strip():
            continue
        titulo(secao["titulo"])
        passos = tuple(
            (str(idx), passo) for idx, passo in enumerate(secao["passos"], start=1) if passo.strip()
        )
        blocos.append(
            Tabela(
                ("#", "Passo"),
                passos,
                larguras_cm=(PASSO_COL_WIDTH_CM, None),
                largura_col0_docx_cm=PASSO_COL_WIDTH_CM,
                com_cabecalho_docx=False,
            )
        )
        campos = tuple(
            (item["campo"], item["descricao"])
            for item in secao.get("campos", [])
            if item["campo"].strip()
        )
        if campos:
            blocos.append(Paragrafo(f"Campos obrigatórios – {secao['titulo']}:", bold=True))
            blocos.append(
                Tabela(("Campo", "Descrição / Instruções"), campos, larguras_cm=(4.5, None))
            )

    regras = tuple(regra for regra in pop.regras if regra.strip())
    if regras:
        titulo("Regras e Restrições")
        for regra in regras:
            blocos.append(
                Tabela(
                    None,
                    (("R", regra),),
                    larguras_cm=(1.5, None),
                    primeira_celula_bold=True,
                )
            )

    if pop.consulta:
        titulo("Consulta e Relatórios")
        blocos.append(Tabela(None, ((pop.consulta,),), larguras_cm=(None,)))

    titulo("Histórico de Revisões")
    revisoes = tuple(
        (rev["revisao"], rev["data"], rev["descricao"], rev["responsavel"])
        for rev in pop.revisoes
        if rev["revisao"].strip()
    )
    blocos.append(
        Tabela(
            ("Revisão", "Data", "Descrição", "Responsável"),
            revisoes,
            larguras_cm=(1.8, 2.4, None, 3.0),
        )
    )
    return blocos

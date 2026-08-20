"""Modelo neutro do documento POP.

Descreve o conteúdo de um POP como uma lista de blocos (títulos, subtítulos,
parágrafos, avisos, banners e tabelas) independente do formato de saída.
Os builders de .docx e .pdf consomem a mesma lista, garantindo numeração,
ordem e conteúdo idênticos nos dois formatos.
"""

from __future__ import annotations

from dataclasses import dataclass

from gerapop.constants import (
    AVISO_PREFIX,
    COR_RESP_CONTROLE,
    COR_RESP_PRESTADOR,
    COR_SUB,
    PASSO_COL_WIDTH_CM,
    SHADING_RESP_CONTROLE,
    SHADING_RESP_PRESTADOR,
    SHADING_SUB,
    SISTEMA_PREFIXO,
    SUB_PREFIXO,
)
from gerapop.models import PopData


@dataclass(frozen=True)
class Titulo:
    numero: int
    texto: str


@dataclass(frozen=True)
class Subtitulo:
    prefixo: str
    texto: str


@dataclass(frozen=True)
class Paragrafo:
    texto: str
    bold: bool = False


@dataclass(frozen=True)
class Aviso:
    texto: str


@dataclass(frozen=True)
class BannerResponsavel:
    texto: str
    cor_fundo: str = SHADING_RESP_PRESTADOR
    cor_texto: str = COR_RESP_PRESTADOR


@dataclass(frozen=True)
class Tabela:
    cabecalho: tuple[str, ...] | None
    linhas: tuple[tuple[str, ...], ...]
    # Larguras (cm) por coluna; None = preencher o restante da página.
    larguras_cm: tuple[float | None, ...] | None = None
    # O .docx não imprime cabeçalho em algumas tabelas específicas se False.
    com_cabecalho_docx: bool = True
    # Destaca a primeira célula de cada linha (ex.: rótulo "R", termo).
    primeira_celula_bold: bool = False
    # Estilo por linha: "" = normal, "sub" = sub-cabeçalho, "sys" = resposta do sistema
    estilos_linha: tuple[str, ...] = ()


Bloco = Titulo | Subtitulo | Paragrafo | Aviso | BannerResponsavel | Tabela


_PALAVRAS_MINUSCULAS = {
    "a",
    "as",
    "à",
    "às",
    "com",
    "da",
    "das",
    "de",
    "do",
    "dos",
    "e",
    "em",
    "na",
    "nas",
    "no",
    "nos",
    "para",
    "por",
}


def titulo_para_header(nome_pop: str) -> str:
    """Versão em título (Title Case) do nome para cabeçalho/rodapé do documento.

    O nome armazenado é em maiúsculas (ex.: "PROSPECÇÃO E FECHAMENTO COMERCIAL"),
    mas o cabeçalho/rodapé padrão CODEBA usa "Prospecção e Fechamento Comercial".
    """
    palavras = nome_pop.strip().split()
    if not palavras:
        return nome_pop
    resultado = []
    for idx, palavra in enumerate(palavras):
        if idx > 0 and palavra.lower() in _PALAVRAS_MINUSCULAS:
            resultado.append(palavra.lower())
        else:
            resultado.append(palavra[0].upper() + palavra[1:].lower())
    return " ".join(resultado)


def _obter_banner_responsavel(responsavel: str) -> BannerResponsavel:
    texto = responsavel.strip()
    if not texto.upper().startswith("RESPONSÁVEL:"):
        texto = f"RESPONSÁVEL: {texto.upper()}"
    else:
        texto = texto.upper()

    resp_upper = responsavel.upper()
    if any(k in resp_upper for k in ("PRESTADOR", "OPERADOR")):
        return BannerResponsavel(texto, SHADING_RESP_PRESTADOR, COR_RESP_PRESTADOR)
    if any(k in resp_upper for k in ("CONTROLE", "TPO", "FISCALIZAÇÃO")):
        return BannerResponsavel(texto, SHADING_RESP_CONTROLE, COR_RESP_CONTROLE)
    return BannerResponsavel(texto, SHADING_SUB, COR_SUB)


def montar_conteudo(pop: PopData) -> list[Bloco]:
    """Blocos do documento na ordem de apresentação padrão CODEBA."""
    blocos: list[Bloco] = []
    numero = 0

    def titulo(texto: str) -> None:
        nonlocal numero
        numero += 1
        blocos.append(Titulo(numero, texto))

    # 1. Objetivo
    titulo("Objetivo")
    blocos.append(Paragrafo(pop.objetivo))

    # 2. Campo de Aplicação
    campo_aplicacao = pop.campo_aplicacao or pop.escopo
    if campo_aplicacao:
        titulo("Campo de Aplicação")
        blocos.append(Paragrafo(campo_aplicacao))

    # 3. Pré-condições
    if pop.pre_condicoes:
        titulo("Pré-condições")
        blocos.append(Paragrafo(pop.pre_condicoes))

    # Aviso / Alerta em destaque
    if pop.aviso:
        aviso_txt = pop.aviso
        if not aviso_txt.startswith("■") and not aviso_txt.startswith("⚠"):
            aviso_txt = f"{AVISO_PREFIX}{aviso_txt}"
        blocos.append(Aviso(aviso_txt))

    # 4. Definições
    if any(item["termo"].strip() for item in pop.definicoes):
        titulo("Definições")
        linhas_def = tuple(
            (item["termo"], item["definicao"]) for item in pop.definicoes if item["termo"].strip()
        )
        blocos.append(
            Tabela(
                ("Termo", "Definição"),
                linhas_def,
                larguras_cm=(4.4, None),
                primeira_celula_bold=True,
            )
        )

    # 5. Matriz de Responsabilidades
    itens_tela = [
        m
        for m in pop.matriz_responsabilidades
        if m.get("tela", "").strip() or m.get("nome_tela", "").strip()
    ]
    itens_fluxo = [
        m
        for m in pop.matriz_responsabilidades
        if m.get("registro", "").strip() or m.get("atividade", "").strip()
    ]
    if itens_tela or itens_fluxo:
        titulo("Matriz de Responsabilidades")
        if itens_fluxo:
            linhas_matriz = tuple(
                (
                    m.get("etapa", ""),
                    m.get("registro", ""),
                    m.get("atividade", ""),
                    m.get("responsavel", ""),
                )
                for m in itens_fluxo
            )
            blocos.append(
                Tabela(
                    ("Etapa", "Registro", "Atividade", "Responsável"),
                    linhas_matriz,
                    larguras_cm=(1.4, 4.6, 5.6, 4.4),
                    primeira_celula_bold=True,
                )
            )
        else:
            linhas_matriz = tuple(
                (
                    m.get("tela", ""),
                    m.get("nome_tela", ""),
                    m.get("etapa", ""),
                    m.get("responsavel", ""),
                )
                for m in itens_tela
            )
            blocos.append(
                Tabela(
                    ("Tela", "Nome da Tela", "Etapa do Processo", "Responsável"),
                    linhas_matriz,
                    larguras_cm=(1.8, 4.6, 5.2, 4.4),
                    primeira_celula_bold=True,
                )
            )

    # 6. Procedimento
    secoes_validas = [s for s in pop.secoes if s["titulo"].strip()]
    if secoes_validas:
        titulo("Procedimento")
        num_procedimento = numero
        for idx, secao in enumerate(secoes_validas, start=1):
            sub_prefixo = f"{num_procedimento}.{idx}"
            # Se o título já começar com o número da subseção (ex: "6.1 Etapa..."), limpa o prefixo
            tit_secao = secao["titulo"].strip()
            if tit_secao.startswith(sub_prefixo):
                tit_limpo = tit_secao[len(sub_prefixo) :].lstrip(" .—–-")
            else:
                tit_limpo = tit_secao

            blocos.append(Subtitulo(sub_prefixo, tit_limpo))

            # Passos com responsável individual (#/Responsável/Passo)
            passos_por_responsavel = [
                (passo.strip(), resp.strip())
                for passo, resp in zip(secao.get("passos", []), secao.get("responsaveis", []))
                if passo.strip()
            ]
            if not passos_por_responsavel:
                # Banner de Responsável da seção
                if secao.get("responsavel", "").strip():
                    blocos.append(_obter_banner_responsavel(secao["responsavel"]))

                linhas_passos: list[tuple[str, str]] = []
                estilos: list[str] = []
                passo_numero = 0
                for passo in secao["passos"]:
                    texto = passo.strip()
                    if not texto:
                        continue
                    if texto.startswith(SUB_PREFIXO):
                        linhas_passos.append(("", texto))
                        estilos.append("sub")
                    elif texto.startswith(SISTEMA_PREFIXO):
                        linhas_passos.append(("—", texto))
                        estilos.append("sys")
                    else:
                        passo_numero += 1
                        linhas_passos.append((str(passo_numero), texto))
                        estilos.append("")

                if linhas_passos:
                    blocos.append(
                        Tabela(
                            ("#", "Passo"),
                            tuple(linhas_passos),
                            larguras_cm=(PASSO_COL_WIDTH_CM, None),
                            com_cabecalho_docx=True,
                            estilos_linha=tuple(estilos),
                        )
                    )
            else:
                blocos.append(
                    Tabela(
                        ("#", "Responsável", "Passo"),
                        tuple(
                            (str(num), resp, passo)
                            for num, (passo, resp) in enumerate(passos_por_responsavel, start=1)
                        ),
                        larguras_cm=(PASSO_COL_WIDTH_CM, 3.2, None),
                    )
                )

            # Campos obrigatórios da seção
            campos = tuple(
                (item["campo"], item["descricao"])
                for item in secao.get("campos", [])
                if item["campo"].strip()
            )
            if campos:
                blocos.append(Paragrafo(f"Campos obrigatórios – {tit_limpo}:", bold=True))
                blocos.append(
                    Tabela(("Campo", "Descrição / Instruções"), campos, larguras_cm=(4.5, None))
                )

    # Regras e Restrições (se houver)
    regras = tuple(regra for regra in pop.regras if regra.strip())
    if regras:
        titulo("Regras e Restrições")
        linhas_regras = tuple((f"R{idx}", regra) for idx, regra in enumerate(regras, start=1))
        blocos.append(
            Tabela(
                ("Regra", "Descrição"),
                linhas_regras,
                larguras_cm=(1.5, None),
                primeira_celula_bold=True,
            )
        )

    # Consulta e Relatórios (se houver)
    if pop.consulta:
        titulo("Consulta e Relatórios")
        blocos.append(Tabela(None, ((pop.consulta,),), larguras_cm=(None,)))

    # Registros obrigatórios (se houver)
    registros = tuple(r for r in pop.registros_obrigatorios if r.get("registro", "").strip())
    if registros:
        titulo("Registros obrigatórios")
        linhas_registros = tuple(
            (r.get("registro", ""), r.get("conteudo", ""), r.get("responsavel", ""))
            for r in registros
        )
        blocos.append(
            Tabela(
                ("Registro", "Conteúdo mínimo", "Responsável"),
                linhas_registros,
                larguras_cm=(4.4, None, 3.6),
            )
        )

    # Critérios de encerramento (se houver)
    if pop.criterios_encerramento.strip():
        titulo("Critérios de encerramento")
        blocos.append(Paragrafo(pop.criterios_encerramento))

    # Indicadores de acompanhamento (se houver)
    if pop.indicadores.strip():
        titulo("Indicadores de acompanhamento")
        blocos.append(Paragrafo(pop.indicadores))

    # Aviso final (ex.: nota de controle no encerramento do documento)
    if pop.aviso_final.strip():
        aviso_final_txt = pop.aviso_final
        if not aviso_final_txt.startswith("■") and not aviso_final_txt.startswith("⚠"):
            aviso_final_txt = f"{AVISO_PREFIX}{aviso_final_txt}"
        blocos.append(Aviso(aviso_final_txt))

    return blocos

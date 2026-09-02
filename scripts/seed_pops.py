"""Alimenta a biblioteca do GeraPOP com POP-COM-001 e POP-OPE-001 (padrão CODEBA)."""

from pathlib import Path

from gerapop.models import PopData
from gerapop.services.docx import gerar_docx
from gerapop.services.pdf import gerar_pdf
from gerapop.storage import _nome_pasta_biblioteca, get_library_dir, list_pops, save_pop

AREA_COM = "DESENVOLVIMENTO DE NEGÓCIOS"


def pop_com_001() -> PopData:
    secoes = [
        {
            "titulo": "Etapa 1 — Seleção da carga-alvo e preparação",
            "responsaveis": [
                "Comercial",
                "Comercial",
                "Comercial + Logística",
                "Gestor comercial",
            ],
            "passos": [
                "Selecionar o corredor ou produto prioritário: milho, soja, cacau, amêndoas, óxido de magnésio, concentrado de níquel, peças industrializadas ou carga geral.",
                "Definir a hipótese de valor para Ilhéus: proximidade da origem/destino, redução de custo, disponibilidade de berço, armazenagem, frequência ou alternativa a portos concorrentes.",
                "Levantar dados preliminares de origem, destino, volume anual, volume por embarque, sazonalidade, frequência, modal terrestre, embalagem e tipo de navegação.",
                "Abrir a oportunidade com identificador único e registrar data, origem do lead, produto, estimativa de volume e próximo passo.",
            ],
            "campos": [],
        },
        {
            "titulo": "Etapa 2 — Identificação e primeiro contato",
            "responsaveis": ["Comercial", "Comercial", "Comercial", "Comercial"],
            "passos": [
                "Identificar o dono da carga e o decisor: produtor, cooperativa, trading, indústria, importador, exportador ou operador logístico.",
                "Registrar razão social, segmento, pessoa de contato, cargo, telefone, e-mail, localização, origem do relacionamento e poder de decisão.",
                "Realizar contato inicial com uma mensagem objetiva: entender o corredor logístico, apresentar Ilhéus como alternativa e solicitar autorização para enviar o formulário de qualificação.",
                "Enviar o questionário de carga e agendar reunião de descoberta com o decisor e, quando possível, com logística, comércio exterior e suprimentos.",
            ],
            "campos": [],
        },
        {
            "titulo": "Etapa 3 — Qualificação da oportunidade",
            "responsaveis": ["Comercial", "Logística", "Comercial", "Gestor comercial"],
            "passos": [
                "Confirmar produto, classificação, quantidade anual, quantidade por navio/caminhão, meses de pico, origem, destino e frequência.",
                "Confirmar condição de venda, transporte até o porto, distância, modal, necessidade de transbordo, armazenagem, silo, pátio, contêiner ou carga a granel.",
                "Mapear portos concorrentes, custo atual, motivo para mudança, prazo de decisão, orçamento e critérios de escolha.",
                "Classificar a oportunidade como descartada, mapeada, qualificada, em estudo, em proposta ou em compromisso; registrar probabilidade e valor potencial.",
            ],
            "campos": [],
        },
        {
            "titulo": "Etapa 4 — Estudo de viabilidade técnico-comercial",
            "responsaveis": [
                "Comercial + CODEBA",
                "Operador portuário",
                "Armador/agente",
                "Logística",
                "Comitê comercial",
            ],
            "passos": [
                "Solicitar validação de disponibilidade de área, berço, janela, regras de acesso, programação e condições institucionais.",
                "Avaliar equipamentos, mão de obra, produtividade, recebimento, carregamento/descarregamento, segregação, armazenagem e limitações operacionais.",
                "Avaliar tipo e porte de navio, calado, janela marítima, frequência, frete, disponibilidade e condições para primeira escala.",
                "Calcular transporte terrestre, armazenagem, seguro, demurrage/detention, taxas, perdas, tempo de ciclo e custo total porta-a-porto.",
                "Emitir parecer com viabilidade, pendências, investimentos necessários, riscos, premissas e recomendação: avançar, ajustar ou encerrar.",
            ],
            "campos": [],
        },
        {
            "titulo": "Etapa 5 — Proposta comercial",
            "responsaveis": ["Comercial", "Operador + CODEBA", "Comercial", "Diretoria comercial"],
            "passos": [
                "Preparar proposta com escopo, volume, frequência, preço/tarifa, capacidade, janela, armazenagem, responsabilidades, SLA, premissas e validade.",
                "Validar tecnicamente as condições antes do envio ao cliente, evitando prometer capacidade, tarifa ou prazo sem confirmação.",
                "Apresentar a proposta ao decisor e registrar objeções, concorrentes, condições solicitadas e data do próximo compromisso.",
                "Aprovar descontos, incentivos, investimentos, exclusividade, compromissos mínimos e demais condições fora da alçada do gestor.",
            ],
            "campos": [],
        },
        {
            "titulo": "Etapa 6 — Negociação e compromisso",
            "responsaveis": [
                "Comercial + Jurídico",
                "Comercial",
                "Diretoria + Cliente",
                "Gestor comercial",
            ],
            "passos": [
                "Definir o instrumento adequado: NDA, carta de intenção, term sheet, reserva de capacidade, contrato de volume, contrato de operação ou outro documento aplicável.",
                "Conferir se o documento contém volume, prazo, preço, responsabilidades, condições de cancelamento, força maior, indicadores, primeira janela e critérios de renovação.",
                "Aprovar e assinar o compromisso, registrando a versão final e os responsáveis por cada obrigação.",
                "Alterar o status para “Compromisso” somente após receber evidência documental do aceite ou assinatura.",
            ],
            "campos": [],
        },
        {
            "titulo": "Etapa 7 — Preparação da primeira operação",
            "responsaveis": [
                "Gestor comercial",
                "Operador + Armador",
                "Cliente + Logística",
                "Comunidade portuária",
                "Gestor comercial",
            ],
            "passos": [
                "Realizar reunião de transição com cliente, CODEBA, operador, armazenador, armador, agente e transportador.",
                "Confirmar navio, janela, berço, produtividade, sequência de operação, documentos e plano de contingência.",
                "Confirmar origem da carga, transportadores, programação terrestre, documentação comercial, aduaneira e requisitos de qualidade.",
                "Executar cadastros, autorizações de acesso, recebimento, armazenagem, carregamento/descarregamento e demais controles aplicáveis.",
                "Acompanhar a primeira operação até a conclusão e registrar incidentes, custos, atrasos e desvios.",
            ],
            "campos": [],
        },
        {
            "titulo": "Etapa 8 — Encerramento e recorrência",
            "responsaveis": [
                "Gestor comercial",
                "Comercial + Operação",
                "Comercial",
                "Gestor comercial",
            ],
            "passos": [
                "Comparar o resultado real com a proposta: volume, tempo, produtividade, custo, nível de serviço e satisfação do cliente.",
                "Registrar lições aprendidas, causas de desvio, ações corretivas e responsáveis.",
                "Solicitar previsão de próximos volumes e negociar calendário recorrente.",
                "Encerrar a oportunidade como convertida somente quando houver primeira operação concluída e plano de recorrência ou renovação.",
            ],
            "campos": [],
        },
    ]

    matriz_fluxo = [
        {
            "etapa": "1",
            "registro": "Ficha de oportunidade",
            "atividade": "Criar e registrar cliente, carga e próximo compromisso",
            "responsavel": "Comercial",
        },
        {
            "etapa": "2",
            "registro": "Avaliação comercial",
            "atividade": "Avaliar viabilidade, risco, tarifa e liberação para proposta",
            "responsavel": "Comitê comercial",
        },
        {
            "etapa": "3",
            "registro": "Proposta/term sheet",
            "atividade": "Negociar condições e formalizar compromisso",
            "responsavel": "Diretoria + Jurídico",
        },
        {
            "etapa": "4",
            "registro": "Primeira operação",
            "atividade": "Programar e acompanhar a primeira carga",
            "responsavel": "Comunidade portuária",
        },
    ]

    return PopData.from_form(
        nome_pop="PROSPECÇÃO E FECHAMENTO COMERCIAL DE NOVAS CARGAS",
        codigo="POP-COM-001",
        versao="01",
        data="20/08/2026",
        area=AREA_COM,
        aviso="DOCUMENTO PROPOSTO PARA VALIDAÇÃO — não substitui normas da CODEBA, contratos, tarifas publicadas, procedimentos aduaneiros ou aprovações formais da autoridade portuária.",
        objetivo="Padronizar a prospecção, qualificação, análise, negociação e fechamento comercial de novas cargas para o Porto de Ilhéus, garantindo rastreabilidade da oportunidade, segregação de responsabilidades, validação técnica e conversão do cliente em primeira operação.",
        campo_aplicacao="Aplica-se à CODEBA, à área de desenvolvimento de negócios, à administração portuária, aos operadores portuários, terminais, armazenadores, armadores, agentes marítimos, transportadores, despachantes e demais integrantes da comunidade portuária envolvidos na atração de cargas.",
        pre_condicoes="Antes de iniciar uma oportunidade, deve existir uma carga-alvo ou corredor logístico identificável, uma pessoa ou organização potencialmente responsável pelo volume e disponibilidade de uma equipe para levantar dados comerciais e operacionais.",
        elaborado_por="Bruno Santos",
        elaborado_cargo="TPO - Fiscalização",
        aprovado_por="[a preencher]",
        aprovado_cargo="[a preencher]",
        definicoes=[
            {
                "termo": "Lead",
                "definicao": "Empresa ou contato ainda não qualificado como oportunidade.",
            },
            {
                "termo": "Oportunidade",
                "definicao": "Lead com carga, volume e hipótese de utilização do Porto de Ilhéus.",
            },
            {
                "termo": "Dono da carga",
                "definicao": "Produtor, cooperativa, trading, indústria, importador ou exportador que controla o volume ou a decisão.",
            },
            {
                "termo": "Term sheet",
                "definicao": "Documento preliminar que consolida condições comerciais antes do contrato definitivo.",
            },
            {
                "termo": "Primeira operação",
                "definicao": "Primeiro embarque ou desembarque realizado após o compromisso comercial.",
            },
        ],
        matriz_responsabilidades=matriz_fluxo,
        secoes=secoes,
        criterios_encerramento="A oportunidade deve ser encerrada como convertida somente quando o cliente tiver aceitado formalmente as condições, a capacidade operacional estiver validada, a primeira operação estiver programada e o compromisso tiver sido registrado. Deve ser encerrada como perdida quando o cliente escolher outro porto, não houver viabilidade, o volume não for confirmado ou não houver retorno após as tentativas previstas.",
        indicadores="A gestão deve acompanhar número de leads, oportunidades qualificadas, volume potencial, valor potencial, taxa de conversão, tempo entre primeiro contato e proposta, tempo entre proposta e compromisso, número de primeiras operações, custo porta-a-porto, produtividade, desvios e volume recorrente.",
        aviso_final="■ NOTA DE CONTROLE: este POP deve ser validado e aprovado pela organização responsável antes de ser utilizado como documento oficial. Dados de clientes e volumes devem ser reais, autorizados e rastreáveis.",
        registros_obrigatorios=[
            {
                "registro": "Ficha de oportunidade",
                "conteudo": "Cliente, produto, origem, destino, volume, decisor e próximo passo",
                "responsavel": "Comercial",
            },
            {
                "registro": "Estudo de viabilidade",
                "conteudo": "Premissas, custos, capacidade, riscos, parecer e aprovação",
                "responsavel": "Comitê comercial",
            },
            {
                "registro": "Proposta comercial",
                "conteudo": "Preço, escopo, prazo, SLA, responsabilidades e validade",
                "responsavel": "Diretoria comercial",
            },
            {
                "registro": "Compromisso",
                "conteudo": "NDA, term sheet, carta ou contrato assinado",
                "responsavel": "Jurídico/Diretoria",
            },
            {
                "registro": "Relatório da primeira operação",
                "conteudo": "Resultado, desvios, indicadores e ações corretivas",
                "responsavel": "Operação + Comercial",
            },
        ],
        revisoes=[
            {
                "revisao": "01",
                "data": "19/08/2026",
                "descricao": "Emissão inicial. Documento proposto para padronizar prospecção e fechamento comercial de novas cargas para o Porto de Ilhéus.",
                "responsavel": "Bruno Santos",
            }
        ],
    )


def pop_ope_001() -> PopData:
    passos_etapa1 = [
        "Acessar o sistema OpenPort através do link: https://openportilheus.codeba.gov.br/openportcodeba/",
        "Inserir Login e Senha.",
        "Clicar no campo de pesquisa localizado no lado superior esquerdo da tela.",
        "Digitar o número 6002, correspondente à tela de Programação de Saída, e clicar na opção correspondente.",
        "Clicar no botão Novo, preencher todos os campos obrigatórios (campos amarelos) e clicar no botão Gravar.",
        "Clicar no botão verde + (localizado abaixo de Mercadorias).",
        "Na tela que abrir, clicar no botão Filtrar.",
        "Selecionar o checkbox do(s) respectivo(s) produto(s).",
        "Com o checkbox selecionado, clicar no botão Adicionar e, em seguida, no botão Sair.",
        "Anotar o número da Programação de Saída gerado e comunicar ao TPO Controle para avaliação e liberação.",
    ]
    passos_etapa2 = [
        "Receber do Operador Portuário o número da Programação de Saída a ser avaliada.",
        "Acessar o sistema OpenPort através do link: https://openportilheus.codeba.gov.br/openportcodeba/",
        "Inserir Login e Senha.",
        "Clicar no campo de pesquisa localizado no lado superior esquerdo da tela.",
        "Digitar o número 6007, correspondente à tela de Avaliar Programação de Saída, e clicar na opção correspondente.",
        "No campo Prog. Saída, digitar o número da programação de saída e clicar no botão Filtrar.",
        "Clicar no botão localizado à esquerda do número da programação de saída.",
        "Na janela que abrir, clicar no botão Liberar. Na mensagem “Deseja liberar a programação de saída?”, clicar em Ok.",
        "Na mensagem “Programação de Saída liberada com sucesso!”, clicar em Ok.",
        "Informar ao Operador Portuário que a Programação de Saída foi liberada.",
    ]

    return PopData.from_form(
        nome_pop="PROGRAMAÇÃO DE SAÍDA",
        codigo="POP-OPE-001",
        versao="02",
        data="19/08/2026",
        area="OPERAÇÕES PORTUÁRIAS",
        aviso="POP EM FASE DE AJUSTES — versão 02 em validação de campo.",
        objetivo="Padronizar o processo de PROGRAMAÇÃO DE SAÍDA dentro do sistema OpenPort, com responsabilidades segregadas por etapa entre o Operador Portuário e o TPO Controle.",
        campo_aplicacao="TPO Controle / Fiéis / Operadores Portuários.",
        pre_condicoes="Este POP é executado em duas etapas com responsáveis distintos — ver Matriz de Responsabilidades (seção 5).",
        elaborado_por="Bruno Santos",
        elaborado_cargo="TPO - Fiscalização",
        aprovado_por="[a preencher]",
        aprovado_cargo="[a preencher]",
        definicoes=[
            {"termo": "OpenPort", "definicao": "Sistema usado pela CODEBA"},
            {"termo": "PS", "definicao": "Programação de Saída"},
            {"termo": "Prestador", "definicao": "Operador Portuário"},
        ],
        matriz_responsabilidades=[
            {
                "tela": "6002",
                "nome_tela": "Programação de Saída",
                "etapa": "Criação e registro da PS",
                "responsavel": "Operador Portuário (Prestador)",
            },
            {
                "tela": "6007",
                "nome_tela": "Avaliar Programação de Saída",
                "etapa": "Avaliação e liberação da PS",
                "responsavel": "TPO Controle",
            },
        ],
        secoes=[
            {
                "titulo": "Etapa 1 — Criação da Programação de Saída (Tela 6002)",
                "responsavel": "OPERADOR PORTUÁRIO (PRESTADOR)",
                "passos": passos_etapa1,
                "campos": [],
            },
            {
                "titulo": "Etapa 2 — Avaliação e Liberação da Programação de Saída (Tela 6007)",
                "responsavel": "TPO CONTROLE",
                "passos": passos_etapa2,
                "campos": [],
            },
        ],
        revisoes=[
            {
                "revisao": "01",
                "data": "18/08/2026",
                "descricao": "Emissão inicial.",
                "responsavel": "Bruno Santos",
            },
            {
                "revisao": "02",
                "data": "19/08/2026",
                "descricao": "Segregação de responsabilidades por tela: Tela 6002 (Operador Portuário) e Tela 6007 (TPO Controle); inclusão da etapa de comunicação entre os responsáveis.",
                "responsavel": "Bruno Santos",
            },
        ],
    )


def pop_ope_002() -> PopData:
    return PopData.from_form(
        nome_pop="ANÚNCIO DE NAVIO",
        codigo="POP-OPE-002",
        versao="03",
        data="26/08/2026",
        area="OPERAÇÕES PORTUÁRIAS",
        aviso="",
        objetivo="Padronizar o processo de ANÚNCIO DE NAVIO dentro do sistema OpenPort através da Tela 2003, estabelecendo a sequência correta de preenchimento das seções Dados, Calado e Mercadorias.",
        campo_aplicacao="Agências Marítimas.",
        pre_condicoes="Este POP é executado em etapa única — ver Matriz de Responsabilidades (seção 5).",
        elaborado_por="Bruno Santos",
        elaborado_cargo="TPO - Fiscalização",
        aprovado_por="Nazaro Firme",
        aprovado_cargo="[a preencher]",
        definicoes=[
            {"termo": "OpenPort", "definicao": "Sistema usado pela CODEBA"},
            {"termo": "Anúncio de Navio", "definicao": "Registro da escala do navio no sistema"},
        ],
        matriz_responsabilidades=[
            {
                "tela": "2003",
                "nome_tela": "Anúncio de Navio",
                "etapa": "Criação do anúncio",
                "responsavel": "Agência Marítima",
            }
        ],
        secoes=[
            {
                "titulo": "Etapa 1 — Criação do Anúncio de Navio (Tela 2003)",
                "responsavel": "AGÊNCIA MARÍTIMA",
                "passos": [
                    "Acessar a Tela 2003 no OpenPort",
                    "Preencher seção Dados do navio",
                    "Preencher seção Calado",
                    "Preencher seção Mercadorias",
                    "Gravar e confirmar anúncio",
                ],
                "campos": [],
            }
        ],
        revisoes=[
            {"revisao": "01", "data": "19/08/2026", "descricao": "Emissão inicial", "responsavel": "Bruno Santos"},
            {"revisao": "02", "data": "21/08/2026", "descricao": "Ajustes e aprimoramentos", "responsavel": "Nazaro Firme"},
            {"revisao": "03", "data": "26/08/2026", "descricao": "Versão oficial em validação", "responsavel": "Bruno Santos"},
        ],
    )


def _pop_id_existente(codigo: str) -> str | None:
    for record in list_pops():
        if record["codigo"] == codigo:
            return record["id"]
    return None


def _bytes_da_biblioteca(pop: PopData, ext: str) -> bytes | None:
    lib_dir = get_library_dir() / _nome_pasta_biblioteca(pop)
    candidate = lib_dir / f"{lib_dir.name}{ext}"
    if candidate.is_file():
        return candidate.read_bytes()
    # varre por código caso nome tenha mudado
    if lib_dir.parent.exists():
        for entry in lib_dir.parent.iterdir():
            if entry.is_dir() and entry.name.startswith(pop.codigo + "_"):
                alt = entry / f"{entry.name}{ext}"
                if alt.is_file():
                    return alt.read_bytes()
    return None


def main() -> None:
    for pop in (pop_com_001(), pop_ope_001(), pop_ope_002()):
        erros = pop.validate()
        if erros:
            raise SystemExit(f"Validação falhou: {erros}")
        docx_bytes = _bytes_da_biblioteca(pop, ".docx") or gerar_docx(pop).getvalue()
        pdf_bytes = _bytes_da_biblioteca(pop, ".pdf") or gerar_pdf(pop).getvalue()
        novo_id = save_pop(
            pop,
            docx_bytes,
            pop_id=_pop_id_existente(pop.codigo),
            pdf=pdf_bytes,
        )
        origem = "biblioteca" if _bytes_da_biblioteca(pop, ".docx") else "gerado"
        print(f"Salvo {pop.codigo} ({pop.nome_pop}) -> {novo_id} [{origem} {len(docx_bytes)} docx / {len(pdf_bytes)} pdf]")

    print("\nBiblioteca atual:")
    for record in list_pops():
        print(
            f"  {record['id']} | {record['codigo']} | {record['nome_pop']} | {record['created_at']}"
        )


if __name__ == "__main__":
    main()

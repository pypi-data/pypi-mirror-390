"""Este módulo guarda todas as funções do MCP visíveis para o Agente usar"""

from os import getenv
from typing import Literal, Sequence
import aiohttp
import ujson
from siga_mcp._types import (
    CategoriasInfraestruturaType,
    EquipeInfraestruturaType,
    EquipeSistemasType,
    FiltrosOSType,
    OrigemAtendimentoAvulsoSistemasType,
    ProjetoType,
    SistemasType,
    TipoAtendimentoAvulsoInfraestruturaType,
    TipoOsSistemasType,
    LinguagemOsSistemasType,
    OrigemOsSistemasType,
    OsInternaSistemasType,
    StatusOsType,
    CriticidadeOsType,
    PrioridadeUsuarioOsType,
)
from siga_mcp.dynamic_constants import (
    CATEGORIA_TO_NUMBER,
    EQUIPE_INFRAESTRUTURA_TO_NUMBER,
    EQUIPE_TO_NUMBER,
    PROJETO_TO_NUMBER,
    SISTEMA_TO_NUMBER,
    TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA,
    TIPO_TO_NUMBER_OS_SISTEMAS,
    LINGUAGEM_TO_NUMBER_OS_SISTEMAS,
    ORIGEM_OS_TO_NUMBER,
    OS_INTERNA_OS_TO_NUMBER,
    STATUS_OS_TO_NUMBER,
    CRITICIDADE_OS_TO_NUMBER,
    PRIORIDADE_USUARIO_OS_TO_NUMBER,
)
from siga_mcp.dynamic_constants import (
    USUARIOS_SISTEMAS_IDS,
    USUARIOS_INFRAESTRUTURA_IDS,
    USUARIOS_SISTEMAS_PARA_ERRO,
    USUARIOS_INFRAESTRUTURA_PARA_ERRO,
)
from siga_mcp.decorators import controlar_acesso_matricula
from siga_mcp.utils import converter_data_siga, normalizar_parametro
from siga_mcp.xml_builder import XMLBuilder


async def buscar_todas_os_usuario(
    *,
    matricula: str | Sequence[str] | Literal["CURRENT_USER"] | None = "CURRENT_USER",
    os: str | Sequence[str] | None = None,
    filtrar_por: Sequence[FiltrosOSType]
    | Literal["Todas OS em Aberto"]
    | str
    | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> str:
    if not matricula and not os:
        return "Erro: É necessário informar pelo menos a matrícula ou o código da OS para realizar a consulta."

    if filtrar_por == "Todas OS em Aberto":
        filtrar_por = [
            "Pendente-Atendimento",
            "Em Teste",
            "Pendente-Teste",
            "Em Atendimento",
            "Em Implantação",
            "Pendente-Liberação",
            "Não Planejada",
            "Pendente-Sist. Administrativos",
            "Pendente-AVA",
            "Pendente-Consultoria",
            "Solicitação em Aprovação",
            "Pendente-Aprovação",
            "Pendente-Sist. Acadêmicos",
            "Pendente-Marketing",
            "Pendente-Equipe Manutenção",
            "Pendente-Equipe Infraestrutura",
            "Pendente-Atualização de Versão",
            "Pendente-Help-Desk",
            "Pendente-Fornecedor",
            "Pendente-Usuário",
        ]

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/os/buscarTodasOsPorMatriculaSigaIA/",
            json={
                "descricaoStatusOs": filtrar_por or "",  # Array ou string puro
                "matricula": matricula or "",  # Array ou string puro
                "codOs": os or "",  # Array ou string puro
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                # Verifica se a requisição HTTP foi bem-sucedida (status 2xx)
                # response.raise_for_status()

                data = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=data["result"],
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={"matricula": str(matricula)},
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception as e:
                # Captura qualquer outro erro não previsto
                return f"Erro ao consultar dados da(s) OS. {e} Matrícula: {matricula}"


@controlar_acesso_matricula
async def inserir_os_sistemas(
    data_solicitacao: str,
    assunto: str,
    descricao: str,
    responsavel: str | Literal["CURRENT_USER"],
    responsavel_atual: str | Literal["CURRENT_USER"],
    matSolicitante: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    criada_por: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    prioridade: str | None = None,
    tempo_previsto: int | None = None,
    data_inicio_previsto: str | None = None,
    data_limite: str | None = None,
    sprint: str | None = None,
    os_predecessora: str | None = None,
    chamado_fornecedor: str | None = None,
    os_principal: str | None = None,
    rotinas: str | None = None,
    classificacao: str | None = None,
    nova: str | None = None,
    data_previsao_entrega: str | None = None,
    modulo: str | None = None,
    tempo_restante: str | None = None,
    ramal: str | None = None,
    data_envio_email_conclusao: str | None = None,
    tipo_transacao: str | None = None,
    acao: str | None = None,
    planejamento: str | None = None,
    grupo: str | None = None,
    sistema: SistemasType = "Sistemas AVA",
    tipo: TipoOsSistemasType = "Implementação",
    equipe: EquipeSistemasType = "Equipe AVA",
    linguagem: LinguagemOsSistemasType = "PHP",
    projeto: ProjetoType = "Operação AVA",
    status: StatusOsType = "Em Atendimento",
    os_interna: OsInternaSistemasType = "Sim",
    origem: OrigemOsSistemasType = "Teams",
    prioridade_usuario: PrioridadeUsuarioOsType = "Nenhuma",
    criticidade: CriticidadeOsType = "Nenhuma",
) -> str:
    if data_solicitacao:
        data_solicitacao = converter_data_siga(data_solicitacao, manter_horas=True)

    if data_inicio_previsto:
        data_inicio_previsto = converter_data_siga(
            data_inicio_previsto, manter_horas=True
        )

    if data_limite:
        data_limite = converter_data_siga(data_limite, manter_horas=True)

    if data_previsao_entrega:
        data_previsao_entrega = converter_data_siga(
            data_previsao_entrega, manter_horas=True
        )

    if data_envio_email_conclusao:
        data_envio_email_conclusao = converter_data_siga(
            data_envio_email_conclusao, manter_horas=True
        )

    # VALIDAÇÃO DOS CAMPOS OBRIGATÓRIOS
    # Validar matSolicitante
    if (
        not matSolicitante
        or matSolicitante == "0"
        or (matSolicitante != "CURRENT_USER" and not matSolicitante.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "mat_solicitante_obrigatorio",
                    "campo_invalido": "matSolicitante",
                    "valor_informado": str(matSolicitante),
                    "mensagem": f"Campo 'matSolicitante' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {matSolicitante}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
            custom_attributes={"sistema": "SIGA"},
        )

    # Validar criada_por
    if (
        not criada_por
        or criada_por == "0"
        or (criada_por != "CURRENT_USER" and not criada_por.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "criada_por_obrigatorio",
                    "campo_invalido": "criada_por",
                    "valor_informado": str(criada_por),
                    "mensagem": f"Campo 'criada_por' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {criada_por}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
            custom_attributes={"sistema": "SIGA"},
        )

    # VALIDAÇÃO DE USUÁRIOS RESPONSÁVEIS
    # Validar responsavel (se não for CURRENT_USER)
    if responsavel != "CURRENT_USER" and responsavel not in USUARIOS_SISTEMAS_IDS:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "responsavel_invalido",
                    "responsavel_informado": responsavel,
                    "mensagem": f"Responsável '{responsavel}' não encontrado na lista de usuários válidos para Sistemas",
                    "usuarios_validos": USUARIOS_SISTEMAS_PARA_ERRO,
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
            custom_attributes={"sistema": "SIGA"},
        )

    # Validar responsavel_atual (se não for CURRENT_USER)
    if (
        responsavel_atual != "CURRENT_USER"
        and responsavel_atual not in USUARIOS_SISTEMAS_IDS
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "responsavel_atual_invalido",
                    "responsavel_atual_informado": responsavel_atual,
                    "mensagem": f"Responsável atual '{responsavel_atual}' não encontrado na lista de usuários válidos para Sistemas",
                    "usuarios_validos": USUARIOS_SISTEMAS_PARA_ERRO,
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
            custom_attributes={"sistema": "SIGA"},
        )

    # NORMALIZANDO PARAMETROS
    # Normaliza parâmetro TIPO (case-insensitive) e valida se existe na constante
    tipo_final, erro_xml = normalizar_parametro(
        tipo,
        TIPO_TO_NUMBER_OS_SISTEMAS,
        data=[
            {
                "status": "erro",
                "tipo_erro": "tipo_invalido",
                "tipo_informado": tipo,
                "mensagem": f"Tipo '{tipo}' não encontrado na constante TIPO_TO_NUMBER_OS_SISTEMAS",
                "tipos_validos": list(TIPO_TO_NUMBER_OS_SISTEMAS.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro SISTEMA (case-insensitive) e valida se existe na constante
    sistema_final, erro_xml = normalizar_parametro(
        sistema,
        SISTEMA_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "sistema_invalido",
                "sistema_informado": sistema,
                "mensagem": f"Sistema '{sistema}' não encontrado na constante SISTEMA_TO_NUMBER",
                "sistemas_validos": list(SISTEMA_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se sistema inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro EQUIPE (case-insensitive) e valida se existe na constante
    equipe_final, erro_xml = normalizar_parametro(
        equipe,
        EQUIPE_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "equipe_invalida",
                "equipe_informada": equipe,
                "mensagem": f"Equipe '{equipe}' não encontrada na constante EQUIPE_TO_NUMBER",
                "equipes_validas": list(EQUIPE_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se equipe inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro PROJETO (case-insensitive) e valida se existe na constante
    projeto_final, erro_xml = normalizar_parametro(
        projeto,
        PROJETO_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "projeto_invalido",
                "projeto_informado": projeto,
                "mensagem": f"Projeto '{projeto}' não encontrado na constante PROJETO_TO_NUMBER",
                "projetos_validos": list(PROJETO_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se projeto inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro LINGUAGEM (case-insensitive) e valida se existe na constante
    linguagem_final, erro_xml = normalizar_parametro(
        linguagem,
        LINGUAGEM_TO_NUMBER_OS_SISTEMAS,
        data=[
            {
                "status": "erro",
                "tipo_erro": "linguagem_invalida",
                "linguagem_informada": linguagem,
                "mensagem": f"Linguagem '{linguagem}' não encontrada na constante LINGUAGEM_TO_NUMBER_OS_SISTEMAS",
                "linguagens_validas": list(LINGUAGEM_TO_NUMBER_OS_SISTEMAS.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se linguagem inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro STATUS (case-insensitive) e valida se existe na constante
    status_final, erro_xml = normalizar_parametro(
        status,
        STATUS_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "status_invalido",
                "status_informado": status,
                "mensagem": f"Status '{status}' não encontrado na constante STATUS_OS_TO_NUMBER",
                "status_validos": list(STATUS_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se status inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro ORIGEM (case-insensitive) e valida se existe na constante
    origem_final, erro_xml = normalizar_parametro(
        origem,
        ORIGEM_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "origem_invalida",
                "origem_informada": origem,
                "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_OS_TO_NUMBER",
                "origens_validas": list(ORIGEM_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se origem inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro OS_INTERNA (case-insensitive) e valida se existe na constante
    os_interna_final, erro_xml = normalizar_parametro(
        os_interna,
        OS_INTERNA_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "os_interna_invalida",
                "os_interna_informada": os_interna,
                "mensagem": f"OS Interna '{os_interna}' não encontrada na constante OS_INTERNA_OS_TO_NUMBER",
                "valores_validos": list(OS_INTERNA_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se os_interna inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro CRITICIDADE (case-insensitive) e valida se existe na constante
    criticidade_final, erro_xml = normalizar_parametro(
        criticidade,
        CRITICIDADE_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "criticidade_invalida",
                "criticidade_informada": criticidade,
                "mensagem": f"Criticidade '{criticidade}' não encontrada na constante CRITICIDADE_OS_TO_NUMBER",
                "criticidades_validas": list(CRITICIDADE_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se criticidade inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro PRIORIDADE_USUARIO (case-insensitive) e valida se existe na constante
    prioridade_usuario_final, erro_xml = normalizar_parametro(
        prioridade_usuario,
        PRIORIDADE_USUARIO_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "prioridade_usuario_invalida",
                "prioridade_usuario_informada": prioridade_usuario,
                "mensagem": f"Prioridade do usuário '{prioridade_usuario}' não encontrada na constante PRIORIDADE_USUARIO_OS_TO_NUMBER",
                "prioridades_validas": list(PRIORIDADE_USUARIO_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se prioridade_usuario inválida, retorna erro e para execução
        return erro_xml

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/os/inserirOsSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "dtSolicitacao": data_solicitacao,
                    "assunto": assunto,
                    "descricao": descricao,
                    "matSolicitante": matSolicitante,
                    "nmSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "origem": origem_final,
                    "tipo": tipo_final,
                    "status": status_final,
                    "equipe": equipe_final,
                    "responsavel": responsavel,
                    "responsavelAtual": responsavel_atual,
                    "matGestor": "",
                    "criadaPor": criada_por,
                    "classe": 1,
                    "osInterna": os_interna_final,
                    "campus": "",
                    "sistema": sistema_final or "",
                    "linguagem": linguagem_final or "",
                    "categoria": "",
                    "projeto": projeto_final or "",
                    "prioridade": prioridade or "",
                    "tempo_previsto": tempo_previsto or "",
                    "dtInicioPrevisto": data_inicio_previsto or "",
                    "dtLimite": data_limite or "",
                    "sprint": sprint or "",
                    "dtConclusao": "",
                    "osPredecessora": os_predecessora or "",
                    "chamadoFornecedor": chamado_fornecedor or "",
                    "osPrincipal": os_principal or "",
                    "rotinas": rotinas or "",
                    "plaqueta": "",
                    "classificacao": classificacao or "",
                    "criticidade": criticidade_final or "",
                    "nova": nova or "",
                    "dtPrevisaoEntrega": data_previsao_entrega or "",
                    "prioridadeUsuario": prioridade_usuario_final or "",
                    "modulo": modulo or "",
                    "tempoRestante": tempo_restante or "",
                    "ramal": ramal or "",
                    "dtEnvioEmailConclusao": data_envio_email_conclusao or "",
                    "tipoTransacao": tipo_transacao or "",
                    "acao": acao or "",
                    "planejamento": planejamento or "",
                    "grupo": grupo or "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar a OS. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "OS cadastrado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar a OS. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "dtSolicitacao": str(data_solicitacao),
                        "assunto": str(assunto),
                        "descricao": str(descricao),
                        "matSolicitante": str(matSolicitante),
                        "origem": str(origem_final),
                        "tipo": str(tipo_final),
                        "status": str(status_final),
                        "equipe": str(equipe_final),
                        "responsavel": str(responsavel),
                        "responsavelAtual": str(responsavel_atual),
                        "criadaPor": str(criada_por),
                        "osInterna": str(os_interna_final),
                        "sistema": str(sistema_final),
                        "linguagem": str(linguagem_final),
                        "projeto": str(projeto_final),
                        "prioridade": str(prioridade),
                        "tempo_previsto": str(tempo_previsto),
                        "dtInicioPrevisto": str(data_inicio_previsto),
                        "dtLimite": str(data_limite),
                        "sprint": str(sprint),
                        "osPredecessora": str(os_predecessora),
                        "chamadoFornecedor": str(chamado_fornecedor),
                        "osPrincipal": str(os_principal),
                        "rotinas": str(rotinas),
                        "classificacao": str(classificacao),
                        "criticidade": str(criticidade_final),
                        "nova": str(nova),
                        "dtPrevisaoEntrega": str(data_previsao_entrega),
                        "prioridadeUsuario": str(prioridade_usuario_final),
                        "modulo": str(modulo),
                        "tempoRestante": str(tempo_restante),
                        "ramal": str(ramal),
                        "dtEnvioEmailConclusao": str(data_envio_email_conclusao),
                        "tipoTransacao": str(tipo_transacao),
                        "acao": str(acao),
                        "planejamento": str(planejamento),
                        "grupo": str(grupo),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


@controlar_acesso_matricula
async def inserir_os_infraestrutura(
    data_solicitacao: str,
    assunto: str,
    descricao: str,
    responsavel: str | Literal["CURRENT_USER"],
    responsavel_atual: str | Literal["CURRENT_USER"],
    matSolicitante: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    criada_por: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    prioridade: str | None = None,
    tempo_previsto: int | None = None,
    data_inicio_previsto: str | None = None,
    data_limite: str | None = None,
    sprint: str | None = None,
    os_predecessora: str | None = None,
    chamado_fornecedor: str | None = None,
    os_principal: str | None = None,
    plaqueta: str | None = None,
    rotinas: str | None = None,
    classificacao: str | None = None,
    nova: str | None = None,
    data_previsao_entrega: str | None = None,
    modulo: str | None = None,
    tempo_restante: str | None = None,
    ramal: str | None = None,
    data_envio_email_conclusao: str | None = None,
    tipo_transacao: str | None = None,
    acao: str | None = None,
    planejamento: str | None = None,
    grupo: str | None = None,
    equipe: EquipeInfraestruturaType = "Help-Desk - Aeroporto",
    tipo: TipoAtendimentoAvulsoInfraestruturaType = "Suporte",
    categoria: CategoriasInfraestruturaType = "AD - Suporte/Dúvidas/Outros",
    projeto: ProjetoType = "Operação Help Desk",
    os_interna: OsInternaSistemasType = "Sim",
    origem: OrigemAtendimentoAvulsoSistemasType = "E-mail",
    status: StatusOsType = "Em Atendimento",
    prioridade_usuario: PrioridadeUsuarioOsType = "Nenhuma",
    criticidade: CriticidadeOsType = "Nenhuma",
) -> str:
    if data_solicitacao:
        data_solicitacao = converter_data_siga(data_solicitacao, manter_horas=True)

    if data_inicio_previsto:
        data_inicio_previsto = converter_data_siga(
            data_inicio_previsto, manter_horas=True
        )

    if data_limite:
        data_limite = converter_data_siga(data_limite, manter_horas=True)

    if data_previsao_entrega:
        data_previsao_entrega = converter_data_siga(
            data_previsao_entrega, manter_horas=True
        )

    if data_envio_email_conclusao:
        data_envio_email_conclusao = converter_data_siga(
            data_envio_email_conclusao, manter_horas=True
        )

    # VALIDAÇÃO DOS CAMPOS OBRIGATÓRIOS
    # Validar matSolicitante
    if (
        not matSolicitante
        or matSolicitante == "0"
        or (matSolicitante != "CURRENT_USER" and not matSolicitante.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "mat_solicitante_obrigatorio",
                    "campo_invalido": "matSolicitante",
                    "valor_informado": str(matSolicitante),
                    "mensagem": f"Campo 'matSolicitante' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {matSolicitante}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
            custom_attributes={"sistema": "SIGA"},
        )

    # Validar criada_por
    if (
        not criada_por
        or criada_por == "0"
        or (criada_por != "CURRENT_USER" and not criada_por.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "criada_por_obrigatorio",
                    "campo_invalido": "criada_por",
                    "valor_informado": str(criada_por),
                    "mensagem": f"Campo 'criada_por' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {criada_por}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
            custom_attributes={"sistema": "SIGA"},
        )

    # VALIDAÇÃO DE USUÁRIOS RESPONSÁVEIS
    # Validar responsavel (se não for CURRENT_USER)
    if responsavel != "CURRENT_USER" and responsavel not in USUARIOS_INFRAESTRUTURA_IDS:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "responsavel_invalido",
                    "responsavel_informado": responsavel,
                    "mensagem": f"Responsável '{responsavel}' não encontrado na lista de usuários válidos para Infraestrutura",
                    "usuarios_validos": USUARIOS_INFRAESTRUTURA_PARA_ERRO,
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
            custom_attributes={"sistema": "SIGA"},
        )

    # Validar responsavel_atual (se não for CURRENT_USER)
    if (
        responsavel_atual != "CURRENT_USER"
        and responsavel_atual not in USUARIOS_INFRAESTRUTURA_IDS
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "responsavel_atual_invalido",
                    "responsavel_atual_informado": responsavel_atual,
                    "mensagem": f"Responsável atual '{responsavel_atual}' não encontrado na lista de usuários válidos para Infraestrutura",
                    "usuarios_validos": USUARIOS_INFRAESTRUTURA_PARA_ERRO,
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
            custom_attributes={"sistema": "SIGA"},
        )

    # NORMALIZANDO PARAMETROS
    # Normaliza parâmetro TIPO (case-insensitive) e valida se existe na constante
    tipo_final, erro_xml = normalizar_parametro(
        tipo,
        TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA,
        data=[
            {
                "status": "erro",
                "tipo_erro": "tipo_invalido",
                "tipo_informado": tipo,
                "mensagem": f"Tipo '{tipo}' não encontrado na constante TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA",
                "tipos_validos": list(
                    TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA.keys()
                ),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro CATEGORIA (case-insensitive) e valida se existe na constante
    categoria_final, erro_xml = normalizar_parametro(
        categoria,
        CATEGORIA_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "categoria_invalida",
                "categoria_informada": categoria,
                "mensagem": f"Categoria '{categoria}' não encontrada na constante CATEGORIA_TO_NUMBER",
                "categorias_validas": list(CATEGORIA_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se categoria inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro EQUIPE (case-insensitive) e valida se existe na constante
    equipe_final, erro_xml = normalizar_parametro(
        equipe,
        EQUIPE_INFRAESTRUTURA_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "equipe_invalida",
                "equipe_informada": equipe,
                "mensagem": f"Equipe '{equipe}' não encontrada na constante EQUIPE_INFRAESTRUTURA_TO_NUMBER",
                "equipes_validas": list(EQUIPE_INFRAESTRUTURA_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se equipe inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro PROJETO (case-insensitive) e valida se existe na constante
    projeto_final, erro_xml = normalizar_parametro(
        projeto,
        PROJETO_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "projeto_invalido",
                "projeto_informado": projeto,
                "mensagem": f"Projeto '{projeto}' não encontrado na constante PROJETO_TO_NUMBER",
                "projetos_validos": list(PROJETO_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se projeto inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro STATUS (case-insensitive) e valida se existe na constante
    status_final, erro_xml = normalizar_parametro(
        status,
        STATUS_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "status_invalido",
                "status_informado": status,
                "mensagem": f"Status '{status}' não encontrado na constante STATUS_OS_TO_NUMBER",
                "status_validos": list(STATUS_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se status inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro ORIGEM (case-insensitive) e valida se existe na constante
    origem_final, erro_xml = normalizar_parametro(
        origem,
        ORIGEM_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "origem_invalida",
                "origem_informada": origem,
                "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_OS_TO_NUMBER",
                "origens_validas": list(ORIGEM_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se origem inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro OS_INTERNA (case-insensitive) e valida se existe na constante
    os_interna_final, erro_xml = normalizar_parametro(
        os_interna,
        OS_INTERNA_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "os_interna_invalida",
                "os_interna_informada": os_interna,
                "mensagem": f"OS Interna '{os_interna}' não encontrada na constante OS_INTERNA_OS_TO_NUMBER",
                "valores_validos": list(OS_INTERNA_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se os_interna inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro CRITICIDADE (case-insensitive) e valida se existe na constante
    criticidade_final, erro_xml = normalizar_parametro(
        criticidade,
        CRITICIDADE_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "criticidade_invalida",
                "criticidade_informada": criticidade,
                "mensagem": f"Criticidade '{criticidade}' não encontrada na constante CRITICIDADE_OS_TO_NUMBER",
                "criticidades_validas": list(CRITICIDADE_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se criticidade inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro PRIORIDADE_USUARIO (case-insensitive) e valida se existe na constante
    prioridade_usuario_final, erro_xml = normalizar_parametro(
        prioridade_usuario,
        PRIORIDADE_USUARIO_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "prioridade_usuario_invalida",
                "prioridade_usuario_informada": prioridade_usuario,
                "mensagem": f"Prioridade do usuário '{prioridade_usuario}' não encontrada na constante PRIORIDADE_USUARIO_OS_TO_NUMBER",
                "prioridades_validas": list(PRIORIDADE_USUARIO_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se prioridade_usuario inválida, retorna erro e para execução
        return erro_xml

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/os/inserirOsSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "dtSolicitacao": data_solicitacao,
                    "assunto": assunto,
                    "descricao": descricao,
                    "matSolicitante": matSolicitante,
                    "nmSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "origem": origem_final,
                    "tipo": tipo_final,
                    "status": status_final,
                    "equipe": equipe_final,
                    "responsavel": responsavel,
                    "responsavelAtual": responsavel_atual,
                    "matGestor": "",
                    "criadaPor": criada_por,
                    "classe": 2,
                    "osInterna": os_interna_final,
                    "campus": "",
                    "sistema": "",
                    "linguagem": "",
                    "categoria": categoria_final or "",
                    "projeto": projeto_final or "",
                    "prioridade": prioridade or "",
                    "tempo_previsto": tempo_previsto or "",
                    "dtInicioPrevisto": data_inicio_previsto or "",
                    "dtLimite": data_limite or "",
                    "sprint": sprint or "",
                    "dtConclusao": "",
                    "osPredecessora": os_predecessora or "",
                    "chamadoFornecedor": chamado_fornecedor or "",
                    "osPrincipal": os_principal or "",
                    "rotinas": rotinas or "",
                    "plaqueta": plaqueta or "",
                    "classificacao": classificacao or "",
                    "criticidade": criticidade_final or "",
                    "nova": nova or "",
                    "dtPrevisaoEntrega": data_previsao_entrega or "",
                    "prioridadeUsuario": prioridade_usuario_final or "",
                    "modulo": modulo or "",
                    "tempoRestante": tempo_restante or "",
                    "ramal": ramal or "",
                    "dtEnvioEmailConclusao": data_envio_email_conclusao or "",
                    "tipoTransacao": tipo_transacao or "",
                    "acao": acao or "",
                    "planejamento": planejamento or "",
                    "grupo": grupo or "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar a OS. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "OS cadastrado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar a OS. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "dtSolicitacao": str(data_solicitacao),
                        "assunto": str(assunto),
                        "descricao": str(descricao),
                        "matSolicitante": str(matSolicitante),
                        "origem": str(origem_final),
                        "tipo": str(tipo_final),
                        "status": str(status_final),
                        "equipe": str(equipe_final),
                        "responsavel": str(responsavel),
                        "responsavelAtual": str(responsavel_atual),
                        "criadaPor": str(criada_por),
                        "osInterna": str(os_interna_final),
                        "categoria": str(categoria_final),
                        "projeto": str(projeto_final),
                        "prioridade": str(prioridade),
                        "tempo_previsto": str(tempo_previsto),
                        "dtInicioPrevisto": str(data_inicio_previsto),
                        "dtLimite": str(data_limite),
                        "sprint": str(sprint),
                        "osPredecessora": str(os_predecessora),
                        "chamadoFornecedor": str(chamado_fornecedor),
                        "osPrincipal": str(os_principal),
                        "rotinas": str(rotinas),
                        "classificacao": str(classificacao),
                        "criticidade": str(criticidade_final),
                        "nova": str(nova),
                        "dtPrevisaoEntrega": str(data_previsao_entrega),
                        "prioridadeUsuario": str(prioridade_usuario_final),
                        "modulo": str(modulo),
                        "tempoRestante": str(tempo_restante),
                        "ramal": str(ramal),
                        "dtEnvioEmailConclusao": str(data_envio_email_conclusao),
                        "tipoTransacao": str(tipo_transacao),
                        "acao": str(acao),
                        "planejamento": str(planejamento),
                        "grupo": str(grupo),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


async def buscar_informacoes_os(
    codigo_os: str | int,
) -> str:
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/os/buscarInfoOsSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "codOs": codigo_os,
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível buscar as informações da OS. Verifique o código informado.",
                        }
                    ]
                elif result_data and len(result_data) > 0:
                    # Sucesso - retorna os dados da OS diretamente
                    return XMLBuilder().build_xml(
                        data=result_data,
                        root_element_name="info_os",
                        item_element_name="os",
                        root_attributes={
                            "codOs": str(codigo_os),
                        },
                        custom_attributes={"sistema": "SIGA"},
                    )
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": f"OS com código '{codigo_os}' não foi encontrada no sistema.",
                        }
                    ]

                # Retorna erro estruturado
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="info_os",
                    item_element_name="resultado",
                    root_attributes={
                        "codOs": str(codigo_os),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


@controlar_acesso_matricula
async def editar_os_sistemas(
    codigo_os: str | int,
    data_solicitacao: str,
    assunto: str,
    descricao: str,
    responsavel: str | Literal["CURRENT_USER"],
    responsavel_atual: str | Literal["CURRENT_USER"],
    matSolicitante: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    criada_por: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    prioridade: str | None = None,
    tempo_previsto: int | None = None,
    data_inicio_previsto: str | None = None,
    data_limite: str | None = None,
    sprint: str | None = None,
    os_predecessora: str | None = None,
    chamado_fornecedor: str | None = None,
    os_principal: str | None = None,
    rotinas: str | None = None,
    classificacao: str | None = None,
    nova: str | None = None,
    data_previsao_entrega: str | None = None,
    modulo: str | None = None,
    tempo_restante: str | None = None,
    ramal: str | None = None,
    data_envio_email_conclusao: str | None = None,
    tipo_transacao: str | None = None,
    acao: str | None = None,
    planejamento: str | None = None,
    grupo: str | None = None,
    sistema: SistemasType = "Sistemas AVA",
    tipo: TipoOsSistemasType = "Implementação",
    equipe: EquipeSistemasType = "Equipe AVA",
    linguagem: LinguagemOsSistemasType = "PHP",
    projeto: ProjetoType = "Operação AVA",
    status: StatusOsType = "Em Atendimento",
    os_interna: OsInternaSistemasType = "Sim",
    origem: OrigemOsSistemasType = "Teams",
    prioridade_usuario: PrioridadeUsuarioOsType = "Nenhuma",
    criticidade: CriticidadeOsType = "Nenhuma",
) -> str:
    if data_solicitacao:
        data_solicitacao = converter_data_siga(data_solicitacao, manter_horas=True)

    if data_inicio_previsto:
        data_inicio_previsto = converter_data_siga(
            data_inicio_previsto, manter_horas=True
        )

    if data_limite:
        data_limite = converter_data_siga(data_limite, manter_horas=True)

    if data_previsao_entrega:
        data_previsao_entrega = converter_data_siga(
            data_previsao_entrega, manter_horas=True
        )

    if data_envio_email_conclusao:
        data_envio_email_conclusao = converter_data_siga(
            data_envio_email_conclusao, manter_horas=True
        )

    # VALIDAÇÃO DOS CAMPOS OBRIGATÓRIOS
    # Validar matSolicitante
    if (
        not matSolicitante
        or matSolicitante == "0"
        or (matSolicitante != "CURRENT_USER" and not matSolicitante.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "mat_solicitante_obrigatorio",
                    "campo_invalido": "matSolicitante",
                    "valor_informado": str(matSolicitante),
                    "mensagem": f"Campo 'matSolicitante' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {matSolicitante}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
            custom_attributes={"sistema": "SIGA"},
        )

    # Validar criada_por
    if (
        not criada_por
        or criada_por == "0"
        or (criada_por != "CURRENT_USER" and not criada_por.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "criada_por_obrigatorio",
                    "campo_invalido": "criada_por",
                    "valor_informado": str(criada_por),
                    "mensagem": f"Campo 'criada_por' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {criada_por}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
            custom_attributes={"sistema": "SIGA"},
        )

    # VALIDAÇÃO DE USUÁRIOS RESPONSÁVEIS
    # Validar responsavel (se não for CURRENT_USER)
    if responsavel != "CURRENT_USER" and responsavel not in USUARIOS_SISTEMAS_IDS:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "responsavel_invalido",
                    "responsavel_informado": responsavel,
                    "mensagem": f"Responsável '{responsavel}' não encontrado na lista de usuários válidos para Sistemas",
                    "usuarios_validos": USUARIOS_SISTEMAS_PARA_ERRO,
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
            custom_attributes={"sistema": "SIGA"},
        )

    # Validar responsavel_atual (se não for CURRENT_USER)
    if (
        responsavel_atual != "CURRENT_USER"
        and responsavel_atual not in USUARIOS_SISTEMAS_IDS
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "responsavel_atual_invalido",
                    "responsavel_atual_informado": responsavel_atual,
                    "mensagem": f"Responsável atual '{responsavel_atual}' não encontrado na lista de usuários válidos para Sistemas",
                    "usuarios_validos": USUARIOS_SISTEMAS_PARA_ERRO,
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
            custom_attributes={"sistema": "SIGA"},
        )

    # NORMALIZANDO PARAMETROS
    # Normaliza parâmetro TIPO (case-insensitive) e valida se existe na constante
    tipo_final, erro_xml = normalizar_parametro(
        tipo,
        TIPO_TO_NUMBER_OS_SISTEMAS,
        data=[
            {
                "status": "erro",
                "tipo_erro": "tipo_invalido",
                "tipo_informado": tipo,
                "mensagem": f"Tipo '{tipo}' não encontrado na constante TIPO_TO_NUMBER_OS_SISTEMAS",
                "tipos_validos": list(TIPO_TO_NUMBER_OS_SISTEMAS.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro SISTEMA (case-insensitive) e valida se existe na constante
    sistema_final, erro_xml = normalizar_parametro(
        sistema,
        SISTEMA_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "sistema_invalido",
                "sistema_informado": sistema,
                "mensagem": f"Sistema '{sistema}' não encontrado na constante SISTEMA_TO_NUMBER",
                "sistemas_validos": list(SISTEMA_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se sistema inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro EQUIPE (case-insensitive) e valida se existe na constante
    equipe_final, erro_xml = normalizar_parametro(
        equipe,
        EQUIPE_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "equipe_invalida",
                "equipe_informada": equipe,
                "mensagem": f"Equipe '{equipe}' não encontrada na constante EQUIPE_TO_NUMBER",
                "equipes_validas": list(EQUIPE_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se equipe inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro PROJETO (case-insensitive) e valida se existe na constante
    projeto_final, erro_xml = normalizar_parametro(
        projeto,
        PROJETO_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "projeto_invalido",
                "projeto_informado": projeto,
                "mensagem": f"Projeto '{projeto}' não encontrado na constante PROJETO_TO_NUMBER",
                "projetos_validos": list(PROJETO_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se projeto inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro LINGUAGEM (case-insensitive) e valida se existe na constante
    linguagem_final, erro_xml = normalizar_parametro(
        linguagem,
        LINGUAGEM_TO_NUMBER_OS_SISTEMAS,
        data=[
            {
                "status": "erro",
                "tipo_erro": "linguagem_invalida",
                "linguagem_informada": linguagem,
                "mensagem": f"Linguagem '{linguagem}' não encontrada na constante LINGUAGEM_TO_NUMBER_OS_SISTEMAS",
                "linguagens_validas": list(LINGUAGEM_TO_NUMBER_OS_SISTEMAS.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se linguagem inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro STATUS (case-insensitive) e valida se existe na constante
    status_final, erro_xml = normalizar_parametro(
        status,
        STATUS_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "status_invalido",
                "status_informado": status,
                "mensagem": f"Status '{status}' não encontrado na constante STATUS_OS_TO_NUMBER",
                "status_validos": list(STATUS_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se status inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro ORIGEM (case-insensitive) e valida se existe na constante
    origem_final, erro_xml = normalizar_parametro(
        origem,
        ORIGEM_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "origem_invalida",
                "origem_informada": origem,
                "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_OS_TO_NUMBER",
                "origens_validas": list(ORIGEM_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se origem inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro OS_INTERNA (case-insensitive) e valida se existe na constante
    os_interna_final, erro_xml = normalizar_parametro(
        os_interna,
        OS_INTERNA_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "os_interna_invalida",
                "os_interna_informada": os_interna,
                "mensagem": f"OS Interna '{os_interna}' não encontrada na constante OS_INTERNA_OS_TO_NUMBER",
                "valores_validos": list(OS_INTERNA_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se os_interna inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro CRITICIDADE (case-insensitive) e valida se existe na constante
    criticidade_final, erro_xml = normalizar_parametro(
        criticidade,
        CRITICIDADE_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "criticidade_invalida",
                "criticidade_informada": criticidade,
                "mensagem": f"Criticidade '{criticidade}' não encontrada na constante CRITICIDADE_OS_TO_NUMBER",
                "criticidades_validas": list(CRITICIDADE_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se criticidade inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro PRIORIDADE_USUARIO (case-insensitive) e valida se existe na constante
    prioridade_usuario_final, erro_xml = normalizar_parametro(
        prioridade_usuario,
        PRIORIDADE_USUARIO_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "prioridade_usuario_invalida",
                "prioridade_usuario_informada": prioridade_usuario,
                "mensagem": f"Prioridade do usuário '{prioridade_usuario}' não encontrada na constante PRIORIDADE_USUARIO_OS_TO_NUMBER",
                "prioridades_validas": list(PRIORIDADE_USUARIO_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_sistemas"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se prioridade_usuario inválida, retorna erro e para execução
        return erro_xml

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/os/updateOsSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "numeroOS": codigo_os,
                    "dtSolicitacao": data_solicitacao,
                    "assunto": assunto,
                    "descricao": descricao,
                    "matSolicitante": matSolicitante,
                    "nmSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "origem": origem_final,
                    "tipo": tipo_final,
                    "status": status_final,
                    "equipe": equipe_final,
                    "responsavel": responsavel,
                    "responsavelAtual": responsavel_atual,
                    "matGestor": "",
                    "criadaPor": criada_por,
                    "area": 1,
                    "osInterna": os_interna_final,
                    "campus": "",
                    "sistema": sistema_final or "",
                    "linguagem": linguagem_final or "",
                    "categoria": "",
                    "projeto": projeto_final or "",
                    "prioridade": prioridade or "",
                    "tempo_previsto": tempo_previsto or "",
                    "dtInicioPrevisto": data_inicio_previsto or "",
                    "dtLimite": data_limite or "",
                    "sprint": sprint or "",
                    "dtConclusao": "",
                    "osPredecessora": os_predecessora or "",
                    "chamadoFornecedor": chamado_fornecedor or "",
                    "osPrincipal": os_principal or "",
                    "rotinas": rotinas or "",
                    "plaqueta": "",
                    "classificacao": classificacao or "",
                    "criticidade": criticidade_final or "",
                    "nova": nova or "",
                    "dtPrevisaoEntrega": data_previsao_entrega or "",
                    "prioridadeUsuario": prioridade_usuario_final or "",
                    "modulo": modulo or "",
                    "tempoRestante": tempo_restante or "",
                    "ramal": ramal or "",
                    "dtEnvioEmailConclusao": data_envio_email_conclusao or "",
                    "tipoTransacao": tipo_transacao or "",
                    "acao": acao or "",
                    "planejamento": planejamento or "",
                    "grupo": grupo or "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível editar a OS. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "OS editada com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao editar a OS. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "numeroOS": str(codigo_os),
                        "dtSolicitacao": str(data_solicitacao),
                        "assunto": str(assunto),
                        "descricao": str(descricao),
                        "matSolicitante": str(matSolicitante),
                        "origem": str(origem_final),
                        "tipo": str(tipo_final),
                        "status": str(status_final),
                        "equipe": str(equipe_final),
                        "responsavel": str(responsavel),
                        "responsavelAtual": str(responsavel_atual),
                        "criadaPor": str(criada_por),
                        "osInterna": str(os_interna_final),
                        "sistema": str(sistema_final),
                        "linguagem": str(linguagem_final),
                        "projeto": str(projeto_final),
                        "prioridade": str(prioridade),
                        "tempo_previsto": str(tempo_previsto),
                        "dtInicioPrevisto": str(data_inicio_previsto),
                        "dtLimite": str(data_limite),
                        "sprint": str(sprint),
                        "osPredecessora": str(os_predecessora),
                        "chamadoFornecedor": str(chamado_fornecedor),
                        "osPrincipal": str(os_principal),
                        "rotinas": str(rotinas),
                        "classificacao": str(classificacao),
                        "criticidade": str(criticidade_final),
                        "nova": str(nova),
                        "dtPrevisaoEntrega": str(data_previsao_entrega),
                        "prioridadeUsuario": str(prioridade_usuario_final),
                        "modulo": str(modulo),
                        "tempoRestante": str(tempo_restante),
                        "ramal": str(ramal),
                        "dtEnvioEmailConclusao": str(data_envio_email_conclusao),
                        "tipoTransacao": str(tipo_transacao),
                        "acao": str(acao),
                        "planejamento": str(planejamento),
                        "grupo": str(grupo),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


@controlar_acesso_matricula
async def editar_os_infraestrutura(
    codigo_os: str | int,
    data_solicitacao: str,
    assunto: str,
    descricao: str,
    responsavel: str | Literal["CURRENT_USER"],
    responsavel_atual: str | Literal["CURRENT_USER"],
    matSolicitante: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    criada_por: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    prioridade: str | None = None,
    tempo_previsto: int | None = None,
    data_inicio_previsto: str | None = None,
    data_limite: str | None = None,
    sprint: str | None = None,
    os_predecessora: str | None = None,
    chamado_fornecedor: str | None = None,
    os_principal: str | None = None,
    rotinas: str | None = None,
    classificacao: str | None = None,
    nova: str | None = None,
    data_previsao_entrega: str | None = None,
    modulo: str | None = None,
    tempo_restante: str | None = None,
    ramal: str | None = None,
    data_envio_email_conclusao: str | None = None,
    tipo_transacao: str | None = None,
    acao: str | None = None,
    planejamento: str | None = None,
    grupo: str | None = None,
    plaqueta: str | None = None,
    categoria: CategoriasInfraestruturaType = "AD - Suporte/Dúvidas/Outros",
    tipo: TipoAtendimentoAvulsoInfraestruturaType = "Suporte",
    equipe: EquipeInfraestruturaType = "Help-Desk - Aeroporto",
    projeto: ProjetoType = "Operação Help Desk",
    status: StatusOsType = "Em Atendimento",
    os_interna: OsInternaSistemasType = "Sim",
    origem: OrigemOsSistemasType = "E-mail",
    prioridade_usuario: PrioridadeUsuarioOsType = "Nenhuma",
    criticidade: CriticidadeOsType = "Nenhuma",
) -> str:
    if data_solicitacao:
        data_solicitacao = converter_data_siga(data_solicitacao, manter_horas=True)

    if data_inicio_previsto:
        data_inicio_previsto = converter_data_siga(
            data_inicio_previsto, manter_horas=True
        )

    if data_limite:
        data_limite = converter_data_siga(data_limite, manter_horas=True)

    if data_previsao_entrega:
        data_previsao_entrega = converter_data_siga(
            data_previsao_entrega, manter_horas=True
        )

    if data_envio_email_conclusao:
        data_envio_email_conclusao = converter_data_siga(
            data_envio_email_conclusao, manter_horas=True
        )

    # VALIDAÇÃO DOS CAMPOS OBRIGATÓRIOS
    # Validar matSolicitante
    if (
        not matSolicitante
        or matSolicitante == "0"
        or (matSolicitante != "CURRENT_USER" and not matSolicitante.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "mat_solicitante_obrigatorio",
                    "campo_invalido": "matSolicitante",
                    "valor_informado": str(matSolicitante),
                    "mensagem": f"Campo 'matSolicitante' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {matSolicitante}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
            custom_attributes={"sistema": "SIGA"},
        )

    # Validar criada_por
    if (
        not criada_por
        or criada_por == "0"
        or (criada_por != "CURRENT_USER" and not criada_por.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "criada_por_obrigatorio",
                    "campo_invalido": "criada_por",
                    "valor_informado": str(criada_por),
                    "mensagem": f"Campo 'criada_por' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {criada_por}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
            custom_attributes={"sistema": "SIGA"},
        )

    # VALIDAÇÃO DE USUÁRIOS RESPONSÁVEIS
    # Validar responsavel (se não for CURRENT_USER)
    if responsavel != "CURRENT_USER" and responsavel not in USUARIOS_INFRAESTRUTURA_IDS:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "responsavel_invalido",
                    "responsavel_informado": responsavel,
                    "mensagem": f"Responsável '{responsavel}' não encontrado na lista de usuários válidos para infraestrutura",
                    "usuarios_validos": USUARIOS_INFRAESTRUTURA_PARA_ERRO,
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
            custom_attributes={"sistema": "SIGA"},
        )

    # Validar responsavel_atual (se não for CURRENT_USER)
    if (
        responsavel_atual != "CURRENT_USER"
        and responsavel_atual not in USUARIOS_INFRAESTRUTURA_IDS
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "responsavel_atual_invalido",
                    "responsavel_atual_informado": responsavel_atual,
                    "mensagem": f"Responsável atual '{responsavel_atual}' não encontrado na lista de usuários válidos para infraestrutura",
                    "usuarios_validos": USUARIOS_INFRAESTRUTURA_PARA_ERRO,
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
            custom_attributes={"sistema": "SIGA"},
        )

    # NORMALIZANDO PARAMETROS
    # Normaliza parâmetro TIPO (case-insensitive) e valida se existe na constante
    tipo_final, erro_xml = normalizar_parametro(
        tipo,
        TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA,
        data=[
            {
                "status": "erro",
                "tipo_erro": "tipo_invalido",
                "tipo_informado": tipo,
                "mensagem": f"Tipo '{tipo}' não encontrado na constante TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA",
                "tipos_validos": list(
                    TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA.keys()
                ),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro CATEGORIA (case-insensitive) e valida se existe na constante
    categoria_final, erro_xml = normalizar_parametro(
        categoria,
        CATEGORIA_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "categoria_invalida",
                "categoria_informada": categoria,
                "mensagem": f"Categoria '{categoria}' não encontrada na constante CATEGORIA_TO_NUMBER",
                "categorias_validas": list(CATEGORIA_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se categoria inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro EQUIPE (case-insensitive) e valida se existe na constante
    equipe_final, erro_xml = normalizar_parametro(
        equipe,
        EQUIPE_INFRAESTRUTURA_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "equipe_invalida",
                "equipe_informada": equipe,
                "mensagem": f"Equipe '{equipe}' não encontrada na constante EQUIPE_INFRAESTRUTURA_TO_NUMBER",
                "equipes_validas": list(EQUIPE_INFRAESTRUTURA_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se equipe inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro PROJETO (case-insensitive) e valida se existe na constante
    projeto_final, erro_xml = normalizar_parametro(
        projeto,
        PROJETO_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "projeto_invalido",
                "projeto_informado": projeto,
                "mensagem": f"Projeto '{projeto}' não encontrado na constante PROJETO_TO_NUMBER",
                "projetos_validos": list(PROJETO_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se projeto inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro STATUS (case-insensitive) e valida se existe na constante
    status_final, erro_xml = normalizar_parametro(
        status,
        STATUS_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "status_invalido",
                "status_informado": status,
                "mensagem": f"Status '{status}' não encontrado na constante STATUS_OS_TO_NUMBER",
                "status_validos": list(STATUS_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se status inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro ORIGEM (case-insensitive) e valida se existe na constante
    origem_final, erro_xml = normalizar_parametro(
        origem,
        ORIGEM_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "origem_invalida",
                "origem_informada": origem,
                "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_OS_TO_NUMBER",
                "origens_validas": list(ORIGEM_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se origem inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro OS_INTERNA (case-insensitive) e valida se existe na constante
    os_interna_final, erro_xml = normalizar_parametro(
        os_interna,
        OS_INTERNA_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "os_interna_invalida",
                "os_interna_informada": os_interna,
                "mensagem": f"OS Interna '{os_interna}' não encontrada na constante OS_INTERNA_OS_TO_NUMBER",
                "valores_validos": list(OS_INTERNA_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se os_interna inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro CRITICIDADE (case-insensitive) e valida se existe na constante
    criticidade_final, erro_xml = normalizar_parametro(
        criticidade,
        CRITICIDADE_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "criticidade_invalida",
                "criticidade_informada": criticidade,
                "mensagem": f"Criticidade '{criticidade}' não encontrada na constante CRITICIDADE_OS_TO_NUMBER",
                "criticidades_validas": list(CRITICIDADE_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se criticidade inválida, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro PRIORIDADE_USUARIO (case-insensitive) e valida se existe na constante
    prioridade_usuario_final, erro_xml = normalizar_parametro(
        prioridade_usuario,
        PRIORIDADE_USUARIO_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "prioridade_usuario_invalida",
                "prioridade_usuario_informada": prioridade_usuario,
                "mensagem": f"Prioridade do usuário '{prioridade_usuario}' não encontrada na constante PRIORIDADE_USUARIO_OS_TO_NUMBER",
                "prioridades_validas": list(PRIORIDADE_USUARIO_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_os_infraestrutura"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se prioridade_usuario inválida, retorna erro e para execução
        return erro_xml

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/os/updateOsSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "numeroOS": codigo_os,
                    "dtSolicitacao": data_solicitacao,
                    "assunto": assunto,
                    "descricao": descricao,
                    "matSolicitante": matSolicitante,
                    "nmSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "origem": origem_final,
                    "tipo": tipo_final,
                    "status": status_final,
                    "equipe": equipe_final,
                    "responsavel": responsavel,
                    "responsavelAtual": responsavel_atual,
                    "matGestor": "",
                    "criadaPor": criada_por,
                    "area": 2,
                    "osInterna": os_interna_final,
                    "campus": "",
                    "sistema": "",
                    "linguagem": "",
                    "categoria": categoria_final or "",
                    "projeto": projeto_final or "",
                    "prioridade": prioridade or "",
                    "tempo_previsto": tempo_previsto or "",
                    "dtInicioPrevisto": data_inicio_previsto or "",
                    "dtLimite": data_limite or "",
                    "sprint": sprint or "",
                    "dtConclusao": "",
                    "osPredecessora": os_predecessora or "",
                    "chamadoFornecedor": chamado_fornecedor or "",
                    "osPrincipal": os_principal or "",
                    "rotinas": rotinas or "",
                    "plaqueta": plaqueta or "",
                    "classificacao": classificacao or "",
                    "criticidade": criticidade_final or "",
                    "nova": nova or "",
                    "dtPrevisaoEntrega": data_previsao_entrega or "",
                    "prioridadeUsuario": prioridade_usuario_final or "",
                    "modulo": modulo or "",
                    "tempoRestante": tempo_restante or "",
                    "ramal": ramal or "",
                    "dtEnvioEmailConclusao": data_envio_email_conclusao or "",
                    "tipoTransacao": tipo_transacao or "",
                    "acao": acao or "",
                    "planejamento": planejamento or "",
                    "grupo": grupo or "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível editar a OS. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "OS editada com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao editar a OS. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "numeroOS": str(codigo_os),
                        "dtSolicitacao": str(data_solicitacao),
                        "assunto": str(assunto),
                        "descricao": str(descricao),
                        "matSolicitante": str(matSolicitante),
                        "origem": str(origem_final),
                        "tipo": str(tipo_final),
                        "status": str(status_final),
                        "equipe": str(equipe_final),
                        "responsavel": str(responsavel),
                        "responsavelAtual": str(responsavel_atual),
                        "criadaPor": str(criada_por),
                        "osInterna": str(os_interna_final),
                        "categoria": str(categoria_final),
                        "projeto": str(projeto_final),
                        "prioridade": str(prioridade),
                        "tempo_previsto": str(tempo_previsto),
                        "dtInicioPrevisto": str(data_inicio_previsto),
                        "dtLimite": str(data_limite),
                        "sprint": str(sprint),
                        "osPredecessora": str(os_predecessora),
                        "chamadoFornecedor": str(chamado_fornecedor),
                        "osPrincipal": str(os_principal),
                        "rotinas": str(rotinas),
                        "plaqueta": str(plaqueta),
                        "classificacao": str(classificacao),
                        "criticidade": str(criticidade_final),
                        "nova": str(nova),
                        "dtPrevisaoEntrega": str(data_previsao_entrega),
                        "prioridadeUsuario": str(prioridade_usuario_final),
                        "modulo": str(modulo),
                        "tempoRestante": str(tempo_restante),
                        "ramal": str(ramal),
                        "dtEnvioEmailConclusao": str(data_envio_email_conclusao),
                        "tipoTransacao": str(tipo_transacao),
                        "acao": str(acao),
                        "planejamento": str(planejamento),
                        "grupo": str(grupo),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


async def alterar_status_os_siga_ia(
    codigo_os: str | int,
    novo_status: str,
) -> str:
    """
    Altera o status de uma Ordem de Serviço no sistema SIGA para qualquer status válido.
    """

    # VALIDAÇÃO 1: Verificar se código da OS foi informado
    if not codigo_os or str(codigo_os).strip() == "":
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "codigo_os_obrigatorio",
                    "campo_invalido": "codigo_os",
                    "valor_informado": str(codigo_os),
                    "mensagem": f"Campo 'codigo_os' é obrigatório. Valor informado: {codigo_os}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "alterar_status_os_siga_ia"},
            custom_attributes={"sistema": "SIGA"},
        )

    # VALIDAÇÃO 2: Verificar se novo status foi informado
    if not novo_status or str(novo_status).strip() == "":
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "novo_status_obrigatorio",
                    "campo_invalido": "novo_status",
                    "valor_informado": str(novo_status),
                    "mensagem": f"Campo 'novo_status' é obrigatório. Valor informado: {novo_status}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "alterar_status_os_siga_ia"},
            custom_attributes={"sistema": "SIGA"},
        )

    # ETAPA 1: Buscar informações da OS e capturar status atual
    try:
        # Buscar dados completos da OS no sistema SIGA
        info_os_xml = await buscar_informacoes_os(codigo_os)

        # Verificar se a OS existe no sistema (busca por indicadores de erro no XML)
        if "<erro" in info_os_xml or "não encontrada" in info_os_xml.lower():
            return XMLBuilder().build_xml(
                data=[
                    {
                        "status": "erro",
                        "tipo_erro": "os_nao_encontrada",
                        "codigo_os": str(codigo_os),
                        "mensagem": f"OS {codigo_os} não encontrada no sistema SIGA",
                    }
                ],
                root_element_name="erro_validacao",
                item_element_name="erro",
                root_attributes={
                    "sistema": "SIGA",
                    "funcao": "alterar_status_os_siga_ia",
                },
                custom_attributes={"sistema": "SIGA"},
            )

        # Valor padrão caso não consiga extrair do XML o Status Atual
        status_atual = "Status não identificado"
        try:
            # Extrair status atual do XML retornado pela busca
            import xml.etree.ElementTree as ET

            root = ET.fromstring(info_os_xml)
            status_element = root.find(".//STATUS_OS")
            if status_element is not None and status_element.text:
                status_atual = status_element.text.strip()
        except Exception:
            pass  # Mantém o padrão se houver erro no parsing do XML

    except Exception as e:
        # Capturar erros gerais na busca da OS (conexão, timeout, etc.)
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "erro_busca_os",
                    "codigo_os": str(codigo_os),
                    "mensagem": f"Erro ao verificar OS {codigo_os}: {str(e)}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "alterar_status_os_siga_ia"},
            custom_attributes={"sistema": "SIGA"},
        )

    # ETAPA 2: Validar e normalizar o novo status informado
    status_final, erro_xml = normalizar_parametro(
        novo_status,
        STATUS_OS_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "status_invalido",
                "status_informado": novo_status,
                "mensagem": f"Status '{novo_status}' não encontrado na constante STATUS_OS_TO_NUMBER",
                "status_validos": list(STATUS_OS_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "alterar_status_os_siga_ia"},
        custom_attributes={"sistema": "SIGA"},
    )

    # Se houver erro na validação do status, retornar erro
    if erro_xml:
        return erro_xml

    # ETAPA 3: Determinar tipo de operação para personalizar feedback ao usuário
    status_conclusao = [
        "Concluída",
        "Concluída por Encaminhamento",
        "Concluída por substituição",
    ]

    status_cancelamento = ["Cancelamento DTD | Arquivado", "Cancelada-Usuário"]

    # Definir verbo apropriado para a mensagem de sucesso
    if novo_status in status_conclusao:
        acao = "concluída"
    elif novo_status in status_cancelamento:
        acao = "cancelada"
    else:
        acao = "alterada"

    # ETAPA 4: Realizar chamada para API do SIGA para alterar o status
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            # Enviar requisição POST para endpoint de alteração de status
            async with session.post(
                "https://ava3.uniube.br/ava/api/os/updateStatusOsSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "numeroOS": codigo_os,
                    "status": status_final,
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # ETAPA 5: Interpretar resposta da API e preparar retorno
                if result_data is None:
                    # API retornou sem result - possível erro de validação
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": f"Não foi possível alterar o status da OS {codigo_os}. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    # Sucesso - API retornou 1 (operação bem-sucedida)
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": f"OS {codigo_os} foi {acao} com sucesso!",
                            "detalhes": f"Status alterado de '{status_atual}' para '{novo_status}'",
                        }
                    ]
                else:
                    # API retornou valor diferente de 1 - erro genérico
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": f"Erro ao alterar status da OS {codigo_os}. Tente novamente.",
                        }
                    ]

                # Retornar XML formatado com resultado da operação
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "codigo_os": str(codigo_os),
                        "status_anterior": status_atual,
                        "status_novo": novo_status,
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

    except Exception as e:
        # Capturar erros de rede, timeout ou outros problemas na requisição HTTP
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "mensagem": f"Erro interno: {str(e)}. Tente novamente mais tarde.",
                }
            ],
            root_element_name="resultado",
            item_element_name="item",
            custom_attributes={"sistema": "SIGA"},
        )


async def concluir_os_siga_ia(
    codigo_os: str | int,
    tipo_conclusao: str = "Concluída",
) -> str:
    """
    Conclui uma Ordem de Serviço no sistema SIGA.
    """
    return await alterar_status_os_siga_ia(
        codigo_os=codigo_os,
        novo_status=tipo_conclusao,
    )


async def cancelar_os_siga_ia(
    codigo_os: str | int,
    tipo_cancelamento: str = "Cancelada-Usuário",
) -> str:
    """
    Cancela uma Ordem de Serviço no sistema SIGA.
    """
    return await alterar_status_os_siga_ia(
        codigo_os=codigo_os,
        novo_status=tipo_cancelamento,
    )

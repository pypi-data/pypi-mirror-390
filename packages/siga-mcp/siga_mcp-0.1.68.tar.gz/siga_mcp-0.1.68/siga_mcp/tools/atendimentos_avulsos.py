"""Este módulo guarda todas as funções do MCP visíveis para o Agente usar"""

from os import getenv
from typing import Literal
import aiohttp
import ujson
from siga_mcp._types import (
    CategoriasInfraestruturaType,
    EquipeInfraestruturaType,
    EquipeSistemasType,
    OrigemAtendimentoAvulsoSistemasType,
    ProjetoType,
    SistemasType,
    TipoAtendimentoAvulsoInfraestruturaType,
    TipoAtendimentoAvulsoSistemasType,
)
from siga_mcp.dynamic_constants import (
    CATEGORIA_TO_NUMBER,
    EQUIPE_INFRAESTRUTURA_TO_NUMBER,
    EQUIPE_TO_NUMBER,
    ORIGEM_TO_NUMBER,
    PROJETO_TO_NUMBER,
    SISTEMA_TO_NUMBER,
    TIPO_TO_NUMBER_ATENDIMENTO_AVULSO,
    TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA,
)
from siga_mcp.decorators import controlar_acesso_matricula
from siga_mcp.utils import converter_data_siga, normalizar_parametro
from siga_mcp.xml_builder import XMLBuilder


async def listar_atendimentos_avulsos(
    *,
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    data_inicio: str,
    data_fim: str,
) -> str:
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio)

    if data_fim:
        data_fim = converter_data_siga(data_fim)

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarAtendimentosAvulsosSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": data_inicio,
                "dataFim": data_fim,
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimentos_avulsos",
                    root_attributes={
                        "matricula": str(matricula),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar atendimentos avulsos."


@controlar_acesso_matricula
async def inserir_atendimento_avulso_sistemas(
    data_inicio: str,
    data_fim: str,
    matricula_solicitante: str | Literal["CURRENT_USER"],
    descricao_atendimento: str,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    tipo: TipoAtendimentoAvulsoSistemasType = "Atividade Interna",
    origem: OrigemAtendimentoAvulsoSistemasType = "Teams",
    sistema: SistemasType = "Sistemas AVA",
    equipe: EquipeSistemasType = "Equipe AVA",
    projeto: ProjetoType = "Operação AVA",
) -> str:
    # VALIDAÇÃO DO CÓDIGO DO ANALISTA
    if (
        not codigo_analista
        or codigo_analista == "0"
        or (codigo_analista != "CURRENT_USER" and not codigo_analista.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "analista_obrigatorio",
                    "campo_invalido": "codigo_analista",
                    "valor_informado": str(codigo_analista),
                    "mensagem": f"Campo 'codigo_analista' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {codigo_analista}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "inserir_atendimento_avulso_sistemas",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Normaliza parâmetro TIPO (case-insensitive) e valida se existe na constante
    tipo_final, erro_xml = normalizar_parametro(
        tipo,
        TIPO_TO_NUMBER_ATENDIMENTO_AVULSO,
        data=[
            {
                "status": "erro",
                "tipo_erro": "tipo_invalido",
                "tipo_informado": tipo,
                "mensagem": f"Tipo '{tipo}' não encontrado na constante TIPO_TO_NUMBER_ATENDIMENTO_AVULSO",
                "tipos_validos": list(TIPO_TO_NUMBER_ATENDIMENTO_AVULSO.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_sistemas",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro ORIGEM (case-insensitive) e valida se existe na constante
    origem_final, erro_xml = normalizar_parametro(
        origem,
        ORIGEM_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "origem_invalida",
                "origem_informada": origem,
                "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_TO_NUMBER",
                "origens_validas": list(ORIGEM_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_sistemas",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se origem inválida, retorna erro e para execução
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_sistemas",
        },
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_sistemas",
        },
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_sistemas",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se projeto inválido, retorna erro e para execução
        return erro_xml

    # FUNÇÃO PARA GRAVAR INFORMAÇÕES
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosAvulsos/inserirAtendimentoAvulsoSigaIA/",
                # "https://9f7a79af77d0.ngrok-free.app/ava/api/atendimentosAvulsos/inserirAtendimentoAvulsoSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "dataIni": data_inicio,
                    "dataFim": data_fim,
                    "matSolicitante": matricula_solicitante,
                    "tipo": tipo_final,
                    "descricao": descricao_atendimento,
                    "origem": origem_final,
                    "area": 1,
                    "equipe": equipe_final,
                    "analista": codigo_analista,
                    "projeto": projeto_final,
                    "sistema": sistema_final,
                    "nomeSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "matGestor": "",
                    "tempoGasto": "",
                    "campus": "",
                    "categoria": "",
                    "plaqueta": "",
                    "ramal": "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar o atendimento avulso. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento avulso cadastrado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento avulso. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimento_avulso",
                    root_attributes={
                        "dataIni": str(data_inicio),
                        "dataFim": str(data_fim),
                        "matSolicitante": str(matricula_solicitante),
                        "tipo": str(tipo_final),
                        "descricao": str(descricao_atendimento),
                        "origem": str(origem_final),
                        "equipe": str(equipe_final),
                        "analista": str(codigo_analista),
                        "projeto": str(projeto_final),
                        "sistema": str(sistema_final),
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


async def buscar_informacoes_atendimento_avulso(
    codigo_atendimento: int,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
) -> str:
    from siga_mcp.tools.atendimentos_os import buscar_informacoes_atendimentos_os

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarInfoAtendimentoAvulsoSigaIA/",
            json={
                "apiKey": getenv("AVA_API_KEY"),
                "atendimento": codigo_atendimento,
                "analista": codigo_analista,
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="info_atendimentos_avulsos",
                    item_element_name="info_atendimento_avulso",
                    root_attributes={
                        "atendimento": str(codigo_atendimento),
                        "analista": str(codigo_analista),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                # Se não encontrou em Atendimento Avulso, tenta buscar em atendimentos OS
                try:
                    return await buscar_informacoes_atendimentos_os(
                        codigo_atendimento, codigo_analista
                    )
                except Exception:
                    return "Erro ao buscar as informações do atendimento em ambas as tabelas (Avulso e OS)."


async def excluir_atendimento_avulso(
    codigo_atendimento: int,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
) -> str:
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosAvulsos/excluiAtendimentoAvulsoSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "atendimento": codigo_atendimento,
                    "analista": codigo_analista,
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Atendimento não encontrado em Avulso. Tente buscar na função excluir_atendimentos_os.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento avulso excluído com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao excluir o atendimento avulso. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="exclusões_atendimento_avulso",
                    item_element_name="exclusão",
                    root_attributes={
                        "atendimento": str(codigo_atendimento),
                        "analista": str(codigo_analista),
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
async def editar_atendimento_avulso_sistemas(
    codigo_atendimento: int,
    data_inicio: str,
    data_fim: str,
    matricula_solicitante: str | Literal["CURRENT_USER"],
    descricao_atendimento: str,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    tipo: TipoAtendimentoAvulsoSistemasType = "Atividade Interna",
    origem: OrigemAtendimentoAvulsoSistemasType = "Teams",
    sistema: SistemasType = "Sistemas AVA",
    equipe: EquipeSistemasType = "Equipe AVA",
    projeto: ProjetoType = "Operação AVA",
) -> str:
    # VALIDAÇÃO DO CÓDIGO DO ANALISTA
    if (
        not codigo_analista
        or codigo_analista == "0"
        or (codigo_analista != "CURRENT_USER" and not codigo_analista.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "analista_obrigatorio",
                    "campo_invalido": "codigo_analista",
                    "valor_informado": str(codigo_analista),
                    "mensagem": f"Campo 'codigo_analista' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {codigo_analista}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "editar_atendimento_avulso_sistemas",  # ← Note que mudou para editar
            },
            custom_attributes={"sistema": "SIGA"},
        )

    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Normaliza parâmetro TIPO (case-insensitive) e valida se existe na constante
    tipo_final, erro_xml = normalizar_parametro(
        tipo,
        TIPO_TO_NUMBER_ATENDIMENTO_AVULSO,
        data=[
            {
                "status": "erro",
                "tipo_erro": "tipo_invalido",
                "tipo_informado": tipo,
                "mensagem": f"Tipo '{tipo}' não encontrado na constante TIPO_TO_NUMBER_ATENDIMENTO_AVULSO",
                "tipos_validos": list(TIPO_TO_NUMBER_ATENDIMENTO_AVULSO.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_sistemas",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro ORIGEM (case-insensitive) e valida se existe na constante
    origem_final, erro_xml = normalizar_parametro(
        origem,
        ORIGEM_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "origem_invalida",
                "origem_informada": origem,
                "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_TO_NUMBER",
                "origens_validas": list(ORIGEM_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_sistemas",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se origem inválida, retorna erro e para execução
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_sistemas",
        },
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_sistemas",
        },
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_sistemas",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se projeto inválido, retorna erro e para execução
        return erro_xml

    # FUNÇÃO PARA GRAVAR INFORMAÇÕES
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosAvulsos/atualizarAtendimentoAvulsoSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "atendimento": codigo_atendimento,
                    "dataIni": data_inicio,
                    "dataFim": data_fim,
                    "matSolicitante": matricula_solicitante,
                    "tipo": tipo_final,
                    "descricao": descricao_atendimento,
                    "origem": origem_final,
                    "area": 1,
                    "equipe": equipe_final,
                    "analista": codigo_analista,
                    "projeto": projeto_final,
                    "sistema": sistema_final,
                    "nomeSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "matGestor": "",
                    "tempoGasto": "",
                    "campus": "",
                    "categoria": "",
                    "plaqueta": "",
                    "ramal": "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Atendimento não encontrado em Avulso Sistemas. Tente buscar nas funções editar_atendimentos_os ou editar_atendimento_avulso_infraestrutura.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento avulso editado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento avulso. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimento_avulso",
                    root_attributes={
                        "codigo_atendimento": str(codigo_atendimento),
                        "dataIni": str(data_inicio),
                        "dataFim": str(data_fim),
                        "matSolicitante": str(matricula_solicitante),
                        "tipo": str(tipo_final),
                        "descricao": str(descricao_atendimento),
                        "origem": str(origem_final),
                        "equipe": str(equipe_final),
                        "analista": str(codigo_analista),
                        "projeto": str(projeto_final),
                        "sistema": str(sistema_final),
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
async def editar_atendimento_avulso_infraestrutura(
    codigo_atendimento: int,
    data_inicio: str,
    data_fim: str,
    matricula_solicitante: str | Literal["CURRENT_USER"],
    descricao_atendimento: str,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    tipo: TipoAtendimentoAvulsoInfraestruturaType = "Suporte",
    origem: OrigemAtendimentoAvulsoSistemasType = "E-mail",
    categoria: CategoriasInfraestruturaType = "AD - Suporte/Dúvidas/Outros",
    equipe: EquipeInfraestruturaType = "Help-Desk - Aeroporto",
    projeto: ProjetoType = "Operação Help Desk",
    plaqueta: str | None = None,
) -> str:
    # VALIDAÇÃO DO CÓDIGO DO ANALISTA
    if (
        not codigo_analista
        or codigo_analista == "0"
        or (codigo_analista != "CURRENT_USER" and not codigo_analista.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "analista_obrigatorio",
                    "campo_invalido": "codigo_analista",
                    "valor_informado": str(codigo_analista),
                    "mensagem": f"Campo 'codigo_analista' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {codigo_analista}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "editar_atendimento_avulso_infraestrutura",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # NORMALIZANDO PARAMETROS"

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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_infraestrutura",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro ORIGEM (case-insensitive) e valida se existe na constante
    origem_final, erro_xml = normalizar_parametro(
        origem,
        ORIGEM_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "origem_invalida",
                "origem_informada": origem,
                "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_TO_NUMBER",
                "origens_validas": list(ORIGEM_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_infraestrutura",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se origem inválida, retorna erro e para execução
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_infraestrutura",
        },
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_infraestrutura",
        },
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "editar_atendimento_avulso_infraestrutura",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se projeto inválido, retorna erro e para execução
        return erro_xml

    # FUNÇÃO PARA GRAVAR INFORMAÇÕES
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosAvulsos/atualizarAtendimentoAvulsoSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "atendimento": codigo_atendimento,
                    "dataIni": data_inicio,
                    "dataFim": data_fim,
                    "matSolicitante": matricula_solicitante,
                    "tipo": tipo_final,
                    "descricao": descricao_atendimento,
                    "origem": origem_final,
                    "area": 2,
                    "equipe": equipe_final,
                    "analista": codigo_analista,
                    "projeto": projeto_final,
                    "sistema": "",
                    "nomeSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "matGestor": "",
                    "tempoGasto": "",
                    "campus": "",
                    "categoria": categoria_final,
                    "plaqueta": plaqueta if plaqueta else "",
                    "ramal": "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Atendimento não encontrado em Avulso Infraestrutura. Tente buscar nas funções editar_atendimentos_os ou editar_atendimento_avulso_sistemas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento avulso editado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento avulso. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="atendimentos_avulsos_infra",
                    item_element_name="atendimento_avulso_infra",
                    root_attributes={
                        "codigo_atendimento": str(codigo_atendimento),
                        "dataIni": str(data_inicio),
                        "dataFim": str(data_fim),
                        "matSolicitante": str(matricula_solicitante),
                        "tipo": str(tipo_final),
                        "descricao": str(descricao_atendimento),
                        "origem": str(origem_final),
                        "equipe": str(equipe_final),
                        "analista": str(codigo_analista),
                        "projeto": str(projeto_final),
                        "categoria": str(categoria_final),
                        "plaqueta": str(plaqueta if plaqueta else ""),
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
async def inserir_atendimento_avulso_infraestrutura(
    data_inicio: str,
    data_fim: str,
    matricula_solicitante: str | Literal["CURRENT_USER"],
    descricao_atendimento: str,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
    tipo: TipoAtendimentoAvulsoInfraestruturaType = "Suporte",
    origem: OrigemAtendimentoAvulsoSistemasType = "E-mail",
    categoria: CategoriasInfraestruturaType = "AD - Suporte/Dúvidas/Outros",
    equipe: EquipeInfraestruturaType = "Help-Desk - Aeroporto",
    projeto: ProjetoType = "Operação Help Desk",
    plaqueta: str | None = None,
) -> str:
    # VALIDAÇÃO DO CÓDIGO DO ANALISTA
    if (
        not codigo_analista
        or codigo_analista == "0"
        or (codigo_analista != "CURRENT_USER" and not codigo_analista.isdigit())
    ):
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "analista_obrigatorio",
                    "campo_invalido": "codigo_analista",
                    "valor_informado": str(codigo_analista),
                    "mensagem": f"Campo 'codigo_analista' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: {codigo_analista}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={
                "sistema": "SIGA",
                "funcao": "inserir_atendimento_avulso_infraestrutura",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # CRIANDO NORMALIZAÇÃO DAS LITERAIS
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_infraestrutura",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    # Normaliza parâmetro ORIGEM (case-insensitive) e valida se existe na constante
    origem_final, erro_xml = normalizar_parametro(
        origem,
        ORIGEM_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "origem_invalida",
                "origem_informada": origem,
                "mensagem": f"Origem '{origem}' não encontrada na constante ORIGEM_TO_NUMBER",
                "origens_validas": list(ORIGEM_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_infraestrutura",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se origem inválida, retorna erro e para execução
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_infraestrutura",
        },
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_infraestrutura",
        },
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
        root_attributes={
            "sistema": "SIGA",
            "funcao": "inserir_atendimento_avulso_infraestrutura",
        },
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se projeto inválido, retorna erro e para execução
        return erro_xml

    # FUNÇÃO PARA GRAVAR INFORMAÇÕES
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosAvulsos/inserirAtendimentoAvulsoSigaIA/",
                # "https://9f7a79af77d0.ngrok-free.app/ava/api/atendimentosAvulsos/inserirAtendimentoAvulsoSigaIA/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "dataIni": data_inicio,
                    "dataFim": data_fim,
                    "matSolicitante": matricula_solicitante,
                    "tipo": tipo_final,
                    "descricao": descricao_atendimento,
                    "origem": origem_final,
                    "area": 2,
                    "equipe": equipe_final,
                    "analista": codigo_analista,
                    "projeto": projeto_final,
                    "sistema": "",
                    "nomeSolicitante": "",
                    "centroCusto": "",
                    "setor": "",
                    "matGestor": "",
                    "tempoGasto": "",
                    "campus": "",
                    "categoria": categoria_final,
                    "plaqueta": plaqueta if plaqueta else "",
                    "ramal": "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar o atendimento avulso. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento avulso cadastrado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento avulso. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="atendimentos_avulsos_infra",
                    item_element_name="atendimento_avulso_infra",
                    root_attributes={
                        "dataIni": str(data_inicio),
                        "dataFim": str(data_fim),
                        "matSolicitante": str(matricula_solicitante),
                        "tipo": str(tipo_final),
                        "descricao": str(descricao_atendimento),
                        "origem": str(origem_final),
                        "equipe": str(equipe_final),
                        "analista": str(codigo_analista),
                        "projeto": str(projeto_final),
                        "categoria": str(categoria_final),
                        "plaqueta": str(plaqueta if plaqueta else ""),
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

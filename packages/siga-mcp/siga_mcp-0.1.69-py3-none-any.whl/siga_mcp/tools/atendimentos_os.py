"""Este módulo guarda todas as funções do MCP visíveis para o Agente usar"""

from os import getenv
from typing import Literal
import aiohttp
import ujson
from siga_mcp._types import (
    TipoAtendimentosOSType,
    TiposAtendimentosOSType,
)
from siga_mcp.dynamic_constants import (
    TYPE_TO_NUMBER,
)

from siga_mcp.decorators import controlar_acesso_matricula
from siga_mcp.utils import converter_data_siga, normalizar_parametro
from siga_mcp.xml_builder import XMLBuilder


async def buscar_informacoes_atendimentos_os(
    codigo_atendimento: int,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
) -> str:
    from siga_mcp.tools.atendimentos_avulsos import (
        buscar_informacoes_atendimento_avulso,
    )

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosOs/buscarInfoAtendimentosOsSigaIA/",
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
                    root_element_name="info_atendimentos_os",
                    item_element_name="info_atendimentos_os",
                    root_attributes={
                        "atendimento": str(codigo_atendimento),
                        "analista": str(codigo_analista),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                # Se não encontrou em Atendimento OS, tenta buscar em atendimentos avulsos
                try:
                    return await buscar_informacoes_atendimento_avulso(
                        codigo_atendimento, codigo_analista
                    )
                except Exception:
                    return "Erro ao buscar as informações do atendimento em ambas as tabelas (OS e Avulso)."


async def editar_atendimentos_os(
    codigo_atendimento: int,
    codigo_os: int,
    data_inicio: str,
    codigo_analista: int,
    descricao_atendimento: str,
    tipo_atendimento: TiposAtendimentosOSType = "Implementação",
    data_fim: str | None = None,
    primeiro_atendimento: bool = False,
    apresenta_solucao: bool = False,
) -> str:
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Normaliza parâmetro TIPO_ATENDIMENTO (case-insensitive) e valida se existe na constante
    tipo_final, erro_xml = normalizar_parametro(
        tipo_atendimento,
        TYPE_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "tipo_invalido",
                "tipo_informado": tipo_atendimento,
                "mensagem": f"Tipo '{tipo_atendimento}' não encontrado na constante TYPE_TO_NUMBER",
                "tipos_validos": list(TYPE_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "editar_atendimentos_os"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/updateAtendimentosOsSigaIA/",
                json={
                    "atendimento": codigo_atendimento,
                    "os": codigo_os,
                    "dataIni": data_inicio,
                    "analista": codigo_analista,
                    "descricao": descricao_atendimento,
                    "tipo": tipo_final,
                    "dataFim": data_fim,
                    "primeiroAtendimento": primeiro_atendimento,
                    "apresentaSolucao": apresenta_solucao,
                    "apiKey": getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Atendimento não encontrado em Atendimentos OS. Este código pode estar em atendimento avulso (sistemas ou infraestrutura). Tente buscar nas funções: editar_atendimento_avulso_sistemas ou editar_atendimento_avulso_infraestrutura.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento editado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao editar o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "os": str(codigo_os),
                        "dataIni": str(data_inicio),
                        "analista": str(codigo_analista),
                        "descricao": str(descricao_atendimento),
                        "tipo": str(tipo_final),
                        "dataFim": str(data_fim),
                        "primeiroAtendimento": str(primeiro_atendimento),
                        "apresentaSolucao": str(apresenta_solucao),
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


async def excluir_atendimentos_os(
    codigo_atendimento: int,
    codigo_analista: str | Literal["CURRENT_USER"] = "CURRENT_USER",
) -> str:
    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/excluiAtendimentosOsSigaIA/",
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
                            "mensagem": "Atendimento não encontrado em OS. Tente buscar na função excluir_atendimento_avulso.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento excluído com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao excluir o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="exclusões_atendimento_os",
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


async def inserir_atendimentos_os(
    codigo_os: int,
    data_inicio: str,
    codigo_analista: int,
    descricao_atendimento: str,
    tipo: TipoAtendimentosOSType = "Implementação",
    data_fim: str | None = None,
    primeiro_atendimento: bool = False,
    apresenta_solucao: bool = False,
) -> str:
    # VALIDAÇÃO DO CÓDIGO DO ANALISTA
    if not codigo_analista or codigo_analista <= 0:
        return XMLBuilder().build_xml(
            data=[
                {
                    "status": "erro",
                    "tipo_erro": "analista_obrigatorio",
                    "campo_invalido": "codigo_analista",
                    "valor_informado": str(codigo_analista),
                    "mensagem": f"Campo 'codigo_analista' é obrigatório e deve ser um número maior que zero. Valor informado: {codigo_analista}",
                }
            ],
            root_element_name="erro_validacao",
            item_element_name="erro",
            root_attributes={"sistema": "SIGA", "funcao": "inserir_atendimentos_os"},
            custom_attributes={"sistema": "SIGA"},
        )

    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    if data_fim:
        data_fim = converter_data_siga(data_fim, manter_horas=True)

    # Normaliza parâmetro TIPO (case-insensitive) e valida se existe na constante
    tipo_final, erro_xml = normalizar_parametro(
        tipo,
        TYPE_TO_NUMBER,
        data=[
            {
                "status": "erro",
                "tipo_erro": "tipo_invalido",
                "tipo_informado": tipo,
                "mensagem": f"Tipo '{tipo}' não encontrado na constante TYPE_TO_NUMBER",
                "tipos_validos": list(TYPE_TO_NUMBER.keys()),
            }
        ],
        root_element_name="erro_validacao",
        item_element_name="erro",
        root_attributes={"sistema": "SIGA", "funcao": "inserir_atendimentos_os"},
        custom_attributes={"sistema": "SIGA"},
    )

    if erro_xml:  # Se tipo inválido, retorna erro e para execução
        return erro_xml

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosOs/inserirAtendimentosOsSigaIA/",
                json={
                    "os": codigo_os,
                    "dataIni": data_inicio,
                    "analista": codigo_analista,
                    "descricao": descricao_atendimento,
                    "tipo": tipo_final,
                    "dataFim": data_fim,
                    "primeiroAtendimento": primeiro_atendimento,
                    "apresentaSolucao": apresenta_solucao,
                    "apiKey": getenv("AVA_API_KEY"),
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Não foi possível salvar o atendimento. Verifique as informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Atendimento cadastrado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao gravar o atendimento. Tente novamente.",
                        }
                    ]

                # Adiciona os root_attributes
                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="ordens_servico",
                    item_element_name="ordem_servico",
                    root_attributes={
                        "os": str(codigo_os),
                        "dataIni": str(data_inicio),
                        "analista": str(codigo_analista),
                        "descricao": str(descricao_atendimento),
                        "tipo": str(tipo_final),
                        "dataFim": str(data_fim),
                        "primeiroAtendimento": str(primeiro_atendimento),
                        "apresentaSolucao": str(apresenta_solucao),
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
async def listar_atendimentos_os(
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    codigo_os: str | int | None = None,
    data_inicio: str | None = None,
    data_fim: str | None = None,
) -> str:
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosOs/buscarAtendimentosOsSigaIA/",
            json={
                "matricula": str(matricula),
                "os": str(codigo_os) if codigo_os else "",
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                retorno = XMLBuilder().build_xml(
                    data=json["result"],
                    root_element_name="atendimentos_os",
                    item_element_name="atendimentos_os",
                    root_attributes={
                        "matricula": str(matricula),
                        "os": str(codigo_os) if codigo_os else "",
                        "dataIni": str(data_inicio) if data_inicio else "",
                        "dataFim": str(data_fim) if data_fim else "",
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar atendimentos OS."

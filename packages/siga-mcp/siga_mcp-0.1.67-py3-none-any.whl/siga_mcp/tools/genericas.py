"""Este módulo guarda todas as funções do MCP visíveis para o Agente usar"""

from os import getenv
import asyncio
from typing import Any, Literal
import zoneinfo
import datetime
import aiohttp
import ujson
import xml.etree.ElementTree as ET
from siga_mcp import memory
from siga_mcp._types import (
    SituacaoUsuarioType,
    EquipeGeralType,
)
from siga_mcp.decorators import controlar_acesso_matricula
from siga_mcp.domain import HoraMinuto, MeioPeriodo

from siga_mcp.utils import converter_data_siga, get_package_version
from siga_mcp.xml_builder import XMLBuilder


# Busca pendências de registros SIGA do usuário.
@controlar_acesso_matricula
async def buscar_pendencias_lancamentos_atendimentos(
    *,
    matricula: str | int | Literal["CURRENT_USER"] = "CURRENT_USER",
    dataIni: str,
    dataFim: str,
) -> str:
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarPendenciasRegistroAtendimentosSigaIA/",
            json={
                "matricula": matricula,
                "dataIni": converter_data_siga(dataIni),
                "dataFim": converter_data_siga(dataFim),
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                # Verifica se a requisição HTTP foi bem-sucedida (status 2xx)
                response.raise_for_status()

                # Converte a resposta para JSON, permitindo qualquer content-type
                data = await response.json(content_type=None)

                retorno = XMLBuilder().build_xml(
                    # Usa [] se 'result' não existir ou for None
                    data=data.get("result", []),
                    root_element_name="pendencias_lançamentos",
                    item_element_name="pendencias_lançamentos",
                    root_attributes={"matricula": str(matricula)},
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                # Captura qualquer outro erro não previsto
                return "Erro ao consultar todas as pendências de registros SIGA do usuário."


# Busca pendências para múltiplas matrículas em paralelo (5-10x mais rápido)
# Ideal para gerentes consultando pendências de toda equipe
# Função separada: PHP não conseguiu implementar array devido à complexidade da SQL
@controlar_acesso_matricula
async def buscar_pendencias_multiplas_matriculas(
    *,
    matriculas: list[str | int],
    dataIni: str,
    dataFim: str,
) -> str:
    """Busca pendências de lançamentos para múltiplas matrículas concorrentemente."""

    if not matriculas:
        return XMLBuilder().build_xml(
            data=[],
            root_element_name="pendencias_lançamentos_multiplas",
            item_element_name="pendencia",
            root_attributes={
                "matricula": "",
                "total_matriculas": "0",
                "processadas_ok": "0",
                "com_erro": "0",
            },
            custom_attributes={"sistema": "SIGA"},
        )

    # Executa todas as requisições concorrentemente, usando a função principal
    tasks = [
        buscar_pendencias_lancamentos_atendimentos(
            matricula=matricula, dataIni=dataIni, dataFim=dataFim
        )
        for matricula in matriculas
    ]

    # Aguarda todas as respostas
    resultados = await asyncio.gather(*tasks, return_exceptions=True)

    # Processa e combina resultados
    pendencias_consolidadas = []
    matriculas_ok = []
    matriculas_erro = []

    for i, resultado in enumerate(resultados):
        matricula_atual = str(matriculas[i])

        if isinstance(resultado, Exception):
            matriculas_erro.append(matricula_atual)
            continue

        if "Erro ao consultar" in resultado:
            matriculas_erro.append(matricula_atual)
            continue

        # Sucesso - parseia o XML para extrair dados completos
        matriculas_ok.append(matricula_atual)

        try:
            # ✅ CORRIGIDO: Parseia o XML retornado da função principal
            root = ET.fromstring(resultado)
            pendencias_reais = []

            # Extrai cada pendência real do XML
            for pendencia_elem in root.findall("pendencias_lançamentos"):
                pendencia_data = {}
                for child in pendencia_elem:
                    pendencia_data[child.tag] = child.text

                # Só adiciona se tem dados válidos
                if pendencia_data:
                    pendencias_reais.append(pendencia_data)

            # ✅ NOVO: Adiciona metadados da matrícula
            resultado_matricula = {
                "matricula": matricula_atual,
                "status": "processado",
                "total_pendencias": len(pendencias_reais),
                "tem_dados": len(pendencias_reais) > 0,
            }

            # ✅ CORRIGIDO: Adiciona pendências como elementos XML estruturados
            if pendencias_reais:
                # Para cada pendência, cria elementos individuais numerados
                for idx, pendencia in enumerate(pendencias_reais):
                    for campo, valor in pendencia.items():
                        # Cria elementos como: pendencia_0_analista, pendencia_0_nome_analista, etc.
                        resultado_matricula[f"pendencia_{idx}_{campo}"] = valor

            pendencias_consolidadas.append(resultado_matricula)

        except ET.ParseError:
            # Se não conseguiu parsear o XML, trata como erro
            matriculas_erro.append(matricula_atual)
            if matricula_atual in matriculas_ok:
                matriculas_ok.remove(matricula_atual)

    # ✅ CORRIGIDO: Para matrículas sem pendências, adiciona resultado básico
    for matricula in matriculas_ok:
        # Verifica se já foi processada (tem pendências)
        ja_processada = any(
            item.get("matricula") == matricula for item in pendencias_consolidadas
        )

        if not ja_processada:
            # Adiciona resultado vazio para matrículas sem pendências
            pendencias_consolidadas.append(
                {
                    "matricula": matricula,
                    "status": "processado",
                    "total_pendencias": 0,
                    "tem_dados": False,
                }
            )

    # Constrói XML consolidado
    return XMLBuilder().build_xml(
        data=pendencias_consolidadas,
        root_element_name="pendencias_lançamentos_multiplas",
        item_element_name="resultado_matricula",
        root_attributes={
            "matricula": ",".join([str(m) for m in matriculas]),
            "total_matriculas": str(len(matriculas)),
            "processadas_ok": str(len(matriculas_ok)),
            "com_erro": str(len(matriculas_erro)),
            "matriculas_ok": ",".join(matriculas_ok),
            "matriculas_erro": ",".join(matriculas_erro),
        },
        custom_attributes={"sistema": "SIGA"},
    )


# Calcula o total de horas trabalhadas do usuário.
@controlar_acesso_matricula
async def listar_horas_trabalhadas(
    *,
    matricula: str | int | list[str | int] | Literal["CURRENT_USER"] = "CURRENT_USER",
    data_inicio: str,
    data_fim: str,
) -> str:
    # Preparar matrícula(s) para envio
    if isinstance(matricula, list):
        matricula_param = matricula  # Lista para DAO
    else:
        matricula_param = matricula  # String/int individual

    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/atendimentosAvulsos/buscarTotalHorasTrabalhadasSigaIA/",
            json={
                "matricula": matricula_param,
                "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                "dataFim": converter_data_siga(data_fim) if data_fim else "",
                "apiKey": getenv("AVA_API_KEY"),
            },
        ) as response:
            try:
                json = await response.json(content_type=None)
                resultado = json["result"]

                retorno = XMLBuilder().build_xml(
                    data=resultado,
                    root_element_name="atendimentos_avulsos",
                    item_element_name="atendimentos_avulsos",
                    root_attributes={
                        "matricula": ",".join(map(str, matricula))
                        if isinstance(matricula, list)
                        else str(matricula),
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return "Erro ao listar horas trabalhadas."


# Lista todos os usuários responsáveis de acordo com a área informada
# Passar para o arquivo tools e montar o docstring.
# Servirá para quando o usuário pedir a lista de usuários responsáveis da OS
async def listar_usuarios_responsaveis_os_siga(area: int) -> str:
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/usuarios/buscarUsuarioResponsavelOsSigaIA/",
            json={
                "apiKey": getenv("AVA_API_KEY"),
                "area": area,
            },
        ) as response:
            try:
                json_data: list[Any] | dict[str, Any] = await response.json(
                    content_type=None
                )

                # Ajustar conforme retorno real da API PHP
                data: list[Any] = (
                    json_data
                    if isinstance(json_data, list)
                    else json_data.get("result", json_data)
                )

                retorno = XMLBuilder().build_xml(
                    data=data,
                    root_element_name="usuarios_responsaveis",
                    item_element_name="usuario_responsavel",
                    root_attributes={
                        "area": str(area),
                        "tipo": "Sistemas" if area == 1 else "Infraestrutura",
                    },
                    custom_attributes={"sistema": "SIGA"},
                )

                return retorno

            except Exception:
                return f"Erro ao listar usuários responsáveis área {area}."


# Esta função é chamada primeiramente pelo Agente IA quando precisa listar usuários
# Busca usuários de uma equipe filtrados por gerente responsável, descrição da equipe e situação do usuário
# Função MCP TOOL que serve como interface assíncrona e DELEGA para dynamic_constants
# Função WRAPPER: não contém lógica de negócio, apenas repassa parâmetros
@controlar_acesso_matricula
async def listar_usuarios_equipe_por_gerente(
    matricula_gerente: str | int | Literal["CURRENT_USER"] | None = None,
    descricao_equipe: EquipeGeralType | None = None,
    situacao_usuario: SituacaoUsuarioType | None = None,
) -> str:
    from siga_mcp.dynamic_constants import listar_usuarios_equipe_por_gerente

    return listar_usuarios_equipe_por_gerente(
        matricula_gerente=matricula_gerente,
        descricao_equipe=descricao_equipe,
        situacao_usuario=situacao_usuario,
    )


# Função utilitária: converte XML de equipes em lista de matrículas para busca de horas trabalhadas
async def extrair_matriculas_do_xml(xml_string: str) -> list[str]:
    import xml.etree.ElementTree as ET

    try:
        root = ET.fromstring(xml_string)
        matriculas: list[str] = []

        # Busca todos os elementos usuario_equipe_gerente
        for user_element in root.findall(".//usuario_equipe_gerente"):
            usuario_elem = user_element.find("usuario")
            if usuario_elem is not None and usuario_elem.text:
                matricula = usuario_elem.text.strip()
                if matricula:  # Garante que não adiciona strings vazias
                    matriculas.append(matricula)

        return matriculas

    except ET.ParseError:
        # XML malformado
        return []
    except Exception:
        # Qualquer outro erro
        return []


async def atualizar_tempo_gasto_atendimento(
    codigo_analista: int,
    data_inicio: str | None = None,
) -> str:
    if data_inicio:
        data_inicio = converter_data_siga(data_inicio, manter_horas=True)

    try:
        async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
            async with session.post(
                "https://ava3.uniube.br/ava/api/atendimentosAvulsos/atualizaTempoGastoAtendimentoAvulso/",
                json={
                    "apiKey": getenv("AVA_API_KEY"),
                    "analista": int(codigo_analista),
                    "dataIni": converter_data_siga(data_inicio) if data_inicio else "",
                },
            ) as response:
                json_response = await response.json(content_type=None)
                result_data = json_response.get("result")

                # Trata a resposta
                if result_data is None:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Tempo gasto não atualizado. Favor verificar informações digitadas.",
                        }
                    ]
                elif result_data == 1:
                    data_final = [
                        {
                            "status": "sucesso",
                            "mensagem": "Tempo gasto atualizado com sucesso!",
                        }
                    ]
                else:
                    data_final = [
                        {
                            "status": "erro",
                            "mensagem": "Erro ao atualizar o tempo gasto. Tente novamente.",
                        }
                    ]

                return XMLBuilder().build_xml(
                    data=data_final,
                    root_element_name="atualizacao_tempo_gasto",
                    item_element_name="tempo_gasto",
                    root_attributes={
                        "analista": str(codigo_analista),
                        "dataIni": str(data_inicio),
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


# @controlar_acesso_matricula
# async def cadastrar_todos_dias_pendentes(
#     colaborador: str | Literal["CURRENT_USER"] = "CURRENT_USER",
#     codigo_os: str | None = None,
#     descricao: str = "debugando codigo",
#     cadastrar_como_atendimento_avulso: bool = True,
# ) -> str:
#     if codigo_os is not None and cadastrar_como_atendimento_avulso:
#         raise ValueError(
#             "Os parâmetros 'codigo_os' e 'cadastrar_como_atendimento_avulso' são mutuamente exclusivos. "
#             "Informe apenas um deles."
#         )

#     pendencias = await buscar_pendencias_lancamentos_atendimentos()

#     raise NotImplementedError("Função ainda não implementada.")


async def atualizar_horarios_colaborador(
    entrada_1: str | None = None,
    saida_1: str | None = None,
    entrada_2: str | None = None,
    saida_2: str | None = None,
) -> str:
    _entrada_1 = memory.periodo.periodos[0].entrada
    if entrada_1:
        _entrada_1 = HoraMinuto.from_string(entrada_1)

    _saida_1 = memory.periodo.periodos[0].saida
    if saida_1:
        _saida_1 = HoraMinuto.from_string(saida_1)

    _entrada_2 = memory.periodo.periodos[1].entrada
    if entrada_2:
        _entrada_2 = HoraMinuto.from_string(entrada_2)

    _saida_2 = memory.periodo.periodos[1].saida
    if saida_2:
        _saida_2 = HoraMinuto.from_string(saida_2)

    primeiro_periodo = MeioPeriodo(
        entrada=_entrada_1 if entrada_1 else memory.periodo.periodos[0].entrada,
        saida=_saida_1 if saida_1 else memory.periodo.periodos[0].saida,
    )

    segundo_periodo = MeioPeriodo(
        entrada=_entrada_2 if entrada_2 else memory.periodo.periodos[1].entrada,
        saida=_saida_2 if saida_2 else memory.periodo.periodos[1].saida,
    )

    memory.periodo.alterar_periodos(novos_periodos=[primeiro_periodo, segundo_periodo])

    return "Horários atualizados com sucesso."


def __version__() -> str:
    brazil_tz = zoneinfo.ZoneInfo("America/Sao_Paulo")

    # Get the current time in the Brazil time zone
    current_time_brazil = datetime.datetime.now(brazil_tz)
    return f"{get_package_version()} - {current_time_brazil}"

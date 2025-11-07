import getpass
from os import getenv
from typing import cast

from siga_mcp._types import TransportType
from rsb.coroutines.run_sync import run_sync
import aiohttp
import ujson


async def __buscar_matricula_por_ad(ad: str) -> tuple[str, str]:
    """Busca a matrícula correspondente a um usuário AD.

    Args:
        ad (str): Nome do usuário AD no formato DOMINIO\\usuario

    Returns:
        int: Matrícula do usuário
    """
    api_key = getenv("AVA_API_KEY")
    async with aiohttp.ClientSession(json_serialize=ujson.dumps) as session:
        async with session.post(
            "https://ava3.uniube.br/ava/api/contasAd/buscarUsuarioAdSigaIA/",
            json={"apiKey": api_key, "descricao": ad},
        ) as response:
            json = await response.json(content_type=None)

            usuario: str = json["result"][0]["USUARIO"]
            nome: str = json["result"][0]["NOME"]
            return usuario, nome


async def __buscar_gestores_dtd() -> list[str]:
    return ["8372", "16500", "24142", "25962"]


# Mapeamento de meses em português
MESES_PT = {
    "janeiro": 1,
    "jan": 1,
    "fevereiro": 2,
    "fev": 2,
    "março": 3,
    "mar": 3,
    "abril": 4,
    "abr": 4,
    "maio": 5,
    "mai": 5,
    "junho": 6,
    "jun": 6,
    "julho": 7,
    "jul": 7,
    "agosto": 8,
    "ago": 8,
    "aug": 8,
    "setembro": 9,
    "set": 9,
    "sep": 9,
    "outubro": 10,
    "out": 10,
    "oct": 10,
    "novembro": 11,
    "nov": 11,
    "dezembro": 12,
    "dez": 12,
    "dec": 12,
}

# Mapeamento de dias da semana em português
DIAS_SEMANA_PT = {
    "segunda": 0,
    "segunda-feira": 0,
    "seg": 0,
    "terça": 1,
    "terça-feira": 1,
    "ter": 1,
    "terca": 1,
    "terca-feira": 1,
    "quarta": 2,
    "quarta-feira": 2,
    "qua": 2,
    "quinta": 3,
    "quinta-feira": 3,
    "qui": 3,
    "sexta": 4,
    "sexta-feira": 4,
    "sex": 4,
    "sábado": 5,
    "sabado": 5,
    "sab": 5,
    "domingo": 6,
    "dom": 6,
}

# Palavras que indicam tempo futuro/passado
TEMPO_FUTURO = [
    "próximo",
    "proximo",
    "que vem",
    "seguinte",
    "vindouro",
    "daqui a",
    "daqui",
    "vindoura",
    "entrante",
]

TEMPO_PASSADO = [
    "passado",
    "anterior",
    "ultimo",
    "último",
    "atrás",
    "atras",
    "ha",
    "há",
    "retrasado",
    "retrasada",
]

# Números por extenso
NUMEROS_EXTENSO = {
    "um": 1,
    "uma": 1,
    "dois": 2,
    "duas": 2,
    "três": 3,
    "tres": 3,
    "quatro": 4,
    "cinco": 5,
    "seis": 6,
    "sete": 7,
    "oito": 8,
    "nove": 9,
    "dez": 10,
    "onze": 11,
    "doze": 12,
    "treze": 13,
    "catorze": 14,
    "quatorze": 14,
    "quinze": 15,
    "dezesseis": 16,
    "dezessete": 17,
    "dezoito": 18,
    "dezenove": 19,
    "vinte": 20,
    "trinta": 30,
}

# Expressões de período do dia
PERIODOS_DIA = {
    "manhã": 8,
    "manha": 8,
    "de manhã": 8,
    "de manha": 8,
    "tarde": 14,
    "de tarde": 14,
    "à tarde": 14,
    "a tarde": 14,
    "noite": 20,
    "de noite": 20,
    "à noite": 20,
    "a noite": 20,
    "madrugada": 2,
    "de madrugada": 2,
}

AD = getpass.getuser()

MCP_TRANSPORT: TransportType = cast(TransportType, getenv("MCP_TRANSPORT")) or "stdio"

# Avoid network calls when running under tests/CI or when explicitly disabled.
_DISABLE_NETWORK = getenv("SIGA_DISABLE_NETWORK", "").lower() in {"1", "true", "yes"}
_PYTEST_RUNNING = getenv("PYTEST_CURRENT_TEST") is not None


def _safe_buscar_matricula() -> tuple[str, str]:
    # Allow overriding via env for deterministic tests
    override = getenv("SIGA_TEST_MATRICULA")
    if override:
        return override, ""
    if MCP_TRANSPORT == "http" or _DISABLE_NETWORK or _PYTEST_RUNNING:
        return "", ""
    try:
        return run_sync(__buscar_matricula_por_ad(AD))
    except Exception:
        # Fall back to empty if lookup fails
        return "", ""


MATRICULA_USUARIO_ATUAL, NOME_USUARIO_ATUAL = _safe_buscar_matricula()


def _safe_buscar_matriculas_liberadas() -> list[str]:
    if _DISABLE_NETWORK or _PYTEST_RUNNING:
        # Minimal default; can be overridden in tests
        return []
    try:
        return run_sync(__buscar_gestores_dtd())
    except Exception:
        return []


MATRICULAS_LIBERADAS = _safe_buscar_matriculas_liberadas()


TEAMS_CLIENT_ID = ""

TEAMS_CLIENT_SECRET = ""

TEAMS_TENANT_ID = ""

PACKAGE_NAME = "siga-mcp"

DEFAULT_PORT = 8000

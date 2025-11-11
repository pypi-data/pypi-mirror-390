# /// script
# requires-python = ">=3.13"
# dependencies = [
#     "aiohttp>=3.12.15",
#     "dateparser>=1.2.2",
#     "fastmcp>=2.11.1",
#     "ujson>=5.10.0",
#     "rock-solid-base>=0.1.13",
#     "langfuse>=3.3.5",
# ]
# ///
from collections.abc import Callable
import importlib
import inspect
from os import getenv
import pkgutil
from types import ModuleType
from typing import Any

from fastmcp import FastMCP
from siga_mcp.dynamic_constants import SYSTEM_INSTRUCTIONS
import siga_mcp.tools
from siga_mcp.constants import DEFAULT_PORT, MCP_TRANSPORT
from siga_mcp.decorators import tool
import warnings

warnings.filterwarnings("ignore", category=DeprecationWarning, module="fastmcp")

mcp = FastMCP(
    "My MCP Server",
    instructions=str(SYSTEM_INSTRUCTIONS),
    host=getenv("HOST"),
    port=int(getenv("PORT", DEFAULT_PORT)),
)


def get_all_functions_from_package(
    package: ModuleType, debug: bool = False
) -> list[Callable[..., Any]]:
    """
    Coleta todas as funções definidas em um pacote e seus submódulos.

    Args:
        package: O módulo/pacote do qual extrair as funções
        debug: Se True, imprime informações de debug

    Returns:
        Lista de funções encontradas no pacote e submódulos
    """
    functions: list[Callable[..., Any]] = []
    seen_functions: set[str] = set()  # Para evitar duplicatas

    if not hasattr(package, "__path__"):
        if debug:
            print(f"{package.__name__} não é um pacote")
        return functions

    # Itera por todos os submódulos (incluindo o principal se tiver __init__.py)
    for _, modname, _ in pkgutil.walk_packages(
        path=package.__path__, prefix=package.__name__ + ".", onerror=lambda x: None
    ):
        try:
            module: ModuleType = importlib.import_module(modname)
            if debug:
                print(f"\n--- Módulo: {modname} ---")

            for name, func in inspect.getmembers(module, inspect.isfunction):
                # Verifica se a função foi definida neste módulo
                if func.__module__ == modname:
                    func_id = f"{func.__module__}.{func.__name__}"
                    if func_id not in seen_functions:
                        seen_functions.add(func_id)
                        functions.append(func)
                        if debug:
                            print(f"  {name} (de {func.__module__})")
                    elif debug:
                        print(f"  {name} (duplicata)")
                elif debug:
                    print(f"  {name} (importada de {func.__module__})")

        except ImportError as e:
            if debug:
                print(f"Erro ao carregar {modname}: {e}")

    return functions


# Com debug para ver o que está acontecendo
tools: list[Callable[..., Any]] = get_all_functions_from_package(
    siga_mcp.tools, debug=False
)


for mcp_tool in tools:
    tool(server=mcp, transport=MCP_TRANSPORT)(mcp_tool)


def main():
    mcp.run(transport=MCP_TRANSPORT, show_banner=False)


if __name__ == "__main__":
    main()

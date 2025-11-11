import asyncio

# from siga_mcp.tools import inserir_os_infraestrutura
# from siga_mcp.dynamic_constants import obter_usuarios_responsavel
from siga_mcp.tools.genericas import (
    buscar_pendencias_multiplas_matriculas,
    buscar_pendencias_lancamentos_atendimentos,
)
from siga_mcp.tools.os import buscar_informacoes_os

from dotenv import load_dotenv

# 🔑 CARREGAR .ENV AUTOMATICAMENTE
load_dotenv()


"""def main() -> str:
return listar_usuarios_responsaveis_os_siga(
    **{
        "area": "1",
    }
)"""


# def main() -> str:
# Testar Sistemas (área 1)
#    docstring_sistemas, ids_sistemas, erro_sistemas = obter_usuarios_responsavel(1)

# Testar Infraestrutura (área 2)
#    docstring_infra, ids_infra, erro_infra = obter_usuarios_responsavel(2)

#    return f"""
#        === SISTEMAS ===
#        {docstring_sistemas}
#        IDs: {ids_sistemas}
#        Erro: {erro_sistemas}
#        === INFRAESTRUTURA ===
#        {docstring_infra}
#        IDs: {ids_infra}
#        Erro: {erro_infra}
#        """


# if __name__ == "__main__":
#    resultado = main()
# print(resultado)


""" async def main() -> str:
    return await inserir_os_infraestrutura(
        **{
            "data_solicitacao": "03/10/2025 08:31:17",
            "assunto": "Teste de gravação Infra",
            "descricao": "Este é apenas um teste de gravação Infra",
            "matSolicitante": "24142",
            "criada_por": "24142",
            "responsavel": "24142",
            "responsavel_atual": "24142",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


""" async def main() -> str:
    return await listar_usuarios_responsaveis_os_siga(
        **{
            "area": "2",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


""" async def main() -> str:
    return await listar_usuarios_equipe_por_gerente(
        **{
            "matricula_gerente": "8372",
            "descricao_equipe": "Equipe AVA",
            "situacao_usuario": "Ativo",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


""" async def main() -> str:
    return await listar_usuarios_equipe_por_gerente(
        **{
            "matricula_gerente": "8372",
            "descricao_equipe": "Equipe AVA",
            "situacao_usuario": "Ativo",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


""" async def main() -> str:
    return await listar_horas_trabalhadas(
        **{
            "matricula": ["24142", "14897"],
            "data_inicio": "13/10/2025",
            "data_fim": "17/10/2025",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


""" async def main() -> str:
    return await atualizar_tempo_gasto_atendimento(
        **{
            "codigo_analista": "24142",
            "data_inicio": "22/10/2025",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


""" async def main() -> str:
    return await inserir_atendimentos_os(
        **{
            "codigo_analista": 24142,
            "codigo_os": 182487,
            "data_inicio": "23/10/2025 08:02",
            "data_fim": "23/10/2025 08:12",
            "descricao_atendimento": "teste",
            "tipo": "Suporte Sistema",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


""" async def main() -> str:
    return await buscar_informacoes_os(
        **{
            "codigo_os": "182487",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


""" async def main() -> str:
    return await editar_os_sistemas(
        **{
            "codigo_os": 194987,
            "assunto": "teste",
            "criada_por": "24142",
            "data_solicitacao": "30/10/2025 15:01",
            "descricao": "testando SIGA IA",
            "matSolicitante": "24142",
            "responsavel": "24142",
            "responsavel_atual": "24142",
            "tipo": "Implementação",
            "origem": "Teams",
            "sistema": "Sistemas AVA",
            "equipe": "Equipe AVA",
            "projeto": "Operação AVA",
            "status": "Em Atendimento",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


""" # RODAR TESTES TANTO GERAL, QUANTO PARA CANCELAMENTO E CONCLUSAO.
async def main() -> str:
    return await concluir_os_siga_ia(
        **{
            "codigo_os": "195011",
            "tipo_conclusao": "Concluída",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


# TESTE: Buscar pendências de múltiplas matrículas concorrentemente
# EFETUA OS TESTES NA SEGUNDA PARA VER SE ESTÁ FUNCIONANDO. ELA IRÁ CONSUMIR A FUNÇÃO ORIGINAL
""" async def main() -> str:
    return await buscar_pendencias_multiplas_matriculas(
        **{
            "matriculas": [
                16500,
                24290,
                25962,
                27342,
                20634,
                23767,
                24056,
                28560,
                23724,
                29306,
                14897,
                24142,
                26302,
                29229,
                25818,
            ],  # Lista de matrículas para testar
            "dataIni": "03/11/2025",
            "dataFim": "07/11/2025",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado) """


# TESTE: Buscar pendências de múltiplas matrículas concorrentemente
# EFETUA OS TESTES NA SEGUNDA PARA VER SE ESTÁ FUNCIONANDO. ELA IRÁ CONSUMIR A FUNÇÃO ORIGINAL
async def main() -> str:
    return await buscar_pendencias_lancamentos_atendimentos(
        **{
            "matricula": 16500,
            "dataIni": "03/11/2025",
            "dataFim": "07/11/2025",
        }
    )


if __name__ == "__main__":
    resultado = asyncio.run(main())
    print(resultado)

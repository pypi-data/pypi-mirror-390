from textwrap import dedent


def docs() -> str:
    return dedent("""\
            Busca informações detalhadas de uma Ordem de Serviço (OS) específica no sistema SIGA.

            Esta função realiza uma consulta ao sistema SIGA através da API do AVA para obter
            todas as informações relacionadas a uma OS específica. É especialmente útil para 
            consultar dados completos antes de realizar qualquer operação de edição na OS.
                  
            Funcionalidade de consulta completa:
            Retorna todos os campos da OS incluindo dados dos responsáveis (atual e original),
            datas formatadas, informações de projeto, sistema, equipe e status atual.

            Funcionalidades:
            - Consulta dados completos de uma OS pelo código/número
            - Retorna informações estruturadas em formato XML
            - Inclui dados dos responsáveis (nomes e matrículas)
            - Formata datas automaticamente (DD/MM/YYYY HH24:MI)
            - Inclui tratamento de erros para requisições mal-sucedidas
            - Utiliza autenticação via API Key do AVA
            - Valida existência da OS no sistema

        
            Args:
                codigo_os (str | int): Código/número único identificador da OS. Obrigatório.
                    Deve ser um valor válido correspondente a uma OS existente no sistema SIGA.
                    Aceita tanto string quanto inteiro. Valores inválidos (vazios, zero ou negativos)
                    são tratados pelo DAO com validação automática.

            Notes:
                - FUNÇÃO ESSENCIAL: Consulta obrigatória antes de edições na OS
                - Requer variável de ambiente AVA_API_KEY configurada
                - A função é assíncrona e deve ser chamada com await
                - Utiliza aiohttp para requisições HTTP assíncronas
                - O XML é formatado usando a classe XMLBuilder interna
                - Validação de entrada realizada automaticamente pelo DAO
                - Retorna dados dos responsáveis com nomes completos (JOIN com tabela de usuários)
                - Todas as datas são formatadas no padrão brasileiro (DD/MM/YYYY HH24:MI)
                - Campos com valores NULL são incluídos no retorno para completude dos dados
            """)

from textwrap import dedent


def docs() -> str:
    return dedent("""\
            Busca informações detalhadas de uma Ordem de Serviço (OS) específica no sistema SIGA.

            Esta função realiza uma consulta ao sistema SIGA através da API do AVA para obter
            todas as informações relacionadas a uma OS específica. É especialmente útil para 
            consultar dados completos antes de realizar qualquer operação de edição na OS.
                  
            **Funcionalidade de consulta completa:**
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

            Endpoint utilizado:
            - URL: https://ava3.uniube.br/ava/api/os/buscarInfoOsSigaIA/
            - Método: POST
            - Autenticação: API Key (AVA_API_KEY)

            Estrutura do XML retornado:
            - Elemento raiz: <info_os> (sucesso) ou <resultado> (erro)
            - Atributos do elemento raiz: codOs (código da OS)
            - Atributos customizados: sistema="SIGA"
            - Item de dados: <os> (sucesso) ou <resultado> (erro)
            - Contém todos os campos da tabela SEG.OS com aliases padronizados

            Args:
                codigo_os (str | int): Código/número único identificador da OS. Obrigatório.
                    Deve ser um valor válido correspondente a uma OS existente no sistema SIGA.
                    Aceita tanto string quanto inteiro. Valores inválidos (vazios, zero ou negativos)
                    são tratados pelo DAO com validação automática.

            Returns:
                str: XML bem formatado contendo as informações da OS encontrada.
                    - Sucesso: XML com dados completos da OS (<info_os><os>...</os></info_os>)
                    - OS não encontrada: XML com mensagem de erro específica
                    - Erro de sistema: XML com mensagem de erro genérica
                    - Formato consistente para todos os cenários de resposta

            Raises:
                Exception: Captura qualquer exceção durante a requisição HTTP ou
                        processamento dos dados, retornando XML com mensagem de erro amigável.

            Example:
                >>> # Busca OS existente
                >>> resultado = await buscar_informacoes_os(12345)
                >>> print(resultado)
                <?xml version="1.0" ?>
                <info_os codOs="12345" sistema="SIGA">
                    <os>
                        <OS_OS>12345</OS_OS>
                        <DT_SOLICITACAO_OS>15/01/2024 14:30</DT_SOLICITACAO_OS>
                        <ASSUNTO_OS>Desenvolvimento de nova funcionalidade</ASSUNTO_OS>
                        <DESCRICAO_OS>Implementar sistema de relatórios...</DESCRICAO_OS>
                        <RESPONSAVEL_OS>3214</RESPONSAVEL_OS>
                        <NOME_RESPONSAVEL>João Silva</NOME_RESPONSAVEL>
                        <STATUS_OS>EM_ANDAMENTO</STATUS_OS>
                        ...
                    </os>
                </info_os>

                >>> # Busca OS inexistente
                >>> resultado = await buscar_informacoes_os(99999)
                >>> print(resultado)
                <?xml version="1.0" ?>
                <info_os codOs="99999" sistema="SIGA">
                    <resultado>
                        <status>erro</status>
                        <mensagem>OS com código '99999' não foi encontrada no sistema.</mensagem>
                    </resultado>
                </info_os>

                >>> # Usando string como código
                >>> resultado = await buscar_informacoes_os("12345")

            Notes:
                - **FUNÇÃO ESSENCIAL**: Consulta obrigatória antes de edições na OS
                - Requer variável de ambiente AVA_API_KEY configurada
                - A função é assíncrona e deve ser chamada com await
                - Utiliza aiohttp para requisições HTTP assíncronas
                - O XML é formatado usando a classe XMLBuilder interna
                - Validação de entrada realizada automaticamente pelo DAO
                - Retorna dados dos responsáveis com nomes completos (JOIN com tabela de usuários)
                - Todas as datas são formatadas no padrão brasileiro (DD/MM/YYYY HH24:MI)
                - Campos com valores NULL são incluídos no retorno para completude dos dados
            """)

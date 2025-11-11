from textwrap import dedent


def docs() -> str:
    return dedent("""\
            Busca informações detalhadas de um atendimento de Ordem de Serviço (OS) específico.

             Esta função realiza uma consulta ao sistema SIGA através da API do AVA para obter
            todas as informações relacionadas a um atendimento de OS específico. 
            Com busca automática: Se não encontrar em OS, busca automaticamente em atendimentos avulsos.
            É especialmente útil para consultar dados antes de realizar qualquer operação no atendimento.
                  
            ORIENTAÇÃO PARA SOLICITAÇÕES GENÉRICAS:
            Quando o usuário solicitar "buscar informações de um atendimento" sem especificar o tipo:
            1. Primeiro: Use esta função (buscar_informacoes_atendimentos_os)
            2. Se não encontrar: Busca automaticamente em atendimentos avulsos
            3. Resultado único: Retorna as informações independente do tipo encontrado

            Esta função é específica para Atendimentos OS, mas com busca automática em:
            - `buscar_informacoes_atendimento_avulso` (tanto Sistemas quanto Infraestrutura)
                  
             Funcionalidade de busca automática:
            Se o atendimento não for encontrado nos registros de OS, a função automaticamente
            tentará buscar nas tabelas de atendimentos avulsos, fornecendo uma experiência
            transparente ao usuário.

            Funcionalidades:
            - Consulta dados completos de um atendimento OS pelo código e analista responsável
            - BUSCA AUTOMÁTICA em atendimentos avulsos se não encontrar em OS
            - Garante precisão na identificação do registro correto (evita ambiguidade entre códigos duplicados)
            - Retorna informações estruturadas em formato XML
            - Inclui tratamento de erros para requisições mal-sucedidas
            - Utiliza autenticação via API Key do AVA

            Args:
                codigo_atendimento: Código único identificador do atendimento OS. Obrigatório.
                    Deve ser um número inteiro válido correspondente a um atendimento existente no sistema SIGA.
                codigo_analista: Matrícula do analista/usuário responsável pelo atendimento OS. Obrigatório.
                    É necessário para garantir a identificação precisa do registro, evitando conflitos com códigos duplicados entre diferentes tipos de atendimento.

            Notes:
                - DIFERENCIAÇÃO DE FUNÇÃO: Esta função busca primeiro em OS, depois automaticamente em avulsos
                - BUSCA AUTOMÁTICA: Transparente ao usuário - retorna o atendimento independente do tipo
                - Requer variável de ambiente AVA_API_KEY configurada
                - A função é assíncrona e deve ser chamada com await
                - Utiliza aiohttp para requisições HTTP assíncronas
                - O XML é formatado usando a classe XMLBuilder interna
                - Ambos os parâmetros (codigo_atendimento e codigo_analista) são obrigatórios para evitar conflitos com códigos duplicados em diferentes tabelas do sistema
            """)

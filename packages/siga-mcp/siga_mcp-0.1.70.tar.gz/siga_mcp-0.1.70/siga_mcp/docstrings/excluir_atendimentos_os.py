from textwrap import dedent


def docs() -> str:
    return dedent("""\
        Exclui um atendimento de Ordem de Serviço (OS) específico do sistema SIGA.

        INSTRUÇÃO PARA O AGENTE IA:
        ANTES de executar esta função de exclusão:
        1. SEMPRE chame primeiro `buscar_informacoes_atendimentos_os(codigo_atendimento, codigo_analista)`
        2. MOSTRE ao usuário TODAS as informações do atendimento que será EXCLUÍDO
        3. PEÇA confirmação explícita do usuário: "Confirma a exclusão? (sim/não)"
        4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
        5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada

        Esta função remove permanentemente um atendimento específico vinculado a uma OS no sistema SIGA.
        Utiliza o código do atendimento e código do analista para garantir identificação precisa.
        ATENÇÃO: Esta operação é irreversível.
                  
        ORIENTAÇÃO PARA SOLICITAÇÕES GENÉRICAS:
        Quando o usuário solicitar "excluir um atendimento" sem especificar o tipo:
        1. Primeiro: Tente esta função (excluir_atendimentos_os)
        2. Se não encontrar: Use automaticamente excluir_atendimento_avulso
        3. Busca automática: Use as funções buscar_informacoes_atendimentos_os e buscar_informacoes_atendimento_avulso para identificar o tipo
        4. Confirmação: Sempre mostre as informações do atendimento antes de excluir

        Esta função é específica para Atendimentos OS. Para atendimentos avulsos, use:
        - `excluir_atendimento_avulso` (tanto Sistemas quanto Infraestrutura)
                  
        Funcionalidade de busca automática:
        Se o atendimento não for encontrado nesta função (atendimentos OS), a mensagem de erro orientará a buscar na função excluir_atendimento_avulso, permitindo busca automática entre os tipos de atendimento.

        Funcionalidades:
            - Exclui atendimento OS pelo código e analista responsável
            - Garante precisão na identificação do registro correto (evita ambiguidade entre códigos duplicados)
            - Retorna informações estruturadas em formato XML com status da operação
            - Inclui tratamento de erros para diferentes cenários de falha
            - Utiliza autenticação via API Key do AVA
            - Orienta busca automática em atendimentos avulsos quando não encontra o registro


        Args:
            codigo_atendimento: Código único identificador do atendimento OS. Obrigatório.
                Deve ser um número inteiro válido correspondente a um atendimento existente no sistema SIGA.
            codigo_analista: Matrícula do analista/usuário responsável pelo atendimento OS. Obrigatório. 
                É necessário para garantir a identificação precisa do registro, evitando conflitos com códigos duplicados entre diferentes tipos de atendimento.

        Returns
        Notes:
            - DIFERENCIAÇÃO DE FUNÇÃO: Esta função exclui atendimentos OS. Para atendimentos avulsos, use excluir_atendimento_avulso
            - BUSCA AUTOMÁTICA: Se não encontrar aqui, o sistema deve automaticamente tentar excluir_atendimento_avulso
            - ATENÇÃO: Esta operação é irreversível. Uma vez excluído, o atendimento não pode ser recuperado
            - Para busca automática: Se não encontrar nesta função, use excluir_atendimento_avulso com os mesmos parâmetros
            - Requer variável de ambiente AVA_API_KEY configurada
            - A função é assíncrona e deve ser chamada com await
            - Utiliza aiohttp para requisições HTTP assíncronas
            - O XML é formatado usando a classe XMLBuilder interna
            - Ambos os parâmetros (codigo_atendimento e codigo_analista) são obrigatórios para evitar conflitos com códigos duplicados em diferentes tabelas do sistema
            - Use com extrema cautela em ambientes de produção
        """)

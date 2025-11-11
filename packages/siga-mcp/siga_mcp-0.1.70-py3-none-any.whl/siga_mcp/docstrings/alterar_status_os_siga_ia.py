from textwrap import dedent


def docs() -> str:
    return dedent("""\
        Esta função permite alterar o status de uma OS (Ordem de Serviço) existente no sistema SIGA
        para qualquer status válido disponível no sistema. Funciona para OS de qualquer área (Sistemas ou Infraestrutura).

        INSTRUÇÃO PARA O AGENTE IA:
        ANTES de executar esta função:
        1. SEMPRE chame primeiro `buscar_informacoes_os(codigo_os)` para verificar se a OS existe
        2. MOSTRE ao usuário as informações da OS encontrada, incluindo o status atual
        3. PEÇA confirmação explícita do usuário: "Confirma a alteração do status da OS {{codigo_os}} de '{{status_atual}}' para '{{novo_status}}'? (sim/não)"
        4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
        5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada

        ORIENTAÇÃO PARA SOLICITAÇÕES:
        - "Alterar status da OS 123 para Em Teste" -> Usar esta função
        - "Mudar OS 456 para Pendente-Aprovação" -> Usar esta função  
        - "Colocar OS 789 em Pendente-Liberação" -> Usar esta função
        - "Concluir OS 321" -> Usar concluir_os_siga_ia() para melhor UX
        - "Cancelar OS 654" -> Usar cancelar_os_siga_ia() para melhor UX

        Args:
            codigo_os (str | int): Código/número da OS (Ordem de Serviço) que terá o status alterado
            novo_status (str): Novo status a ser aplicado à OS. 

        Returns:
            str: confirmação da alteração com detalhes da operação

        Notes:
            - ATENÇÃO: Esta operação modifica permanentemente o status da OS
            - DIFERENCIAÇÃO DE FUNÇÃO: Esta função altera apenas o status. Para editar outros dados da OS, use editar_os_sistemas ou editar_os_infraestrutura
            - VALIDAÇÃO PRÉVIA: A função primeiro verifica se a OS existe usando buscar_informacoes_os()
            - CAMPOS OBRIGATÓRIOS: codigo_os e novo_status são obrigatórios
            - MAPEAMENTO AUTOMÁTICO: Os status em texto são automaticamente convertidos para códigos numéricos
            - FEEDBACK RICO: Retorna informações detalhadas da operação incluindo status anterior e novo
            - CASE-INSENSITIVE: A validação de status é case-insensitive (não diferencia maiúsculas/minúsculas)
            - A função realiza validação case-insensitive do status usando a constante STATUS_OS_TO_NUMBER
            - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
            - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
            - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente
            - Esta função funciona para OS de qualquer área (Sistemas ou Infraestrutura)
            - Utiliza a constante STATUS_OS_TO_NUMBER para mapear valores para códigos numéricos
            - Todos os parâmetros enviados são incluídos como atributos no XML de resposta
        """)

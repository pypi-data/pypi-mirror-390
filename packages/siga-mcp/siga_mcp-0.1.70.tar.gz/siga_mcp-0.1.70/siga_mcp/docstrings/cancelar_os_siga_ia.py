from textwrap import dedent


def docs() -> str:
    return dedent("""\
        Cancela uma Ordem de Serviço no sistema SIGA.

        **INSTRUÇÃO PARA O AGENTE IA:**
        ANTES de executar esta função:
        1. SEMPRE chame primeiro `buscar_informacoes_os(codigo_os)` para verificar se a OS existe
        2. MOSTRE ao usuário as informações da OS encontrada, incluindo o status atual
        3. PEÇA confirmação explícita do usuário: "Confirma o cancelamento da OS {{codigo_os}}? (sim/não)"
        4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
        5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada

        Esta é uma função de conveniência para cancelar uma OS. Internamente chama alterar_status_os_siga_ia()
        com status de cancelamento para melhor experiência do usuário.

        **ORIENTAÇÃO PARA SOLICITAÇÕES:**
        - "Cancelar OS 123" → Usar esta função
        - "Anular OS 456" → Usar esta função  
        - "Marcar OS 789 como cancelada" → Usar esta função
        - "Arquivar OS 321" → Usar esta função

        Args:
            codigo_os: Código da OS a ser cancelada
            tipo_cancelamento: Tipo de cancelamento (padrão: "Cancelada-Usuário").

        Notes:
            - **FUNÇÃO DE CONVENIÊNCIA**: Internamente chama alterar_status_os_siga_ia()
            - **UX MELHORADA**: Mais intuitivo para usuários que querem apenas cancelar uma OS
            - **VALIDAÇÕES**: Todas as validações são feitas pela função principal alterar_status_os_siga_ia()
            - **MESMO COMPORTAMENTO**: Retorna exatamente o mesmo XML de alterar_status_os_siga_ia()
            - **ATENÇÃO**: Esta operação modifica permanentemente o status da OS para um estado de cancelamento
            - **DIFERENCIAÇÃO DE FUNÇÃO**: Esta é uma função específica para cancelamento. Para outras alterações de status, use alterar_status_os_siga_ia()
            - A função aceita apenas status de cancelamento válidos (Cancelada-Usuário, Cancelamento DTD | Arquivado)
            - A validação de tipo_cancelamento é case-insensitive (não diferencia maiúsculas/minúsculas)
            - Esta função funciona para OS de qualquer área (Sistemas ou Infraestrutura)
            - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
            - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
        """)

from textwrap import dedent


def docs() -> str:
    return dedent("""\
        Conclui uma Ordem de Serviço no sistema SIGA.

        **INSTRUÇÃO PARA O AGENTE IA:**
        ANTES de executar esta função:
        1. SEMPRE chame primeiro `buscar_informacoes_os(codigo_os)` para verificar se a OS existe
        2. MOSTRE ao usuário as informações da OS encontrada, incluindo o status atual
        3. PEÇA confirmação explícita do usuário: "Confirma a conclusão da OS {{codigo_os}}? (sim/não)"
        4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
        5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada

        Esta é uma função de conveniência para concluir uma OS. Internamente chama alterar_status_os_siga_ia()
        com status de conclusão para melhor experiência do usuário.

        **ORIENTAÇÃO PARA SOLICITAÇÕES:**
        - "Concluir OS 123" → Usar esta função
        - "Finalizar OS 456" → Usar esta função  
        - "Marcar OS 789 como concluída" → Usar esta função
        - "Fechar OS 321" → Usar esta função

        Args:
            codigo_os:  Código da OS a ser concluída
            tipo_conclusao: Tipo de conclusão

        Notes:
            - **FUNÇÃO DE CONVENIÊNCIA**: Internamente chama alterar_status_os_siga_ia()
            - **UX MELHORADA**: Mais intuitivo para usuários que querem apenas concluir uma OS
            - **VALIDAÇÕES**: Todas as validações são feitas pela função principal alterar_status_os_siga_ia()
            - **MESMO COMPORTAMENTO**: Retorna exatamente o mesmo XML de alterar_status_os_siga_ia()
            - **ATENÇÃO**: Esta operação modifica permanentemente o status da OS para um estado de conclusão
            - **DIFERENCIAÇÃO DE FUNÇÃO**: Esta é uma função específica para conclusão. Para outras alterações de status, use alterar_status_os_siga_ia()
            - A função aceita apenas status de conclusão válidos (Concluída, Concluída por Encaminhamento, Concluída por substituição)
            - A validação de tipo_conclusao é case-insensitive (não diferencia maiúsculas/minúsculas)
            - Esta função funciona para OS de qualquer área (Sistemas ou Infraestrutura)
            - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
            - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
        """)

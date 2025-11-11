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

        **Endpoint utilizado:** `updateStatusOsSigaIA` (via alterar_status_os_siga_ia)

        **Estrutura do XML retornado:**
        
        **Sucesso:**
        ```xml
        <ordens_servico codigo_os="123" status_anterior="Em Andamento" status_novo="Concluída" sistema="SIGA">
            <ordem_servico sistema="SIGA">
                <status>sucesso</status>
                <mensagem>OS 123 foi concluída com sucesso!</mensagem>
                <detalhes>Status alterado de 'Em Andamento' para 'Concluída'</detalhes>
            </ordem_servico>
        </ordens_servico>
        ```

        **Em caso de erro de validação (OS não encontrada):**
        ```xml
        <erro_validacao sistema="SIGA" funcao="alterar_status_os_siga_ia">
            <erro sistema="SIGA">
                <status>erro</status>
                <tipo_erro>os_nao_encontrada</tipo_erro>
                <codigo_os>999</codigo_os>
                <mensagem>OS 999 não encontrada no sistema SIGA</mensagem>
            </erro>
        </erro_validacao>
        ```

        **Em caso de erro de validação (tipo de conclusão inválido):**
        ```xml
        <erro_validacao sistema="SIGA" funcao="alterar_status_os_siga_ia">
            <erro sistema="SIGA">
                <status>erro</status>
                <tipo_erro>status_invalido</tipo_erro>
                <status_informado>Tipo Inválido</status_informado>
                <mensagem>Status 'Tipo Inválido' não encontrado na constante STATUS_OS_TO_NUMBER</mensagem>
                <status_validos>['Não Planejada', 'Pendente-Atendimento', 'Em Atendimento', 'Pendente-Teste', 'Em Teste', 'Pendente-Liberação', 'Em Implantação', 'Concluída', 'Concluída por Encaminhamento', 'Concluída por substituição', 'Pendente-Help-Desk', 'Pendente-Equipe Manutenção', 'Pendente-Marketing', 'Pendente-Sist. Acadêmicos', 'Pendente-Sist. Administrativos', 'Pendente-Consultoria', 'Pendente-Atualização de Versão', 'Pendente-AVA', 'Pendente-Equipe Infraestrutura', 'Pendente-Aprovação', 'Pendente-Fornecedor', 'Pendente-Usuário', 'Cancelamento DTD | Arquivado', 'Cancelada-Usuário', 'Solicitação em Aprovação']</status_validos>
            </erro>
        </erro_validacao>
        ```

        **Em caso de erro (dados inválidos):**
        ```xml
        <ordens_servico codigo_os="123" status_anterior="Em Andamento" status_novo="Concluída" sistema="SIGA">
            <ordem_servico sistema="SIGA">
                <status>erro</status>
                <mensagem>Não foi possível alterar o status da OS 123. Verifique as informações digitadas.</mensagem>
            </ordem_servico>
        </ordens_servico>
        ```

        **Em caso de outros erros:**
        ```xml
        <ordens_servico codigo_os="123" status_anterior="Em Andamento" status_novo="Concluída" sistema="SIGA">
            <ordem_servico sistema="SIGA">
                <status>erro</status>
                <mensagem>Erro ao alterar status da OS 123. Tente novamente.</mensagem>
            </ordem_servico>
        </ordens_servico>
        ```

        Args:
            codigo_os (str | int): **[OBRIGATÓRIO]** Código da OS a ser concluída
            tipo_conclusao (str): Tipo de conclusão (padrão: "Concluída"). Opções válidas:
                - "Concluída" (código 8) - padrão
                - "Concluída por Encaminhamento" (código 9)
                - "Concluída por substituição" (código 10)

        Returns:
            str: XML formatado com resultado da operação (mesmo formato de alterar_status_os_siga_ia):
                - Em caso de sucesso: confirmação da conclusão com detalhes da operação
                - Em caso de erro de validação: detalhes do erro (OS não encontrada, tipo de conclusão inválido, etc.)
                - Em caso de erro de API: mensagem de erro específica
                - Em caso de erro interno: mensagem de erro genérica

                O XML sempre inclui os parâmetros da operação como atributos do elemento raiz.

        Raises:
            Não levanta exceções diretamente. Todos os erros são capturados e retornados
            como XML formatado com informações detalhadas do erro.

        Examples:
            >>> # Concluir OS com status padrão
            >>> resultado = await concluir_os_siga_ia("123")
            
            >>> # Concluir OS com tipo específico
            >>> resultado = await concluir_os_siga_ia("456", "Concluída por Encaminhamento")

            >>> # Concluir OS com tipo de substituição
            >>> resultado = await concluir_os_siga_ia("789", "Concluída por substituição")

            >>> # Exemplo com tipo inválido (retorna erro)
            >>> resultado = await concluir_os_siga_ia("123", "Tipo Inexistente")  # Erro!

            >>> # Exemplo com código OS vazio (retorna erro)
            >>> resultado = await concluir_os_siga_ia("", "Concluída")  # Erro!

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

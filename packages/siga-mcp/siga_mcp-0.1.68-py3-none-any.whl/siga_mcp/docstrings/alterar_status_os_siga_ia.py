from textwrap import dedent


def docs() -> str:
    return dedent("""\
        Altera o status de uma Ordem de Serviço no sistema SIGA para qualquer status válido.

        **INSTRUÇÃO PARA O AGENTE IA:**
        ANTES de executar esta função:
        1. SEMPRE chame primeiro `buscar_informacoes_os(codigo_os)` para verificar se a OS existe
        2. MOSTRE ao usuário as informações da OS encontrada, incluindo o status atual
        3. PEÇA confirmação explícita do usuário: "Confirma a alteração do status da OS {{codigo_os}} de '{{status_atual}}' para '{{novo_status}}'? (sim/não)"
        4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
        5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada

        Esta função permite alterar o status de uma OS (Ordem de Serviço) existente no sistema SIGA
        para qualquer status válido disponível no sistema. Funciona para OS de qualquer área (Sistemas ou Infraestrutura).

        **ORIENTAÇÃO PARA SOLICITAÇÕES:**
        - "Alterar status da OS 123 para Em Teste" → Usar esta função
        - "Mudar OS 456 para Pendente-Aprovação" → Usar esta função  
        - "Colocar OS 789 em Pendente-Liberação" → Usar esta função
        - "Concluir OS 321" → Usar concluir_os_siga_ia() para melhor UX
        - "Cancelar OS 654" → Usar cancelar_os_siga_ia() para melhor UX

        **Endpoint utilizado:** `updateStatusOsSigaIA`

        **Estrutura do XML retornado:**
        
        **Sucesso:**
        ```xml
        <ordens_servico codigo_os="123" status_anterior="Em Andamento" status_novo="Em Teste" sistema="SIGA">
            <ordem_servico sistema="SIGA">
                <status>sucesso</status>
                <mensagem>OS 123 foi alterada com sucesso!</mensagem>
                <detalhes>Status alterado de 'Em Andamento' para 'Em Teste'</detalhes>
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

        **Em caso de erro de validação (status inválido):**
        ```xml
        <erro_validacao sistema="SIGA" funcao="alterar_status_os_siga_ia">
            <erro sistema="SIGA">
                <status>erro</status>
                <tipo_erro>status_invalido</tipo_erro>
                <status_informado>Status Inválido</status_informado>
                <mensagem>Status 'Status Inválido' não encontrado na constante STATUS_OS_TO_NUMBER</mensagem>
                <status_validos>['Não Planejada', 'Pendente-Atendimento', 'Em Atendimento', 'Pendente-Teste', 'Em Teste', 'Pendente-Liberação', 'Em Implantação', 'Concluída', 'Concluída por Encaminhamento', 'Concluída por substituição', 'Pendente-Help-Desk', 'Pendente-Equipe Manutenção', 'Pendente-Marketing', 'Pendente-Sist. Acadêmicos', 'Pendente-Sist. Administrativos', 'Pendente-Consultoria', 'Pendente-Atualização de Versão', 'Pendente-AVA', 'Pendente-Equipe Infraestrutura', 'Pendente-Aprovação', 'Pendente-Fornecedor', 'Pendente-Usuário', 'Cancelamento DTD | Arquivado', 'Cancelada-Usuário', 'Solicitação em Aprovação']</status_validos>
            </erro>
        </erro_validacao>
        ```

        **Em caso de erro de validação (campo obrigatório):**
        ```xml
        <erro_validacao sistema="SIGA" funcao="alterar_status_os_siga_ia">
            <erro sistema="SIGA">
                <status>erro</status>
                <tipo_erro>codigo_os_obrigatorio</tipo_erro>
                <campo_invalido>codigo_os</campo_invalido>
                <valor_informado></valor_informado>
                <mensagem>Campo 'codigo_os' é obrigatório. Valor informado: </mensagem>
            </erro>
        </erro_validacao>
        ```

        **Em caso de erro (dados inválidos):**
        ```xml
        <ordens_servico codigo_os="123" status_anterior="Em Andamento" status_novo="Em Teste" sistema="SIGA">
            <ordem_servico sistema="SIGA">
                <status>erro</status>
                <mensagem>Não foi possível alterar o status da OS 123. Verifique as informações digitadas.</mensagem>
            </ordem_servico>
        </ordens_servico>
        ```

        **Em caso de outros erros:**
        ```xml
        <ordens_servico codigo_os="123" status_anterior="Em Andamento" status_novo="Em Teste" sistema="SIGA">
            <ordem_servico sistema="SIGA">
                <status>erro</status>
                <mensagem>Erro ao alterar status da OS 123. Tente novamente.</mensagem>
            </ordem_servico>
        </ordens_servico>
        ```

        Args:
            codigo_os (str | int): **[OBRIGATÓRIO]** Código/número da OS (Ordem de Serviço) que terá o status alterado
            novo_status (str): **[OBRIGATÓRIO]** Novo status a ser aplicado à OS. Deve ser um dos status válidos:
                **WORKFLOW NORMAL:**
                - "Não Planejada" (código 1)
                - "Pendente-Atendimento" (código 2)
                - "Em Atendimento" (código 3)
                - "Pendente-Teste" (código 4)
                - "Em Teste" (código 5)
                - "Pendente-Liberação" (código 6)
                - "Em Implantação" (código 7)

                **STATUS DE CONCLUSÃO:**
                - "Concluída" (código 8)
                - "Concluída por Encaminhamento" (código 9)
                - "Concluída por substituição" (código 10)

                **STATUS DE PENDÊNCIA:**
                - "Pendente-Help-Desk" (código 87)
                - "Pendente-Equipe Manutenção" (código 88)
                - "Pendente-Marketing" (código 89)
                - "Pendente-Sist. Acadêmicos" (código 90)
                - "Pendente-Sist. Administrativos" (código 91)
                - "Pendente-Consultoria" (código 92)
                - "Pendente-Atualização de Versão" (código 93)
                - "Pendente-AVA" (código 94)
                - "Pendente-Equipe Infraestrutura" (código 95)
                - "Pendente-Aprovação" (código 96)
                - "Pendente-Fornecedor" (código 97)
                - "Pendente-Usuário" (código 98)
                - "Solicitação em Aprovação" (código 101)

                **STATUS DE CANCELAMENTO:**
                - "Cancelamento DTD | Arquivado" (código 99)
                - "Cancelada-Usuário" (código 100)

        Returns:
            str: XML formatado contendo:
                - Em caso de sucesso: confirmação da alteração com detalhes da operação
                - Em caso de erro de validação: detalhes do erro (OS não encontrada, status inválido, etc.)
                - Em caso de erro de API: mensagem de erro específica
                - Em caso de erro interno: mensagem de erro genérica

                O XML sempre inclui os parâmetros da operação como atributos do elemento raiz.

        Raises:
            Não levanta exceções diretamente. Todos os erros são capturados e retornados
            como XML formatado com informações detalhadas do erro.

        Examples:
            >>> # Alterar para status de workflow
            >>> xml = await alterar_status_os_siga_ia("123", "Em Teste")

            >>> # Alterar para status de pendência
            >>> xml = await alterar_status_os_siga_ia("456", "Pendente-Aprovação")

            >>> # Alterar para status de implantação
            >>> xml = await alterar_status_os_siga_ia("789", "Em Implantação")

            >>> # Concluir uma OS
            >>> xml = await alterar_status_os_siga_ia("321", "Concluída")

            >>> # Cancelar uma OS
            >>> xml = await alterar_status_os_siga_ia("654", "Cancelada-Usuário")

            >>> # Exemplo com status inválido (retorna erro)
            >>> xml = await alterar_status_os_siga_ia("123", "Status Inexistente")  # Erro!

            >>> # Exemplo com código OS vazio (retorna erro)
            >>> xml = await alterar_status_os_siga_ia("", "Em Teste")  # Erro!

        Notes:
            - **ATENÇÃO**: Esta operação modifica permanentemente o status da OS
            - **DIFERENCIAÇÃO DE FUNÇÃO**: Esta função altera apenas o status. Para editar outros dados da OS, use editar_os_sistemas ou editar_os_infraestrutura
            - **VALIDAÇÃO PRÉVIA**: A função primeiro verifica se a OS existe usando buscar_informacoes_os()
            - **CAMPOS OBRIGATÓRIOS**: codigo_os e novo_status são obrigatórios
            - **MAPEAMENTO AUTOMÁTICO**: Os status em texto são automaticamente convertidos para códigos numéricos
            - **FEEDBACK RICO**: Retorna informações detalhadas da operação incluindo status anterior e novo
            - **CASE-INSENSITIVE**: A validação de status é case-insensitive (não diferencia maiúsculas/minúsculas)
            - A função realiza validação case-insensitive do status usando a constante STATUS_OS_TO_NUMBER
            - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
            - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
            - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente
            - Esta função funciona para OS de qualquer área (Sistemas ou Infraestrutura)
            - Utiliza a constante STATUS_OS_TO_NUMBER para mapear valores para códigos numéricos
            - Todos os parâmetros enviados são incluídos como atributos no XML de resposta
        """)

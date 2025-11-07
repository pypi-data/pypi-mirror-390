from siga_mcp.dynamic_constants import PROJETO_TO_NUMBER
from siga_mcp.dynamic_constants import USUARIOS_SISTEMAS_DOCSTRING
from siga_mcp.utils import montar_string
from textwrap import dedent


def docs() -> str:
    return dedent(f"""\
        Edita uma Ordem de Serviço existente no sistema SIGA para a área de Sistemas.

        **INSTRUÇÃO PARA O AGENTE IA:**
        ANTES de executar esta função de edição:
        1. SEMPRE chame primeiro `buscar_informacoes_os(codigo_os)`
        2. MOSTRE ao usuário os dados atuais vs. dados que serão alterados em formato claro e comparativo
        3. PEÇA confirmação explícita do usuário: "Confirma as alterações? (sim/não)"
        4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
        5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada

        Esta função edita uma OS (Ordem de Serviço) existente para **ÁREA SISTEMAS** (área=1),
        atualizando informações como datas, descrição, tipo, origem, sistema, linguagem, equipe, projeto e responsável.
        Realiza validação de todos os campos obrigatórios e conversão automática de datas.

        **ORIENTAÇÃO PARA SOLICITAÇÕES GENÉRICAS:**
        Quando o usuário solicitar "editar OS" sem especificar área:
        1. **Perguntar qual área**: Sistemas (1) ou Infraestrutura (2)
        2. **Se escolher Sistemas**: Usar esta função
        3. **Se escolher Infraestrutura**: Direcionar para `editar_os_infraestrutura`

        **Endpoint utilizado:** `updateOsSigaIA`

        **Estrutura do XML retornado:**
        
        **Sucesso:**
        ```xml
        <ordens_servico numeroOS="12345" dtSolicitacao="15/05/2025 10:09:00" assunto="Implementação novo módulo AVA"
                        descricao="Desenvolver funcionalidade de relatórios avançados"
                        matSolicitante="123456" tipo="15" origem="3" equipe="SGA" 
                        responsavel="789" sistema="67" linguagem="1" projeto="61">
            <ordem_servico sistema="SIGA">
                <status>sucesso</status>
                <mensagem>OS editada com sucesso!</mensagem>
            </ordem_servico>
        </ordens_servico>
        ```

        **Em caso de erro de validação (campo inválido):**
        ```xml
        <erro_validacao sistema="SIGA" funcao="editar_os_sistemas">
            <erro sistema="SIGA">
                <status>erro</status>
                <tipo_erro>tipo_invalido</tipo_erro>
                <tipo_informado>Tipo Inválido</tipo_informado>
                <mensagem>Tipo 'Tipo Inválido' não encontrado na constante TIPO_TO_NUMBER_OS_SISTEMAS</mensagem>
                <tipos_validos>['Implementação', 'Manutenção Corretiva', 'Monitoramento', 'Mudança de Escopo', 'Suporte Infraestrutura', 'Suporte Sistema', 'Treinamento']</tipos_validos>
            </erro>
        </erro_validacao>
        ```

        **Em caso de erro de validação (matSolicitante obrigatório):**
        ```xml
        <erro_validacao sistema="SIGA" funcao="editar_os_sistemas">
            <erro sistema="SIGA">
                <status>erro</status>
                <tipo_erro>mat_solicitante_obrigatorio</tipo_erro>
                <campo_invalido>matSolicitante</campo_invalido>
                <valor_informado>0</valor_informado>
                <mensagem>Campo 'matSolicitante' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: 0</mensagem>
            </erro>
        </erro_validacao>
        ```

        **Em caso de erro de validação (criada_por obrigatório):**
        ```xml
        <erro_validacao sistema="SIGA" funcao="editar_os_sistemas">
            <erro sistema="SIGA">
                <status>erro</status>
                <tipo_erro>criada_por_obrigatorio</tipo_erro>
                <campo_invalido>criada_por</campo_invalido>
                <valor_informado>abc</valor_informado>
                <mensagem>Campo 'criada_por' é obrigatório e deve ser 'CURRENT_USER' ou um número válido maior que zero. Valor informado: abc</mensagem>
            </erro>
        </erro_validacao>
        ```

        **Em caso de erro (dados inválidos):**
        ```xml
        <ordens_servico numeroOS="12345" dtSolicitacao="15/05/2025 10:09:00" assunto="Implementação novo módulo AVA"
                        matSolicitante="123456" tipo="15" descricao="Descrição"
                        origem="3" equipe="SGA" responsavel="789" sistema="67" linguagem="1" projeto="61">
            <ordem_servico sistema="SIGA">
                <status>erro</status>
                <mensagem>Não foi possível editar a OS. Verifique as informações digitadas.</mensagem>
            </ordem_servico>
        </ordens_servico>
        ```

        **Em caso de outros erros:**
        ```xml
        <ordens_servico numeroOS="12345" dtSolicitacao="15/05/2025 10:09:00" assunto="Implementação novo módulo AVA"
                        matSolicitante="123456" tipo="15" descricao="Descrição"
                        origem="3" equipe="SGA" responsavel="789" sistema="67" linguagem="1" projeto="61">
            <ordem_servico sistema="SIGA">
                <status>erro</status>
                <mensagem>Erro ao editar a OS. Tente novamente.</mensagem>
            </ordem_servico>
        </ordens_servico>
        ```

        Args:
            codigo_os (str | int): **[OBRIGATÓRIO]** Código/número da OS (Ordem de Serviço) que será editada
            data_solicitacao (str): Data e hora da solicitação da OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            assunto (str): Descrição resumida (título) da OS
            descricao (str): Descrição detalhada da OS a ser realizada
            matSolicitante (str | Literal["CURRENT_USER"]): **[OBRIGATÓRIO]** Matrícula do usuário que está solicitando a OS.
            Deve ser "CURRENT_USER" ou um número válido maior que zero. Não aceita valores vazios, "0" ou não-numéricos.
            responsavel (str | Literal["CURRENT_USER"]): Matrícula do usuário responsável pela OS
            {USUARIOS_SISTEMAS_DOCSTRING}
            responsavel_atual (str | Literal["CURRENT_USER"]): Matrícula do usuário responsável atual pela OS
            {USUARIOS_SISTEMAS_DOCSTRING}
            criada_por (str | Literal["CURRENT_USER"]): **[OBRIGATÓRIO]** Matrícula do usuário que criou a OS.
            Deve ser "CURRENT_USER" ou um número válido maior que zero. Não aceita valores vazios, "0" ou não-numéricos.
            prioridade (str | None): Código da Solicitação prioritária da OS
            tempo_previsto (int | None): Cálculo do tempo previsto para a conclusão da OS
            data_inicio_previsto (str | None): Data e hora previsto para iniciar a OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            data_limite (str | None): Data e hora limite para realização da OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            sprint (str | None): Descrição dos sprints
            os_predecessora (str | None): Código da OS predecessora da OS em andamento
            chamado_fornecedor (str | None): Código do chamado do fornecedor
            rotinas (str | None): Descrição da rotina
            os_principal (str | None): Código da OS principal
            classificacao (str | None): Classificação da OS
            nova (str | None): Código para verificar se a OS é nova ou transferência de responsável atual
            data_previsao_entrega (str | None): Data e hora da previsão de entrega da OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            modulo (str | None): Módulo da OS
            tempo_restante (str | None): Tempo restante para concluir a OS
            ramal (str | None): Número do Ramal
            data_envio_email_conclusao (str | None): Data e hora para o envio do email de conclusão da OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            tipo_transacao (str | None): código do tipo da transação
            acao (str | None): código da ação
            planejamento (str | None): Descrição do Planejamento da OS
            grupo (str | None): Grupo da OS
            sistema (Literal): Sistema relacionado à OS, deve ser um dos valores válidos disponíveis na constante SISTEMA_TO_NUMBER:
                - "Sistemas AVA" (padrão)
                - "SGA - Acadêmico"
                - "RMS (Requisições, Materiais e Serviços)"
                - "SGA - Financeiro"
                - "Recursos Humanos"
                - "Financeiro e Contábil"
                - "Saúde"
                - "SGA - Web"
                - E muitos outros sistemas disponíveis na constante
            tipo (Literal): Tipo da OS, deve ser um dos valores válidos:
                - "Implementação" (código 15) - padrão
                - "Manutenção Corretiva" (código 17)
                - "Monitoramento" (código 22)
                - "Mudança de Escopo" (código 25)
                - "Suporte Infraestrutura" (código 26)
                - "Suporte Sistema" (código 14)
                - "Treinamento" (código 18)
            equipe (Literal): Equipe responsável pela OS:
                - "SGA - Acadêmico" (código SGA)
                - "RMS (Requisições, Materiais e Serviços)" (código RMS)
                - "SGA - Financeiro" (código SGA-FIN)
                - "Recursos Humanos" (código RH)
                - "Financeiro e Contábil" (código FINANC)
                - "Saúde" (código SAUDE)
                - "SGA - Web" (código WEB)
                - "Administador de Banco de Dados" (código DBA)
                - "Escritório de Projetos" (código PMO)
                - "Analytics" (código ANALY)
                - "Equipe AVA" (código AVA) - padrão
            linguagem (Literal): Linguagem de programação/tecnologia da OS, deve ser um dos valores válidos:
                - "C#" (código 1)
                - "Fox" (código 2)
                - "SQL" (código 3)
                - "ASP.Net" (código 4)
                - "Access" (código 5)
                - "PHP" (código 6) - padrão
                - "Extrator de Dados" (código 7)
                - "MV Painel de Indicadores" (código 8)
                - "MV Editor" (código 9)
                - "Gerador de Relatórios" (código 10)
                - "Gerador de Cubos" (código 11)
                - "Power BI" (código 12)
                - "Gerador de Tela" (código 13)
                - "Editor de Regra" (código 14)
                - "Delphi" (código 15)
                - "Script SO" (código 16)
                - "Node.js" (código 17)
                - "Senior - Gerador de visão dinâmica" (código 18)
                - "Analytics" (código 19)
            projeto (Literal): Projeto relacionado à OS:
                {montar_string(PROJETO_TO_NUMBER)} O padrão é: "Operação AVA"
            status (Literal): Status da OS, deve ser um dos valores válidos:
                - "Não Planejada" (código 1)
                - "Pendente-Atendimento" (código 2)
                - "Em Atendimento" (código 3) - padrão
                - "Pendente-Teste" (código 4)
                - "Em Teste" (código 5)
                - "Pendente-Liberação" (código 6)
                - "Em Implantação" (código 7)
                - "Concluída" (código 8)
                - "Concluída por Encaminhamento" (código 9)
                - "Concluída por substituição" (código 10)
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
                - "Cancelamento DTD | Arquivado" (código 99)
                - "Cancelada-Usuário" (código 100)
                - "Solicitação em Aprovação" (código 101)
            os_interna (Literal): Indica se a OS é interna, deve ser um dos valores válidos:
                - "Não" (código 0)
                - "Sim" (código 1) - padrão
            criticidade (Literal): Criticidade da OS, deve ser um dos valores válidos:
                - "Nenhuma" (código 0) - padrão
                - "Baixa" (código 1)
                - "Média" (código 2)
                - "Alta" (código 3)    
            prioridade_usuario (Literal): Prioridade definida pelo usuário, deve ser um dos valores válidos:
                - "Nenhuma" (código 0) - padrão
                - "Urgente" (código 1)
                - "Alta" (código 2)
                - "Média" (código 3)
                - "Baixa" (código 4)
            origem (Literal): Origem da solicitação da OS, deve ser um dos valores válidos:
                - "E-mail" (código 1)
                - "Pessoalmente" (código 2)
                - "Teams" (código 3) - padrão
                - "Telefone" (código 4)
                - "WhatsApp" (código 5)
                - "Siga" (código 6)
                - "Plantão" (código 7)
                - "SATIC" (código 8)
                - "SAE" (código 11)
        Returns:
            str: XML formatado contendo:
                - Em caso de sucesso: confirmação da edição com status "sucesso"
                - Em caso de erro de validação: detalhes do erro (tipo inválido, matSolicitante obrigatório, criada_por obrigatório, responsável inválido, sistema inválido, linguagem inválida, etc.)
                - Em caso de erro de API: mensagem de erro específica
                - Em caso de erro interno: mensagem de erro genérica

                O XML sempre inclui os parâmetros enviados como atributos do elemento raiz.

        Raises:
            Não levanta exceções diretamente. Todos os erros são capturados e retornados
            como XML formatado com informações detalhadas do erro.

        Examples:
            >>> # Editar OS de sistemas existente
            >>> xml = await editar_os_sistemas(
            ...     codigo_os="12345",
            ...     data_solicitacao="hoje 09:00",
            ...     assunto="Implementação novo módulo AVA - ATUALIZADO",
            ...     descricao="Desenvolver funcionalidade de relatórios avançados - requisitos atualizados",
            ...     matSolicitante="654321",
            ...     tipo="Implementação",
            ...     sistema="Sistemas AVA",
            ...     linguagem="PHP",
            ...     equipe="Equipe AVA",
            ...     projeto="Operação AVA"
            ... )

            >>> # Exemplo com tipo inválido (retorna erro)
            >>> xml = await editar_os_sistemas(
            ...     codigo_os="12345",
            ...     data_solicitacao="2024-01-15 09:00:00",
            ...     assunto="Teste",
            ...     descricao="Teste de OS",
            ...     matSolicitante="123456",
            ...     tipo="Tipo Inexistente"  # Erro!
            ... )

            >>> # Exemplo com matSolicitante inválido (retorna erro)
            >>> xml = await editar_os_sistemas(
            ...     codigo_os="12345",
            ...     data_solicitacao="2024-01-15 09:00:00",
            ...     assunto="Teste",
            ...     descricao="Teste de OS",
            ...     matSolicitante="0",  # Erro!
            ...     responsavel="123456",
            ...     responsavel_atual="123456"
            ... )

        Notes:
            - **ATENÇÃO**: Esta operação modifica permanentemente os dados da OS
            - **DIFERENCIAÇÃO DE FUNÇÃO**: Esta função edita OS existente para área sistemas (área=1). Para criar nova, use inserir_os_sistemas. Para buscar informações de uma OS, use buscar_informacoes_os
            - **VALIDAÇÕES OBRIGATÓRIAS**: Campos matSolicitante e criada_por devem ser "CURRENT_USER" ou números válidos maiores que zero (não aceita valores vazios, "0" ou não-numéricos)
            - A função realiza validação case-insensitive de todos os campos (tipo, origem, sistema, linguagem, equipe, projeto) 
            - As datas são automaticamente convertidas usando converter_data_siga com manter_horas=True 
            - Utiliza as constantes: TIPO_TO_NUMBER_OS_SISTEMAS, SISTEMA_TO_NUMBER, EQUIPE_TO_NUMBER, LINGUAGEM_TO_NUMBER_OS_SISTEMAS, PROJETO_TO_NUMBER, STATUS_OS_TO_NUMBER, OS_INTERNA_OS_TO_NUMBER, ORIGEM_OS_TO_NUMBER, PRIORIDADE_USUARIO_OS_TO_NUMBER, CRITICIDADE_OS_TO_NUMBER para mapear valores para códigos numéricos 
            - Todos os parâmetros enviados são incluídos como atributos no XML de resposta 
            - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY 
            - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML 
            - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente 
            - Campos opcionais como nomeSolicitante, centroCusto, etc. são enviados vazios por padrão 
            - Esta função atualiza OS (Ordens de Serviços) existentes para área de sistemas
        """)

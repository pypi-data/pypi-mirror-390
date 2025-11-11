from textwrap import dedent


def docs() -> str:
    return dedent("""\
            Edita as informações de um atendimento avulso infraestrutura existente no sistema SIGA.

            INSTRUÇÃO PARA O AGENTE IA:
            ANTES de executar esta função de edição:
            1. SEMPRE chame primeiro `buscar_informacoes_atendimento_avulso(codigo_atendimento, codigo_analista)`
            2. MOSTRE ao usuário os dados atuais vs. dados que serão alterados em formato claro e comparativo
            3. PEÇA confirmação explícita do usuário: "Confirma as alterações? (sim/não)"
            4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
            5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada
                  
            Esta função atualiza um registro de atendimento avulso independente de qualquer Ordem de Serviço, incluindo informações como datas, descrição, tipo, origem, categoria, equipe, projeto e plaqueta.
            Realiza validação de todos os campos obrigatórios e conversão automática de datas.
                  
            Funcionalidade de busca automática:
            Se o atendimento não for encontrado nesta função (atendimentos avulso infraestrutura), a mensagem de erro orientará a buscar nas funções editar_atendimentos_os ou editar_atendimento_avulso_sistemas, permitindo busca automática entre os tipos de atendimento.

            Args:
                codigo_atendimento: Código do atendimento avulso a ser editado.
                data_inicio: Data e hora de início do atendimento avulso. Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
                data_fim: Data e hora de fim do atendimento avulso. Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
                matricula_solicitante: Matrícula do usuário que está solicitando o atendimento avulso
                descricao_atendimento: Descrição detalhada do atendimento avulso a ser realizado
                codigo_analista: Matrícula do analista/usuário responsável pelo atendimento avulso
                tipo: Tipo do atendimento avulso, deve ser um dos valores válidos:
                   
                origem: Canal/origem do atendimento avulso, deve ser um dos valores válidos:
                categoria: Categoria relacionado ao atendimento avulso, deve ser um dos valores válidos.
                equipe: Equipe responsável pelo atendimento avulso, deve ser uma das equipes válidas.
                projeto: Projeto relacionado ao atendimento avulso, deve ser um dos valores válidos.
                plaqueta: Plaqueta relacionado ao equipamento que está sendo atendido.

            Notes:
                - ATENÇÃO: Esta operação modifica permanentemente os dados do atendimento
                - DIFERENCIAÇÃO DE TIPOS: Esta função é específica para atendimentos avulso infraestrutura. Para outros tipos, use as funções específicas
                - Para busca automática: Se não encontrar nesta função, use editar_atendimentos_os ou editar_atendimento_avulso_sistemas com os mesmos parâmetros
                - A função realiza validação case-insensitive de todos os campos (tipo, origem, categoria, equipe, projeto)
                - As datas são automaticamente convertidas usando converter_data_siga com manter_horas=True
                - Utiliza as constantes: TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA, ORIGEM_TO_NUMBER, CATEGORIA_TO_NUMBER, EQUIPE_INFRAESTRUTURA_TO_NUMBER, PROJETO_TO_NUMBER para mapear valores para códigos numéricos
                - Todos os parâmetros enviados são incluídos como atributos no XML de resposta
                - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
                - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
                - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente
                - Campos opcionais como nomeSolicitante, centroCusto, etc. são enviados vazios por padrão
                - Esta função edita atendimentos avulsos independentes, não vinculados a nenhuma OS
            """)

from siga_mcp.dynamic_constants import PROJETO_TO_NUMBER
from siga_mcp.dynamic_constants import USUARIOS_INFRAESTRUTURA_DOCSTRING
from siga_mcp.utils import montar_string
from textwrap import dedent


def docs() -> str:
    return dedent(f"""\
        Edita uma Ordem de Serviço existente no sistema SIGA para a área de Infraestrutura.

        **INSTRUÇÃO PARA O AGENTE IA:**
        ANTES de executar esta função de edição:
        1. SEMPRE chame primeiro `buscar_informacoes_os(codigo_os)`
        2. MOSTRE ao usuário os dados atuais vs. dados que serão alterados em formato claro e comparativo
        3. PEÇA confirmação explícita do usuário: "Confirma as alterações? (sim/não)"
        4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
        5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada

        Esta função edita uma OS (Ordem de Serviço) existente para **ÁREA INFRAESTRUTURA** (área=2),
        atualizando informações como datas, descrição, tipo, origem, categoria, equipe, projeto e responsável.
        Realiza validação de todos os campos obrigatórios e conversão automática de datas.

        **ORIENTAÇÃO PARA SOLICITAÇÕES GENÉRICAS:**
        Quando o usuário solicitar "editar OS" sem especificar área:
        1. **Perguntar qual área**: Sistemas (1) ou Infraestrutura (2)
        2. **Se escolher Infraestrutura**: Usar esta função
        3. **Se escolher Sistemas**: Direcionar para `editar_os_sistemas`

        Args:
            codigo_os: Código/número da OS (Ordem de Serviço) que será editada
            data_solicitacao: Data e hora da solicitação da OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            assunto: Descrição resumida (título) da OS
            descricao: Descrição detalhada da OS a ser realizada
            matSolicitante: Matrícula do usuário que está solicitando a OS.
            Deve ser "CURRENT_USER" ou um número válido maior que zero. Não aceita valores vazios, "0" ou não-numéricos.
            responsavel: Matrícula do usuário responsável pela OS.
            responsavel_atual: Matrícula do usuário responsável atual pela OS.
            criada_por: Matrícula do usuário que criou a OS.
            prioridade: Código da Solicitação prioritária da OS
            tempo_previsto: Cálculo do tempo previsto para a conclusão da OS
            data_inicio_previsto: Data e hora previsto para iniciar a OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            data_limite: Data e hora limite para realização da OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            sprint: Descrição dos sprints
            os_predecessora: Código da OS predecessora da OS em andamento
            chamado_fornecedor: Código do chamado do fornecedor
            rotinas: Descrição da rotina
            plaqueta: Plaqueta relacionado ao equipamento que está sendo atendido.
            os_principal: Código da OS principal
            classificacao: Classificação da OS
            nova: Código para verificar se a OS é nova ou transferência de responsável atual
            data_previsao_entrega: Data e hora da previsão de entrega da OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            modulo: Módulo da OS
            tempo_restante: Tempo restante para concluir a OS
            ramal: Número do Ramal
            data_envio_email_conclusao: Data e hora para o envio do email de conclusão da OS (Ordem de Serviço).
                Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
            tipo_transacao: código do tipo da transação
            acao: código da ação
            planejamento: Descrição do Planejamento da OS
            grupo: Grupo da OS
            tipo: Tipo da OS, deve ser um dos valores válidos:
            categoria: Categoria relacionado a OS, deve ser um dos valores válidos:
            equipe: Equipe responsável pela OS.
            projeto: Projeto relacionado à OS.
            status: Status da OS, deve ser um dos valores válidos.
            os_interna: Indica se a OS é interna, deve ser um dos valores válidos.
            criticidade: Criticidade da OS, deve ser um dos valores válidos.
            prioridade_usuario: Prioridade definida pelo usuário, deve ser um dos valores válidos.
            origem: Origem da solicitação da OS, deve ser um dos valores válidos.

        Notes:
            - **ATENÇÃO**: Esta operação modifica permanentemente os dados da OS
            - **DIFERENCIAÇÃO DE FUNÇÃO**: Esta função edita OS existente para área infraestrutura (área=2). Para criar nova, use inserir_os_infraestrutura. Para buscar informações de uma OS, use buscar_informacoes_os
            - **VALIDAÇÕES OBRIGATÓRIAS**: Campos matSolicitante e criada_por devem ser "CURRENT_USER" ou números válidos maiores que zero (não aceita valores vazios, "0" ou não-numéricos)
            - A função realiza validação case-insensitive de todos os campos (tipo, origem, categoria, equipe, projeto) 
            - As datas são automaticamente convertidas usando converter_data_siga com manter_horas=True 
            - Utiliza as constantes: TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA, CATEGORIA_TO_NUMBER, EQUIPE_INFRAESTRUTURA_TO_NUMBER, PROJETO_TO_NUMBER, STATUS_OS_TO_NUMBER, OS_INTERNA_OS_TO_NUMBER, ORIGEM_OS_TO_NUMBER, PRIORIDADE_USUARIO_OS_TO_NUMBER, CRITICIDADE_OS_TO_NUMBER para mapear valores para códigos numéricos 
            - Todos os parâmetros enviados são incluídos como atributos no XML de resposta 
            - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY 
            - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML 
            - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente 
            - Campos opcionais como nomeSolicitante, centroCusto, etc. são enviados vazios por padrão 
            - Esta função atualiza OS (Ordens de Serviços) existentes
        """)

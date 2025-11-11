def docs() -> str:
    return """
Edita as informações de um atendimento de Ordem de Serviço (OS) no sistema SIGA.

INSTRUÇÃO PARA O AGENTE IA:
ANTES de executar esta função de edição:
1. SEMPRE chame primeiro `buscar_informacoes_atendimentos_os(codigo_atendimento, codigo_analista)`
2. MOSTRE ao usuário os dados atuais vs. dados que serão alterados
3. PEÇA confirmação explícita do usuário: "Confirma as alterações? (sim/não)"
4. SÓ EXECUTE esta função se o usuário confirmar explicitamente

Esta função permite atualizar todos os campos de um atendimento existente, incluindo
datas, descrição, tipo, tempo gasto e flags de controle. Realiza validação do tipo
de atendimento e conversão automática de datas para o formato esperado pelo SIGA.

Args:
    codigo_atendimento: Código único do atendimento a ser editado
    codigo_os: Código da Ordem de Serviço à qual o atendimento pertence
    data_inicio: Data e hora de início do atendimento (formato aceito pelo converter_data_siga)
    codigo_analista: Matrícula do analista/usuário responsável pelo atendimento
    descricao_atendimento: Descrição detalhada do atendimento realizado
    tipo_atendimento: Tipo do atendimento, deve ser um dos valores válidos
    data_fim: Data e hora de fim do atendimento.
        Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem".
        Se None, será enviado como string vazia.
    primeiro_atendimento: Flag indicando se é o primeiro atendimento da OS.
    apresenta_solucao: Flag indicando se o atendimento apresenta solução.

Notes:
    - ATENÇÃO: Esta operação modifica permanentemente os dados do atendimento 
    - DIFERENCIAÇÃO DE TIPOS: Esta função é específica para atendimentos OS. Para atendimentos avulsos, use as funções específicas
    - Para busca automática: Se não encontrar nesta função, use as funções de edição de atendimento avulso com os mesmos parâmetros
    - A função realiza validação case-insensitive do tipo_atendimento
    - As datas são automaticamente convertidas usando converter_data_siga com manter_horas=True
    - A função utiliza a constante TYPE_TO_NUMBER para mapear tipos para códigos numéricos
    - Todos os parâmetros enviados são incluídos como atributos no XML de resposta
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
"""

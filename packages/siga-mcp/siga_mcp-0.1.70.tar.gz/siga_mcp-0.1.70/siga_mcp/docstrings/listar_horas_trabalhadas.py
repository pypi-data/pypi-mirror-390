def docs() -> str:
    return """
Calcula e lista o total de horas trabalhadas de um ou múltiplos analistas em um período específico.

Esta função consolida as horas trabalhadas de analista(s) considerando tanto os
atendimentos de Ordens de Serviço (OS) quanto os atendimentos avulsos realizados
no período especificado. Fornece um resumo completo da produtividade do(s) analista(s).
Suporta busca individual ou em lote para otimização de performance.

Args:
    matricula: 
        Matrícula do analista ou lista de matrículas dos analistas cujas horas
        trabalhadas serão calculadas. Se "CURRENT_USER", calcula para o usuário atual
        (matrícula do .env). Para múltiplos analistas, forneça uma lista de matrículas.
        Defaults to "CURRENT_USER".
    
    data_inicio: 
        Data de início do período para cálculo das horas.
        Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
        Este parâmetro é obrigatório.
    
    data_fim: 
        Data de fim do período para cálculo das horas.
        Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
        Este parâmetro é obrigatório.

Notes:
    - **OTIMIZAÇÃO**: Função otimizada para múltiplas matrículas - uma consulta em vez de N consultas
    - **COMPATIBILIDADE**: Mantém total compatibilidade com uso individual (uma matrícula)
    - **PERFORMANCE**: Para múltiplos analistas, utiliza consulta em lote no banco de dados
    - **INTEGRAÇÃO COM EQUIPES**: Use com extrair_matriculas_do_xml para relatórios de equipe completos
    - **FLUXO DE EQUIPES**: listar_usuarios_equipe_por_gerente → extrair_matriculas_do_xml → listar_horas_trabalhadas
    - As datas são automaticamente convertidas usando converter_data_siga() quando fornecidas
    - A função utiliza a API de cálculo de horas trabalhadas do sistema SIGA
    - O cálculo inclui tanto atendimentos de OS quanto atendimentos avulsos
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - Em caso de falha na requisição HTTP ou parsing JSON, retorna mensagem de erro simples
    - O parâmetro matricula aceita tanto valores individuais quanto listas
    - Os parâmetros data_inicio e data_fim são obrigatórios (não têm valor padrão)
    - A resposta da API é processada através do XMLBuilder para formatação consistente
    - Esta função é útil para relatórios de produtividade e controle de horas individuais ou por equipe
    - O resultado consolida informações de múltiplas fontes (OS e atendimentos avulsos)
    - **QTD_HORAS**: Formato "HH:MM" representando total de horas e minutos trabalhados
    - **ESCALABILIDADE**: Suporta desde consultas individuais até equipes inteiras em uma única chamada
"""

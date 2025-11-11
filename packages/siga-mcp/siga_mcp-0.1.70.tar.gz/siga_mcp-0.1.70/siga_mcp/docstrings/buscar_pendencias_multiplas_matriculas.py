def docs() -> str:
    return """
Busca pendências de lançamentos de atendimentos para múltiplas matrículas concorrentemente no sistema SIGA.

Esta função otimiza a consulta de pendências de lançamentos para vários analistas simultaneamente,
consolidando os dados detalhados de registros ausentes de Ordens de Serviço (OS), Atendimentos OS e 
Atendimentos Avulsos em um período específico. Executa requisições concorrentes para melhor performance 
e retorna dados completos das pendências (não apenas metadados).

Args: 
    matriculas: 
        Lista de matrículas dos analistas cujas pendências de lançamentos serão consultadas. Deve conter pelo menos uma matrícula válida. Não aceita "CURRENT_USER" individual, mas este é resolvido pela função base se necessário. Este parâmetro é obrigatório.

    dataIni: 
        Data de início do período para consulta das pendências.
        Aceita formatos de data padrão ou palavras-chave em português ("hoje", "ontem", etc.).
        Este parâmetro é obrigatório.

    dataFim: 
        Data de fim do período para consulta das pendências.
        Aceita formatos de data padrão ou palavras-chave em português ("hoje", "ontem", etc.).
        Este parâmetro é obrigatório.

Notes: 
    - DADOS COMPLETOS: Retorna datas e tipos específicos das pendências (não apenas metadados) 
    - OTIMIZAÇÃO DE PERFORMANCE: Execução concorrente 
    - 5-10x mais rápida que consultas sequenciais 
    - COMPATIBILIDADE: Use buscar_pendencias_lancamentos_atendimentos() para consultas individuais 
    - ROBUSTEZ: Falhas individuais não impedem o processamento das demais matrículas 
    - PARSING INTELIGENTE: Extrai dados completos do XML retornado pela função base 
    - CONTROLE DE ACESSO: Aplica @controlar_acesso_matricula automaticamente 
    - INTEGRAÇÃO COM EQUIPES: Use com extrair_matriculas_do_xml para relatórios detalhados de equipe 
    - ESCALABILIDADE: Suporta desde pequenas equipes até departamentos inteiros com dados completos 
    - MONITORAMENTO AVANÇADO: Fornece estatísticas + dados reais das pendências por matrícula 
    - RELATÓRIOS GERENCIAIS: Ideal para análises detalhadas de produtividade e identificação de padrões 
    """

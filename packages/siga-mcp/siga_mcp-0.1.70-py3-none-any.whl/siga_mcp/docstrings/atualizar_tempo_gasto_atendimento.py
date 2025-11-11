def docs() -> str:
    return """
Atualiza o tempo gasto dos atendimentos de um analista em uma data específica no sistema SIGA.

Esta função recalcula automaticamente o tempo total gasto por um analista em todos os seus 
atendimentos (avulsos e OS) em uma data específica. É utilizada principalmente após 
inserções, edições ou exclusões de atendimentos para manter a consistência dos dados.

Funcionalidade:
- Recalcula tempo gasto de TODOS os atendimentos do analista na data especificada
- Atualiza tanto atendimentos avulsos quanto atendimentos de OS
- Se data_inicio não for informada, utiliza a data de ontem por padrão
- Operação atômica: garante consistência dos dados através de transações

Args: 
    codigo_analista (int): Código/matrícula do analista cujo tempo gasto será recalculado. 
        Deve corresponder a um analista válido no sistema SIGA. 
    data_inicio (str | None, optional): Data para recálculo do tempo gasto no formato DD/MM/YYYY. 
        Aceita formatos de data ou palavras-chave como "hoje", "ontem", "agora". Se None ou não informado, utiliza a data de ontem por padrão. Defaults to None.

Notes: 
    - OPERAÇÃO AUTOMÁTICA: Esta função é chamada automaticamente após inserções, edições e exclusões de atendimentos para manter consistência 
    - COMPORTAMENTO PADRÃO: Quando data_inicio não é informada, a procedure SEG.P_CALCULA_TEMPO_GASTO utiliza automaticamente a data de ontem 
    - TRANSAÇÃO SEGURA: Utiliza transações para garantir integridade dos dados 
    - PERFORMANCE: Recalcula apenas os atendimentos da data especificada, não todo o histórico do analista 
    - FLEXIBILIDADE DE DATA: Aceita diversos formatos de data através da função converter_data_siga com manter_horas=True 
    - ABRANGÊNCIA: Atualiza tanto atendimentos avulsos (sistemas e infraestrutura) quanto atendimentos de OS 
    - VALIDAÇÃO: Verifica se o analista existe antes de processar 
    - ATOMICIDADE: Se houver erro durante o recálculo, nenhuma alteração é mantida 
    - API KEY: Utiliza automaticamente a chave da variável de ambiente AVA_API_KEY 
    - TIMEOUT: Configurado para requisições assíncronas com tratamento de timeout 
    - LOGS: Retorna informações detalhadas para facilitar debug e monitoramento 
    - COMPATIBILIDADE: Funciona com todos os tipos de atendimento do sistema SIGA

"""

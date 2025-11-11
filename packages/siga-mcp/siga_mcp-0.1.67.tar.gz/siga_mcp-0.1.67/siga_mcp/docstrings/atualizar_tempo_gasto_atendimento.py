def docs() -> str:
    return """
Atualiza o tempo gasto dos atendimentos de um analista em uma data específica no sistema SIGA.

Esta função recalcula automaticamente o tempo total gasto por um analista em todos os seus 
atendimentos (avulsos e OS) em uma data específica. É utilizada principalmente após 
inserções, edições ou exclusões de atendimentos para manter a consistência dos dados.

**Funcionalidade:**
- Recalcula tempo gasto de TODOS os atendimentos do analista na data especificada
- Atualiza tanto atendimentos avulsos quanto atendimentos de OS
- Se data_inicio não for informada, utiliza a data de ontem por padrão
- Operação atômica: garante consistência dos dados através de transações

**Endpoint utilizado:** `atualizaTempoGastoAtendimentoAvulso`

**Estrutura do XML retornado:**

**Sucesso:**
```xml
<ordens_servico analista="789" dataIni="22/10/2024" sistema="SIGA">
    <ordem_servico sistema="SIGA">
        <status>sucesso</status>
        <mensagem>Tempo gasto atualizado com sucesso!</mensagem>
    </ordem_servico>
</ordens_servico>
```

**Em caso de erro da API (analista não encontrado, API key inválida, etc.):**
```xml
<ordens_servico analista="789" dataIni="22/10/2024" sistema="SIGA">
    <ordem_servico sistema="SIGA">
        <status>erro</status>
        <mensagem>Erro da API: Analista não encontrado na base de dados</mensagem>
    </ordem_servico>
</ordens_servico>
```
**Em caso de erro da API (sem detalhes específicos):**
```xml
<ordens_servico analista="789" dataIni="22/10/2024" sistema="SIGA">
    <ordem_servico sistema="SIGA">
        <status>erro</status>
        <mensagem>Erro da API: Tempo gasto não atualizado. Favor verificar informações digitadas.</mensagem>
    </ordem_servico>
</ordens_servico>
```

**Em caso de erro interno (falha de conexão, timeout, etc.):**
```xml
<resultado sistema="SIGA">
    <item sistema="SIGA">
        <status>erro</status>
        <mensagem>Erro interno: Connection timeout. Tente novamente mais tarde.</mensagem>
    </item>
</resultado>
```

Args: 
    codigo_analista (int): Código/matrícula do analista cujo tempo gasto será recalculado. 
        Deve corresponder a um analista válido no sistema SIGA. 
    data_inicio (str | None, optional): Data para recálculo do tempo gasto no formato DD/MM/YYYY. 
        Aceita formatos de data ou palavras-chave como "hoje", "ontem", "agora". Se None ou não informado, utiliza a data de ontem por padrão. Defaults to None.

Returns: 
    str: XML formatado contendo: 
        - Em caso de sucesso: confirmação da atualização com status "sucesso" 
        - Em caso de erro da API: status "erro" com mensagem específica do erro 
        - Em caso de erro interno: status "erro" com mensagem de erro técnico

    O XML sempre inclui os parâmetros enviados (analista e dataIni) como atributos 
    do elemento raiz para facilitar o debug e rastreamento.

Raises: 
    Não levanta exceções diretamente. Todos os erros são capturados e retornados como XML formatado com informações detalhadas do erro, incluindo erros de: 
        - Conexão de rede 
        - Timeout de requisição 
        - Resposta inválida da API 
        - Erros de validação do sistema SIGA

Examples: 
    >>> # Recalcular tempo gasto para ontem (comportamento padrão) 
    >>> xml = await atualizar_tempo_gasto_atendimento(codigo_analista=789)

    >>> # Recalcular tempo gasto para data específica
    >>> xml = await atualizar_tempo_gasto_atendimento(
    ...     codigo_analista=789,
    ...     data_inicio="01/12/2024"
    ... )

    >>> # Recalcular usando palavras-chave de data
    >>> xml = await atualizar_tempo_gasto_atendimento(
    ...     codigo_analista=456,
    ...     data_inicio="hoje"
    ... )

    >>> # Recalcular para ontem explicitamente
    >>> xml = await atualizar_tempo_gasto_atendimento(
    ...     codigo_analista=123,
    ...     data_inicio="ontem"
    ... )

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

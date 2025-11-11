def docs() -> str:
    return """
Lista todos os atendimentos de Ordens de Serviço (OS) de um usuário com filtros opcionais.

INSTRUÇÃO PARA O AGENTE IA:
Para solicitações GENÉRICAS de listagem de atendimentos:
1. SEMPRE execute AMBAS as funções: `listar_atendimentos_os` E `listar_atendimentos_avulsos`
2. Solicitações genéricas incluem: "liste meus atendimentos", "mostre meus lançamentos", "atendimentos de hoje/ontem/semana", etc.
3. COMBINE os resultados de forma organizada para dar visão completa ao usuário
4. Execute APENAS esta função quando o usuário especificar explicitamente "atendimentos OS" ou "atendimentos de ordem de serviço"
5. Use os mesmos filtros (datas, período) em ambas as funções para consistência

EXEMPLOS DE SOLICITAÇÕES QUE REQUEREM AMBAS AS FUNÇÕES:
- "Liste todos os meus atendimentos de hoje"
- "Mostre meus lançamentos da semana passada"  
- "Quais foram meus atendimentos de ontem?"
- "Atendimentos realizados este mês"

Esta função busca atendimentos vinculados a Ordens de Serviço realizados por um analista,
permitindo filtrar por OS específica, período de datas, ou buscar todos os atendimentos.
Diferente dos atendimentos avulsos, estes estão sempre associados a uma OS.


Args:
    matricula: Matrícula do usuário/analista cujos
        atendimentos de OS serão listados. Se "CURRENT_USER", busca atendimentos do usuário atual
            (matrícula do .env). Defaults to "CURRENT_USER".
    codigo_os: Código específico da Ordem de Serviço
        para filtrar atendimentos. Se None ou não fornecido, busca atendimentos
        de todas as OSs. Defaults to None.
    data_inicio: Data de início do período de busca.
        Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
        Se None, não aplica filtro de data inicial. Defaults to None.
    data_fim: Data de fim do período de busca.
        Aceita formatos de data ou palavras-chave "hoje" ou "ontem".
        Se None, não aplica filtro de data final. Defaults to None.

Notes:
    - As datas são automaticamente convertidas usando converter_data_siga() quando fornecidas
    - A função utiliza a API de atendimentos de OS do sistema SIGA
    - Atendimentos de OS são diferentes de atendimentos avulsos (vinculados a OSs específicas)
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - Em caso de falha na requisição HTTP ou parsing JSON, retorna mensagem de erro simples
    - Todos os parâmetros são opcionais, permitindo buscas flexíveis
    - Parâmetros None ou vazios são enviados como strings vazias para a API
    - O parâmetro matricula usa o tipo Literal["CURRENT_USER"] para permitir valores verdadeiramente opcionais
    - A resposta da API é processada através do XMLBuilder para formatação consistente
    - Os atributos do XML de resposta refletem exatamente os filtros aplicados na busca
"""

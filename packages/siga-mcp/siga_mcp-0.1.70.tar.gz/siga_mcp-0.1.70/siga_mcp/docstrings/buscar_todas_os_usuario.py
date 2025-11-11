def docs() -> str:
    return """
Busca Ordens de Serviço (OS) do sistema SIGA com filtros avançados e flexíveis.

Esta função oferece uma interface completa para consulta de OS no sistema SIGA,
permitindo filtros por matrícula, código de OS, status, e período. Suporta consultas
tanto individuais quanto em lote, sendo ideal para relatórios e análises.

Funcionalidades:
- Consulta por matrícula única ou múltiplas matrículas
- Busca por código de OS específico ou múltiplas OS
- Filtros por status predefinidos ou customizados
- Filtro por período (data início e fim)
- Grupo especial "Todas OS em Aberto" para consultas rápidas
- Suporte a linguagem natural para datas
- Validação de parâmetros obrigatórios


Args:
    matricula: Matrícula(s) do(s) usuário(s).
    os: Código(s) da(s) OS para consulta específica.
    filtrar_por: Status para filtrar as OS.
    data_inicio: Data de início do período de consulta. Aceita formatos de data padrão ou palavras-chave em português.
    data_fim: Data de fim do período de consulta. Aceita formatos de data padrão ou palavras-chave em português.

Note:
    - Pelo menos 'matricula' ou 'os' deve ter valor válido para executar a consulta
    - Requer variável de ambiente AVA_API_KEY configurada
    - A função é assíncrona e deve ser chamada com await
    - Utiliza a função converter_data_siga() para processar datas
    - Suporte a linguagem natural para datas ("hoje", "ontem", "agora")
    - Utiliza aiohttp para requisições HTTP assíncronas
    - O XML é formatado usando a classe XMLBuilder interna
    - Parâmetros são keyword-only (uso obrigatório de nomes dos parâmetros)
    - O filtro "Todas OS em Aberto" é expandido automaticamente para todos os status em aberto

"""

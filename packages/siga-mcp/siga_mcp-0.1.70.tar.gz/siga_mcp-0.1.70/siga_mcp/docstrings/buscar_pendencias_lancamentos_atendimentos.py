def docs() -> str:
    return """
Busca pendências de lançamentos de atendimentos no sistema SIGA para um analista específico.

Esta função identifica os dias em que o usuário (analista) não efetuou nenhum tipo de
registro no sistema SIGA, incluindo criação de OS, Atendimentos OS ou Atendimentos Avulsos.
É uma ferramenta essencial para controle de produtividade e identificação de lacunas
nos registros de trabalho.

Funcionalidades:
- Identifica dias sem registros de atividades no SIGA
- Suporte a diferentes formatos de data (incluindo linguagem natural)
- Filtragem por período específico (data início e fim)
- Tratamento robusto de erros HTTP e de processamento
- Retorno estruturado em formato XML

Tipos de registros verificados:
- Criação de Ordens de Serviço (OS)
- Atendimentos de OS
- Atendimentos Avulsos
- Qualquer outro tipo de lançamento no SIGA

Args:
    matricula: Matrícula do analista para consulta.
                                                Pode ser string, número inteiro ou "CURRENT_USER".
                                                Se "CURRENT_USER", utiliza matrícula do usuário atual do arquivo .env.
                                                Defaults to "CURRENT_USER".
    dataIni: Data de início do período de consulta.
                                                        Aceita formatos de data padrão ou
                                                        palavras-chave em português.
    dataFim: Data de fim do período de consulta.
                                                        Aceita formatos de data padrão ou
                                                        palavras-chave em português.

Note:
    - Requer variável de ambiente AVA_API_KEY configurada
    - A função é assíncrona e deve ser chamada com await
    - Utiliza a função converter_data_siga() para processar datas
    - Suporte a linguagem natural para datas ("hoje", "ontem", "agora")
    - Utiliza aiohttp para requisições HTTP assíncronas
    - O XML é formatado usando a classe XMLBuilder interna
    - Parâmetros são keyword-only (uso obrigatório de nomes dos parâmetros)
"""

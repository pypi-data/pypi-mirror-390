def docs() -> str:
    return """
Insere um novo atendimento avulso no sistema SIGA para a área de Infraestrutura.

INSTRUÇÃO PARA O AGENTE IA:
ANTES de executar esta função de inserção:
1. MOSTRE ao usuário TODAS as informações que serão criadas/inseridas no sistema
2. APRESENTE os dados de forma clara e organizada (datas, descrição, tipo, origem, categoria, equipe, projeto, analista, plaqueta, etc.)
3. PEÇA confirmação explícita do usuário: "Confirma a criação? (sim/não)"
4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada

Esta função cria um novo registro de atendimento avulso independente de qualquer Ordem de Serviço,
incluindo informações como datas, descrição, tipo, origem, categoria, equipe, projeto e plaqueta.
Realiza validação de todos os campos obrigatórios e conversão automática de datas.

ORIENTAÇÃO PARA SOLICITAÇÕES GENÉRICAS:
Quando o usuário solicitar "inserir/criar um atendimento" sem especificar o tipo:
1. Perguntar qual tipo: Atendimento OS, Atendimento Avulso Sistemas, ou Atendimento Avulso Infraestrutura
2. Se escolher "Avulso": Perguntar se é de Sistemas ou Infraestrutura
3. Depois de definir o tipo: Direcionar para a função específica correspondente

Esta função é específica para Atendimentos Avulso Infraestrutura. Para outros tipos, use:
- `inserir_atendimentos_os` (vinculados a OS)  
- `inserir_atendimento_avulso_sistemas` (área de Sistemas)

Args:
    data_inicio: Data e hora de início do atendimento avulso.
        Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
    data_fim: Data e hora de fim do atendimento avulso.
        Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
    matricula_solicitante: Matrícula do usuário que está solicitando o atendimento avulso
    descricao_atendimento: Descrição detalhada do atendimento avulso a ser realizado
    codigo_analista: Matrícula do analista/usuário responsável pelo atendimento avulso.
    Deve ser "CURRENT_USER" ou um número válido maior que zero. Não aceita valores vazios, "0" ou não-numéricos.
    tipo: Tipo do atendimento avulso, deve ser um dos valores válidos.
    origem: Canal/origem do atendimento avulso, deve ser um dos valores válidos.
    categoria: Categoria relacionado ao atendimento avulso, deve ser um dos valores válidos.
    equipe: Equipe responsável pelo atendimento avulso, deve ser uma das equipes válidas.
    projeto: Projeto relacionado ao atendimento avulso, deve ser um dos valores válidos.
    plaqueta: Plaqueta relacionado ao equipamento que está sendo atendido.

Notes:
    - DIFERENCIAÇÃO DE FUNÇÃO: Esta função cria novos atendimentos avulso infraestrutura. Para editar, use editar_atendimento_avulso_infraestrutura
    - VALIDAÇÃO OBRIGATÓRIA: Campo codigo_analista deve ser "CURRENT_USER" ou um número válido maior que zero (não aceita valores vazios, "0" ou não-numéricos)
    - Esta função é específica para ÁREA INFRAESTRUTURA (área=2)
    - A função realiza validação case-insensitive de todos os campos (tipo, origem, categoria, equipe, projeto)
    - As datas são automaticamente convertidas usando converter_data_siga com manter_horas=True
    - Utiliza as constantes: TIPO_TO_NUMBER_ATENDIMENTO_AVULSO_INFRAESTRUTURA, ORIGEM_TO_NUMBER, CATEGORIA_TO_NUMBER, EQUIPE_INFRAESTRUTURA_TO_NUMBER, PROJETO_TO_NUMBER para mapear valores para códigos numéricos
    - Todos os parâmetros enviados são incluídos como atributos no XML de resposta
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
    - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente
    - Campos opcionais como nomeSolicitante, centroCusto, etc. são enviados vazios por padrão
    - Esta função cria atendimentos avulsos independentes, não vinculados a nenhuma OS
"""

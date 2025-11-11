def docs() -> str:
    return """
Insere um novo atendimento em uma Ordem de Serviço (OS) no sistema SIGA.

INSTRUÇÃO PARA O AGENTE IA:
ANTES de executar esta função de inserção:
1. MOSTRE ao usuário TODAS as informações que serão criadas/inseridas no sistema
2. APRESENTE os dados de forma clara e organizada (OS, datas, descrição, tipo, analista, etc.)
3. PEÇA confirmação explícita do usuário: "Confirma a criação? (sim/não)"
4. SÓ EXECUTE esta função se o usuário confirmar explicitamente
5. Se o usuário não confirmar, cancele a operação e informe que foi cancelada

Esta função cria um novo registro de atendimento associado a uma OS existente,
incluindo informações como datas, descrição, tipo, tempo gasto e flags de controle.
Realiza validação do tipo de atendimento e conversão automática de datas.

ORIENTAÇÃO PARA SOLICITAÇÕES GENÉRICAS:
Quando o usuário solicitar "inserir/criar um atendimento" sem especificar o tipo:
1. Perguntar qual tipo: Atendimento OS, Atendimento Avulso Sistemas, ou Atendimento Avulso Infraestrutura
2. Se escolher "Avulso": Perguntar se é de Sistemas ou Infraestrutura
3. Depois de definir o tipo: Direcionar para a função específica correspondente

Esta função é específica para Atendimentos OS. Para outros tipos, use:
- `inserir_atendimento_avulso_sistemas` (área de Sistemas)  
- `inserir_atendimento_avulso_infraestrutura` (área de Infraestrutura)

Args:
    codigo_os: Código da Ordem de Serviço à qual o atendimento será associado
    data_inicio: Data e hora de início do atendimento. Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem"
    codigo_analista: Matrícula do analista/usuário responsável pelo atendimento. Deve ser um número maior que zero. Não aceita valores vazios, zero ou negativos.
    descricao_atendimento: Descrição detalhada do atendimento a ser realizado
    tipo: Tipo do atendimento, deve ser um dos valores válidos.
    data_fim: Data e hora de fim do atendimento. Aceita formatos de data ou palavras-chave como "hoje", "agora", "ontem". Se None, será enviado como string vazia. Defaults to None.
    primeiro_atendimento: Flag indicando se é o primeiro atendimento da OS.
    apresenta_solucao: Flag indicando se o atendimento apresenta solução.

Notes:
    - DIFERENCIAÇÃO DE FUNÇÃO: Esta função cria novos atendimentos OS. Para editar, use editar_atendimentos_os
    - VALIDAÇÃO OBRIGATÓRIA: Campo codigo_analista deve ser maior que zero (não aceita valores vazios, zero ou negativos)
    - A função realiza validação case-insensitive do tipo de atendimento
    - As datas são automaticamente convertidas usando converter_data_siga com manter_horas=True
    - A função utiliza a constante TYPE_TO_NUMBER para mapear tipos para códigos numéricos
    - Todos os parâmetros enviados são incluídos como atributos no XML de resposta
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - Em caso de falha na requisição HTTP, retorna erro interno formatado em XML
    - O resultado da API (1 = sucesso, outros valores = erro) é interpretado automaticamente
    - Esta função cria um novo atendimento, diferente de editar_atendimentos_os que modifica existente

"""

def docs() -> str:
    return """
Extrai matrículas de usuários do XML retornado pela função listar_usuarios_equipe_por_gerente.

Esta função utilitária assíncrona parseia o XML gerado por listar_usuarios_equipe_por_gerente e extrai
todas as matrículas encontradas, retornando uma lista limpa e pronta para uso em outras
funções do sistema. É especialmente útil para integração com a função listar_horas_trabalhadas,
permitindo buscar horas trabalhadas de toda uma equipe de forma otimizada.

A função trata automaticamente casos de XML malformado, elementos ausentes ou vazios,
garantindo sempre o retorno de uma lista válida (mesmo que vazia) sem quebrar o fluxo
de execução do código.

Args:
    xml_string: 
        String contendo o XML retornado pela função listar_usuarios_equipe_por_gerente.
        Deve estar no formato esperado com elementos <usuario_equipe_gerente> contendo
        subelementos <usuario> com as matrículas. Aceita qualquer XML válido,
        incluindo casos de erro, aviso ou resultado vazio.

Notes:
    - FUNÇÃO UTILITÁRIA ASSÍNCRONA: Projetada especificamente para integração entre funções de equipe e horas
    - ROBUSTEZ: Nunca falha - sempre retorna lista válida mesmo com XML inválido
    - PERFORMANCE: Parsing rápido usando xml.etree.ElementTree nativo do Python
    - INTEGRAÇÃO OTIMIZADA: Funciona perfeitamente com listar_horas_trabalhadas otimizada para listas
    - CASOS DE ERRO: XML de erro/aviso retorna lista vazia, permitindo tratamento adequado
    - LIMPEZA AUTOMÁTICA: Remove espaços em branco das matrículas automaticamente
    - XPATH USADO: './/usuario_equipe_gerente' para buscar todos os elementos independente da profundidade
    - VALIDAÇÃO: Verifica se elemento <usuario> existe e contém texto antes de adicionar à lista
    - FLUXO RECOMENDADO: 
      1. Chamar listar_usuarios_equipe_por_gerente
      2. Chamar await extrair_matriculas_do_xml com o resultado
      3. Verificar se lista não está vazia
      4. Chamar listar_horas_trabalhadas com a lista de matrículas
    - REUTILIZAÇÃO: Pode ser usada com qualquer XML que siga o padrão de usuarios_equipe_gerente
    - THREAD-SAFE: Função pura sem estado, segura para uso concorrente
    - MEMORIA: Eficiente - processa XML em streaming sem carregar tudo na memória
"""

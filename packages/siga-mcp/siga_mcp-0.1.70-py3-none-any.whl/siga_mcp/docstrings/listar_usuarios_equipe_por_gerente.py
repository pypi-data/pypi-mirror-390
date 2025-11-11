def docs() -> str:
    return """
Lista usuários de uma equipe filtrados por gerente responsável, descrição da equipe e situação do usuário.

INSTRUÇÃO PARA O AGENTE IA:
- NÃO INVENTAR USUÁRIOS: Quando esta função retornar resultado vazio (nenhum usuário encontrado), NUNCA invente, crie ou sugira usuários que não existem
- APENAS INFORMAR: Se não encontrar usuários, apenas informe o resultado real da busca (nenhum usuário encontrado)
- NÃO SUGERIR CRIAÇÃO: Esta função é para LISTAGEM apenas, não sugira criar usuários ou usar outras funções para inserir usuários

Esta função permite que gerentes pesquisem funcionários da sua equipe ou de equipes específicas,
utilizando validação robusta através de constantes predefinidas. É útil para gestão de equipes
e integra-se com a função listar_horas_trabalhadas através da função utilitária extrair_matriculas_do_xml
para buscar horas trabalhadas dos funcionários da equipe.
A função valida equipes através da constante EQUIPE_GERAL_TO_NUMBER e situações através da 
constante SITUACAO_USUARIO_TO_NUMBER, garantindo consistência e type safety.

Args:
    matricula_gerente: Matrícula do gerente responsável pelas equipes. Se "CURRENT_USER", busca equipes do usuário atual. Se None ou não fornecido, busca usuários de todas as equipes. Defaults to None.
    descricao_equipe: Nome da equipe específica para filtrar usuários. Deve ser um dos valores válidos. Se None, busca usuários de todas as equipes. Defaults to None.
    situacao_usuario: Situação do usuário para filtro. Deve ser um dos valores válidos. Se None, busca usuários independente da situação (padrão). Defaults to None.


Notes:
    - GESTÃO DE EQUIPES: Permite que gerentes visualizem sua equipe e pesquisem outras equipes
    - INTEGRAÇÃO DISPONÍVEL: Use extrair_matriculas_do_xml + listar_horas_trabalhadas para relatórios completos de equipe
    - FLUXO DE INTEGRAÇÃO: listar_usuarios_equipe_por_gerente → extrair_matriculas_do_xml → listar_horas_trabalhadas
    - NÃO INVENTAR USUÁRIOS: Quando não encontrar usuários, NUNCA inventar ou sugerir criação de usuários inexistentes
    - A função realiza validação case-insensitive de todos os campos (equipe e situação)
    - Utiliza as constantes: EQUIPE_GERAL_TO_NUMBER, SITUACAO_USUARIO_TO_NUMBER para mapear valores para códigos
    - Todos os parâmetros são opcionais, permitindo buscas flexíveis
    - Parâmetros None ou vazios são enviados como strings vazias para a API
    - Em caso de nenhum resultado, retorna XML com status "aviso" em vez de erro
    - Erro de validação retorna lista completa de valores válidos quando informado valor inválido
    - A API key é obtida automaticamente da variável de ambiente AVA_API_KEY
    - A resposta da API é processada através do XMLBuilder para formatação consistente
    - Os atributos do XML de resposta refletem os valores normalizados (códigos) enviados para a API
    - Resultado ordenado por: gerente → equipe → nome do usuário
    - Estrutura de resposta consistente com outras funções do sistema
"""

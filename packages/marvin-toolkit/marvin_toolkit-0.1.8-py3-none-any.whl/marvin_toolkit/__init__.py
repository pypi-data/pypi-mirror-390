# Conteúdo do arquivo: marvin_toolkit/__init__.py
# (Versão de Teste - Apenas com o módulo UI)

print("INFO: Carregando 'marvin_toolkit' (VersÃO DE TESTE)...")

# "Promove" as funções do 'ui.py' para o nível principal
from .ui import (
    clicar_imagem_local
    # Adicione aqui qualquer outra função que já esteja dentro do ui.py
    # ex: capturar_evidencia,
    # ex: limpar_evidencias_antigas
)

# Deixe as outras importações COMENTADAS por enquanto:
# from .qase import (
#     obter_run_id, 
#     atualizar_caso_de_teste_geral
# )
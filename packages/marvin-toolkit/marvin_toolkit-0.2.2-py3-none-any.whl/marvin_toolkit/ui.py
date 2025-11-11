import time
from pathlib import Path
import os

def clicar_imagem_local(nome_arquivo_imagem, button='left', timeout=30):
    """
    Aguarda por uma imagem local (na pasta do script) e clica nela.
    Já inclui o tratamento de erro (try/except) e log.

    :param nome_arquivo_imagem: Nome do arquivo da imagem (ex: 'meu_botao.png')
    :param button: Botão do mouse ('left' ou 'right')
    :param timeout: Tempo máximo de espera pela imagem
    """
    try:
        # 1. Espera a imagem aparecer (esta é a parte que usa o timeout)
        screen.wait_image(nome_arquivo_imagem, timeout=timeout)
        
        # 2. Clica na imagem (agora que sabemos que ela está lá)
        mouse.click_image(nome_arquivo_imagem, button=button)
        
       
        
    except Exception as e:
        
        raise Exception(f"Falha ao aguardar ou clicar na imagem '{nome_arquivo_imagem}'")
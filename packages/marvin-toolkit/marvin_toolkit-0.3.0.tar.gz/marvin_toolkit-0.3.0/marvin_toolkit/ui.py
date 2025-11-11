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
    

# No final do arquivo: marvin_toolkit/ui.py

def hello_test():
    """
    Uma função de teste simples que não depende de nada do Marvin.
    Apenas retorna uma string para provar que a importação funcionou.
    """
    return ">>> SUCESSO! A biblioteca 'marvin-toolkit' foi carregada e executada."
import os
from pathlib import Path
from datetime import datetime

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
        
        # 3. Log de sucesso
        print(f"Imagem local '{nome_arquivo_imagem}' clicada com sucesso.")
        
    except Exception as e:
        # 4. Erro genérico e descritivo
        #    (Note que a mensagem de erro agora é correta e não "Falha ao clicar no botão módulos")
        print(f"Falha ao clicar na imagem local '{nome_arquivo_imagem}': {e}")
        raise Exception(f"Falha ao aguardar ou clicar na imagem '{nome_arquivo_imagem}'")
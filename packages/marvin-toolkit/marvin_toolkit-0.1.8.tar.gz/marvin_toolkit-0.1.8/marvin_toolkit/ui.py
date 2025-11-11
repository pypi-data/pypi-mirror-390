# No topo do arquivo: marvin_toolkit/ui.py
import os
from pathlib import Path
# ... (outros imports) ...

# --- Bloco de Importação CORRETO ---
try:
    # Importa os módulos de actions pelo caminho completo
    from marvin_core.actions import console
    from marvin_core.actions import screen
    from marvin_core.actions import mouse
    from marvin_core.actions import timer
    from marvin_core.actions import keyboard
except ImportError:
    # (Opcional) Lógica para rodar fora do Marvin
    print("AVISO: Módulos Marvin (console, screen, etc.) não encontrados.")
    class MockMarvinObject:
        def __getattr__(self, name):
            def mock_call(*args, **kwargs):
                print(f"Mock Call: {name}({args}, {kwargs})")
            return mock_call
    console = screen = mouse = timer = keyboard = MockMarvinObject()


# --- Fim do Bloco de Importação ---


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
        console.log(f"Imagem local '{nome_arquivo_imagem}' clicada com sucesso.")
        
    except Exception as e:
        # 4. Erro genérico e descritivo
        #    (Note que a mensagem de erro agora é correta e não "Falha ao clicar no botão módulos")
        console.log(f"Falha ao clicar na imagem local '{nome_arquivo_imagem}': {e}")
        raise Exception(f"Falha ao aguardar ou clicar na imagem '{nome_arquivo_imagem}'")
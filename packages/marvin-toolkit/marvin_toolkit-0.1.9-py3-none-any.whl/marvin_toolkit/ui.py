import pyautogui
import time
from pathlib import Path
import os

# Define o caminho base como uma constante global
# O 'r' antes da string é crucial para o Windows entender o caminho corretamente
PASTA_ASSETS_GLOBAL = Path(r"C:\Program Files\Marvin\assets_global")

def clicar_imagem_global_pyautogui(nome_imagem: str, button: str = 'left', timeout: int = 30, confidence: float = 0.9):
    """
    Procura por uma imagem na pasta 'assets_global' e clica nela.
    Esta função usa 'pyautogui' e implementa uma lógica de timeout.

    :param nome_imagem: O nome do arquivo da imagem (ex: 'botao_ok.png')
    :param button: 'left', 'middle', or 'right'
    :param timeout: Tempo máximo (em segundos) para esperar a imagem aparecer
    :param confidence: A precisão da busca (0.0 a 1.0). Use 0.8 ou 0.9.
    """
    
    # 1. Monta o caminho completo da imagem
    caminho_completo = PASTA_ASSETS_GLOBAL / nome_imagem
    
    # 2. Verifica se o arquivo de imagem realmente existe
    if not os.path.exists(caminho_completo):
        print(f"❌ ERRO: Arquivo de imagem não encontrado no caminho: {caminho_completo}")
        raise FileNotFoundError(f"Imagem não encontrada: {caminho_completo}")
        
    print(f"Procurando por '{nome_imagem}' por até {timeout} segundos...")
    
    inicio = time.time()
    localizacao = None
    
    # 3. Lógica de espera (Timeout)
    while (time.time() - inicio) < timeout:
        try:
            # Tenta localizar o CENTRO da imagem na tela
            localizacao = pyautogui.locateCenterOnScreen(
                str(caminho_completo), 
                confidence=confidence
            )
            
            # Se encontrou, sai do loop
            if localizacao:
                break
        except pyautogui.ImageNotFoundException:
            # Isso acontece se a imagem não estiver na tela
            pass
        
        # Pausa por meio segundo antes de tentar de novo
        time.sleep(0.5)

    # 4. Ação Final (Clicar ou Falhar)
    if localizacao:
        print(f"✅ Imagem '{nome_imagem}' encontrada em {localizacao}. Clicando...")
        pyautogui.click(localizacao, button=button)
        print("Clique realizado com sucesso.")
    else:
        # Se o loop terminar e a 'localizacao' ainda for None, o tempo estourou
        print(f"❌ ERRO: Timeout! Imagem '{nome_imagem}' não foi encontrada na tela após {timeout} segundos.")
        raise Exception(f"Timeout: Imagem '{nome_imagem}' não encontrada.")
    
    
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
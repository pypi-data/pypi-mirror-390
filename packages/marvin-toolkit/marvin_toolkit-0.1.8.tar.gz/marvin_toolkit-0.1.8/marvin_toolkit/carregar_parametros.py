from datetime import datetime
import requests
import json
import os
from pathlib import Path
import pandas as pd
import pyautogui
import time


def carregar_parametros_globais():
    """
    Carrega configurações do QASE, run_name da planilha e IDs dos casos de teste salvos no arquivo JSON.
    Retorna: api_token, project_id, base_url, run_name_excel, ids_dos_testes
    """
    parametros_global = Path(r"C:\Program Files\Marvin\parametros_global")
    try:
        # Lê a planilha 'qase_config' e extrai cada valor de uma vez
        api_token = pd.read_excel(parametros_global / "qase_config.xlsx", engine='openpyxl')['api_token'][0]
        project_id = pd.read_excel(parametros_global / "qase_config.xlsx", engine='openpyxl')['project_id'][0]
        base_url = pd.read_excel(parametros_global / "qase_config.xlsx", engine='openpyxl')['base_url'][0]
        
        # Lê a planilha 'run_name' e extrai o valor
        run_name_excel = pd.read_excel(parametros_global / "run_name.xlsx", engine='openpyxl')['run_name'][0]

        # Monta o caminho onde está o arquivo json com os ids dos casos de teste
        arquivo_json_ids = parametros_global / "qase_test_cases_id.json"
        
        # Abre o arquivo JSON, lê seu conteúdo e o transforma em um dicionário Python
        with open(arquivo_json_ids, 'r', encoding='utf-8') as f:
            ids_dos_testes = json.load(f)

        console.log("Configurações carregadas com sucesso!")
        console.log(f"Nome da Run: {run_name_excel}")
        console.log(f"Project ID: {project_id}")
        console.log(f"Base URL: {base_url}")
        console.log(f"API Token: {api_token}")
        console.log(f"ID para 'Abrir Tela': {ids_dos_testes['tc_abrir_tela']}")
        console.log(f"ID para 'Encerrar Período': {ids_dos_testes['tc_encerrar_periodo']}")

        return api_token, project_id, base_url, run_name_excel, ids_dos_testes

    except Exception as e:
        console.log(f"ERRO ao carregar as informações do arquivo qase_config: {e}")
        raise

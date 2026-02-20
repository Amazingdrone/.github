import time
import os
import glob
import pandas as pd
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Define a pasta onde o robô está rodando
PASTA_ATUAL = os.path.abspath(os.path.dirname(__file__))

def clean_currency(x):
    """Limpa valores monetários para cálculos"""
    if pd.isna(x): return np.nan
    if isinstance(x, (int, float)): return float(x)
    x = str(x).replace('R$', '').replace('%', '').strip().replace('.', '').replace(',', '.')
    try: return float(x)
    except: return np.nan

def processar_tabela(caminho_arquivo):
    """Lê a planilha baixada, faz os cálculos e salva a versão final"""
    print(f"Processando arquivo: {caminho_arquivo}")
    try: 
        df = pd.read_csv(caminho_arquivo, sep=';')
    except: 
        df = pd.read_excel(caminho_arquivo)
        
    if 'Codigo' in df.columns: df = df.rename(columns={'Codigo': 'Código'})
        
    # Cálculos Numéricos
    df['Crédito Num'] = df['Credito R$'].apply(clean_currency)
    df['Entrada Num'] = df['Entrada R$'].apply(clean_currency)
    df['Parcelas Num'] = pd.to_numeric(df['Parcelas'], errors='coerce')
    df['Valor Parcela Num'] = df['Valor das Parcelas'].apply(clean_currency)
    
    # Fórmulas Descobertas
    df['Total das parcelas'] = df['Parcelas Num'] * df['Valor Parcela Num']
    df['Custo Total'] = df['Total das parcelas'] + df['Entrada Num']
    df['% Entrada'] = (df['Entrada Num'] / df['Crédito Num']) * 100
    df['% Total'] = ((df['Custo Total'] - df['Crédito Num']) / df['Crédito Num']) * 100

    # Formatação para Exibição
    df_final = pd.DataFrame()
    df_final['Código'] = df['Código']
    df_final['Segmento'] = df['Segmento'].str.replace('Veiculos', 'Veículos')
    df_final['Administradora'] = df['Administradora']
    df_final['Crédito R$'] = df['Crédito Num'].apply(lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['Entrada R$'] = df['Entrada Num'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['% Entrada'] = df['% Entrada'].apply(lambda x: f"{x:,.2f}%".replace(".", ","))
    df_final['Parcelas'] = df['Parcelas Num'].astype(int)
    df_final['Valor das Parcelas'] = df['Valor Parcela Num'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['Total das parcelas'] = df['Total das parcelas'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['Custo Total'] = df['Custo Total'].apply(lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['% Total'] = df['% Total'].apply(lambda x: f"{x:,.2f}%".replace(".", ","))

    # Salva o arquivo que o Streamlit vai ler
    caminho_final = os.path.join(PASTA_ATUAL, "tabela_do_dia.xlsx")
    df_final.to_excel(caminho_final, index=False)
    print(f"Sucesso! {caminho_final} gerado.")

def baixar_planilha():
    """Entra no site e baixa o arquivo usando clique forçado via JavaScript"""
    options = webdriver.ChromeOptions()
    options.add_argument('--headless') # Roda sem interface gráfica
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Configura download automático para a pasta atual
    prefs = {"download.default_directory": PASTA_ATUAL, "download.prompt_for_download": False}
    options.add_experimental_option("prefs", prefs)
    
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        url = "https://cartascontempladas.com.br/ver-todas-as-cartas-contempladas/"
        driver.get(url)
        print(f"Acessando {url}...")
        
        wait = WebDriverWait(driver, 20)
        
        # XPath do botão (ajustado para o link que contém a imagem)
        xpath_do_botao = '//*[@id="preTabelaCartas"]/div/div[2]/div[1]/a'
        
        # Espera o botão ficar clicável
        botao = wait.until(EC.presence_of_element_located((By.XPATH, xpath_do_botao)))
        
        # CLIQUE FORÇADO VIA JAVASCRIPT: Ignora banners de cookies ou sobreposições
        driver.execute_script("arguments[0].click();", botao)
        print("Botão clicado via JavaScript. Aguardando download...")
        
        # Tempo para garantir que o download finalize no servidor
        time.sleep(15)
        
        # Localiza o arquivo baixado (csv ou xlsx) ignorando a tabela_do_dia.xlsx
        arquivos = glob.glob(os.path.join(PASTA_ATUAL, '*.*'))
        planilhas = [f for f in arquivos if 'tabela_do_dia' not in f and (f.endswith('.csv') or f.endswith('.xlsx'))]
        
        if planilhas:
            arquivo_recente = max(planilhas, key=os.path.getctime)
            processar_tabela(arquivo_recente)
            os.remove(arquivo_recente) # Limpa o arquivo original baixado
        else:
            print("Erro: Nenhuma planilha nova encontrada na pasta.")
            
    except Exception as e:
        print(f"Ocorreu um erro durante a execução: {e}")
        raise e
    finally:
        driver.quit()

if __name__ == "__main__":
    baixar_planilha()

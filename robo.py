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

PASTA_ATUAL = os.path.abspath(os.path.dirname(__file__))


def clean_currency(x):
    if pd.isna(x): return np.nan
    if isinstance(x, (int, float)): return float(x)
    x = str(x).replace('R$', '').replace('%', '').strip().replace('.', '').replace(',', '.')
    try:
        return float(x)
    except:
        return np.nan


def processar_tabela(caminho_arquivo):
    try:
        df = pd.read_csv(caminho_arquivo, sep=';')
    except:
        df = pd.read_excel(caminho_arquivo)

    if 'Codigo' in df.columns: df = df.rename(columns={'Codigo': 'Código'})

    df['Crédito Num'] = df['Credito R$'].apply(clean_currency)
    df['Entrada Num'] = df['Entrada R$'].apply(clean_currency)
    df['Parcelas Num'] = pd.to_numeric(df['Parcelas'], errors='coerce')
    df['Valor Parcela Num'] = df['Valor das Parcelas'].apply(clean_currency)

    df['Total das parcelas'] = df['Parcelas Num'] * df['Valor Parcela Num']
    df['Custo Total'] = df['Total das parcelas'] + df['Entrada Num']
    df['% Entrada'] = (df['Entrada Num'] / df['Crédito Num']) * 100
    df['% Total'] = ((df['Custo Total'] - df['Crédito Num']) / df['Crédito Num']) * 100

    df_final = pd.DataFrame()
    df_final['Código'] = df['Código']
    df_final['Segmento'] = df['Segmento'].str.replace('Veiculos', 'Veículos')
    df_final['Administradora'] = df['Administradora']
    df_final['Crédito R$'] = df['Crédito Num'].apply(
        lambda x: f"{x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['Entrada R$'] = df['Entrada Num'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['% Entrada'] = df['% Entrada'].apply(lambda x: f"{x:,.2f}%".replace(".", ","))
    df_final['Parcelas'] = df['Parcelas Num'].astype(int)
    df_final['Valor das Parcelas'] = df['Valor Parcela Num'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['Total das parcelas'] = df['Total das parcelas'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['Custo Total'] = df['Custo Total'].apply(
        lambda x: f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
    df_final['% Total'] = df['% Total'].apply(lambda x: f"{x:,.2f}%".replace(".", ","))

    caminho_final = os.path.join(PASTA_ATUAL, "tabela_do_dia.xlsx")
    df_final.to_excel(caminho_final, index=False)
    print("Sucesso! tabela_do_dia.xlsx criada.")


def baixar_planilha():
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')

    prefs = {"download.default_directory": PASTA_ATUAL, "download.prompt_for_download": False}
    options.add_experimental_option("prefs", prefs)

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    try:
        driver.get("https://cartascontempladas.com.br/ver-todas-as-cartas-contempladas/")
        wait = WebDriverWait(driver, 15)

        # O SEU XPATH FOI INSERIDO AQUI:
        xpath_do_botao = '//*[@id="preTabelaCartas"]/div/div[2]/div[1]/a/figure/img'

        botao = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_do_botao)))
        botao.click()
        time.sleep(10)

        arquivos = glob.glob(os.path.join(PASTA_ATUAL, '*.*'))
        planilhas = [f for f in arquivos if 'tabela_do_dia' not in f and (f.endswith('.csv') or f.endswith('.xlsx'))]

        if planilhas:
            arquivo_recente = max(planilhas, key=os.path.getctime)
            processar_tabela(arquivo_recente)
            os.remove(arquivo_recente)
        else:
            print("Nenhuma planilha encontrada após o download.")
    finally:
        driver.quit()


if __name__ == "__main__":
    baixar_planilha()
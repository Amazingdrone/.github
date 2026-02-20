import streamlit as st
import pandas as pd
import os
from datetime import datetime

st.set_page_config(page_title="Tabela Sr. Jean", layout="wide")

# Cabeçalho VIP
st.markdown(f"# ☕ Bom dia, Sr. Jean, tudo bem?")
st.markdown(f"### Tabela atualizada: **{datetime.now().strftime('%d/%m/%Y')}**")

arquivo = "tabela_do_dia.xlsx"

if os.path.exists(arquivo):
    # O BOTAO DE DOWNLOAD AGORA É A PRIMEIRA COISA
    data_arq = datetime.now().strftime('%d_%m_%Y')
    with open(arquivo, "rb") as f:
        st.download_button(
            label="📥 CLIQUE AQUI PARA BAIXAR O EXCEL (TABELA_DATA.xlsx)",
            data=f,
            file_name=f"TABELA_{data_arq}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    st.markdown("---")

    try:
        df = pd.read_excel(arquivo)
        if not df.empty:
            st.success("Dados carregados com sucesso. Veja abaixo:")
            st.dataframe(df, use_container_width=True, height=600)
        else:
            st.error("Sr. Jean, o arquivo foi gerado mas está VAZIO. O site pode ter bloqueado o acesso hoje.")
            st.info("Tente rodar o robô novamente no GitHub Actions em alguns minutos.")
    except Exception as e:
        st.error(f"Erro ao ler a tabela: {e}")
else:
    st.warning("⚠️ Sr. Jean, a tabela ainda não foi criada hoje. Vá ao GitHub e aperte 'Run Workflow'.")

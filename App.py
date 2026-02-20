import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Cartas Disponíveis Hoje", layout="wide")
st.title("☕ Bom dia! Suas Cartas de Consórcio")
st.write("Aqui está a tabela atualizada de hoje. Pronta para oferecer aos clientes!")

arquivo_pronto = "tabela_do_dia.xlsx"

if os.path.exists(arquivo_pronto):
    try:
        df_final = pd.read_excel(arquivo_pronto)
        st.success("Tabela carregada com sucesso!")
        st.dataframe(df_final, use_container_width=True)

        with open(arquivo_pronto, "rb") as file:
            st.download_button(
                label="📥 FAZER DOWNLOAD (Excel)",
                data=file,
                file_name="TABELA_PRONTA_CLIENTES.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
    except Exception as e:
        st.error(f"Erro ao ler a tabela: {e}")
else:
    st.warning("A tabela de hoje está sendo gerada ou ainda não foi processada.")
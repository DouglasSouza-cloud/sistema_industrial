import streamlit as st

st.set_page_config(layout="wide")

st.title("📊 Dashboard Industrial - Sistema de Monitoramento")

if "rodando" not in st.session_state:
    st.session_state.rodando = False
    st.session_state.dados = []
    st.session_state.tempos = []
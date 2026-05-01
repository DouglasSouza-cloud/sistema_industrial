import streamlit as st

st.set_page_config(layout="wide")

st.title("📊 Dashboard Industrial - Sistema de Monitoramento")

# 🔥 Estado do sistema
if "rodando" not in st.session_state:
    st.session_state.rodando = False
    st.session_state.dados = []
    st.session_state.tempos = []

# 🎛 Controles
colA, colB = st.columns(2)

if colA.button("▶ Iniciar"):
    st.session_state.rodando = True

if colB.button("⛔ Parar"):
    st.session_state.rodando = False
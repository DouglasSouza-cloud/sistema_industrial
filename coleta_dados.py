import streamlit as st
import random
from datetime import datetime
import pandas as pd
import plotly.express as px
import mysql.connector
import os
from dotenv import load_dotenv
import time

load_dotenv()

def get_conn():
    return mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        port=int(os.getenv("DB_PORT"))
    )

st.set_page_config(layout="wide")
st.title("📊 Dashboard Industrial")

META = 250

if "dados" not in st.session_state:
    st.session_state.dados = []
    st.session_state.tempos = []
    st.session_state.rodando = False

col1, col2 = st.columns(2)

if col1.button("▶ Iniciar"):
    st.session_state.rodando = True

if col2.button("⛔ Parar"):
    st.session_state.rodando = False

placeholder = st.empty()

# 🔥 LOOP (IGUAL ANTES)
if st.session_state.rodando:

    for i in range(100000):  # loop longo

        if not st.session_state.rodando:
            break

        valor = round(random.uniform(100, 400), 2)
        horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # salva no banco
        try:
            conn = get_conn()
            cursor = conn.cursor()

            sql = "INSERT INTO producao (horario, producao) VALUES (%s, %s)"
            cursor.execute(sql, (horario, valor))
            conn.commit()

            cursor.close()
            conn.close()

        except:
            pass

        # salva local (só últimos 20)
        st.session_state.dados.append(valor)
        st.session_state.tempos.append(horario)

        if len(st.session_state.dados) > 20:
            st.session_state.dados.pop(0)
            st.session_state.tempos.pop(0)

        df = pd.DataFrame({
            "Horário": st.session_state.tempos,
            "Produção": st.session_state.dados
        })

        media = df["Produção"].mean()
        abaixo_meta = df[df["Produção"] < META]

        with placeholder.container():

            c1, c2, c3 = st.columns(3)

            c1.metric("📊 Média", round(media, 2))
            c2.metric("❌ Abaixo da Meta", len(abaixo_meta))
            c3.metric("📈 Último Valor", valor)

            fig = px.line(df, x="Horário", y="Produção", markers=True)

            # 🔥 linha da meta
            fig.add_hline(
                y=META,
                line_dash="dash",
                line_color="red",
                annotation_text="Meta",
                annotation_position="top left"
)
            st.plotly_chart(fig, use_container_width=True)

            st.dataframe(df)

        time.sleep(1)
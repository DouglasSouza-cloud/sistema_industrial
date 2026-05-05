import streamlit as st
import random
from datetime import datetime
import pandas as pd
import plotly.express as px
import mysql.connector
import os
import time
from dotenv import load_dotenv

# =========================
# 🔐 CONFIG (LOCAL + DEPLOY)
# =========================
load_dotenv()

def get_secret(key):
    # tenta pegar do Streamlit (deploy)
    if key in st.secrets:
        return st.secrets[key]
    # senão pega do .env (local)
    return os.getenv(key)

# =========================
# 🔌 CONEXÃO
# =========================
def get_conn():
    return mysql.connector.connect(
        host=get_secret("DB_HOST"),
        user=get_secret("DB_USER"),
        password=get_secret("DB_PASSWORD"),
        database=get_secret("DB_NAME"),
        port=int(get_secret("DB_PORT"))
    )

# =========================
# ⚙ CONFIG
# =========================
st.set_page_config(layout="wide")
st.title("📊 Dashboard Industrial - Monitoramento")

META = 250

# =========================
# 🔥 ESTADO
# =========================
if "tempo_critico" not in st.session_state:
    st.session_state.tempo_critico = 0

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

# =========================
# 🔄 LOOP TEMPO REAL
# =========================
if st.session_state.rodando:

    for _ in range(100000):

        if not st.session_state.rodando:
            break

        valor = round(random.uniform(100, 400), 2)
        horario = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # 💾 MYSQL
        try:
            conn = get_conn()
            cursor = conn.cursor()

            sql = "INSERT INTO producao (horario, producao) VALUES (%s, %s)"
            cursor.execute(sql, (horario, valor))
            conn.commit()

            cursor.close()
            conn.close()

        except Exception as e:
            st.error(f"Erro no MySQL: {e}")

        # 📊 DADOS LOCAIS (limitado)
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
        ultimo = df["Produção"].iloc[-1]
        abaixo_meta = df[df["Produção"] < META]
        eficiencia = (ultimo / META) * 100

        # ⏱ TEMPO CRÍTICO CONTÍNUO
        if ultimo < META:
            st.session_state.tempo_critico += 1
        else:
            st.session_state.tempo_critico = 0

        # =========================
        # 🎛 DASHBOARD
        # =========================
        with placeholder.container():

            # STATUS
            if ultimo < META:
                st.error("🔴 STATUS: PRODUÇÃO ABAIXO DA META")
            else:
                st.success("🟢 STATUS: OPERAÇÃO NORMAL")

            st.divider()

            # MÉTRICAS
            c1, c2, c3, c4, c5 = st.columns(5)

            c1.metric("📊 Média", round(media, 2))
            c2.metric("📈 Última Produção", ultimo)
            c3.metric("❌ Ocorrências", len(abaixo_meta))
            c4.metric("⚙ Eficiência", f"{eficiencia:.1f}%")
            c5.metric("⏱ Tempo Crítico", f"{st.session_state.tempo_critico}s")

            st.divider()

            # GRÁFICO
            fig = px.line(
                df,
                x="Horário",
                y="Produção",
                markers=True
            )

            fig.update_traces(
                marker=dict(
                    color=[
                        "green" if v >= META else "red"
                        for v in df["Produção"]
                    ]
                )
            )

            fig.add_hline(
                y=META,
                line_dash="dash",
                line_color="white",
                annotation_text="Meta"
            )

            fig.update_layout(
                template="plotly_dark",
                xaxis_title="Tempo",
                yaxis_title="Produção"
            )

            st.plotly_chart(fig, use_container_width=True)

            st.divider()

            # ALERTAS
            st.subheader("🚨 Alertas")

            if not abaixo_meta.empty:
                st.error(f"{len(abaixo_meta)} ocorrências abaixo da meta")
            else:
                st.success("Nenhuma ocorrência crítica")

            st.divider()

            # LOG
            st.subheader("📋 Log de Ocorrências")

            if not abaixo_meta.empty:
                st.dataframe(abaixo_meta.tail(10), use_container_width=True)
            else:
                st.info("Sem registros críticos recentes")

        time.sleep(1)
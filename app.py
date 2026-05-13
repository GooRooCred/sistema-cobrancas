import streamlit as st
from supabase import create_client
import pandas as pd
from datetime import datetime

# =============================
# CONFIG
# =============================
SUPABASE_URL = "SUA_URL"
SUPABASE_KEY = "SUA_KEY"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(layout="wide")
st.title("💰 Sistema de Cobranças")

# =============================
# FUNÇÃO LOG
# =============================
def registrar_log(boleto, acao, dados):
    supabase.table("cobrancas_log").insert({
        "boleto": boleto,
        "acao": acao,
        "dados": dados
    }).execute()

# =============================
# FILTROS
# =============================
st.sidebar.header("Filtros")

f_boleto = st.sidebar.text_input("Boleto")
f_pagador = st.sidebar.text_input("Pagador")
f_fundo = st.sidebar.text_input("Fundo")

# =============================
# CONSULTA (SCROLL + PAGINAÇÃO)
# =============================
st.header("🔎 Consulta Geral")

page_size = 100
page = st.number_input("Página", min_value=1, value=1)

query = supabase.table("cobrancas").select("*")

if f_boleto:
    query = query.ilike("boleto", f"%{f_boleto}%")

if f_pagador:
    query = query.ilike("pagador", f"%{f_pagador}%")

if f_fundo:
    query = query.ilike("fundo", f"%{f_fundo}%")

inicio = (page - 1) * page_size
fim = inicio + page_size - 1

res = query.range(inicio, fim).execute()
df = pd.DataFrame(res.data)

st.dataframe(df, use_container_width=True, height=500)

# =============================
# EXPORTAR
# =============================
if not df.empty:
    st.download_button(
        "📥 Exportar CSV",
        df.to_csv(index=False).encode("utf-8"),
        "cobrancas.csv"
    )

# =============================
# INSERÇÃO COMPLETA
# =============================
st.header("➕ Novo Registro")

with st.form("form_insert"):
    cols = st.columns(3)

    dados = {
        "boleto": cols[0].text_input("Boleto"),
        "seu_numero": cols[1].text_input("Seu Número"),
        "pagador": cols[2].text_input("Pagador"),

        "valor_do_titulo": st.number_input("Valor do Título", step=0.01),
        "valor_cobrado": st.number_input("Valor Cobrado", step=0.01),
        "oscilacao": st.number_input("Oscilação", step=0.01),

        "conta_cobranca": st.text_input("Conta Cobrança"),
        "lote": st.text_input("Lote"),
        "verba_rescisao": st.text_input("Verba Rescisão"),
        "gooroo": st.text_input("Gooroo"),
        "fundo": st.text_input("Fundo"),

        "boleto_manual": st.checkbox("Boleto Manual"),
        "checagem": st.text_input("Checagem"),
        "observacao": st.text_area("Observação"),

        "evidencia1": st.text_input("Evidência 1"),
        "evidencia2": st.text_input("Evidência 2"),
        "evidencia3": st.text_input("Evidência 3")
    }

    submitted = st.form_submit_button("Inserir")

    if submitted:
        supabase.table("cobrancas").insert(dados).execute()
        registrar_log(dados["boleto"], "INSERT", dados)
        st.success("Inserido!")

# =============================
# EDIÇÃO COMPLETA
# =============================
st.header("✏️ Editar Registro")

edit_boleto = st.text_input("Digite o boleto")

if st.button("Carregar Registro"):
    res = supabase.table("cobrancas").select("*").eq("boleto", edit_boleto).execute()

    if res.data:
        r = res.data[0]

        with st.form("form_edit"):
            novo = {}

            for campo, valor in r.items():
                if campo == "created_at":
                    continue

                if isinstance(valor, bool):
                    novo[campo] = st.checkbox(campo, value=valor)
                elif isinstance(valor, (int, float)):
                    novo[campo] = st.number_input(campo, value=float(valor or 0))
                else:
                    novo[campo] = st.text_input(campo, value=str(valor or ""))

            salvar = st.form_submit_button("Salvar Alterações")

            if salvar:
                supabase.table("cobrancas").update(novo).eq("boleto", edit_boleto).execute()
                registrar_log(edit_boleto, "UPDATE", novo)
                st.success("Atualizado!")

# =============================
# EXCLUSÃO
# =============================
st.header("❌ Excluir")

del_boleto = st.text_input("Boleto para excluir")

if st.button("Excluir Registro"):
    supabase.table("cobrancas").delete().eq("boleto", del_boleto).execute()
    registrar_log(del_boleto, "DELETE", {})
    st.warning("Excluído!")

# =============================
# HISTÓRICO
# =============================
st.header("🕓 Histórico")

hist_boleto = st.text_input("Ver histórico do boleto")

if st.button("Buscar Histórico"):
    res = supabase.table("cobrancas_log").select("*").eq("boleto", hist_boleto).order("data", desc=True).execute()
    df_hist = pd.DataFrame(res.data)
    st.dataframe(df_hist, use_container_width=True)

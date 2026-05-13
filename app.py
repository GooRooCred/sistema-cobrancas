import streamlit as st
from supabase import create_client
import pandas as pd

# =============================
# CONFIG
# =============================
SUPABASE_URL = "https://pbwkygsohtnotzdzfsfp.supabase.co"
SUPABASE_KEY = "sb_publishable_GZQLNBq0Ag8UMxNWZZs_Dg_B_bdejTc"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(
    page_title="Sistema de Cobranças",
    page_icon="💰",
    layout="wide"
)

# =============================
# ESTILO
# =============================
st.markdown("""
<style>
.main {
    background-color: #f5f7fa;
}
.stButton>button {
    border-radius: 8px;
    background-color: #4CAF50;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# =============================
# MENU
# =============================
menu = st.sidebar.radio(
    "📌 Menu",
    ["Dashboard", "Consulta", "Inserir", "Editar", "Excluir", "Histórico"]
)

st.sidebar.markdown("---")
st.sidebar.caption("Sistema de Cobranças v1.0")

# =============================
# DASHBOARD
# =============================
# =============================
# DASHBOARD
# =============================
if menu == "Dashboard":
    st.title("📊 Dashboard")

    res_count = supabase.table("cobrancas").select("*", count="exact").limit(1).execute()
    total = res_count.count

    res_total = supabase.rpc("total_valor_cobrado").execute()
    valor_total = res_total.data or 0

    valor_formatado = f"R$ {float(valor_total):,.2f}"

    col1, col2 = st.columns(2)

    col1.metric("Total de Registros", total)
    col2.metric("Valor Total", valor_formatado)
# =============================
# CONSULTA
# =============================
elif menu == "Consulta":
    st.title("🔎 Consulta")

    filtro = st.text_input("Buscar por boleto ou pagador")

    query = supabase.table("cobrancas").select("*")

    if filtro:
        query = query.ilike("boleto", f"%{filtro}%")

    res = query.limit(200).execute()
    df = pd.DataFrame(res.data)

    st.dataframe(df, use_container_width=True)

# =============================
# INSERIR
# =============================
elif menu == "Inserir":
    st.title("➕ Novo Registro")

    with st.form("form_insert"):
        col1, col2 = st.columns(2)

        boleto = col1.text_input("Boleto")
        seu_numero = col2.text_input("Seu Número")

        pagador = st.text_input("Pagador")
        valor = st.number_input("Valor Cobrado", step=0.01)

        submit = st.form_submit_button("Salvar")

        if submit:
            supabase.table("cobrancas").insert({
                "boleto": boleto,
                "seu_numero": seu_numero,
                "pagador": pagador,
                "valor_cobrado": valor
            }).execute()

            st.success("Registro inserido!")

# =============================
# EDITAR
# =============================
elif menu == "Editar":
    st.title("✏️ Editar")

    boleto = st.text_input("Digite o boleto")

    if st.button("Buscar"):
        res = supabase.table("cobrancas").select("*").eq("boleto", boleto).execute()

        if res.data:
            r = res.data[0]

            novo_pagador = st.text_input("Pagador", r["pagador"])
            novo_valor = st.number_input("Valor", value=float(r["valor_cobrado"] or 0))

            if st.button("Salvar"):
                supabase.table("cobrancas").update({
                    "pagador": novo_pagador,
                    "valor_cobrado": novo_valor
                }).eq("boleto", boleto).execute()

                st.success("Atualizado!")

# =============================
# EXCLUIR
# =============================
elif menu == "Excluir":
    st.title("❌ Excluir")

    boleto = st.text_input("Boleto")

    if st.button("Excluir"):
        supabase.table("cobrancas").delete().eq("boleto", boleto).execute()
        st.warning("Excluído!")

# =============================
# HISTÓRICO
# =============================
elif menu == "Histórico":
    st.title("🕓 Histórico")

    boleto = st.text_input("Boleto")

    if st.button("Buscar"):
        res = supabase.table("cobrancas_log").select("*").eq("boleto", boleto).execute()
        df = pd.DataFrame(res.data)

        st.dataframe(df, use_container_width=True)

import streamlit as st
from supabase import create_client
import pandas as pd
import numpy as np
import io

# =============================
# FORMAT BR
# =============================
def format_brl(valor):
    try:
        valor = float(valor or 0)
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except:
        return "0,00"

# =============================
# FORMAT FLOAT
# =============================
def to_float(valor):
    try:
        if valor is None:
            return 0.0

        # se já for número
        if isinstance(valor, (int, float)):
            return float(valor)

        valor = str(valor).strip()

        # se tiver vírgula (formato BR)
        if "," in valor:
            valor = valor.replace(".", "").replace(",", ".")

        return float(valor)

    except:
        return 0.0
#================================
# FUNÇÃO DATA BR
#================================
def format_data_br(valor):
    try:
        if pd.isna(valor):
            return ""

        return pd.to_datetime(valor).strftime("%d/%m/%Y")
    except:
        return valor

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
if menu == "Dashboard":
    st.title("📊 Dashboard")

    res_count = supabase.table("cobrancas").select("*", count="exact").limit(1).execute()
    total = res_count.count or 0

    res_total = supabase.rpc("total_valor_cobrado").execute()
    valor_total = res_total.data or 0

    res_osc = supabase.rpc("total_oscilacao").execute()
    total_oscilacao = res_osc.data or 0

    valor_formatado = f"R$ {format_brl(valor_total)}"
    oscilacao_formatada = f"R$ {format_brl(total_oscilacao)}"

    col1, col2, col3 = st.columns(3)

    col1.metric("Total de Registros", total)
    col2.metric("Valor Total", valor_formatado)
    col3.metric("Total Oscilação", oscilacao_formatada)

# =============================
# CONSULTA
# =============================
elif menu == "Consulta":
    st.title("🔎 Consulta")

    filtro = st.text_input("Buscar por boleto ou pagador")

    query = supabase.table("cobrancas").select("""
        seu_numero, boleto, vencimento, data_da_liquidacao,
        valor_do_titulo, valor_cobrado, oscilacao, pagador,
        lote, verba_rescisao, gooroo, fundo,
        boleto_manual, checagem, observacao, evidencia1
    """)

    if filtro:
        query = query.ilike("boleto", f"%{filtro}%")

    res = query.limit(200).execute()
    df = pd.DataFrame(res.data)

    # =========================
    # FORMATAR VALORES
    # =========================
    valor_cols = [
        "valor_do_titulo",
        "oscilacao",
        "boleto_manual",
        "valor_cobrado"
    ]

    for col in valor_cols:
        if col in df.columns:
            df[col] = df[col].apply(format_brl)

    # =========================
    # FORMATAR DATAS
    # =========================
    data_cols = [
        "vencimento",
        "data_da_liquidacao"
    ]

    for col in data_cols:
        if col in df.columns:
            df[col] = df[col].apply(format_data_br)

    st.dataframe(df, use_container_width=True)

# =============================
# INSERIR
# =============================
elif menu == "Inserir":

    st.title("➕ Inserir Registros")

    aba = st.radio("Escolha o tipo de inserção:", ["Manual", "Importar Excel"])

    # =============================
    # MANUAL
    # =============================
    if aba == "Manual":
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
    # IMPORTAR EXCEL
    # =============================
    elif aba == "Importar Excel":

        st.subheader("📂 Importar arquivo Excel")

        todas_colunas = [
            "seu_numero", "boleto", "vencimento", "data_da_liquidacao",
            "valor_do_titulo", "valor_cobrado", "oscilacao", "pagador", 
            "lote", "verba_rescisao", "gooroo", "fundo",
            "boleto_manual", "checagem", "observacao", "evidencia1"
        ]

        # MODELO
        df_modelo = pd.DataFrame(columns=todas_colunas)

        buffer = io.BytesIO()
        df_modelo.to_excel(buffer, index=False)
        buffer.seek(0)

        st.download_button(
            label="📥 Baixar modelo Excel",
            data=buffer,
            file_name="modelo_importacao.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

        st.markdown("---")

        arquivo = st.file_uploader("Selecione o arquivo (.xlsx)", type=["xlsx"])

        if arquivo:
            df = pd.read_excel(arquivo)

            # 🔥 CONVERSÃO NUMÉRICA
            valor_cols = [
                "valor_do_titulo",
                "oscilacao",
                "boleto_manual",
                "valor_cobrado"
            ]

            for col in valor_cols:
                if col in df.columns:
                    df[col] = df[col].apply(to_float)

            colunas_minimas = ["boleto"]
            colunas_faltando = [col for col in colunas_minimas if col not in df.columns]

            if colunas_faltando:
                st.error(f"❌ Colunas obrigatórias faltando: {colunas_faltando}")
            else:
                st.success("✅ Arquivo válido!")
                st.dataframe(df.head(20), use_container_width=True)
                st.write(f"📌 Total de linhas: {len(df)}")

                df = df.replace({np.nan: None})

                if st.button("Importar dados"):

                    colunas_presentes = [col for col in todas_colunas if col in df.columns]
                    df_final = df[colunas_presentes]

                    dados = df_final.to_dict(orient="records")

                    batch_size = 500
                    total = len(dados)

                    progresso = st.progress(0)
                    status = st.empty()

                    for i in range(0, total, batch_size):
                        lote = dados[i:i+batch_size]
                        supabase.table("cobrancas").insert(lote).execute()

                        progresso.progress(min((i + batch_size) / total, 1.0))
                        status.text(f"Enviando {i + len(lote)} de {total}")

                    st.success(f"✅ {total} registros inseridos com sucesso!")

# =============================
# EDITAR
# =============================
elif menu == "Editar":
    st.title("✏️ Editar")

    boleto = st.text_input("Digite o boleto")

    if st.button("Buscar") and boleto:
        res = supabase.table("cobrancas").select("*").eq("boleto", boleto).execute()

        if res.data:
            st.session_state["registro"] = res.data[0]
            st.session_state["boleto_edit"] = boleto
        else:
            st.warning("Boleto não encontrado")

    if "registro" in st.session_state:
        r = st.session_state["registro"]

        novo_pagador = st.text_input("Pagador", value=r.get("pagador", ""))
        novo_valor = st.number_input("Valor", value=float(r.get("valor_cobrado") or 0))

        if st.button("Salvar alterações"):

            supabase.table("cobrancas_log").insert({
                "boleto": st.session_state["boleto_edit"],
                "pagador": novo_pagador,
                "valor_cobrado": novo_valor
            }).execute()

            supabase.table("cobrancas").update({
                "pagador": novo_pagador,
                "valor_cobrado": novo_valor
            }).eq("boleto", st.session_state["boleto_edit"]).execute()

            st.success("Atualizado e registrado no histórico!")

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

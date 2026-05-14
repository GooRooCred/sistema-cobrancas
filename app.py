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
elif menu == "Inserir":
    st.title("➕ Inserir Registros")

    aba = st.radio("Escolha o tipo de inserção:", ["Manual", "Importar Excel"])

    # =============================
    # INSERÇÃO MANUAL
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
    # IMPORTAÇÃO EXCEL
    # =============================
    elif aba == "Importar Excel":
        import io

        st.subheader("📂 Importar arquivo Excel")

        todas_colunas = [
            "seu_numero", "boleto", "vencimento", "data_da_liquidacao",
            "valor_do_titulo", "valor_cobrado", "oscilacao", "pagador",
            "conta_cobranca", "lote", "verba_rescisao", "gooroo", "fundo",
            "boleto_manual", "checagem", "observacao", "evidencia1"
        ]

        # 📥 Modelo
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

        # 📤 Upload
        arquivo = st.file_uploader("Selecione o arquivo (.xlsx)", type=["xlsx"])

        if arquivo:
            df = pd.read_excel(arquivo)

            colunas_minimas = ["boleto"]

            colunas_faltando = [col for col in colunas_minimas if col not in df.columns]

            if colunas_faltando:
                st.error(f"❌ Coluna obrigatória faltando: {colunas_faltando}")
            else:
                st.success("✅ Arquivo válido!")
                st.dataframe(df.head(), use_container_width=True)

                if st.button("Importar dados"):
                    colunas_presentes = [col for col in todas_colunas if col in df.columns]

                    dados = df[colunas_presentes].to_dict(orient="records")

                    supabase.table("cobrancas").insert(dados).execute()

                    st.success(f"{len(dados)} registros inseridos com sucesso!")# =============================
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

            novo_pagador = st.text_input("Pagador", r.get("pagador", ""))
            novo_valor = st.number_input(
                "Valor",
                value=float(r.get("valor_cobrado") or 0)
            )

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

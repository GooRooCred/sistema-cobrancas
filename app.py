import streamlit as st
from supabase import create_client
import pandas as pd
import numpy as np
import io
import bcrypt

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

# =============================
# LOG AUDITORIA
# =============================
def registrar_log(
    acao,
    boleto=None,
    seu_numero=None,
    pagador=None,
    valor_anterior=None,
    valor_novo=None,
    observacao=None
):

    try:

        supabase.table(
            "auditoria"
        ).insert({

            "usuario":
                st.session_state.get(
                    "usuario"
                ),

            "perfil":
                st.session_state.get(
                    "perfil"
                ),

            "acao":
                acao,

            "boleto":
                boleto,

            "seu_numero":
                seu_numero,

            "pagador":
                pagador,

            "valor_anterior":
                valor_anterior,

            "valor_novo":
                valor_novo,

            "observacao":
                observacao

        }).execute()

    except:
        pass

COLUNAS_AMIGAVEIS = {
    "seu_numero": "SEU NUMERO",
    "boleto": "BOLETO",
    "vencimento": "VENCIMENTO",
    "data_da_liquidacao": "DATA PAGAMENTO",
    "valor_do_titulo": "R$ TITULO",
    "valor_cobrado": "R$ COBRADO",
    "oscilacao": "OSCILAÇÃO",
    "pagador": "CLIENTE/PAGADOR",
    "lote": "LOTE",
    "boleto_manual": "BOLETO MANUAL",
    "checagem": "VALIDAÇÃO",
    "observacao": "OBSERVAÇÃO",
    "evidencia1": "EVIDÊNCIA"
}

# ================================
# FUNÇÃO DATA BR
# ================================
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
# LOGIN
# =============================
if "logado" not in st.session_state:
    st.session_state["logado"] = False

if not st.session_state["logado"]:

    st.title("🔒 Login")

    usuario = st.text_input("Usuário")

    senha = st.text_input(
        "Senha",
        type="password"
    )

    if st.button("Entrar"):

        try:
            res = (
                supabase.table("usuarios")
                .select("*")
                .eq("usuario", usuario)
                .eq("ativo", True)
                .execute()
            )

            if not res.data:
                st.error("Usuário ou senha inválidos")
                st.stop()

            user = res.data[0]

            senha_ok = bcrypt.checkpw(
                senha.encode(),
                user["senha_hash"].encode()
            )

            if senha_ok:

                st.session_state["logado"] = True

                st.session_state["usuario"] = (
                    user["usuario"]
                )

                st.session_state["perfil"] = (
                    user["perfil"]
                )

                st.rerun()

            else:
                st.error(
                    "Usuário ou senha inválidos"
                )

        except Exception as e:
            st.error(
                f"Erro no login: {e}"
            )

    st.stop()

# =============================
# ESTILO
# =============================
st.markdown("""
<style>

.main {
    background-color: #f5f7fa;
}

/* BOTÕES */
.stButton>button {
    border-radius: 10px;
    background-color: #4CAF50;
    color: white;
    font-weight: bold;
    height: 42px;
}

/* MÉTRICAS */
[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #EAEAEA;
    padding: 20px;
    border-radius: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

[data-testid="stMetricLabel"] {
    font-size: 18px;
    font-weight: 700;
}

[data-testid="stMetricValue"] {
    font-size: 34px;
    font-weight: bold;
    color: #111;
}

</style>
""", unsafe_allow_html=True)

# =============================
# MENU POR PERFIL
# =============================
perfil = st.session_state.get(
    "perfil",
    "leitura"
)

if perfil == "superadmin":

    opcoes_menu = [
        "Dashboard",
        "Consulta",
        "Inserir",
        "Editar",
        "Excluir",
        "Histórico",
        "Usuários"
    ]

elif perfil == "admin":

    opcoes_menu = [
        "Dashboard",
        "Consulta",
        "Inserir",
        "Editar",
        "Excluir",
        "Histórico"
    ]

elif perfil == "operador":

    opcoes_menu = [
        "Dashboard",
        "Consulta",
        "Inserir",
        "Editar",
        "Histórico"
    ]

else:

    opcoes_menu = [
        "Dashboard",
        "Consulta"
    ]

# 🔥 ESTA PARTE É OBRIGATÓRIA
menu = st.sidebar.radio(
    "📌 Menu",
    opcoes_menu
)

# =============================
# CONTROLE DE TROCA DE MENU
# =============================
menu_anterior = st.session_state.get("menu_anterior")

if menu_anterior != menu:

    # limpa edição anterior
    if "registro" in st.session_state:
        del st.session_state["registro"]

    if "boleto_edit" in st.session_state:
        del st.session_state["boleto_edit"]

st.session_state["menu_anterior"] = menu

if st.sidebar.button("Logout"):

    st.session_state.clear()

    st.rerun()

st.sidebar.markdown("---")

if "usuario" in st.session_state:

    st.sidebar.write(
        f"👤 {st.session_state.get('usuario', '')}"
    )

    st.sidebar.write(
        f"🔐 Perfil: {st.session_state.get('perfil', '')}"
    )

st.sidebar.caption(
    "Sistema Base Geral - Conciliação GooRoo v1.0"
)

# =============================
# DASHBOARD
# =============================
if menu == "Dashboard":

    st.title("📊 Dashboard")

    # =============================
    # TOTAL GERAL
    # =============================
    res_count = (
        supabase.table("cobrancas")
        .select("*", count="exact")
        .limit(1)
        .execute()
    )

    total_registros = res_count.count or 0

    # =============================
    # VALOR TOTAL
    # =============================
    res_total = supabase.rpc(
        "total_valor_cobrado"
    ).execute()

    valor_total_geral = res_total.data or 0

    # =============================
    # OSCILAÇÃO TOTAL
    # =============================
    res_osc = supabase.rpc(
        "total_oscilacao"
    ).execute()

    oscilacao_total_geral = res_osc.data or 0

    # =============================
    # MÉTRICAS GERAIS
    # =============================
    st.subheader("📌 Visão Geral")

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "📄 Total Registros",
        total_registros
    )

    col2.metric(
        "💰 Valor Total",
        f"R$ {format_brl(valor_total_geral)}"
    )

    col3.metric(
        "📈 Oscilação Total",
        f"R$ {format_brl(oscilacao_total_geral)}"
    )

    st.markdown("---")

    # =============================
    # FILTRO POR DATA
    # =============================
    st.subheader("📅 Filtrar por Período")

    col_f1, col_f2 = st.columns(2)

    data_inicio = col_f1.date_input(
        "Data Inicial",
        format="DD/MM/YYYY"
    )

    data_fim = col_f2.date_input(
        "Data Final",
        format="DD/MM/YYYY"
    )

    # =============================
    # QUERY FILTRO
    # =============================
    res = (
        supabase.table("cobrancas")
        .select("*")
        .gte("data_da_liquidacao", str(data_inicio))
        .lte("data_da_liquidacao", str(data_fim))
        .execute()
    )

    df_dash = pd.DataFrame(res.data)

    total_boletos = len(df_dash)

    total_valor = 0
    total_oscilacao = 0

    if not df_dash.empty:

        if "valor_cobrado" in df_dash.columns:
            total_valor = (
                df_dash["valor_cobrado"]
                .apply(to_float)
                .sum()
            )

        if "oscilacao" in df_dash.columns:
            total_oscilacao = (
                df_dash["oscilacao"]
                .apply(to_float)
                .sum()
            )

    # =============================
    # MÉTRICAS FILTRADAS
    # =============================
    st.subheader("📊 Resultado do Período TOTAL")

    col4, col5, col6 = st.columns(3)

    col4.metric(
        "📄 Boletos no Período",
        total_boletos
    )

    col5.metric(
        "💰 Valor no Período",
        f"R$ {format_brl(total_valor)}"
    )

    col6.metric(
        "📈 Oscilação Período",
        f"R$ {format_brl(total_oscilacao)}"
    )

    # =============================
    # VALIDAÇÃO
    # =============================
    if not df_dash.empty and "boleto" in df_dash.columns:

        # =============================
        # BOLETOS BANCÁRIOS
        # =============================
        df_boletos = df_dash[
            (df_dash["boleto"].notna()) &
            (df_dash["boleto"] != "") &
            (df_dash["seu_numero"].notna()) &
            (df_dash["seu_numero"] != "")
        ]

        st.markdown("---")
        st.subheader("🏦 Boletos Bancários")

        qtd_boletos = len(df_boletos)

        valor_boletos = 0
        oscilacao_boletos = 0

        if not df_boletos.empty:

            if "valor_cobrado" in df_boletos.columns:
                valor_boletos = (
                    df_boletos["valor_cobrado"]
                    .apply(to_float)
                    .sum()
                )

            if "oscilacao" in df_boletos.columns:
                oscilacao_boletos = (
                    df_boletos["oscilacao"]
                    .apply(to_float)
                    .sum()
                )

        col_b1, col_b2, col_b3 = st.columns(3)

        col_b1.metric(
            "Quantidade",
            qtd_boletos
        )

        col_b2.metric(
            "Valor Total",
            f"R$ {format_brl(valor_boletos)}"
        )

        col_b3.metric(
            "Oscilação",
            f"R$ {format_brl(oscilacao_boletos)}"
        )

        # =============================
        # MOVIMENTAÇÕES OPERACIONAIS
        # =============================
        df_operacional = df_dash[
            (df_dash["boleto"].isna()) |
            (df_dash["boleto"] == "") |
            (df_dash["seu_numero"].isna()) |
            (df_dash["seu_numero"] == "")
        ]

        st.markdown("---")
        st.subheader("🔄 Movimentações Operacionais")

        qtd_operacional = len(df_operacional)

        valor_operacional = 0
        oscilacao_operacional = 0

        if not df_operacional.empty:

            if "valor_cobrado" in df_operacional.columns:
                valor_operacional = (
                    df_operacional["valor_cobrado"]
                    .apply(to_float)
                    .sum()
                )

            if "oscilacao" in df_operacional.columns:
                oscilacao_operacional = (
                    df_operacional["oscilacao"]
                    .apply(to_float)
                    .sum()
                )

        col_o1, col_o2, col_o3 = st.columns(3)

        col_o1.metric(
            "Quantidade",
            qtd_operacional
        )

        col_o2.metric(
            "Valor Total",
            f"R$ {format_brl(valor_operacional)}"
        )

        col_o3.metric(
            "Oscilação",
            f"R$ {format_brl(oscilacao_operacional)}"
        )

        # =============================
        # AGRUPAMENTO OPERACIONAL
        # =============================
        if not df_operacional.empty:

            agrupado = (
                df_operacional.groupby("pagador")
                .agg(
                    quantidade=("pagador", "size"),
                    valor_total=("valor_cobrado", "sum")
                )
                .reset_index()
                .sort_values("valor_total", ascending=False)
            )

            st.markdown("### 📋 Detalhamento")

            for _, row in agrupado.iterrows():

                st.write(
                    f"• {row['pagador']} "
                    f"({row['quantidade']} registros) "
                    f"- R$ {format_brl(row['valor_total'])}"
                )

    else:
        st.info("Nenhum dado encontrado no período.")

    # =============================
    # FORMATAÇÃO
    # =============================
    valor_formatado = f"R$ {format_brl(total_valor)}"

    oscilacao_formatada = f"R$ {format_brl(total_oscilacao)}"

# =============================
# CONSULTA
# =============================
elif menu == "Consulta":

    st.title("🔎 Consulta")

    # =============================
    # BUSCA
    # =============================
    col1, col2, col3, col4 = st.columns(
        [3,3,2,1],
        vertical_alignment="bottom"
    )
    
    filtro_boleto = col1.text_input(
        "Buscar boleto"
    )
    
    filtro_pagador = col2.text_input(
        "Cliente/Pagador"
    )
    
    filtro_valor = col3.text_input(
        "Valor Título"
    )
    
    buscar = col4.button(
        "Buscar",
        use_container_width=True
    )

    # =============================
    # QUERY
    # =============================
    query = supabase.table("cobrancas").select(
        "seu_numero, boleto, vencimento, data_da_liquidacao, "
        "valor_do_titulo, valor_cobrado, oscilacao, pagador, "
        "lote, boleto_manual, checagem, observacao, evidencia1"
    )

    if buscar:

        # =========================
        # BOLETO
        # =========================
        if filtro_boleto:
            query = query.ilike(
                "boleto",
                f"%{filtro_boleto}%"
            )
    
        # =========================
        # PAGADOR
        # =========================
        if filtro_pagador:
            query = query.ilike(
                "pagador",
                f"%{filtro_pagador}%"
            )
    
        # =========================
        # VALOR TÍTULO
        # =========================
        if filtro_valor:
    
            valor_busca = to_float(
                filtro_valor
            )
    
            query = query.eq(
                "valor_do_titulo",
                valor_busca
            )
    
    res = query.limit(200).execute()
    
    df = pd.DataFrame(res.data)
    # =============================
    # FORMATA DATAS
    # =============================
    data_cols = [
        "vencimento",
        "data_da_liquidacao"
    ]

    for col in data_cols:

        if col in df.columns:

            df[col] = pd.to_datetime(
                df[col],
                errors="coerce"
            ).dt.strftime("%d/%m/%Y")

    # =============================
    # FORMATA VALORES
    # =============================
    valor_cols = [
        "valor_do_titulo",
        "oscilacao",
        "boleto_manual",
        "valor_cobrado"
    ]

    for col in valor_cols:

        if col in df.columns:
            df[col] = df[col].apply(format_brl)

    # =============================
    # RENOMEIA COLUNAS
    # =============================
    df = df.rename(columns=COLUNAS_AMIGAVEIS)

    # =============================
    # MOSTRAR RESULTADOS
    # =============================
    st.dataframe(
        df,
        use_container_width=True
    )

    # =============================
    # DETALHES DA PESQUISA
    # =============================
    if buscar and res.data:
    
        st.markdown("---")
        st.subheader("👁 Detalhes dos Registros")
    
        for registro in res.data:
    
            titulo = (
                f"{registro.get('boleto', 'Sem boleto')} - "
                f"{registro.get('pagador', '')}"
            )
    
            with st.expander(
                titulo,
                expanded=False
            ):
    
                for chave, valor in registro.items():
    
                    nome_coluna = COLUNAS_AMIGAVEIS.get(
                        chave,
                        chave.upper()
                    )
    
                    # =========================
                    # DATAS
                    # =========================
                    if chave in [
                        "vencimento",
                        "data_da_liquidacao"
                    ]:
    
                        try:
                            valor = pd.to_datetime(
                                valor
                            ).strftime("%d/%m/%Y")
                        except:
                            pass
    
                    # =========================
                    # VALORES
                    # =========================
                    if chave in [
                        "valor_do_titulo",
                        "valor_cobrado",
                        "oscilacao",
                        "boleto_manual"
                    ]:
    
                        valor = (
                            f"R$ {format_brl(valor)}"
                        )
    
                    st.write(
                        f"**{nome_coluna}:** {valor}"
                    )
# =============================
# INSERIR
# =============================
elif menu == "Inserir":

    if st.session_state.get("perfil") not in [
        "admin",
        "operador"
    ]:
        st.error("⛔ Acesso negado")
        st.stop()

    st.title("➕ Inserir Registros")

    # =============================
    # ESCOLHA TIPO
    # =============================
    aba = st.radio(
        "Escolha o tipo de inserção:",
        [
            "Manual",
            "Importar Excel"
        ]
    )

    # =============================
    # MANUAL
    # =============================
    if aba == "Manual":

        col1, col2 = st.columns(2)

        boleto = col1.text_input("BOLETO")
        seu_numero = col2.text_input("SEU NUMERO")

        pagador = st.text_input("CLIENTE")

        col3, col4 = st.columns(2)

        valor_titulo = col3.number_input(
            "R$ TITULO",
            step=0.01
        )

        valor_cobrado = col4.number_input(
            "R$ COBRADO",
            step=0.01
        )

        col5, col6 = st.columns(2)

        vencimento = col5.date_input(
            "VENCIMENTO",
            format="DD/MM/YYYY"
        )

        data_pagamento = col6.date_input(
            "DATA PAGAMENTO",
            format="DD/MM/YYYY"
        )

        col7, col8 = st.columns(2)
            
        # =============================
        # OSCILAÇÃO AUTOMÁTICA
        # =============================
        oscilacao = valor_cobrado - valor_titulo
        col7.text_input(
            "OSCILAÇÃO",
            value=format_brl(oscilacao),
            disabled=True
        )

        lote = col8.text_input("LOTE")
            
        observacao = st.text_area("OBSERVAÇÃO")
        evidencia1 = st.text_input("EVIDÊNCIA")
            
        submit = st.button("Salvar")

        if submit:

            try:
        
                supabase.table("cobrancas").insert({
        
                    "boleto": boleto,
                    "seu_numero": seu_numero,
                    "pagador": pagador,
        
                    "valor_do_titulo": valor_titulo,
                    "valor_cobrado": valor_cobrado,
        
                    "vencimento": str(vencimento),
                    "data_da_liquidacao": str(data_pagamento),
        
                    "oscilacao": oscilacao,
                    "lote": lote,
        
                    "observacao": observacao,
                    "evidencia1": evidencia1
        
                }).execute()

                # =============================
                # LOG
                # =============================
                registrar_log(
                    acao="INSERIR",
                    boleto=boleto,
                    seu_numero=seu_numero,
                    pagador=pagador,
                    valor_novo=valor_cobrado,
                    observacao="Inserção manual"
                )
        
                st.success("✅ Registro inserido com sucesso!")
        
            except Exception as e:
        
                erro = str(e)
        
                if "duplicate key" in erro or "unique_boleto" in erro:
        
                    st.warning("⚠️ Boleto já existe na base de dados!")
        
                else:
        
                    st.error(f"Erro ao inserir: {erro}")

    # =============================
    # IMPORTAR EXCEL
    # =============================
    elif aba == "Importar Excel":

        st.subheader("📂 Importar arquivo Excel")

        todas_colunas = [
            "seu_numero", "boleto", "vencimento", "data_da_liquidacao",
            "valor_do_titulo", "valor_cobrado", "oscilacao", "pagador", 
            "lote","boleto_manual", "checagem", "observacao", "evidencia1"
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
            df["boleto"] = df["boleto"].replace("", None)

            # =============================
            # CONVERTE DATAS
            # =============================
            colunas_data = [
                "vencimento",
                "data_da_liquidacao"
            ]
            
            for col in colunas_data:
            
                if col in df.columns:
            
                    df[col] = pd.to_datetime(
                        df[col],
                        dayfirst=True,
                        errors="coerce"
                    ).dt.strftime("%Y-%m-%d")

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

                #===================================
                # 🔥 MOSTRAR DADOS (PREVIEW)
                #===================================
                st.write("📊 Prévia dos dados importados:")
                st.dataframe(df.head(20), use_container_width=True)
                
                #=========================
                # SOMA VALOR COBRADO
                #=========================
                total_valor_cobrado = 0
                
                if "valor_cobrado" in df.columns:
                    total_valor_cobrado = df["valor_cobrado"].apply(to_float).sum()
                    
                #======================
                # SOMA OSCILAÇÃO
                #======================
                total_oscilacao = 0
                
                if "oscilacao" in df.columns:
                    total_oscilacao = df["oscilacao"].apply(to_float).sum()
                
                    
                # =============================
                # MÉTRICAS
                # =============================
                col1, col2, col3 = st.columns(3)
                
                col1.metric(
                    "Total de Linhas",
                    len(df)
                )
                
                col2.metric(
                    "Valor Cobrado",
                    f"R$ {format_brl(total_valor_cobrado)}"
                )
                
                col3.metric(
                    "Oscilação",
                    f"R$ {format_brl(total_oscilacao)}"
                )

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
                    
                        try:
                            supabase.table("cobrancas").upsert(
                                lote,
                                on_conflict="boleto"
                            ).execute()
                        
                        except Exception as e:
                            st.error(f"Erro ao importar lote: {e}")
                            st.stop()
                    
                        progresso.progress(min((i + batch_size) / total, 1.0))
                        status.text(f"Enviando {i + len(lote)} de {total}")

                    st.success(f"✅ {total} registros inseridos com sucesso!")

# =============================
# EDITAR
# =============================
elif menu == "Editar":

    # =============================
    # PERMISSÃO
    # =============================
    if st.session_state.get("perfil") not in [
        "admin",
        "operador"
    ]:
        st.error("⛔ Acesso negado")
        st.stop()

    st.title("✏️ Editar")

    # =============================
    # BUSCAR BOLETO
    # =============================
    boleto = st.text_input(
        "Digite o boleto"
    )

    if st.button("Buscar") and boleto:

        res = (
            supabase.table("cobrancas")
            .select("*")
            .eq("boleto", boleto)
            .execute()
        )

        if res.data:

            st.session_state["registro"] = (
                res.data[0]
            )

            st.session_state["boleto_edit"] = (
                boleto
            )

        else:
            st.warning(
                "Boleto não encontrado"
            )

    # =============================
    # MOSTRAR REGISTRO
    # =============================
    if "registro" in st.session_state:

        r = st.session_state["registro"]

        # =========================
        # CAMPOS
        # =========================
        col1, col2 = st.columns(2)

        novo_boleto = col1.text_input(
            "BOLETO",
            value=r.get("boleto", ""),
            disabled=True
        )

        novo_seu_numero = col2.text_input(
            "SEU NUMERO",
            value=r.get("seu_numero", ""),
            disabled=True
        )

        novo_pagador = st.text_input(
            "CLIENTE",
            value=r.get("pagador", "")
        )

        # =========================
        # VALORES
        # =========================
        col3, col4 = st.columns(2)

        novo_valor_titulo = col3.number_input(
            "R$ TITULO",
            value=float(
                r.get("valor_do_titulo") or 0
            ),
            step=0.01
        )

        novo_valor_cobrado = col4.number_input(
            "R$ COBRADO",
            value=float(
                r.get("valor_cobrado") or 0
            ),
            step=0.01
        )

        # =========================
        # DATAS
        # =========================
        col5, col6 = st.columns(2)

        novo_vencimento = col5.date_input(
            "VENCIMENTO",
            value=pd.to_datetime(
                r.get("vencimento")
            ).date(),
            format="DD/MM/YYYY"
        )

        nova_data_pagamento = col6.date_input(
            "DATA PAGAMENTO",
            value=pd.to_datetime(
                r.get("data_da_liquidacao")
            ).date(),
            format="DD/MM/YYYY"
        )

        # =========================
        # OSCILAÇÃO AUTOMÁTICA
        # =========================
        col7, col8 = st.columns(2)

        nova_oscilacao = (
            novo_valor_cobrado
            - novo_valor_titulo
        )

        col7.text_input(
            "OSCILAÇÃO",
            value=format_brl(
                nova_oscilacao
            ),
            disabled=True
        )

        novo_lote = col8.text_input(
            "LOTE",
            value=r.get("lote", "")
        )

        # =========================
        # OBSERVAÇÕES
        # =========================
        nova_observacao = st.text_area(
            "OBSERVAÇÃO",
            value=r.get(
                "observacao",
                ""
            )
        )

        nova_evidencia = st.text_input(
            "EVIDÊNCIA",
            value=r.get(
                "evidencia1",
                ""
            )
        )

        # =========================
        # SALVAR ALTERAÇÕES
        # =========================
        if st.button(
            "Salvar alterações"
        ):
        
            # histórico
            (
                supabase.table(
                    "cobrancas_log"
                )
                .insert({
                    "boleto": novo_boleto,
                    "pagador": novo_pagador,
                    "valor_cobrado":
                        novo_valor_cobrado
                })
                .execute()
            )
        
            # update
            (
                supabase.table(
                    "cobrancas"
                )
                .update({
        
                    "boleto":
                        novo_boleto,
        
                    "seu_numero":
                        novo_seu_numero,
        
                    "pagador":
                        novo_pagador,
        
                    "valor_do_titulo":
                        novo_valor_titulo,
        
                    "valor_cobrado":
                        novo_valor_cobrado,
        
                    "oscilacao":
                        nova_oscilacao,
        
                    "vencimento":
                        str(
                            novo_vencimento
                        ),
        
                    "data_da_liquidacao":
                        str(
                            nova_data_pagamento
                        ),
        
                    "lote":
                        novo_lote,
        
                    "observacao":
                        nova_observacao,
        
                    "evidencia1":
                        nova_evidencia
        
                })
                .eq(
                    "boleto",
                    st.session_state[
                        "boleto_edit"
                    ]
                )
                .execute()
            )
        
            # =========================
            # LOG AUDITORIA
            # =========================
            registrar_log(
                acao="EDITAR",
        
                boleto=novo_boleto,
        
                seu_numero=
                    novo_seu_numero,
        
                pagador=
                    novo_pagador,
        
                valor_anterior=
                    r.get(
                        "valor_cobrado"
                    ),
        
                valor_novo=
                    novo_valor_cobrado,
        
                observacao=
                    "Registro editado"
            )
        
            st.success(
                "✅ Registro atualizado!"
            )


# =============================
# EXCLUIR
# =============================
elif menu == "Excluir":

    # =============================
    # PERMISSÃO
    # =============================
    if st.session_state.get("perfil") != "superadmin":
        st.error("⛔ Acesso negado")
        st.stop()

    st.title("❌ Excluir")

    # =========================
    # BUSCAR REGISTRO
    # =========================
    if st.button("Buscar") and boleto:

        res = (
            supabase.table("cobrancas")
            .select("*")
            .eq("boleto", boleto)
            .execute()
        )

        if res.data:

            st.session_state["registro_excluir"] = (
                res.data[0]
            )

        else:
            st.warning("Boleto não encontrado")

    # =========================
    # MOSTRAR DADOS
    # =========================
    if "registro_excluir" in st.session_state:

        r = st.session_state["registro_excluir"]

        st.markdown(
            "### ⚠️ Confirme os dados antes de excluir"
        )

        col1, col2 = st.columns(2)

        col1.write(
            f"**BOLETO:** {r.get('boleto', '')}"
        )

        col1.write(
            f"**CLIENTE:** {r.get('pagador', '')}"
        )

        col2.write(
            f"**SEU NÚMERO:** {r.get('seu_numero', '')}"
        )

        col2.write(
            f"**VALOR:** R$ {format_brl(r.get('valor_cobrado', 0))}"
        )

        st.markdown("---")

        # =========================
        # CONFIRMAR EXCLUSÃO
        # =========================
        if st.button("🗑 Confirmar Exclusão"):

            # =========================
            # LOG AUDITORIA
            # =========================
            registrar_log(
                acao="EXCLUIR",
        
                boleto=r.get(
                    "boleto"
                ),
        
                seu_numero=r.get(
                    "seu_numero"
                ),
        
                pagador=r.get(
                    "pagador"
                ),
        
                valor_anterior=r.get(
                    "valor_cobrado"
                ),
        
                observacao=
                    "Registro excluído"
            )
        
            (
                supabase.table(
                    "cobrancas"
                )
                .delete()
                .eq(
                    "boleto",
                    r.get("boleto")
                )
                .execute()
            )
        
            del st.session_state[
                "registro_excluir"
            ]
        
            st.success(
                "Registro excluído com sucesso!"
            )


# =============================
# HISTÓRICO
# =============================
elif menu == "Histórico":

    if st.session_state.get("perfil") not in [
        "admin",
        "operador"
    ]:
        st.error("⛔ Acesso negado")
        st.stop()

    st.title("🕓 Histórico")

# =============================
# USUÁRIOS
# =============================
elif menu == "Usuários":

    # =============================
    # PERMISSÃO
    # =============================
    if st.session_state.get("perfil") != "superadmin":
        st.error("⛔ Acesso negado")
        st.stop()

    st.title("👥 Usuários")

    # =============================
    # CRIAR USUÁRIO
    # =============================
    st.subheader("➕ Criar usuário")

    col1, col2 = st.columns(2)

    novo_usuario = col1.text_input(
        "Usuário"
    )

    nova_senha = col2.text_input(
        "Senha",
        type="password"
    )

    col3, col4 = st.columns(2)

    perfil_usuario = col3.selectbox(
        "Perfil",
        [
            "superadmin",
            "admin",
            "operador",
            "leitura"
        ]
    )

    ativo = col4.checkbox(
        "Usuário ativo",
        value=True
    )

    if st.button("Criar usuário"):

        if not novo_usuario or not nova_senha:
            st.warning(
                "Preencha usuário e senha"
            )
            st.stop()

        existe = (
            supabase.table("usuarios")
            .select("usuario")
            .eq(
                "usuario",
                novo_usuario
            )
            .execute()
        )

        if existe.data:
            st.error(
                "Usuário já existe"
            )
            st.stop()

        senha_hash = bcrypt.hashpw(
            nova_senha.encode(),
            bcrypt.gensalt()
        ).decode()

        (
            supabase.table("usuarios")
            .insert({
                "usuario":
                    novo_usuario,

                "senha_hash":
                    senha_hash,

                "perfil":
                    perfil_usuario,

                "ativo":
                    ativo
            })
            .execute()
        )

        st.success(
            "✅ Usuário criado!"
        )

        st.rerun()

    st.markdown("---")

    # =============================
    # GERENCIAR USUÁRIOS
    # =============================
    st.subheader(
        "⚙️ Gerenciar usuários"
    )

    res = (
        supabase.table("usuarios")
        .select("*")
        .execute()
    )

    usuarios = res.data

    for user in usuarios:

        usuario = user.get(
            "usuario"
        )

        perfil_atual = user.get(
            "perfil",
            "leitura"
        )

        ativo_atual = user.get(
            "ativo",
            True
        )

        with st.expander(
            f"👤 {usuario} ({perfil_atual})"
        ):

            novo_perfil = st.selectbox(
                "Perfil",
                [
                    "superadmin",
                    "admin",
                    "operador",
                    "leitura"
                ],
                index=[
                    "superadmin",
                    "admin",
                    "operador",
                    "leitura"
                ].index(perfil_atual),
                key=f"perfil_{usuario}"
            )

            novo_ativo = st.checkbox(
                "Usuário ativo",
                value=ativo_atual,
                key=f"ativo_{usuario}"
            )

            nova_senha_user = st.text_input(
                "Nova senha (opcional)",
                type="password",
                key=f"senha_{usuario}"
            )

            col_btn1, col_btn2 = st.columns(2)

            # =====================
            # SALVAR
            # =====================
            if col_btn1.button(
                "💾 Salvar alterações",
                key=f"salvar_{usuario}"
            ):

                dados_update = {
                    "perfil":
                        novo_perfil,

                    "ativo":
                        novo_ativo
                }

                if nova_senha_user:

                    senha_hash = (
                        bcrypt.hashpw(
                            nova_senha_user.encode(),
                            bcrypt.gensalt()
                        ).decode()
                    )

                    dados_update[
                        "senha_hash"
                    ] = senha_hash

                (
                    supabase.table(
                        "usuarios"
                    )
                    .update(
                        dados_update
                    )
                    .eq(
                        "usuario",
                        usuario
                    )
                    .execute()
                )

                st.success(
                    f"{usuario} atualizado!"
                )

                st.rerun()

            # =====================
            # EXCLUIR
            # =====================
            if col_btn2.button(
                "🗑 Excluir usuário",
                key=f"delete_{usuario}"
            ):

                # impedir excluir si mesmo
                if (
                    usuario
                    == st.session_state.get(
                        "usuario"
                    )
                ):
                    st.error(
                        "Você não pode excluir seu próprio usuário."
                    )
                    st.stop()

                # impedir excluir último superadmin
                supers = (
                    supabase.table(
                        "usuarios"
                    )
                    .select("*")
                    .eq(
                        "perfil",
                        "superadmin"
                    )
                    .execute()
                )

                if (
                    perfil_atual
                    == "superadmin"
                    and len(
                        supers.data
                    ) <= 1
                ):
                    st.error(
                        "Não é possível excluir o último superadmin."
                    )
                    st.stop()

                (
                    supabase.table(
                        "usuarios"
                    )
                    .delete()
                    .eq(
                        "usuario",
                        usuario
                    )
                    .execute()
                )

                st.success(
                    f"{usuario} removido!"
                )

                st.rerun()

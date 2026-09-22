import pandas as pd
import streamlit as st

# Tenta importar o módulo de banco de dados
try:
    import modulos.database as db

    HAS_DB = True
except ImportError:
    HAS_DB = False

# -----------------------------------------------------------------------------
# 1. CONFIGURAÇÃO DA PÁGINA E DESIGN SYSTEM (VERDE-ÁGUA, LILÁS E BRANCO)
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="NutriDAY - Nutrição Esportiva & Clínica",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        /* Fundo geral e fontes */
        .stApp {
            background-color: #F8FAF9;
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Botões Principais - Verde-Água (#2EC4B6) */
        .stButton>button {
            background-color: #2EC4B6 !important;
            color: #FFFFFF !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 600 !important;
            transition: all 0.2s ease-in-out;
        }
        .stButton>button:hover {
            background-color: #25A195 !important;
            box-shadow: 0px 4px 10px rgba(46, 196, 182, 0.25);
        }

        /* Títulos e Cabeçalhos */
        h1, h2, h3, h4 {
            color: #2A363B !important;
            font-weight: 700 !important;
        }
        
        /* Cards / Expanders com Borda em Lilás Suave (#EFE6FA) */
        div[data-testid="stExpander"] {
            background-color: #FFFFFF !important;
            border: 1px solid #EFE6FA !important;
            border-radius: 12px !important;
            box-shadow: 0px 2px 6px rgba(155, 81, 224, 0.05) !important;
        }
        
        /* Sidebar Styling */
        section[data-testid="stSidebar"] {
            background-color: #FFFFFF !important;
            border-right: 1px solid #EFE6FA !important;
        }
        
        /* Métricas (Cards Highlight) */
        div[data-testid="stMetricValue"] {
            color: #9B51E0 !important;
            font-weight: 700 !important;
        }

        /* Estilização de Tabs */
        button[data-baseweb="tab"] {
            color: #2A363B !important;
            font-weight: 600 !important;
        }
        button[aria-selected="true"] {
            color: #9B51E0 !important;
            border-bottom-color: #9B51E0 !important;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# Inicialização do banco de dados (se o módulo estiver presente)
if HAS_DB:
    try:
        db.inicializar_banco()
    except Exception as e:
        st.sidebar.error(f"Erro na conexão PostgreSQL: {e}")

# -----------------------------------------------------------------------------
# 2. MENU LATERAL & NAVEGAÇÃO
# -----------------------------------------------------------------------------
st.sidebar.title("NutriDAY")
st.sidebar.caption("Painel Clínico & Nutrição Esportiva")

aba_selecionada = st.sidebar.radio(
    "Navegação",
    [
        "Planejamento Alimentar",
        "Cálculos Esportivos (TMB/GET)",
        "Banco de Dados & Alimentos",
    ],
)

# -----------------------------------------------------------------------------
# ABA 1: PLANEJAMENTO ALIMENTAR
# -----------------------------------------------------------------------------
if aba_selecionada == "Planejamento Alimentar":
    st.title("Planejamento Alimentar")

    col_paciente, col_meta = st.columns([2, 1])

    with col_paciente:
        nome_paciente = st.text_input(
            "Nome do Paciente / Atleta", placeholder="Ex: Dra. Andressa Rezende"
        )
    with col_meta:
        meta_calorica = st.number_input(
            "Meta Calórica Diária (kcal)", value=2000, step=50
        )

    st.subheader("Refeições do Dia")

    categorias_refeicao = [
        "Café da Manhã",
        "Lanche da Manhã",
        "Almoço",
        "Pré-Treino",
        "Pós-Treino",
        "Jantar",
        "Ceia",
    ]

    for ref in categorias_refeicao:
        with st.expander(f"📌 {ref}"):
            col_ing, col_qtd, col_add = st.columns([3, 2, 1])
            alimento = col_ing.text_input(
                f"Alimento para {ref}", key=f"ing_{ref}"
            )
            quantidade = col_qtd.text_input(
                "Quantidade (ex: 100g, 2 fatias)", key=f"qtd_{ref}"
            )

            if col_add.button("Adicionar", key=f"btn_{ref}"):
                st.success(f"Alimento adicionado ao {ref}!")

# -----------------------------------------------------------------------------
# ABA 2: CÁLCULOS ESPORTIVOS (TMB / GET)
# -----------------------------------------------------------------------------
elif aba_selecionada == "Cálculos Esportivos (TMB/GET)":
    st.title("Avaliação Metabólica Esportiva")

    c1, c2, c3, c4 = st.columns(4)
    sexo = c1.selectbox("Sexo", ["Feminino", "Masculino"])
    idade = c2.number_input("Idade", value=25, min_value=10, max_value=100)
    peso = c3.number_input(
        "Peso (kg)", value=70.0, step=0.5, format="%.1f"
    )
    altura = c4.number_input("Altura (cm)", value=170, min_value=100, max_value=230)

    fator_atividade = st.select_slider(
        "Nível de Atividade Física (Fator AF)",
        options=[
            "Sedentário (1.2)",
            "Levemente Ativo (1.375)",
            "Moderadamente Ativo (1.55)",
            "Altamente Ativo (1.725)",
            "Extremamente Ativo (1.9)",
        ],
        value="Moderadamente Ativo (1.55)",
    )

    # Extrai o valor numérico do fator de atividade
    fator_num = float(fator_atividade.split("(")[1].replace(")", ""))

    # Fórmula de Mifflin-St Jeor para TMB
    if sexo == "Masculino":
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) + 5
    else:
        tmb = (10 * peso) + (6.25 * altura) - (5 * idade) - 161

    get = tmb * fator_num

    st.markdown("---")
    st.subheader("Resultados Calculados")

    m1, m2, m3 = st.columns(3)
    m1.metric("TMB (Metabolismo Basal)", f"{tmb:.0f} kcal")
    m2.metric("GET (Gasto Energético Total)", f"{get:.0f} kcal")
    m3.metric("Fator AF Utilizado", f"{fator_num}")

# -----------------------------------------------------------------------------
# ABA 3: BANCO DE DADOS & ALIMENTOS (POSTGRESQL - NEON)
# -----------------------------------------------------------------------------
elif aba_selecionada == "Banco de Dados & Alimentos":
    st.title("Gestão de Alimentos no PostgreSQL")

    if not HAS_DB:
        st.warning(
            "O módulo `modulos.database` não foi localizado localmente. Certifique-se de salvar as alterações."
        )
    else:
        with st.expander("➕ Cadastrar Novo Alimento Customizado"):
            col1, col2, col3, col4, col5 = st.columns(5)
            nome = col1.text_input("Nome do Alimento")
            kcal = col2.number_input("Kcal (100g)", min_value=0.0, step=1.0)
            prot = col3.number_input("Proteína (g)", min_value=0.0, step=0.1)
            carb = col4.number_input("Carboidrato (g)", min_value=0.0, step=0.1)
            gord = col5.number_input("Gordura (g)", min_value=0.0, step=0.1)

            if st.button("Salvar no Banco de Dados"):
                if nome:
                    try:
                        db.salvar_alimento_custom(nome, kcal, prot, carb, gord)
                        st.success(
                            f"Alimento '{nome}' cadastrado permanentemente no Neon!"
                        )
                        st.rerun()
                    except Exception as err:
                        st.error(f"Erro ao salvar alimento: {err}")
                else:
                    st.warning("Por favor, preencha o nome do alimento.")

        st.subheader("Tabela de Alimentos Cadastrados")

        try:
            df_alimentos = db.carregar_alimentos_custom()
            if df_alimentos is not None and not df_alimentos.empty:
                st.dataframe(
                    df_alimentos, use_container_width=True, hide_index=True
                )
            else:
                st.info(
                    "Nenhum alimento personalizado cadastrado até o momento."
                )
        except Exception as err:
            st.error(
                f"Erro ao carregar lista de alimentos do banco de dados: {err}"
            )
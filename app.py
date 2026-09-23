import pandas as pd
import streamlit as st

# Tenta importar os módulos do sistema
from modulos.calculos import (
    calcular_imc,
    calcular_peso_ideal,
    classificar_imc,
    somar_totais_diarios,
)
from modulos.pdf import criar_pdf_plano
from modulos.taco import carregar_tabela_taco

try:
    import modulos.database as db

    HAS_DB = True
except ImportError:
    HAS_DB = False

# Configuração da Página
st.set_page_config(
    page_title="NutriDAY - Dra. Andressa Santos", layout="wide"
)

# Inicializa o banco de dados Neon se disponível
if HAS_DB:
    try:
        db.inicializar_banco()
    except Exception:
        pass

# -----------------------------------------------------------------------------
# ESTILIZAÇÃO CSS (VERDE-ÁGUA, LILÁS E BRANCO - SEM EMOJIS)
# -----------------------------------------------------------------------------
st.markdown(
    """
<style>
    .stApp {
        background-color: #FFFFFF;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    /* Header Principal */
    .main-header {
        background: linear-gradient(135deg, #2EC4B6 0%, #25A195 100%);
        padding: 24px 32px;
        border-radius: 12px;
        color: white;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        margin-bottom: 25px;
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.1rem;
        font-weight: 700;
        color: #FFFFFF !important;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin-top: 4px;
        font-size: 0.95rem;
        color: #F0FDF4;
        font-weight: 400;
    }

    /* Botões em Verde-Água */
    .stButton>button {
        border-radius: 8px;
        border: none;
        background-color: #2EC4B6;
        color: white !important;
        font-weight: 600;
        padding: 10px 24px;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #25A195;
        color: white !important;
    }

    /* Tabs em Lilás */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        background-color: #FFFFFF;
        border: 1px solid #EFE6FA;
        color: #4A5568;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #9B51E0 !important;
        color: white !important;
        border-color: #9B51E0 !important;
    }

    /* Sidebar & Cartões */
    section[data-testid="stSidebar"] {
        background-color: #F8FAF9 !important;
        border-right: 1px solid #EFE6FA !important;
    }
    
    div[data-testid="stMetricValue"] {
        color: #9B51E0 !important;
        font-weight: 700 !important;
    }

    hr {
        border-color: #EFE6FA;
        margin: 28px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Definir as refeições do sistema
refeicoes_nomes = [
    "Café da Manhã",
    "Lanche da Manhã (Pré-Treino)",
    "Almoço",
    "Lanche da Tarde (Pós-Treino)",
    "Jantar",
    "Ceia",
]

# Inicialização de variáveis de sessão
if "dieta" not in st.session_state:
    st.session_state.dieta = {ref: [] for ref in refeicoes_nomes}
else:
    for ref in refeicoes_nomes:
        if ref not in st.session_state.dieta:
            st.session_state.dieta[ref] = []

if "alimentos_custom" not in st.session_state:
    st.session_state.alimentos_custom = pd.DataFrame(
        columns=[
            "nome",
            "energia_kcal",
            "proteina_g",
            "carboidrato_g",
            "lipideos_g",
        ]
    )

if "fichas_pacientes" not in st.session_state:
    st.session_state.fichas_pacientes = []

# Carregamento da tabela TACO
df_taco_base = carregar_tabela_taco()

# Unificação das tabelas
if not st.session_state.alimentos_custom.empty:
    df_taco = pd.concat(
        [df_taco_base, st.session_state.alimentos_custom], ignore_index=True
    )
else:
    df_taco = df_taco_base

# -----------------------------------------------------------------------------
# MENU LATERAL - NAVEGAÇÃO ENTRE PLANO E FICHAS DOS PACIENTES
# -----------------------------------------------------------------------------
st.sidebar.title("NutriDAY")
st.sidebar.caption("Painel Clínico - Dra. Andressa Santos")

menu_opcao = st.sidebar.radio(
    "Menu de Acesso", ["Prescrição Nutricional", "Fichas dos Pacientes"]
)

# -----------------------------------------------------------------------------
# PÁGINA 1: PRESCRIÇÃO NUTRICIONAL
# -----------------------------------------------------------------------------
if menu_opcao == "Prescrição Nutricional":
    # Header
    st.markdown(
        """
    <div class="main-header">
        <h1>NutriDAY</h1>
        <p>Prescrição Nutricional e Esportiva | Dra. Andressa Santos</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    # Seção 1: Paciente e Perfil Esportivo
    st.markdown("### Identificação e Perfil do Paciente")
    col_dados, col_esporte = st.columns([1, 1], gap="large")

    with col_dados:
        nome_paciente = st.text_input("Nome Completo", "Lucas Mendes")
        c_sexo, c_idade = st.columns(2)
        sexo = c_sexo.selectbox("Sexo Biológico", ["Masculino", "Feminino"])
        idade = c_idade.number_input(
            "Idade (anos)", min_value=1, max_value=120, value=28, step=1
        )

        c1, c2 = st.columns(2)
        peso = c1.number_input(
            "Peso (kg)", min_value=1.0, max_value=300.0, value=75.0, step=0.1
        )
        altura = c2.number_input(
            "Altura (m)", min_value=0.5, max_value=2.5, value=1.78, step=0.01
        )

    with col_esporte:
        modalidade = st.text_input(
            "Modalidade Esportiva / Treino", "Musculação 5x/semana + Corrida"
        )

        fator_ativ_map = {
            "Sedentário (Pouco ou nenhum exercício)": 1.2,
            "Leve (Treino 1 a 3 dias/semana)": 1.375,
            "Moderado (Treino 3 a 5 dias/semana)": 1.55,
            "Intenso (Treino pesado 6 a 7 dias/semana)": 1.725,
            "Muito Intenso / Atleta (2 treinos por dia)": 1.9,
        }
        fator_sel = st.selectbox(
            "Nível de Atividade Física", list(fator_ativ_map.keys()), index=2
        )
        fator_atividade = fator_ativ_map[fator_sel]

        objetivo = st.selectbox(
            "Objetivo Nutricional",
            [
                "Hipertrofia (Ganho de Massa)",
                "Emagrecimento / Definição",
                "Manutenção e Performance",
            ],
        )

        restricoes = st.text_input(
            "Restrições Alimentares / Suplementação Atual",
            placeholder="Ex: Intolerância à Lactose, Usa Creatina 5g e Whey...",
        )

    # Cálculos Metabólicos & Esportivos
    imc = calcular_imc(peso, altura)
    classificacao = classificar_imc(imc)
    peso_ideal = calcular_peso_ideal(altura)

    # TMB (Mifflin-St Jeor)
    if sexo == "Masculino":
        tmb = (10 * peso) + (6.25 * (altura * 100)) - (5 * idade) + 5
    else:
        tmb = (10 * peso) + (6.25 * (altura * 100)) - (5 * idade) - 161

    get = tmb * fator_atividade

    # Meta Calórica
    if objetivo == "Hipertrofia (Ganho de Massa)":
        meta_kcal = get + 400
    elif objetivo == "Emagrecimento / Definição":
        meta_kcal = get - 500
    else:
        meta_kcal = get

    st.markdown("---")

    # Seção 2: Painel de Avaliação Energética
    st.markdown("### Avaliação Metabólica e Metas Calóricas")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)

    m_col1.metric("IMC", f"{imc:.1f} kg/m²", classificacao)
    m_col2.metric("Basal (TMB)", f"{int(tmb)} kcal")
    m_col3.metric("Gasto Total (GET)", f"{int(get)} kcal")
    m_col4.metric("Meta Calórica Diária", f"{int(meta_kcal)} kcal")

    st.markdown("---")

    # Seção 3: Cadastro de Alimentos Personalizados
    with st.expander(
        "Cadastrar Novo Alimento / Suplemento (Fora da TACO)", expanded=False
    ):
        st.write(
            "Insira os dados nutricionais referentes a **100g** do alimento ou suplemento:"
        )
        c_nome, c_kcal, c_prot, c_carb, c_gord = st.columns(5)

        novo_nome = c_nome.text_input(
            "Nome do Alimento", placeholder="Ex: Whey Iso, Barra de Proteína"
        )
        nova_kcal = c_kcal.number_input(
            "Kcal (100g)", min_value=0.0, step=1.0, value=0.0
        )
        nova_prot = c_prot.number_input(
            "Proteína g (100g)", min_value=0.0, step=0.1, value=0.0
        )
        novo_carb = c_carb.number_input(
            "Carboidrato g (100g)", min_value=0.0, step=0.1, value=0.0
        )
        nova_gord = c_gord.number_input(
            "Gordura g (100g)", min_value=0.0, step=0.1, value=0.0
        )

        if st.button("Salvar Alimento"):
            if novo_nome.strip():
                if HAS_DB:
                    try:
                        db.salvar_alimento_custom(
                            novo_nome.strip(),
                            nova_kcal,
                            nova_prot,
                            novo_carb,
                            nova_gord,
                        )
                    except Exception:
                        pass

                novo_item = pd.DataFrame(
                    [
                        {
                            "nome": f"[Personalizado] {novo_nome.strip()}",
                            "energia_kcal": float(nova_kcal),
                            "proteina_g": float(nova_prot),
                            "carboidrato_g": float(novo_carb),
                            "lipideos_g": float(nova_gord),
                        }
                    ]
                )
                st.session_state.alimentos_custom = pd.concat(
                    [st.session_state.alimentos_custom, novo_item],
                    ignore_index=True,
                )
                st.success(f"Alimento '{novo_nome}' cadastrado com sucesso!")
                st.rerun()
            else:
                st.warning("Informe o nome do alimento.")

    st.markdown("---")

    # Seção 4: Prescrição do Plano Alimentar
    st.markdown("### Plano Alimentar")

    tabs = st.tabs(refeicoes_nomes)

    for i, ref in enumerate(refeicoes_nomes):
        with tabs[i]:
            st.write(f"#### {ref}")
            c_alimento, c_qtd, c_btn = st.columns([3, 1, 1], gap="medium")

            lista_alimentos = (
                df_taco["nome"].tolist() if not df_taco.empty else []
            )
            alimento_sel = c_alimento.selectbox(
                "Selecione o alimento", lista_alimentos, key=f"sel_{ref}"
            )
            qtd_gramas = c_qtd.number_input(
                "Quantidade (g)",
                min_value=5,
                max_value=1000,
                value=100,
                step=5,
                key=f"qtd_{ref}",
            )

            c_btn.markdown(
                "<div style='padding-top: 28px;'></div>", unsafe_allow_html=True
            )
            if c_btn.button("Adicionar Alimento", key=f"btn_{ref}"):
                if not df_taco.empty and alimento_sel:
                    row = df_taco[df_taco["nome"] == alimento_sel].iloc[0]
                    fator = qtd_gramas / 100.0

                    # Tratamento para valores nulos (NaN) da tabela TACO
                    kcal_val = float(pd.Series(row.get("energia_kcal")).fillna(0).iloc[0])
                    prot_val = float(pd.Series(row.get("proteina_g")).fillna(0).iloc[0])
                    carb_val = float(pd.Series(row.get("carboidrato_g")).fillna(0).iloc[0])
                    gord_val = float(pd.Series(row.get("lipideos_g")).fillna(0).iloc[0])

                    item = {
                        "nome": alimento_sel,
                        "quantidade_g": qtd_gramas,
                        "energia_kcal": round(kcal_val * fator, 1),
                        "proteina_g": round(prot_val * fator, 1),
                        "carboidrato_g": round(carb_val * fator, 1),
                        "lipideos_g": round(gord_val * fator, 1),
                    }
                    st.session_state.dieta[ref].append(item)
                    st.toast(
                        f"Alimento '{alimento_sel}' adicionado com sucesso."
                    )

            if st.session_state.dieta.get(ref):
                st.markdown("##### Alimentos Adicionados:")
                items_para_remover = []
                for idx, item in enumerate(st.session_state.dieta[ref]):
                    col_item_nome, col_item_qtd, col_item_kcal, col_item_del = (
                        st.columns([3, 1, 1, 1])
                    )
                    col_item_nome.write(f"• **{item['nome']}**")
                    col_item_qtd.write(f"{item['quantidade_g']} g")
                    col_item_kcal.write(f"{item['energia_kcal']} kcal")
                    if col_item_del.button("Remover", key=f"del_{ref}_{idx}"):
                        items_para_remover.append(idx)

                if items_para_remover:
                    for idx in reversed(items_para_remover):
                        removido = st.session_state.dieta[ref].pop(idx)
                        st.toast(f"Alimento '{removido['nome']}' removido.")
                    st.rerun()

    st.markdown("---")

    # Seção 5: Balanço Nutricional e Métricas g/kg
    st.markdown("### Balanço Nutricional e Relatório Esportivo (g/kg)")

    total_kcal, total_prot, total_carb, total_gord = somar_totais_diarios(
        st.session_state.dieta
    )

    prot_gkg = total_prot / peso if peso > 0 else 0
    carb_gkg = total_carb / peso if peso > 0 else 0
    gord_gkg = total_gord / peso if peso > 0 else 0

    b1, b2, b3, b4 = st.columns(4)
    b1.metric(
        "Energia Prescrita",
        f"{total_kcal:.1f} kcal",
        f"Meta: {int(meta_kcal)} kcal",
    )
    b2.metric("Proteína Total", f"{total_prot:.1f} g", f"{prot_gkg:.2f} g/kg")
    b3.metric(
        "Carboidrato Total", f"{total_carb:.1f} g", f"{carb_gkg:.2f} g/kg"
    )
    b4.metric("Gordura Total", f"{total_gord:.1f} g", f"{gord_gkg:.2f} g/kg")

    # Seção 6: Guardar Ficha do Paciente
    st.markdown("---")
    st.markdown("### Guardar Ficha do Paciente")

    if st.button("Guardar Ficha do Paciente na Sessão"):
        ficha_nova = {
            "nome": nome_paciente,
            "sexo": sexo,
            "idade": idade,
            "peso": peso,
            "altura": altura,
            "imc": imc,
            "objetivo": objetivo,
            "total_kcal": total_kcal,
            "meta_kcal": meta_kcal,
        }
        st.session_state.fichas_pacientes.append(ficha_nova)
        st.success(
            f"Ficha de {nome_paciente} salva! Aceda ao menu 'Fichas dos Pacientes' na barra lateral."
        )

    # Seção 7: Exportação em PDF
    st.markdown("---")
    st.markdown("### Exportar Documento")

    if st.button("Gerar Relatório em PDF"):
        try:
            pdf_bytes = criar_pdf_plano(
                nome_paciente=str(nome_paciente or "Paciente"),
                sexo=str(sexo),
                idade=int(idade or 0),
                peso=float(peso or 0.0),
                altura=float(altura or 0.0),
                imc=float(imc or 0.0),
                classificacao=str(classificacao),
                peso_ideal=float(peso_ideal or 0.0),
                restricoes=str(restricoes or ""),
                dieta=st.session_state.get("dieta", {}),
                total_kcal=float(total_kcal or 0.0),
                total_prot=float(total_prot or 0.0),
                total_carb=float(total_carb or 0.0),
                total_gord=float(total_gord or 0.0),
            )
            st.session_state["pdf_pronto"] = pdf_bytes
            st.success(
                "PDF gerado com sucesso! Clique no botão abaixo para descarregar."
            )
        except Exception as e:
            st.error(f"Erro ao gerar o relatório em PDF: {str(e)}")

    if (
        "pdf_pronto" in st.session_state
        and st.session_state["pdf_pronto"] is not None
    ):
        st.download_button(
            label="Baixar Plano Alimentar (PDF)",
            data=st.session_state["pdf_pronto"],
            file_name=f"NutriDAY_{str(nome_paciente).replace(' ', '_')}.pdf",
            mime="application/pdf",
        )

# -----------------------------------------------------------------------------
# PÁGINA 2: FICHAS E ACOMPANHAMENTO DOS PACIENTES
# -----------------------------------------------------------------------------
elif menu_opcao == "Fichas dos Pacientes":
    st.markdown(
        """
    <div class="main-header">
        <h1>Fichas e Acompanhamento de Pacientes</h1>
        <p>Gestão de Consultas e Histórico Clínico | Dra. Andressa Santos</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.subheader("Pacientes Cadastrados")

    if st.session_state.fichas_pacientes:
        df_fichas = pd.DataFrame(st.session_state.fichas_pacientes)
        st.dataframe(df_fichas, use_container_width=True, hide_index=True)
    else:
        st.info(
            "Nenhum paciente guardado até ao momento. Preencha os dados na página 'Prescrição Nutricional' e clique em 'Guardar Ficha do Paciente'."
        )
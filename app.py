import pandas as pd
import streamlit as st

from modulos.calculos import (
    calcular_imc,
    classificar_imc,
    calcular_peso_ideal,
    somar_totais_diarios,
)
from modulos.pdf import criar_pdf_plano
from modulos.taco import carregar_tabela_taco

# Configuração da Página
st.set_page_config(page_title="NutriDAY — Dra. Andressa Santos", layout="wide")

# Estilização CSS Clean & Profissional
st.markdown(
    """
<style>
    .stApp {
        background-color: #f8fafc;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
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
        color: #ffffff !important;
        letter-spacing: -0.5px;
    }
    .main-header p {
        margin-top: 4px;
        font-size: 0.95rem;
        color: #e2e8f0;
        font-weight: 400;
    }

    .imc-card {
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.02);
    }
    .imc-label {
        color: #64748b;
        font-weight: 600;
        font-size: 0.85rem;
        margin-bottom: 4px;
    }
    .imc-value {
        color: #0f172a;
        font-weight: 700;
        font-size: 1.8rem;
        margin-bottom: 8px;
    }
    .imc-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 12px;
    }
    .peso-ideal-box {
        border-top: 1px solid #f1f5f9;
        padding-top: 10px;
        margin-top: 4px;
        font-size: 0.9rem;
        color: #334155;
    }

    .badge-verde {
        background-color: #dcfce7;
        color: #15803d;
    }
    .badge-laranja {
        background-color: #ffedd5;
        color: #c2410c;
    }
    .badge-vermelho {
        background-color: #fee2e2;
        color: #b91c1c;
    }

    .stButton>button {
        border-radius: 8px;
        border: none;
        background-color: #059669;
        color: white;
        font-weight: 600;
        padding: 10px 24px;
        transition: background-color 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #047857;
        color: white;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 6px;
        padding: 8px 16px;
        background-color: #ffffff;
        border: 1px solid #e2e8f0;
        color: #475569;
        font-weight: 500;
    }
    .stTabs [aria-selected="true"] {
        background-color: #059669 !important;
        color: white !important;
        border-color: #059669 !important;
    }

    hr {
        border-color: #e2e8f0;
        margin: 28px 0;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Inicialização da lista de alimentos customizados
if "alimentos_custom" not in st.session_state:
    st.session_state.alimentos_custom = pd.DataFrame(
        columns=["nome", "energia_kcal", "proteina_g", "carboidrato_g", "lipideos_g"]
    )

# Carregamento da tabela TACO oficial
df_taco_base = carregar_tabela_taco()

# Unificação das tabelas (TACO + Alimentos Personalizados)
if not st.session_state.alimentos_custom.empty:
    df_taco = pd.concat([df_taco_base, st.session_state.alimentos_custom], ignore_index=True)
else:
    df_taco = df_taco_base

# Header
st.markdown(
    """
<div class="main-header">
    <h1>NutriDAY</h1>
    <p>Prescrição Nutricional & Gestão Clínica | Dra. Andressa Santos</p>
</div>
""",
    unsafe_allow_html=True,
)

# Seção 1: Paciente & Avaliação Antropométrica
col_dados, col_imc = st.columns([2, 1], gap="large")

with col_dados:
    st.markdown("### Identificação do Paciente")
    nome_paciente = st.text_input("Nome Completo", "Lucas Mendes")

    c_sexo, c_idade = st.columns(2)
    sexo = c_sexo.selectbox("Sexo", ["Feminino", "Masculino"])
    idade = c_idade.number_input(
        "Idade (anos)", min_value=1, max_value=120, value=30, step=1
    )

    c1, c2 = st.columns(2)
    peso = c1.number_input(
        "Peso (kg)", min_value=1.0, max_value=300.0, value=70.0, step=0.1
    )
    altura = c2.number_input(
        "Altura (m)", min_value=0.5, max_value=2.5, value=1.72, step=0.01
    )

    restricoes = st.text_input(
        "Restrições Alimentares / Alergias / Intolerâncias",
        placeholder="Ex: Intolerância à Lactose, Alergia a Frutos do Mar, Não consome glúten...",
    )

imc = calcular_imc(peso, altura)
classificacao = classificar_imc(imc)
peso_ideal = calcular_peso_ideal(altura)

if classificacao == "Abaixo do Peso":
    badge_class = "badge-vermelho"
elif classificacao == "Sobrepeso":
    badge_class = "badge-laranja"
elif "Obesidade" in classificacao:
    badge_class = "badge-vermelho"
else:
    badge_class = "badge-verde"

with col_imc:
    st.markdown("### Avaliação Antropométrica")
    st.markdown(
        f"""
    <div class="imc-card">
        <div class="imc-label">IMC Atual</div>
        <div class="imc-value">{imc:.2f} kg/m²</div>
        <div class="imc-badge {badge_class}">{classificacao}</div>
        <div class="peso-ideal-box">
            <b>Peso Ideal Recomendado:</b> {peso_ideal:.1f} kg
        </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

st.markdown("---")

# Seção de Cadastro de Novo Alimento Personalizado
with st.expander("➕ Cadastrar Novo Alimento (Fora da Tabela TACO)", expanded=False):
    st.write("Insira os dados nutricionais referente a **100g** do alimento:")
    c_nome, c_kcal, c_prot, c_carb, c_gord = st.columns(5)
    
    novo_nome = c_nome.text_input("Nome do Alimento", placeholder="Ex: Whey Protein Pro")
    nova_kcal = c_kcal.number_input("Kcal (100g)", min_value=0.0, step=1.0, value=0.0)
    nova_prot = c_prot.number_input("Proteína g (100g)", min_value=0.0, step=0.1, value=0.0)
    novo_carb = c_carb.number_input("Carboidrato g (100g)", min_value=0.0, step=0.1, value=0.0)
    nova_gord = c_gord.number_input("Gordura g (100g)", min_value=0.0, step=0.1, value=0.0)

    if st.button("Salvar Alimento Personalizado"):
        if novo_nome.strip():
            novo_item = pd.DataFrame([{
                "nome": f"⭐ {novo_nome.strip()}",
                "energia_kcal": float(nova_kcal),
                "proteina_g": float(nova_prot),
                "carboidrato_g": float(novo_carb),
                "lipideos_g": float(nova_gord),
            }])
            st.session_state.alimentos_custom = pd.concat(
                [st.session_state.alimentos_custom, novo_item], ignore_index=True
            )
            st.success(f"Alimento '{novo_nome}' adicionado com sucesso!")
            st.rerun()
        else:
            st.warning("Informe o nome do alimento.")

st.markdown("---")

# Seção 2: Refeições
st.markdown("### Prescrição do Plano Alimentar")

refeicoes_nomes = ["Desjejum", "Almoço", "Lanche da Tarde", "Jantar", "Ceia"]
tabs = st.tabs(refeicoes_nomes)

if "dieta" not in st.session_state:
    st.session_state.dieta = {ref: [] for ref in refeicoes_nomes}

for i, ref in enumerate(refeicoes_nomes):
    with tabs[i]:
        st.write(f"#### {ref}")
        c_alimento, c_qtd, c_btn = st.columns([3, 1, 1], gap="medium")

        lista_alimentos = df_taco["nome"].tolist() if not df_taco.empty else []
        alimento_sel = c_alimento.selectbox(
            "Selecione o alimento (TACO / Personalizados)", lista_alimentos, key=f"sel_{ref}"
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
                item = {
                    "nome": alimento_sel,
                    "quantidade_g": qtd_gramas,
                    "energia_kcal": round(float(row.get("energia_kcal", 0.0)) * fator, 1),
                    "proteina_g": round(float(row.get("proteina_g", 0.0)) * fator, 1),
                    "carboidrato_g": round(float(row.get("carboidrato_g", 0.0)) * fator, 1),
                    "lipideos_g": round(float(row.get("lipideos_g", 0.0)) * fator, 1),
                }
                st.session_state.dieta[ref].append(item)
                st.toast(f"Alimento '{alimento_sel}' adicionado com sucesso.")

        if st.session_state.dieta[ref]:
            st.markdown("##### Alimentos Adicionados:")
            
            items_para_remover = []
            for idx, item in enumerate(st.session_state.dieta[ref]):
                col_item_nome, col_item_qtd, col_item_kcal, col_item_del = st.columns([3, 1, 1, 1])
                col_item_nome.write(f"• **{item['nome']}**")
                col_item_qtd.write(f"{item['quantidade_g']} g")
                col_item_kcal.write(f"{item['energia_kcal']} kcal")
                if col_item_del.button("🗑️ Remover", key=f"del_{ref}_{idx}"):
                    items_para_remover.append(idx)
            
            if items_para_remover:
                for idx in reversed(items_para_remover):
                    removido = st.session_state.dieta[ref].pop(idx)
                    st.toast(f"Alimento '{removido['nome']}' removido.")
                st.rerun()

st.markdown("---")

# Seção 3: Totais
st.markdown("### Balanço Nutricional Diário")

total_kcal, total_prot, total_carb, total_gord = somar_totais_diarios(
    st.session_state.dieta
)

m1, m2, m3, m4 = st.columns(4)
m1.metric("Valor Energético", f"{total_kcal:.1f} kcal")
m2.metric("Proteínas", f"{total_prot:.1f} g")
m3.metric("Carboidratos", f"{total_carb:.1f} g")
m4.metric("Lipídeos", f"{total_gord:.1f} g")

# Seção 4: Exportação PDF
st.markdown("---")
st.markdown("### Exportar Documento")

if st.button("Gerar Relatório em PDF"):
    try:
        pdf_data = criar_pdf_plano(
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

        st.download_button(
            label="Baixar Plano Alimentar (PDF)",
            data=pdf_data,
            file_name=f"NutriDAY_{str(nome_paciente).replace(' ', '_')}.pdf",
            mime="application/pdf",
        )
    except Exception as e:
        st.error(f"Erro ao gerar o relatório em PDF: {str(e)}")
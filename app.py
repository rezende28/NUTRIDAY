import base64
import pandas as pd
import streamlit as st

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

st.set_page_config(page_title="NutriDAY - Dra. Andressa Santos", layout="wide")

if HAS_DB:
    try:
        db.inicializar_banco()
    except Exception:
        pass

# Estilização CSS Clean (Verde-Água, Lilás, Branco - Sem emojis)
st.markdown(
    """
<style>
    .stApp { background-color: #FFFFFF; font-family: 'Inter', sans-serif; }
    .main-header {
        background: linear-gradient(135deg, #2EC4B6 0%, #25A195 100%);
        padding: 24px 32px; border-radius: 12px; color: white; margin-bottom: 25px;
    }
    .main-header h1 { margin: 0; font-size: 2.1rem; font-weight: 700; color: #FFFFFF !important; }
    .main-header p { margin-top: 4px; font-size: 0.95rem; color: #F0FDF4; }
    .stButton>button {
        border-radius: 8px; border: none; background-color: #2EC4B6; color: white !important; font-weight: 600; padding: 8px 20px;
    }
    .stButton>button:hover { background-color: #25A195; }
    .stTabs [aria-selected="true"] { background-color: #9B51E0 !important; color: white !important; border-color: #9B51E0 !important; }
    section[data-testid="stSidebar"] { background-color: #F8FAF9 !important; border-right: 1px solid #EFE6FA !important; }
    div[data-testid="stMetricValue"] { color: #9B51E0 !important; font-weight: 700 !important; }
    hr { border-color: #EFE6FA; margin: 24px 0; }
    
    /* Estilo do botão customizado para abrir PDF em nova aba */
    .btn-open-pdf {
        display: inline-block;
        background-color: #9B51E0;
        color: white !important;
        font-weight: 600;
        padding: 10px 24px;
        border-radius: 8px;
        text-decoration: none;
        transition: all 0.2s ease;
        text-align: center;
        margin-top: 10px;
    }
    .btn-open-pdf:hover {
        background-color: #8230D8;
        color: white !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

refeicoes_nomes = [
    "Café da Manhã",
    "Lanche da Manhã (Pré-Treino)",
    "Almoço",
    "Lanche da Tarde (Pós-Treino)",
    "Jantar",
    "Ceia",
]

if "dieta" not in st.session_state:
    st.session_state.dieta = {ref: [] for ref in refeicoes_nomes}
else:
    for ref in refeicoes_nomes:
        if ref not in st.session_state.dieta:
            st.session_state.dieta[ref] = []

if "alimentos_custom" not in st.session_state:
    st.session_state.alimentos_custom = pd.DataFrame(
        columns=["nome", "energia_kcal", "proteina_g", "carboidrato_g", "lipideos_g"]
    )

if "fichas_pacientes" not in st.session_state:
    st.session_state.fichas_pacientes = []

df_taco_base = carregar_tabela_taco()
if not st.session_state.alimentos_custom.empty:
    df_taco = pd.concat([df_taco_base, st.session_state.alimentos_custom], ignore_index=True)
else:
    df_taco = df_taco_base

st.sidebar.title("NutriDAY")
st.sidebar.caption("Painel Clínico - Dra. Andressa Santos")
menu_opcao = st.sidebar.radio("Menu de Acesso", ["Prescrição Nutricional", "Fichas dos Pacientes"])

if menu_opcao == "Prescrição Nutricional":
    st.markdown(
        """
    <div class="main-header">
        <h1>NutriDAY</h1>
        <p>Prescrição Nutricional e Esportiva | Dra. Andressa Santos</p>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown("### Identificação e Perfil do Paciente")
    col_dados, col_esporte = st.columns([1, 1], gap="large")

    with col_dados:
        nome_paciente = st.text_input("Nome Completo", "Lucas Mendes")
        c_sexo, c_idade = st.columns(2)
        sexo = c_sexo.selectbox("Sexo Biológico", ["Masculino", "Feminino"])
        idade = c_idade.number_input("Idade (anos)", min_value=1, max_value=120, value=28, step=1)

        c1, c2 = st.columns(2)
        peso = c1.number_input("Peso (kg)", min_value=1.0, max_value=300.0, value=75.0, step=0.1)
        altura = c2.number_input("Altura (m)", min_value=0.5, max_value=2.5, value=1.78, step=0.01)

    with col_esporte:
        modalidade = st.text_input("Modalidade Esportiva / Treino", "Musculação 5x/semana + Corrida")
        fator_ativ_map = {
            "Sedentário (Pouco ou nenhum exercício)": 1.2,
            "Leve (Treino 1 a 3 dias/semana)": 1.375,
            "Moderado (Treino 3 a 5 dias/semana)": 1.55,
            "Intenso (Treino pesado 6 a 7 dias/semana)": 1.725,
            "Muito Intenso / Atleta (2 treinos por dia)": 1.9,
        }
        fator_sel = st.selectbox("Nível de Atividade Física", list(fator_ativ_map.keys()), index=2)
        fator_atividade = fator_ativ_map[fator_sel]
        objetivo = st.selectbox(
            "Objetivo Nutricional",
            ["Hipertrofia (Ganho de Massa)", "Emagrecimento / Definição", "Manutenção e Performance"],
        )
        restricoes = st.text_input("Restrições Alimentares / Suplementação Atual", placeholder="Ex: Usa Creatina 5g e Whey...")

    imc = calcular_imc(peso, altura)
    classificacao = classificar_imc(imc)
    peso_ideal = calcular_peso_ideal(altura)

    if sexo == "Masculino":
        tmb = (10 * peso) + (6.25 * (altura * 100)) - (5 * idade) + 5
    else:
        tmb = (10 * peso) + (6.25 * (altura * 100)) - (5 * idade) - 161

    get = tmb * fator_atividade

    if objetivo == "Hipertrofia (Ganho de Massa)":
        meta_kcal = get + 400
    elif objetivo == "Emagrecimento / Definição":
        meta_kcal = get - 500
    else:
        meta_kcal = get

    st.markdown("---")
    st.markdown("### Avaliação Metabólica e Metas Calóricas")
    m_col1, m_col2, m_col3, m_col4 = st.columns(4)
    m_col1.metric("IMC", f"{imc:.1f} kg/m²", classificacao)
    m_col2.metric("Basal (TMB)", f"{int(tmb)} kcal")
    m_col3.metric("Gasto Total (GET)", f"{int(get)} kcal")
    m_col4.metric("Meta Calórica Diária", f"{int(meta_kcal)} kcal")

    st.markdown("---")
    with st.expander("Cadastrar Novo Alimento / Suplemento (Fora da TACO)", expanded=False):
        c_nome, c_kcal, c_prot, c_carb, c_gord = st.columns(5)
        novo_nome = c_nome.text_input("Nome do Alimento", placeholder="Ex: Whey Iso")
        nova_kcal = c_kcal.number_input("Kcal (100g)", min_value=0.0, step=1.0, value=0.0)
        nova_prot = c_prot.number_input("Proteína g (100g)", min_value=0.0, step=0.1, value=0.0)
        novo_carb = c_carb.number_input("Carboidrato g (100g)", min_value=0.0, step=0.1, value=0.0)
        nova_gord = c_gord.number_input("Gordura g (100g)", min_value=0.0, step=0.1, value=0.0)

        if st.button("Salvar Alimento"):
            if novo_nome.strip():
                if HAS_DB:
                    try:
                        db.salvar_alimento_custom(novo_nome.strip(), nova_kcal, nova_prot, novo_carb, nova_gord)
                    except Exception:
                        pass
                novo_item = pd.DataFrame([{
                    "nome": f"[Personalizado] {novo_nome.strip()}",
                    "energia_kcal": float(nova_kcal),
                    "proteina_g": float(nova_prot),
                    "carboidrato_g": float(novo_carb),
                    "lipideos_g": float(nova_gord),
                }])
                st.session_state.alimentos_custom = pd.concat([st.session_state.alimentos_custom, novo_item], ignore_index=True)
                st.success(f"Alimento '{novo_nome}' cadastrado com sucesso!")
                st.rerun()

    st.markdown("---")
    st.markdown("### Plano Alimentar")
    tabs = st.tabs(refeicoes_nomes)

    for i, ref in enumerate(refeicoes_nomes):
        with tabs[i]:
            st.write(f"#### {ref}")
            c_alimento, c_qtd, c_btn = st.columns([3, 1, 1], gap="medium")
            lista_alimentos = df_taco["nome"].tolist() if not df_taco.empty else []
            alimento_sel = c_alimento.selectbox("Selecione o alimento", lista_alimentos, key=f"sel_{ref}")
            qtd_gramas = c_qtd.number_input("Quantidade (g)", min_value=5, max_value=1000, value=100, step=5, key=f"qtd_{ref}")

            c_btn.markdown("<div style='padding-top: 28px;'></div>", unsafe_allow_html=True)
            if c_btn.button("Adicionar Alimento", key=f"btn_{ref}"):
                if not df_taco.empty and alimento_sel:
                    row = df_taco[df_taco["nome"] == alimento_sel].iloc[0]
                    fator = qtd_gramas / 100.0

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
                    st.toast(f"Alimento '{alimento_sel}' adicionado com sucesso.")

            if st.session_state.dieta.get(ref):
                st.markdown("##### Alimentos Adicionados:")
                items_para_remover = []
                for idx, item in enumerate(st.session_state.dieta[ref]):
                    col_item_nome, col_item_qtd, col_item_kcal, col_item_del = st.columns([3, 1, 1, 1])
                    col_item_nome.write(f"• **{item['nome']}**")
                    col_item_qtd.write(f"{item['quantidade_g']} g")
                    col_item_kcal.write(f"{item['energia_kcal']} kcal")
                    if col_item_del.button("Remover", key=f"del_{ref}_{idx}"):
                        items_para_remover.append(idx)

                if items_para_remover:
                    for idx in reversed(items_para_remover):
                        st.session_state.dieta[ref].pop(idx)
                    st.rerun()

    st.markdown("---")
    st.markdown("### Balanço Nutricional e Relatório Esportivo (g/kg)")
    total_kcal, total_prot, total_carb, total_gord = somar_totais_diarios(st.session_state.dieta)

    prot_gkg = total_prot / peso if peso > 0 else 0
    carb_gkg = total_carb / peso if peso > 0 else 0
    gord_gkg = total_gord / peso if peso > 0 else 0

    b1, b2, b3, b4 = st.columns(4)
    b1.metric("Energia Prescrita", f"{total_kcal:.1f} kcal", f"Meta: {int(meta_kcal)} kcal")
    b2.metric("Proteína Total", f"{total_prot:.1f} g", f"{prot_gkg:.2f} g/kg")
    b3.metric("Carboidrato Total", f"{total_carb:.1f} g", f"{carb_gkg:.2f} g/kg")
    b4.metric("Gordura Total", f"{total_gord:.1f} g", f"{gord_gkg:.2f} g/kg")

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
            "modalidade": modalidade,
            "objetivo": objetivo,
            "total_kcal": total_kcal,
            "meta_kcal": meta_kcal,
        }
        st.session_state.fichas_pacientes.append(ficha_nova)
        st.success(f"Ficha de {nome_paciente} salva com sucesso!")

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
                modalidade=str(modalidade or ""),
                fator_sel=str(fator_sel or ""),
                objetivo=str(objetivo or ""),
            )
            st.session_state["pdf_pronto"] = pdf_bytes
            st.success("PDF gerado com sucesso!")
        except Exception as e:
            st.error(f"Erro ao gerar o relatório em PDF: {str(e)}")

    if "pdf_pronto" in st.session_state and st.session_state["pdf_pronto"] is not None:
        b64_pdf = base64.b64encode(st.session_state["pdf_pronto"]).decode("utf-8")
        
        # Gera o botão HTML/JS para abrir em nova aba
        pdf_display = f"""
            <a href="data:application/pdf;base64,{b64_pdf}" target="_blank" class="btn-open-pdf">
                Visualizar e Imprimir PDF (Nova Aba)
            </a>
        """
        st.markdown(pdf_display, unsafe_allow_html=True)

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
        for idx, ficha in enumerate(st.session_state.fichas_pacientes):
            with st.expander(f"Paciente: {ficha['nome']} — {ficha['objetivo']}"):
                col_e1, col_e2, col_e3 = st.columns(3)
                ficha["nome"] = col_e1.text_input("Nome Completo", value=ficha["nome"], key=f"f_nome_{idx}")
                ficha["idade"] = col_e2.number_input("Idade", value=int(ficha["idade"]), key=f"f_idade_{idx}")
                ficha["sexo"] = col_e3.selectbox("Sexo", ["Masculino", "Feminino"], index=0 if ficha["sexo"] == "Masculino" else 1, key=f"f_sexo_{idx}")

                col_e4, col_e5, col_e6 = st.columns(3)
                ficha["peso"] = col_e4.number_input("Peso (kg)", value=float(ficha["peso"]), key=f"f_peso_{idx}")
                ficha["altura"] = col_e5.number_input("Altura (m)", value=float(ficha["altura"]), key=f"f_altura_{idx}")
                ficha["modalidade"] = col_e6.text_input("Treino / Modalidade", value=ficha.get("modalidade", ""), key=f"f_mod_{idx}")

                col_b1, col_b2 = st.columns(2)
                if col_b1.button("Salvar Alterações", key=f"save_f_{idx}"):
                    st.success("Ficha atualizada com sucesso!")
                    st.rerun()

                if col_b2.button("Excluir Ficha", key=f"del_f_{idx}"):
                    st.session_state.fichas_pacientes.pop(idx)
                    st.success("Ficha excluída com sucesso!")
                    st.rerun()
    else:
        st.info("Nenhum paciente salvo até o momento. Preencha os dados na Prescrição Nutricional e clique em 'Guardar Ficha do Paciente'.")
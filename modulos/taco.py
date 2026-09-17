import os
import pandas as pd
import streamlit as st

def carregar_tabela_taco():
    """Carrega a Tabela TACO lendo exatamente a estrutura informada."""
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_csv = os.path.join(BASE_DIR, "dados", "tabela_taco.csv")
    caminho_excel = os.path.join(BASE_DIR, "dados", "tabela_taco.xlsx")

    df_raw = None

    # Tenta carregar o CSV com o separador ';' e encoding latin1
    if os.path.exists(caminho_csv):
        try:
            df_raw = pd.read_csv(caminho_csv, sep=';', encoding='latin1', header=None, on_bad_lines='skip')
        except Exception:
            try:
                df_raw = pd.read_csv(caminho_csv, sep=';', encoding='utf-8', header=None, on_bad_lines='skip')
            except Exception:
                pass

    # Se não leu CSV, tenta ler o Excel diretamente
    if df_raw is None and os.path.exists(caminho_excel):
        try:
            df_raw = pd.read_excel(caminho_excel, header=None)
        except Exception as e:
            st.error(f"Erro ao ler arquivo Excel: {e}")

    if df_raw is None:
        st.error("Arquivo 'tabela_taco.csv' ou 'tabela_taco.xlsx' não encontrado na pasta 'dados/'.")
        return pd.DataFrame()

    try:
        dados_alimentos = []

        for idx, row in df_raw.iterrows():
            col0 = str(row[0]).strip() if pd.notnull(row[0]) else ""
            col1 = str(row[1]).strip() if pd.notnull(row[1]) else ""

            # Garante que seja uma linha de alimento válida:
            # - Deve ter o número do alimento na 1ª coluna (ex: 1, 2, 3...)
            # - Deve ter o nome na 2ª coluna
            if col0.isdigit() and len(col1) > 2 and not col1.lower().startswith("descri"):
                
                # Trata conversão numérica com vírgula decimal
                def para_float(val):
                    try:
                        val_str = str(val).replace(',', '.').strip()
                        return float(val_str)
                    except ValueError:
                        return 0.0

                # Posições exatas da tabela oficial TACO:
                # col 1: Descrição
                # col 3: Energia (kcal)
                # col 5: Proteína (g)
                # col 6: Lipídeos (g)
                # col 8: Carboidrato (g)
                energia = para_float(row[3]) if len(row) > 3 else 0.0
                proteina = para_float(row[5]) if len(row) > 5 else 0.0
                lipideos = para_float(row[6]) if len(row) > 6 else 0.0
                carboidrato = para_float(row[8]) if len(row) > 8 else 0.0

                dados_alimentos.append({
                    "id": int(col0),
                    "nome": col1,
                    "energia_kcal": energia,
                    "proteina_g": proteina,
                    "carboidrato_g": carboidrato,
                    "lipideos_g": lipideos
                })

        df = pd.DataFrame(dados_alimentos)

        if df.empty:
            st.error("Nenhum alimento foi carregado. Verifique o formato do arquivo.")
            return pd.DataFrame()

        # Remove duplicados e ordena em ORDEM ALFABÉTICA (A a Z)
        df = df.drop_duplicates(subset=["nome"])
        df = df.sort_values(by="nome").reset_index(drop=True)

        return df

    except Exception as e:
        st.error(f"Erro ao processar dados da Tabela TACO: {e}")
        return pd.DataFrame()
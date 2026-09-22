import pandas as pd
import sqlalchemy
import streamlit as st


# Conecta ao banco usando os dados do Secrets
def get_db_connection():
    db_url = st.secrets["postgres"]["url"]
    engine = sqlalchemy.create_engine(db_url)
    return engine


# Cria as tabelas iniciais caso não existam
def inicializar_banco():
    engine = get_db_connection()
    with engine.connect() as conn:
        conn.execute(
            sqlalchemy.text(
                """
            CREATE TABLE IF NOT EXISTS alimentos_custom (
                id SERIAL PRIMARY KEY,
                nome VARCHAR(255) NOT NULL,
                energia_kcal FLOAT,
                proteina_g FLOAT,
                carboidrato_g FLOAT,
                lipideos_g FLOAT
            );
        """
            )
        )
        conn.commit()


# Carrega os alimentos do banco
def carregar_alimentos_custom():
    engine = get_db_connection()
    query = "SELECT nome, energia_kcal, proteina_g, carboidrato_g, lipideos_g FROM alimentos_custom"
    return pd.read_sql(query, engine)


# Salva um novo alimento personalizado
def salvar_alimento_custom(nome, kcal, prot, carb, gord):
    engine = get_db_connection()
    with engine.connect() as conn:
        stmt = sqlalchemy.text(
            """
            INSERT INTO alimentos_custom (nome, energia_kcal, proteina_g, carboidrato_g, lipideos_g)
            VALUES (:nome, :kcal, :prot, :carb, :gord)
        """
        )
        conn.execute(
            stmt,
            {
                "nome": f"[Personalizado] {nome}",
                "kcal": kcal,
                "prot": prot,
                "carb": carb,
                "gord": gord,
            },
        )
        conn.commit()
import os
import psycopg2
from psycopg2.extras import RealDictCursor

def get_db_connection():
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        return None
    return psycopg2.connect(db_url)

def inicializar_banco():
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            # Tabela de alimentos personalizados
            cur.execute("""
                CREATE TABLE IF NOT EXISTS alimentos_customizados (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    energia_kcal FLOAT NOT NULL,
                    proteina_g FLOAT NOT NULL,
                    carboidrato_g FLOAT NOT NULL,
                    lipideos_g FLOAT NOT NULL
                );
            """)
            # Tabela de pacientes
            cur.execute("""
                CREATE TABLE IF NOT EXISTS pacientes (
                    id SERIAL PRIMARY KEY,
                    nome VARCHAR(255) NOT NULL,
                    sexo VARCHAR(50),
                    idade INT,
                    peso FLOAT,
                    altura FLOAT,
                    imc FLOAT,
                    modalidade VARCHAR(255),
                    objetivo VARCHAR(255),
                    total_kcal FLOAT,
                    meta_kcal FLOAT
                );
            """)
            conn.commit()
    finally:
        conn.close()

def salvar_paciente_db(nome, sexo, idade, peso, altura, imc, modalidade, objetivo, total_kcal, meta_kcal):
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO pacientes (nome, sexo, idade, peso, altura, imc, modalidade, objetivo, total_kcal, meta_kcal)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id;
            """, (nome, sexo, idade, peso, altura, imc, modalidade, objetivo, total_kcal, meta_kcal))
            paciente_id = cur.fetchone()[0]
            conn.commit()
            return paciente_id
    finally:
        conn.close()

def listar_pacientes_db():
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT * FROM pacientes ORDER BY id DESC;")
            return cur.fetchall()
    finally:
        conn.close()

def atualizar_paciente_db(p_id, nome, sexo, idade, peso, altura, modalidade):
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                UPDATE pacientes
                SET nome = %s, sexo = %s, idade = %s, peso = %s, altura = %s, modalidade = %s
                WHERE id = %s;
            """, (nome, sexo, idade, peso, altura, modalidade, p_id))
            conn.commit()
    finally:
        conn.close()

def deletar_paciente_db(p_id):
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM pacientes WHERE id = %s;", (p_id,))
            conn.commit()
    finally:
        conn.close()

def salvar_alimento_custom(nome, kcal, prot, carb, gord):
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cur:
            cur.execute("""
                INSERT INTO alimentos_customizados (nome, energia_kcal, proteina_g, carboidrato_g, lipideos_g)
                VALUES (%s, %s, %s, %s, %s);
            """, (nome, kcal, prot, carb, gord))
            conn.commit()
    finally:
        conn.close()
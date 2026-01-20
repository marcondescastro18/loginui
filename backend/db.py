import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_connection():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return None

def get_user_by_email(email):
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # Tenta selecionar com nome, se falhar, sem nome
        try:
            cur.execute("SELECT id, email, senha, nome FROM usuarios WHERE email = %s AND ativo = TRUE", (email,))
        except psycopg2.ProgrammingError:
            # Coluna nome não existe, tenta sem ela
            cur.execute("SELECT id, email, senha FROM usuarios WHERE email = %s AND ativo = TRUE", (email,))
        user = cur.fetchone()
        cur.close()
        return user
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return None
    finally:
        conn.close()

def create_session(usuario_id, token, ip_address):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO sessoes (usuario_id, token, endereco_ip, expirado_em) VALUES (%s, %s, %s, NOW() + INTERVAL '24 hours')", (usuario_id, token, ip_address))
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return False
    finally:
        conn.close()

def log_access(usuario_id, email, tipo_evento, ip_address, sucesso, mensagem):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("INSERT INTO registros_acesso (usuario_id, email, tipo_evento, endereco_ip, sucesso, mensagem) VALUES (%s, %s, %s, %s, %s, %s)", (usuario_id, email, tipo_evento, ip_address, sucesso, mensagem))
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return False
    finally:
        conn.close()

def update_last_access(usuario_id):
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute("UPDATE usuarios SET ultimo_acesso = NOW() WHERE id = %s", (usuario_id,))
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro: {e}")
        return False
    finally:
        conn.close()

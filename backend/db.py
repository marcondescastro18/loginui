#!/usr/bin/env python3
"""
db.py - Funções de Acesso ao Banco de Dados

Módulo responsável por todas as operações de banco de dados:
- Conexão com PostgreSQL
- Autenticação de usuários
- Gerenciamento de sessões
- Logs de acesso

Schema do Banco (Simplificado):
- usuarios: id, email, senha, criado_em
- sessoes: id, usuario_id, token, endereco_ip, expirado_em, criado_em
- registros_acesso: id, usuario_id, tipo_evento, endereco_ip, sucesso, mensagem, criado_em

Todas as funções incluem tratamento de exceções e rollback automático.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from config import Config

def get_connection():
    """
    Estabelece conexão com o banco de dados PostgreSQL.
    
    Utiliza as configurações definidas em Config para conectar ao banco.
    Em caso de erro, imprime a mensagem e retorna None.
    
    Returns:
        psycopg2.connection: Objeto de conexão ativa ou None em caso de erro
        
    Exemplo:
        conn = get_connection()
        if conn:
            cur = conn.cursor()
            # executar queries
            conn.close()
    """
    try:
        # Estabelece conexão usando credenciais do Config
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        return conn
    except psycopg2.Error as e:
        # Log do erro (em produção, use logging adequado)
        print(f"Erro ao conectar ao banco de dados: {e}")
        return None

def get_user_by_email(email):
    """
    Busca usuário por email.
    Schema real: id, email, senha, criado_em
    NÃO existem colunas: nome, ativo, atualizado_em, ultimo_acesso
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # SELECT apenas colunas que EXISTEM no banco: id, email, senha, criado_em
        # Removido: AND ativo = TRUE (coluna não existe)
        cur.execute("SELECT id, email, senha, criado_em FROM usuarios WHERE email = %s", (email,))
        user = cur.fetchone()
        cur.close()
        return user
    except psycopg2.Error as e:
        print(f"Erro ao buscar usuário: {e}")
        return None
    finally:
        conn.close()

def create_session(usuario_id, token, ip_address):
    """
    Cria sessão após login bem-sucedido.
    Inclui tratamento de exceção com rollback.
    """
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO sessoes (usuario_id, token, endereco_ip, expirado_em) "
            "VALUES (%s, %s, %s, NOW() + INTERVAL '24 hours')", 
            (usuario_id, token, ip_address)
        )
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro ao criar sessão: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def log_access(usuario_id, tipo_evento, ip_address, sucesso, mensagem):
    """
    Registra tentativa de acesso.
    Compatível com schema sem coluna 'email' em registros_acesso.
    Usa apenas usuario_id (pode ser NULL para tentativas falhadas sem usuário encontrado).
    """
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        # INSERT apenas colunas garantidas: usuario_id, tipo_evento, endereco_ip, sucesso, mensagem
        # Remove coluna 'email' que não existe em registros_acesso
        cur.execute(
            "INSERT INTO registros_acesso (usuario_id, tipo_evento, endereco_ip, sucesso, mensagem) "
            "VALUES (%s, %s, %s, %s, %s)", 
            (usuario_id, tipo_evento, ip_address, sucesso, mensagem)
        )
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        print(f"Erro ao registrar acesso: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def update_last_access(usuario_id):
    """
    FUNÇÃO DESABILITADA: coluna ultimo_acesso NÃO existe no schema real.
    Schema real da tabela usuarios: id, email, senha, criado_em
    Retorna True sem executar UPDATE para evitar erro SQL.
    """
    # NÃO executa UPDATE pois coluna ultimo_acesso não existe
    # Mantém função para compatibilidade com código existente
    return True

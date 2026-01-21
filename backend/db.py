#!/usr/bin/env python3
"""
db.py - Funções de Acesso ao Banco de Dados

Módulo responsável por todas as operações de banco de dados:
- Conexão com PostgreSQL
- Autenticação de usuários
- Gerenciamento de sessões
- Logs de acesso

Schema do Banco (REAL - Confirmado no banco de produção):
- usuarios: id, email, senha, criado_em
  (NÃO possui: nome, ativo, atualizado_em, ultimo_acesso)
  
- sessoes: id, usuario_id, token, endereco_ip, agente_usuario, expirado_em, criado_em
  
- registros_acesso: id, usuario_id, tipo_evento, endereco_ip, sucesso, mensagem, criado_em
  (NÃO possui: email)

CORREÇÕES APLICADAS:
- Removido uso de coluna 'nome' em usuarios
- Removido uso de coluna 'email' em registros_acesso
- Removido uso de coluna 'ultimo_acesso' em usuarios
- Tratamento robusto de exceções SQL com rollback
- Apenas colunas existentes são utilizadas

Todas as funções incluem tratamento de exceções e rollback automático
para prevenir crash do Gunicorn.
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
        # Log do erro (em produção, usar logging adequado)
        print(f"[ERRO SQL] Erro ao conectar ao banco de dados: {e}")
        return None

def get_user_by_email(email):
    """
    Busca usuário por email.
    
    CORREÇÃO APLICADA:
    - SELECT apenas colunas EXISTENTES: id, email, senha, criado_em
    - NÃO usa: nome, ativo, atualizado_em, ultimo_acesso (não existem)
    
    Args:
        email (str): Email do usuário a ser buscado
        
    Returns:
        dict: Dicionário com dados do usuário ou None se não encontrado
              Campos retornados: id, email, senha, criado_em
              
    Exemplo:
        usuario = get_user_by_email('teste@email.com')
        if usuario:
            print(f"ID: {usuario['id']}, Email: {usuario['email']}")
    """
    conn = get_connection()
    if not conn:
        return None
    try:
        cur = conn.cursor(cursor_factory=RealDictCursor)
        # SELECT apenas colunas que EXISTEM no banco: id, email, senha, criado_em
        # NÃO inclui: nome, ativo, atualizado_em, ultimo_acesso
        cur.execute(
            "SELECT id, email, senha, criado_em FROM usuarios WHERE email = %s", 
            (email,)
        )
        user = cur.fetchone()
        cur.close()
        return user
    except psycopg2.Error as e:
        print(f"[ERRO SQL] Erro ao buscar usuário: {e}")
        return None
    finally:
        conn.close()

def create_session(usuario_id, token, ip_address):
    """
    Cria sessão após login bem-sucedido.
    
    Inclui tratamento de exceção com rollback automático para prevenir
    crash do Gunicorn em caso de erro SQL.
    
    Args:
        usuario_id (int): ID do usuário
        token (str): Token JWT gerado
        ip_address (str): Endereço IP do cliente
        
    Returns:
        bool: True se criado com sucesso, False caso contrário
        
    Exemplo:
        if create_session(1, 'jwt_token_aqui', '192.168.1.1'):
            print('Sessão criada!')
    """
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        # INSERT na tabela sessoes com expiração de 24 horas
        cur.execute(
            "INSERT INTO sessoes (usuario_id, token, endereco_ip, expirado_em) "
            "VALUES (%s, %s, %s, NOW() + INTERVAL '24 hours')", 
            (usuario_id, token, ip_address)
        )
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        # Em caso de erro SQL, faz rollback e retorna False
        print(f"[ERRO SQL] Erro ao criar sessão: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

def log_access(usuario_id, tipo_evento, ip_address, sucesso, mensagem):
    """
    Registra tentativa de acesso no log.
    
    CORREÇÃO APLICADA:
    - INSERT apenas colunas EXISTENTES em registros_acesso
    - NÃO usa coluna 'email' (não existe nesta tabela)
    - Usa apenas: usuario_id, tipo_evento, endereco_ip, sucesso, mensagem, criado_em
    
    Args:
        usuario_id (int): ID do usuário (pode ser None para tentativas sem usuário encontrado)
        tipo_evento (str): Tipo do evento ('login', 'logout', etc)
        ip_address (str): Endereço IP do cliente
        sucesso (bool): Se a operação foi bem-sucedida
        mensagem (str): Mensagem descritiva do evento
        
    Returns:
        bool: True se registrado com sucesso, False caso contrário
        
    Exemplo:
        log_access(1, 'login', '192.168.1.1', True, 'Login bem-sucedido')
        log_access(None, 'login', '192.168.1.1', False, 'Usuário não encontrado')
    """
    conn = get_connection()
    if not conn:
        return False
    try:
        cur = conn.cursor()
        # INSERT apenas colunas garantidas: usuario_id, tipo_evento, endereco_ip, sucesso, mensagem
        # REMOVE coluna 'email' que NÃO existe em registros_acesso
        cur.execute(
            "INSERT INTO registros_acesso (usuario_id, tipo_evento, endereco_ip, sucesso, mensagem) "
            "VALUES (%s, %s, %s, %s, %s)", 
            (usuario_id, tipo_evento, ip_address, sucesso, mensagem)
        )
        conn.commit()
        cur.close()
        return True
    except psycopg2.Error as e:
        # Em caso de erro SQL, faz rollback e retorna False
        print(f"[ERRO SQL] Erro ao registrar acesso: {e}")
        conn.rollback()
        return False
    finally:
        conn.close()

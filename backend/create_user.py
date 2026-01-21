#!/usr/bin/env python3
"""
create_user.py - Script de Criação de Usuários

Script interativo para criar novos usuários no sistema com senha segura.
Utiliza bcrypt para hash das senhas com 10 rounds (padrão).

CORREÇÃO APLICADA:
- Remove uso de coluna 'nome' (NÃO existe no banco)
- Remove uso de coluna 'ativo' (NÃO existe no banco)
- INSERT apenas colunas existentes: email, senha

Schema Real da Tabela usuarios:
- id (SERIAL PRIMARY KEY)
- email (VARCHAR UNIQUE NOT NULL)
- senha (VARCHAR NOT NULL)
- criado_em (TIMESTAMP DEFAULT CURRENT_TIMESTAMP)

Funcionalidades:
- Solicita email e senha
- Gera hash bcrypt da senha
- Verifica se usuário já existe
- Insere usuário no banco de dados
- Confirma criação com ID gerado

Uso:
    python create_user.py
    
    # Ou importar como módulo
    from create_user import create_user
    create_user('novo@email.com', 'senha123')

Segurança:
- NUNCA armazena senhas em texto puro
- Usa bcrypt com salt automático
- Valida duplicação de email
- Prepared statements (proteção SQL injection)

Requisitos:
- bcrypt instalado: pip install bcrypt
- Banco de dados configurado
- Variáveis de ambiente (.env)
"""

import bcrypt
import psycopg2
from config import Config

def hash_password(password):
    """
    Gera hash bcrypt seguro da senha.
    
    Utiliza bcrypt.gensalt() que gera um salt aleatório automaticamente.
    O hash resultante inclui o salt e pode ser verificado com bcrypt.checkpw().
    
    Args:
        password (str): Senha em texto puro
        
    Returns:
        str: Hash bcrypt da senha (formato: $2b$10$...)
        
    Exemplo:
        hash_senha = hash_password('123456')
        # Retorna: '$2b$10$N9qo8uLOickgx2ZMRZoMye...'
    """
    # Gera salt com complexidade padrão (10 rounds)
    salt = bcrypt.gensalt()
    # Gera hash combinando senha + salt
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    # Retorna como string (não bytes)
    return hashed.decode('utf-8')

def create_user(email, password):
    """
    Cria novo usuário no banco com senha hasheada.
    
    CORREÇÃO APLICADA:
    - INSERT apenas colunas EXISTENTES: email, senha
    - NÃO usa: nome, ativo (não existem no schema real)
    
    Valida se o email já existe antes de inserir.
    Usa prepared statements para prevenir SQL injection.
    Inclui tratamento robusto de exceções com rollback.
    
    Args:
        email (str): Email do usuário (único)
        password (str): Senha em texto puro (será hasheada)
        
    Returns:
        bool: True se criado com sucesso, False caso contrário
        
    Exemplo:
        if create_user('teste@email.com', '123456'):
            print('Usuário criado!')
    """
    try:
        # Gerar hash da senha
        password_hash = hash_password(password)
        print(f"✓ Hash gerado: {password_hash[:30]}...")
        
        # Conectar ao banco
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        cur = conn.cursor()
        
        # Verificar se usuário já existe
        cur.execute("SELECT id FROM usuarios WHERE email = %s", (email,))
        if cur.fetchone():
            print(f"❌ Erro: Usuário com email '{email}' já existe!")
            cur.close()
            conn.close()
            return False
        
        # Inserir usuário - APENAS colunas existentes: email, senha
        # NÃO usa: nome, ativo (não existem no banco)
        cur.execute(
            "INSERT INTO usuarios (email, senha) VALUES (%s, %s) RETURNING id",
            (email, password_hash)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        return True
        
    except psycopg2.Error as db_error:
        # Tratamento específico para erros de banco
        print(f"❌ Erro de banco de dados ao criar usuário: {db_error}")
        try:
            if conn:
                conn.rollback()
        except:
            pass
        return False
        
    except Exception as e:
        # Tratamento genérico
        print(f"❌ Erro ao criar usuário: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 CRIAR NOVO USUÁRIO COM SENHA SEGURA")
    print("=" * 60)
    print("\nSchema real: usuarios (id, email, senha, criado_em)")
    print("NÃO existe coluna 'nome' ou 'ativo'\n")
    
    email = input("📧 Email: ").strip()
    password = input("🔑 Senha: ").strip()
    
    print("\n⏳ Criando usuário...")
    create_user(email, password)
    print()

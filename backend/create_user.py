#!/usr/bin/env python3
"""
create_user.py - Script de Criação de Usuários

Script interativo para criar novos usuários no sistema com senha segura.
Utiliza bcrypt para hash das senhas com 10 rounds (padrão).

Funcionalidades:
- Solicita email, senha e nome (opcional)
- Gera hash bcrypt da senha
- Verifica se usuário já existe
- Insere usuário no banco de dados
- Confirma criação com ID gerado

Uso:
    python create_user.py
    
    # Ou importar como módulo
    from create_user import create_user
    create_user('novo@email.com', 'senha123', 'Nome Usuário')

Segurança:
- NUNCA armazena senhas em texto puro
- Usa bcrypt com salt automático
- Valida duplicação de email

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

def create_user(email, password, nome=None):
    """
    Cria novo usuário no banco com senha hasheada.
    
    Valida se o email já existe antes de inserir.
    Usa prepared statements para prevenir SQL injection.
    
    Args:
        email (str): Email do usuário (único)
        password (str): Senha em texto puro (será hasheada)
        nome (str, optional): Nome do usuário. Defaults to None.
        
    Returns:
        bool: True se criado com sucesso, False caso contrário
        
    Exemplo:
        if create_user('teste@email.com', '123456', 'Usuário Teste'):
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
        
        # Inserir usuário
        cur.execute(
            "INSERT INTO usuarios (email, senha, nome, ativo) VALUES (%s, %s, %s, TRUE) RETURNING id",
            (email, password_hash, nome)
        )
        user_id = cur.fetchone()[0]
        conn.commit()
        
        cur.close()
        conn.close()
        
        print(f"✅ Usuário criado com sucesso!")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        print(f"   Nome: {nome or 'Não informado'}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar usuário: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 CRIAR NOVO USUÁRIO COM SENHA SEGURA")
    print("=" * 60)
    
    email = input("\n📧 Email: ").strip()
    password = input("🔑 Senha: ").strip()
    nome = input("👤 Nome (opcional): ").strip() or None
    
    print("\n⏳ Criando usuário...")
    create_user(email, password, nome)
    print()

#!/usr/bin/env python3
"""
Script para criar usuário com senha hasheada usando bcrypt
Uso: python create_user.py
"""

import bcrypt
import psycopg2
from config import Config

def hash_password(password):
    """Gera hash bcrypt da senha"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def create_user(email, password, nome=None):
    """Cria novo usuário no banco com senha hasheada"""
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

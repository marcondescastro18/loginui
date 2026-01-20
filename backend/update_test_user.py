#!/usr/bin/env python3
"""
Script para atualizar usuário existente com senha hasheada
"""

import bcrypt
import psycopg2
from config import Config

def hash_password(password):
    """Gera hash bcrypt da senha"""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def update_user_password(email, new_password):
    """Atualiza senha do usuário existente"""
    try:
        # Gerar hash da senha
        password_hash = hash_password(new_password)
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
        
        # Atualizar senha
        cur.execute(
            "UPDATE usuarios SET senha = %s, atualizado_em = NOW() WHERE email = %s RETURNING id",
            (password_hash, email)
        )
        result = cur.fetchone()
        
        if not result:
            print(f"❌ Erro: Usuário com email '{email}' não encontrado!")
            cur.close()
            conn.close()
            return False
        
        conn.commit()
        user_id = result[0]
        
        cur.close()
        conn.close()
        
        print(f"✅ Senha atualizada com sucesso!")
        print(f"   ID: {user_id}")
        print(f"   Email: {email}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao atualizar senha: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("🔐 ATUALIZAR SENHA DO USUÁRIO teste@email.com")
    print("=" * 60)
    
    email = "teste@email.com"
    password = "123456"
    
    print(f"\n📧 Email: {email}")
    print(f"🔑 Nova senha: {password}")
    print("\n⏳ Atualizando senha...")
    
    update_user_password(email, password)
    print()

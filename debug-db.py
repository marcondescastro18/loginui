#!/usr/bin/env python3
"""
Script para verificar usuários no banco de dados
Cole este conteúdo no terminal do EasyPanel backend
"""

import psycopg2
import os

# Configuração
DB_HOST = os.getenv('DB_HOST', 'login_login-aut-db')
DB_PORT = int(os.getenv('DB_PORT', 5432))
DB_USER = os.getenv('DB_USER', 'postgres')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'fa0e7201e1773b163eb3')
DB_NAME = os.getenv('DB_NAME', 'auth_db')

try:
    print('🔍 Conectando ao banco de dados...')
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME
    )
    
    cur = conn.cursor()
    
    print('\n' + '='*80)
    print('📊 TABELA: usuarios')
    print('='*80)
    
    # Contar registros
    cur.execute("SELECT COUNT(*) FROM usuarios")
    count = cur.fetchone()[0]
    print(f'\n👥 Total de usuários: {count}\n')
    
    # Listar usuários
    cur.execute("SELECT id, email, LEFT(senha, 20) as senha_inicio, nome, ativo FROM usuarios")
    rows = cur.fetchall()
    
    for row in rows:
        print(f"ID: {row[0]}")
        print(f"Email: {row[1]}")
        print(f"Senha (início): {row[2]}")
        print(f"Tipo: {'bcrypt' if row[2].startswith('$2') else 'plaintext'}")
        print(f"Nome: {row[3]}")
        print(f"Ativo: {row[4]}")
        print()
    
    # Testar login
    print('='*80)
    print('🔐 TESTANDO LOGIN: teste@email.com / 123456')
    print('='*80)
    
    cur.execute("SELECT id, email, senha FROM usuarios WHERE email = %s", ('teste@email.com',))
    user = cur.fetchone()
    
    if user:
        print(f'\n✅ Usuário encontrado!')
        print(f'ID: {user[0]}')
        print(f'Email: {user[1]}')
        print(f'Senha completa: {user[2]}')
        print(f'Tipo: {"bcrypt" if user[2].startswith("$2") else "plaintext"}')
        print(f'Comprimento: {len(user[2])} caracteres')
    else:
        print('\n❌ Usuário NÃO encontrado!')
    
    cur.close()
    conn.close()
    
    print('\n✅ Conexão fechada\n')
    
except Exception as e:
    print(f'\n❌ Erro: {e}\n')
    import traceback
    traceback.print_exc()

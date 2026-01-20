#!/usr/bin/env python3
"""
Script para verificar usuário teste@email.com
Execute no terminal do backend EasyPanel com: python check_teste_user.py
"""

import sys
import os

# Adicionar o diretório do backend ao path
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

try:
    from config import Config
    from db import get_user_by_email
    
    print('\n' + '='*80)
    print('🔍 VERIFICANDO USUÁRIO: teste@email.com')
    print('='*80 + '\n')
    
    # Tentar buscar o usuário
    usuario = get_user_by_email('teste@email.com')
    
    if usuario:
        print('✅ USUÁRIO ENCONTRADO!\n')
        print(f'ID: {usuario["id"]}')
        print(f'Email: {usuario["email"]}')
        print(f'Nome: {usuario["nome"]}')
        print(f'Senha (primeiros 20 chars): {usuario["senha"][:20]}')
        print(f'Comprimento da senha: {len(usuario["senha"])} caracteres')
        
        if usuario["senha"].startswith('$2b$') or usuario["senha"].startswith('$2a$'):
            print('Tipo: ✅ BCRYPT (hash seguro)')
        else:
            print('Tipo: ⚠️  PLAINTEXT (senha em texto puro)')
        
        print('\n🔐 PRÓXIMOS PASSOS:')
        if usuario["senha"].startswith('$2b$') or usuario["senha"].startswith('$2a$'):
            print('✅ Senha já está em bcrypt. Teste o login agora!')
        else:
            print('⚠️  Senha está em plaintext. Execute: python backend/update_test_user.py')
    else:
        print('❌ USUÁRIO NÃO ENCONTRADO!\n')
        print('Verifique se a tabela "usuarios" existe e tem registros.')
        print('\nListe todos os usuários:')
        
        import psycopg2
        from psycopg2.extras import RealDictCursor
        
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        cur.execute("SELECT COUNT(*) as count FROM usuarios")
        count = cur.fetchone()['count']
        
        print(f'\nTotal de usuários: {count}\n')
        
        if count > 0:
            cur.execute("SELECT id, email, nome FROM usuarios LIMIT 5")
            for row in cur.fetchall():
                print(f'  - {row["email"]} ({row["nome"]})')
        
        cur.close()
        conn.close()
    
    print('\n' + '='*80 + '\n')
    
except ImportError as e:
    print(f'\n❌ Erro de importação: {e}')
    print('\nTente rodar este comando no terminal do backend:')
    print('cd /app && python check_teste_user.py')
except Exception as e:
    print(f'\n❌ Erro: {e}')
    import traceback
    traceback.print_exc()

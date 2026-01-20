#!/usr/bin/env python3

import sys
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

try:
    from config import Config
    from db import get_user_by_email
    import bcrypt
    
    print('\n🔍 VERIFICANDO USUÁRIO teste@email.com\n')
    
    usuario = get_user_by_email('teste@email.com')
    
    if usuario:
        print('✅ Usuário encontrado!\n')
        print(f'ID: {usuario["id"]}')
        print(f'Email: {usuario["email"]}')
        print(f'Senha armazenada: {usuario["senha"]}')
        print(f'Comprimento: {len(usuario["senha"])} caracteres')
        
        # Detectar tipo
        if usuario["senha"].startswith('$2'):
            print('Tipo: BCRYPT\n')
            
            # Testar se a senha 123456 bate
            try:
                resultado = bcrypt.checkpw(b'123456', usuario["senha"].encode())
                print(f'Teste bcrypt.checkpw("123456"): {resultado}')
                if resultado:
                    print('✅ SENHA CORRETA!')
                else:
                    print('❌ SENHA INCORRETA')
            except Exception as e:
                print(f'Erro ao testar bcrypt: {e}')
        else:
            print('Tipo: PLAINTEXT\n')
            
            # Testar plaintext
            if usuario["senha"] == '123456':
                print('✅ SENHA CORRETA!')
            else:
                print(f'❌ SENHA INCORRETA')
                print(f'Esperado: 123456')
                print(f'Encontrado: {usuario["senha"]}')
    else:
        print('❌ Usuário NÃO encontrado!\n')
        
        # Listar todos
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
        cur.execute("SELECT id, email FROM usuarios")
        rows = cur.fetchall()
        
        print(f'Usuários no banco ({len(rows)}):')
        for row in rows:
            print(f'  - {row["email"]} (id={row["id"]})')
        
        cur.close()
        conn.close()
    
    print()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()

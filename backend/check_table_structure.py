#!/usr/bin/env python3
"""
Verificar estrutura real da tabela usuarios
"""

import sys
sys.path.insert(0, '/app')
sys.path.insert(0, '/app/backend')

try:
    from config import Config
    import psycopg2
    
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    
    cur = conn.cursor()
    
    print('\n' + '='*80)
    print('📋 ESTRUTURA DA TABELA: usuarios')
    print('='*80 + '\n')
    
    # Ver colunas
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'usuarios'
        ORDER BY ordinal_position
    """)
    
    print('Colunas:\n')
    for row in cur.fetchall():
        nullable = '✅ Pode ser NULL' if row[2] == 'YES' else '❌ NOT NULL'
        print(f'  - {row[0]:<20} {row[1]:<15} {nullable}')
    
    # Ver registros
    print('\n' + '='*80)
    print('📊 DADOS')
    print('='*80 + '\n')
    
    cur.execute("SELECT * FROM usuarios LIMIT 5")
    if cur.description:
        # Cabeçalho
        print('Registro:')
        for desc in cur.description:
            print(f'  - {desc[0]}')
        print()
        
        rows = cur.fetchall()
        for idx, row in enumerate(rows, 1):
            print(f'Usuário {idx}:')
            for i, val in enumerate(row):
                col_name = cur.description[i][0]
                print(f'  {col_name}: {val}')
            print()
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""
Adicionar coluna 'nome' à tabela usuarios se não existir
Execute no terminal do backend com: python fix_table.py
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
    print('🔧 VERIFICANDO COLUNA "nome" NA TABELA "usuarios"')
    print('='*80 + '\n')
    
    # Verificar se coluna existe
    cur.execute("""
        SELECT column_name 
        FROM information_schema.columns
        WHERE table_name = 'usuarios' AND column_name = 'nome'
    """)
    
    if cur.fetchone():
        print('✅ Coluna "nome" já existe!')
    else:
        print('⚠️  Coluna "nome" não existe. Adicionando...\n')
        
        # Adicionar coluna
        cur.execute("""
            ALTER TABLE usuarios 
            ADD COLUMN nome VARCHAR(255) DEFAULT NULL
        """)
        conn.commit()
        
        print('✅ Coluna "nome" adicionada com sucesso!')
    
    # Mostrar estrutura atualizada
    print('\n📋 Estrutura atual da tabela:\n')
    cur.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'usuarios'
        ORDER BY ordinal_position
    """)
    
    for row in cur.fetchall():
        nullable = '(NULL)' if row[2] == 'YES' else '(NOT NULL)'
        print(f'  ✓ {row[0]:<20} {row[1]:<20} {nullable}')
    
    print('\n' + '='*80 + '\n')
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f'❌ Erro: {e}')
    import traceback
    traceback.print_exc()

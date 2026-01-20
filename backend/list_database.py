#!/usr/bin/env python3
"""
Script para listar todas as tabelas e seus dados
Execute no terminal do backend no EasyPanel
"""

import sys
sys.path.append('/app')

from config import Config
import psycopg2
from psycopg2.extras import RealDictCursor

def list_all_tables():
    try:
        conn = psycopg2.connect(
            host=Config.DB_HOST,
            port=Config.DB_PORT,
            user=Config.DB_USER,
            password=Config.DB_PASSWORD,
            database=Config.DB_NAME
        )
        
        print('✅ Conectado ao banco de dados\n')
        print('=' * 80)
        print('📊 ESTRUTURA DO BANCO DE DADOS')
        print('=' * 80)
        
        cur = conn.cursor(cursor_factory=RealDictCursor)
        
        # Listar todas as tabelas
        cur.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            ORDER BY table_name
        """)
        tables = cur.fetchall()
        
        print(f'\n🗂️  Total de tabelas: {len(tables)}\n')
        
        for table in tables:
            table_name = table['table_name']
            print('─' * 80)
            print(f'📋 Tabela: {table_name.upper()}')
            print('─' * 80)
            
            # Listar colunas
            cur.execute("""
                SELECT 
                    column_name,
                    data_type,
                    character_maximum_length,
                    is_nullable,
                    column_default
                FROM information_schema.columns
                WHERE table_name = %s
                ORDER BY ordinal_position
            """, (table_name,))
            columns = cur.fetchall()
            
            print('\nColunas:')
            for idx, col in enumerate(columns, 1):
                col_type = col['data_type']
                if col['character_maximum_length']:
                    col_type += f"({col['character_maximum_length']})"
                
                nullable = 'NULL' if col['is_nullable'] == 'YES' else 'NOT NULL'
                default = f" DEFAULT {col['column_default']}" if col['column_default'] else ''
                
                print(f"  {idx}. {col['column_name']:<20} {col_type:<25} {nullable}{default}")
            
            # Contar registros
            cur.execute(f"SELECT COUNT(*) as count FROM {table_name}")
            count = cur.fetchone()['count']
            print(f'\n📊 Total de registros: {count}')
            
            # Mostrar registros
            if count > 0:
                cur.execute(f"SELECT * FROM {table_name} LIMIT 5")
                rows = cur.fetchall()
                
                print(f'\n🔍 Primeiros {len(rows)} registros:')
                for idx, row in enumerate(rows, 1):
                    print(f'\n  Registro {idx}:')
                    for key, value in row.items():
                        if isinstance(value, str) and len(value) > 60:
                            value = value[:57] + '...'
                        print(f'    {key}: {value}')
            print()
        
        print('=' * 80)
        print('✅ Consulta concluída!')
        print('=' * 80)
        
        cur.close()
        conn.close()
        
    except Exception as e:
        print(f'❌ Erro: {e}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    list_all_tables()

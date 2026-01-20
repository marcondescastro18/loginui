import sys
sys.path.append('backend')

from config import Config
import psycopg2

try:
    conn = psycopg2.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME
    )
    
    cur = conn.cursor()
    cur.execute("SELECT id, email, senha, nome, ativo FROM usuarios WHERE email = 'teste@email.com'")
    user = cur.fetchone()
    
    if user:
        print("✅ Usuário encontrado no banco:")
        print(f"   ID: {user[0]}")
        print(f"   Email: {user[1]}")
        print(f"   Senha: {user[2][:50]}{'...' if len(user[2]) > 50 else ''}")
        print(f"   Senha Length: {len(user[2])}")
        print(f"   Senha Type: {'bcrypt' if user[2].startswith('$2') else 'plaintext'}")
        print(f"   Nome: {user[3]}")
        print(f"   Ativo: {user[4]}")
    else:
        print("❌ Usuário NÃO encontrado")
    
    cur.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Erro: {e}")

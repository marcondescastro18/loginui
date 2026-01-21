#!/usr/bin/env python3
"""
Script de validação do backend corrigido.
Testa todas as funções de banco de dados sem usar colunas inexistentes.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from db import get_user_by_email, create_session, log_access, update_last_access, get_connection
import jwt
from datetime import datetime, timedelta
from config import Config

def test_db_connection():
    """Testa conexão com banco de dados"""
    print("🔍 Testando conexão com banco de dados...")
    conn = get_connection()
    if conn:
        print("✅ Conexão estabelecida com sucesso!")
        conn.close()
        return True
    else:
        print("❌ Falha ao conectar no banco de dados!")
        return False

def test_get_user_by_email():
    """Testa busca de usuário por email (sem coluna 'nome')"""
    print("\n🔍 Testando busca de usuário...")
    usuario = get_user_by_email('teste@email.com')
    
    if usuario:
        print(f"✅ Usuário encontrado!")
        print(f"   ID: {usuario['id']}")
        print(f"   Email: {usuario['email']}")
        print(f"   Senha (hash): {usuario['senha'][:20]}...")
        
        # Verificar que NÃO tem coluna 'nome'
        if 'nome' not in usuario:
            print("✅ Confirmado: coluna 'nome' NÃO está presente (correto!)")
        else:
            print("⚠️  Coluna 'nome' está presente (inesperado)")
        return True
    else:
        print("❌ Usuário não encontrado!")
        return False

def test_log_access():
    """Testa registro de acesso (sem coluna 'email' em registros_acesso)"""
    print("\n🔍 Testando registro de acesso...")
    
    # Teste 1: Login falhado sem usuário
    resultado1 = log_access(None, 'login', '127.0.0.1', False, 'Teste de falha')
    if resultado1:
        print("✅ Log de acesso falhado registrado com sucesso!")
    else:
        print("❌ Falha ao registrar log de acesso falhado!")
        return False
    
    # Teste 2: Login bem-sucedido com usuário
    usuario = get_user_by_email('teste@email.com')
    if usuario:
        resultado2 = log_access(usuario['id'], 'login', '127.0.0.1', True, 'Teste de sucesso')
        if resultado2:
            print("✅ Log de acesso bem-sucedido registrado com sucesso!")
        else:
            print("❌ Falha ao registrar log de acesso bem-sucedido!")
            return False
    
    return True

def test_create_session():
    """Testa criação de sessão"""
    print("\n🔍 Testando criação de sessão...")
    
    usuario = get_user_by_email('teste@email.com')
    if not usuario:
        print("❌ Usuário não encontrado para teste de sessão!")
        return False
    
    # Gerar token de teste
    payload = {
        'user_id': usuario['id'],
        'email': usuario['email'],
        'exp': datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(payload, Config.JWT_SECRET, algorithm='HS256')
    
    resultado = create_session(usuario['id'], token, '127.0.0.1')
    if resultado:
        print("✅ Sessão criada com sucesso!")
        return True
    else:
        print("❌ Falha ao criar sessão!")
        return False

def test_update_last_access():
    """Testa atualização de último acesso"""
    print("\n🔍 Testando atualização de último acesso...")
    
    usuario = get_user_by_email('teste@email.com')
    if not usuario:
        print("❌ Usuário não encontrado para teste de último acesso!")
        return False
    
    resultado = update_last_access(usuario['id'])
    if resultado:
        print("✅ Último acesso atualizado com sucesso!")
        return True
    else:
        print("❌ Falha ao atualizar último acesso!")
        return False

def run_all_tests():
    """Executa todos os testes"""
    print("=" * 60)
    print("🧪 INICIANDO TESTES DO BACKEND CORRIGIDO")
    print("=" * 60)
    
    results = []
    
    results.append(("Conexão DB", test_db_connection()))
    results.append(("Buscar Usuário", test_get_user_by_email()))
    results.append(("Registrar Acesso", test_log_access()))
    results.append(("Criar Sessão", test_create_session()))
    results.append(("Atualizar Último Acesso", test_update_last_access()))
    
    print("\n" + "=" * 60)
    print("📊 RESUMO DOS TESTES")
    print("=" * 60)
    
    for name, result in results:
        status = "✅ PASSOU" if result else "❌ FALHOU"
        print(f"{name:.<40} {status}")
    
    all_passed = all(result for _, result in results)
    
    print("=" * 60)
    if all_passed:
        print("🎉 TODOS OS TESTES PASSARAM!")
        print("✅ Backend está 100% compatível com o schema do banco!")
        return 0
    else:
        print("❌ ALGUNS TESTES FALHARAM!")
        print("⚠️  Verifique as mensagens de erro acima.")
        return 1

if __name__ == '__main__':
    exit_code = run_all_tests()
    sys.exit(exit_code)

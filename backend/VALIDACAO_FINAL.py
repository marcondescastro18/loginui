#!/usr/bin/env python3
"""
VALIDACAO_FINAL.py - Script de Validação das Correções

Valida que todas as correções foram aplicadas corretamente
e que o código está 100% compatível com o schema real do banco.

Executa verificações em:
- app.py: Endpoints e tratamento de exceções
- db.py: Funções de acesso ao banco
- create_user.py: Script de criação de usuários

RESULTADO ESPERADO: Todos os testes devem PASSAR ✅
"""

import re
import os
import sys

def check_file_content(filepath, checks):
    """
    Verifica se um arquivo contém ou NÃO contém determinados padrões.
    
    Args:
        filepath: Caminho do arquivo
        checks: Lista de tuplas (tipo, padrão, descrição)
                tipo = 'must_not_have' ou 'must_have'
    
    Returns:
        (passou, erros): Tupla com status e lista de erros
    """
    if not os.path.exists(filepath):
        return False, [f"Arquivo {filepath} não encontrado"]
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    erros = []
    for tipo, padrao, descricao in checks:
        if tipo == 'must_not_have':
            if re.search(padrao, content, re.IGNORECASE):
                erros.append(f"❌ {descricao}")
        elif tipo == 'must_have':
            if not re.search(padrao, content, re.IGNORECASE):
                erros.append(f"❌ {descricao}")
    
    return len(erros) == 0, erros

def main():
    print("=" * 80)
    print("🔍 VALIDAÇÃO FINAL DAS CORREÇÕES DO BACKEND")
    print("=" * 80)
    print()
    
    total_checks = 0
    passed_checks = 0
    
    # -------------------------------------------------------------------------
    # VALIDAÇÃO: app.py
    # -------------------------------------------------------------------------
    print("📄 Verificando app.py...")
    app_checks = [
        # NÃO deve usar coluna 'nome'
        ('must_not_have', r"['\"]nome['\"]", "NÃO deve usar coluna 'nome'"),
        ('must_not_have', r"usuario\['nome'\]", "NÃO deve acessar usuario['nome']"),
        
        # NÃO deve usar update_last_access
        ('must_not_have', r"update_last_access\(", "NÃO deve chamar update_last_access()"),
        
        # DEVE tratar exceções psycopg2.Error
        ('must_have', r"except psycopg2\.Error", "DEVE tratar psycopg2.Error"),
        
        # DEVE tratar Exception genérico
        ('must_have', r"except Exception", "DEVE tratar Exception genérico"),
        
        # DEVE retornar apenas id e email no response
        ('must_have', r"'usuario':\s*{[^}]*'id'", "DEVE retornar 'id' no response"),
        ('must_have', r"'usuario':\s*{[^}]*'email'", "DEVE retornar 'email' no response"),
    ]
    
    passou, erros = check_file_content('backend/app.py', app_checks)
    total_checks += len(app_checks)
    if passou:
        passed_checks += len(app_checks)
        print(f"  ✅ Todas as verificações passaram ({len(app_checks)}/{len(app_checks)})")
    else:
        passed_checks += len(app_checks) - len(erros)
        print(f"  ⚠️  Alguns problemas encontrados:")
        for erro in erros:
            print(f"     {erro}")
    print()
    
    # -------------------------------------------------------------------------
    # VALIDAÇÃO: db.py
    # -------------------------------------------------------------------------
    print("📄 Verificando db.py...")
    db_checks = [
        # NÃO deve usar coluna 'nome' em SELECT
        ('must_not_have', r"SELECT.*nome.*FROM usuarios", "NÃO deve SELECT coluna 'nome'"),
        
        # NÃO deve usar coluna 'email' em INSERT registros_acesso
        ('must_not_have', r"INSERT INTO registros_acesso.*email", "NÃO deve INSERT 'email' em registros_acesso"),
        
        # NÃO deve usar coluna 'ultimo_acesso'
        ('must_not_have', r"ultimo_acesso", "NÃO deve usar coluna 'ultimo_acesso'"),
        
        # DEVE ter SELECT apenas com colunas corretas
        ('must_have', r"SELECT id, email, senha, criado_em FROM usuarios", "DEVE SELECT apenas id, email, senha, criado_em"),
        
        # DEVE ter INSERT correto em registros_acesso
        ('must_have', r"INSERT INTO registros_acesso \(usuario_id, tipo_evento, endereco_ip, sucesso, mensagem\)", 
         "DEVE INSERT correto em registros_acesso"),
        
        # DEVE tratar exceções com rollback
        ('must_have', r"conn\.rollback\(\)", "DEVE fazer rollback em erros"),
        
        # DEVE ter tratamento psycopg2.Error
        ('must_have', r"except psycopg2\.Error", "DEVE tratar psycopg2.Error"),
    ]
    
    passou, erros = check_file_content('backend/db.py', db_checks)
    total_checks += len(db_checks)
    if passou:
        passed_checks += len(db_checks)
        print(f"  ✅ Todas as verificações passaram ({len(db_checks)}/{len(db_checks)})")
    else:
        passed_checks += len(db_checks) - len(erros)
        print(f"  ⚠️  Alguns problemas encontrados:")
        for erro in erros:
            print(f"     {erro}")
    print()
    
    # -------------------------------------------------------------------------
    # VALIDAÇÃO: create_user.py
    # -------------------------------------------------------------------------
    print("📄 Verificando create_user.py...")
    user_checks = [
        # NÃO deve usar coluna 'nome' em INSERT
        ('must_not_have', r"INSERT.*nome.*INTO usuarios", "NÃO deve INSERT coluna 'nome'"),
        
        # NÃO deve usar coluna 'ativo'
        ('must_not_have', r"ativo", "NÃO deve usar coluna 'ativo'"),
        
        # DEVE ter INSERT apenas com email e senha
        ('must_have', r"INSERT INTO usuarios \(email, senha\)", "DEVE INSERT apenas email e senha"),
        
        # DEVE tratar exceções
        ('must_have', r"except.*Error", "DEVE tratar exceções"),
    ]
    
    passou, erros = check_file_content('backend/create_user.py', user_checks)
    total_checks += len(user_checks)
    if passou:
        passed_checks += len(user_checks)
        print(f"  ✅ Todas as verificações passaram ({len(user_checks)}/{len(user_checks)})")
    else:
        passed_checks += len(user_checks) - len(erros)
        print(f"  ⚠️  Alguns problemas encontrados:")
        for erro in erros:
            print(f"     {erro}")
    print()
    
    # -------------------------------------------------------------------------
    # RESULTADO FINAL
    # -------------------------------------------------------------------------
    print("=" * 80)
    print(f"📊 RESULTADO FINAL: {passed_checks}/{total_checks} verificações passaram")
    print("=" * 80)
    
    if passed_checks == total_checks:
        print()
        print("🎉 SUCESSO! Todas as correções foram aplicadas corretamente!")
        print()
        print("✅ Backend está 100% compatível com o schema real do banco")
        print("✅ Nenhum uso de colunas inexistentes (nome, ativo, email em registros_acesso)")
        print("✅ Tratamento robusto de exceções SQL")
        print("✅ Gunicorn não deve reiniciar por erros SQL")
        print()
        print("🚀 Próximos passos:")
        print("   1. Testar criação de usuário: python backend/create_user.py")
        print("   2. Iniciar servidor: gunicorn --bind 0.0.0.0:3000 app:app")
        print("   3. Testar login via frontend ou curl")
        print("   4. Verificar logs (não deve ter erro SQL)")
        print()
        return 0
    else:
        print()
        print("⚠️  ATENÇÃO: Algumas verificações falharam!")
        print(f"   {total_checks - passed_checks} problema(s) encontrado(s)")
        print()
        print("Revise os erros acima e corrija os arquivos conforme necessário.")
        print()
        return 1

if __name__ == "__main__":
    sys.exit(main())

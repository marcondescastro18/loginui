#!/usr/bin/env python3
"""
config.py - Configurações da Aplicação

Gerencia todas as variáveis de ambiente e configurações do sistema.
Carrega valores do arquivo .env e define valores padrão quando não especificados.

Variáveis obrigatórias:
- JWT_SECRET: Chave secreta para assinatura de tokens JWT (mínimo 32 caracteres)

Variáveis opcionais com defaults:
- DB_HOST: Host do PostgreSQL (padrão: login_auth_db)
- DB_PORT: Porta do PostgreSQL (padrão: 5432)
- DB_USER: Usuário do banco (padrão: auth_db)
- DB_PASSWORD: Senha do banco (padrão: Senha123456)
- DB_NAME: Nome do banco (padrão: auth_db)
- DEBUG: Modo debug (padrão: False)
- PORT: Porta da aplicação (padrão: 3000)

Uso:
    from config import Config
    print(Config.DB_HOST)
"""

import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env para os.environ
load_dotenv()

class Config:
    """
    Classe de configuração que centraliza todas as variáveis de ambiente.
    Todas as propriedades são carregadas na inicialização da aplicação.
    """
    
    # Configurações do Banco de Dados PostgreSQL
    DB_HOST = os.getenv('DB_HOST', 'login_auth_db')  # Host do servidor PostgreSQL
    DB_PORT = os.getenv('DB_PORT', '5432')           # Porta padrão do PostgreSQL
    DB_USER = os.getenv('DB_USER', 'auth_db')        # Usuário do banco
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Senha123456')  # Senha do banco
    DB_NAME = os.getenv('DB_NAME', 'auth_db')        # Nome do banco de dados
    
    # Configurações de Segurança
    JWT_SECRET = os.getenv('JWT_SECRET')  # Chave secreta para JWT - OBRIGATÓRIA
    
    # Configurações da Aplicação
    DEBUG = os.getenv('DEBUG', False)     # Modo debug (True/False)
    PORT = int(os.getenv('PORT', 3000))   # Porta onde a aplicação vai rodar

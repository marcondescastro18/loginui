import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'postgres')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'auth_db')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Senha123456')
    DB_NAME = os.getenv('DB_NAME', 'auth_db')
    JWT_SECRET = os.getenv('JWT_SECRET', 'sua_chave_secreta_aqui')
    DEBUG = os.getenv('DEBUG', False)
    PORT = int(os.getenv('PORT', 3000))

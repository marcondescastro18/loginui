import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    DB_HOST = os.getenv('DB_HOST', 'login_auth_db')
    DB_PORT = os.getenv('DB_PORT', '5432')
    DB_USER = os.getenv('DB_USER', 'auth_db')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'Senha123456')
    DB_NAME = os.getenv('DB_NAME', 'auth_db')
    JWT_SECRET = os.getenv('JWT_SECRET', 'sk-prod-2026-login-system-az9x4kL8pQ2mN6tV1wJe3rF5uD7sB9cH0')
    DEBUG = os.getenv('DEBUG', False)
    PORT = int(os.getenv('PORT', 3000))

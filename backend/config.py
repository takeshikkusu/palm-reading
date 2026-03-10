"""
アプリケーション設定。
環境変数から読み取り、デフォルトは開発用。
"""
import os


def get_env(key: str, default: str = "") -> str:
    return os.environ.get(key, default).strip()


# Gemini
GEMINI_API_KEY = get_env("GEMINI_API_KEY")
GEMINI_MODEL = get_env("GEMINI_MODEL", "gemini-2.0-flash-exp")

# Flask
FLASK_ENV = get_env("FLASK_ENV", "development")
DEBUG = FLASK_ENV == "development"

# CORS: 本番ではフロントのオリジンを明示することを推奨
CORS_ORIGINS = get_env("CORS_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173")
if CORS_ORIGINS:
    CORS_ORIGINS_LIST = [o.strip() for o in CORS_ORIGINS.split(",") if o.strip()]
else:
    CORS_ORIGINS_LIST = []

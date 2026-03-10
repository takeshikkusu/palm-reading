"""
Flaskアプリケーションのエントリポイント。
依存性の組み立てはここで行い、Clean Architectureの最外層として動作する。
"""
from flask import Flask
from flask_cors import CORS

from backend.config import CORS_ORIGINS_LIST, GEMINI_API_KEY, GEMINI_MODEL
from backend.infrastructure.gemini_llm import GeminiLLMAdapter
from backend.interfaces.flask_controller import create_diagnosis_blueprint
from backend.usecases.diagnose_palm import DiagnosePalmUseCase


def create_app() -> Flask:
    app = Flask(__name__)

    CORS(app, origins=CORS_ORIGINS_LIST, supports_credentials=True)

    if not GEMINI_API_KEY:
        app.logger.warning("GEMINI_API_KEY が未設定です。/.env または環境変数を設定してください。")

    # Infrastructure
    llm = GeminiLLMAdapter(api_key=GEMINI_API_KEY or "dummy", model=GEMINI_MODEL)
    # Use case
    diagnose_use_case = DiagnosePalmUseCase(llm=llm)
    # Interface (Controller)
    bp = create_diagnosis_blueprint(diagnose_use_case)
    app.register_blueprint(bp)

    @app.route("/")
    def index():
        return {"service": "Palm AI", "version": "1.0.0", "docs": "/api/health"}

    return app


app = create_app()

if __name__ == "__main__":
    from backend.config import DEBUG
    app.run(host="0.0.0.0", port=5000, debug=DEBUG)

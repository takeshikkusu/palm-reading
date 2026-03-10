"""
Interfaces層: Flaskコントローラ（最外層）
HTTPの入出力のみを担当。Use caseを呼び出し、結果をJSONで返す。
"""
import base64
import re

from flask import Blueprint, request, jsonify, current_app

from backend.usecases.diagnose_palm import DiagnosePalmUseCase


# 依存性はapp.pyで注入するため、ファクトリでBlueprintを返す
def create_diagnosis_blueprint(diagnose_use_case: DiagnosePalmUseCase) -> Blueprint:
    bp = Blueprint("diagnosis", __name__, url_prefix="/api")

    ALLOWED_MIME = re.compile(r"^image/(jpeg|jpg|png|gif|webp)$", re.I)
    MAX_SIZE_MB = 5
    MAX_BYTES = MAX_SIZE_MB * 1024 * 1024

    @bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @bp.route("/diagnose", methods=["POST"])
    def diagnose():
        """
        POST body: multipart/form-data または JSON
        - image: ファイル、または base64 文字列
        - prompt: オプションの質問
        """
        try:
            image_b64 = None
            mime_type = None
            prompt = None

            if request.is_json:
                data = request.get_json() or {}
                image_b64 = data.get("image")
                mime_type = data.get("mime_type")
                prompt = data.get("prompt")
            else:
                if "image" in request.files:
                    file = request.files["image"]
                    if file.filename:
                        mime_type = file.mimetype
                        raw = file.read()
                        if len(raw) > MAX_BYTES:
                            return (
                                jsonify({"error": f"画像は{MAX_SIZE_MB}MB以下にしてください"}),
                                400,
                            )
                        image_b64 = base64.b64encode(raw).decode("utf-8")
                if not image_b64 and "image" in request.form:
                    image_b64 = request.form.get("image")
                if not mime_type and "mime_type" in request.form:
                    mime_type = request.form.get("mime_type")
                prompt = request.form.get("prompt") or None

            if not image_b64:
                return jsonify({"error": "画像を送信してください"}), 400

            # データURLの場合はpayloadだけ取り出す
            if isinstance(image_b64, str) and image_b64.startswith("data:"):
                match = re.match(r"data:([^;]+);base64,(.+)", image_b64)
                if match:
                    mime, payload = match.group(1), match.group(2)
                    if not ALLOWED_MIME.match(mime):
                        return jsonify({"error": "対応形式: JPEG, PNG, GIF, WebP"}), 400
                    image_b64 = payload
                    mime_type = mime
                else:
                    return jsonify({"error": "不正なデータURLです"}), 400

            if not mime_type:
                # data URL ではない生base64の場合、暫定で JPEG として扱う
                mime_type = "image/jpeg"
            if not ALLOWED_MIME.match(str(mime_type)):
                return jsonify({"error": "対応形式: JPEG, PNG, GIF, WebP"}), 400

            result = diagnose_use_case.execute(image_base64=image_b64, mime_type=mime_type, user_prompt=prompt)
            return jsonify(result.to_dict()), 200

        except ValueError as e:
            current_app.logger.warning("Bad request in /api/diagnose: %s", e)
            return jsonify({"error": str(e)}), 400
        except Exception as e:
            # 詳細をサーバーログに出しておく（Render の Events で確認可能）
            current_app.logger.exception("Unexpected error in /api/diagnose")
            return jsonify({"error": "診断中にエラーが発生しました"}), 500

    return bp

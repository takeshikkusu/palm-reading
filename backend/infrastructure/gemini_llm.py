"""
Infrastructure層: Gemini APIアダプタ
LLMPortの実装。APIキー・HTTPはここに閉じる。
"""
import base64
from typing import Optional

from backend.interfaces.llm_port import LLMPort


SYSTEM_PROMPT = """あなたは手相の専門家です。手のひらの画像を見て、以下のJSON形式のみで回答してください。
他の説明や前置きは書かず、JSONだけを返してください。

{
  "summary": "全体の印象を2〜3文で",
  "life_line": "生命線についての解説",
  "head_line": "知能線についての解説",
  "heart_line": "感情線についての解説",
  "fate_line": "運命線がある場合の解説（分からなければ null）",
  "advice": "今日からできるアドバイス（任意）"
}
"""


class GeminiLLMAdapter(LLMPort):
    """Google Gemini APIを用いたLLMPortの実装。"""

    def __init__(self, api_key: str, model: str = "models/gemini-1.5-flash") -> None:
        self._api_key = api_key
        self._model = self._normalize_model_name(model)

    @staticmethod
    def _normalize_model_name(model: str) -> str:
        """
        google-generativeai は 'models/...' の形式が基本。
        例: 'gemini-1.5-flash' -> 'models/gemini-1.5-flash'
        """
        m = (model or "").strip()
        if not m:
            return "models/gemini-1.5-flash"
        if m.startswith("models/"):
            return m
        return f"models/{m}"

    def generate_palm_reading(self, image_base64: str, mime_type: str, prompt: Optional[str] = None) -> str:
        import google.generativeai as genai

        genai.configure(api_key=self._api_key)
        model = genai.GenerativeModel(self._model, system_instruction=SYSTEM_PROMPT)

        # Base64 → バイナリ
        try:
            image_bytes = base64.b64decode(image_base64, validate=True)
        except Exception:
            raise ValueError("画像のBase64が不正です")

        # google-generativeai は Blob（mime_type + data）を parts として扱える
        image_part = {"mime_type": mime_type, "data": image_bytes}
        user_text = "手相を診断してください。"
        if prompt and prompt.strip():
            user_text += f"\n\nユーザーからの質問: {prompt.strip()}"

        contents = [user_text, image_part]
        config = genai.types.GenerationConfig(
            temperature=0.7,
            max_output_tokens=1024,
        )
        # response_mime_type はモデル対応時のみ有効
        if hasattr(genai.types.GenerationConfig, "response_mime_type"):
            config.response_mime_type = "application/json"

        response = model.generate_content(contents, generation_config=config)

        if not response or not response.text:
            raise ValueError("診断結果を取得できませんでした")

        return response.text.strip()

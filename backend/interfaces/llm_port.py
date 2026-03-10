"""
Interfaces層: LLMポート（抽象インターフェース）
Use caseがLLMに依存する際の契約。実装はInfrastructure層。
"""
from abc import ABC, abstractmethod
from typing import Optional


class LLMPort(ABC):
    """
    LLM呼び出しの抽象インターフェース。
    Gemini以外（OpenAI, Claude等）への差し替えが可能になる。
    """

    @abstractmethod
    def generate_palm_reading(
        self,
        image_base64: str,
        mime_type: str,
        prompt: Optional[str] = None,
    ) -> str:
        """
        手のひら画像から診断テキストを生成する。

        Args:
            image_base64: Base64エンコードされた画像データ
            mime_type: 画像のMIMEタイプ（例: image/jpeg）
            prompt: オプションの追加プロンプト（質問など）

        Returns:
            診断結果のJSON文字列（パースはUse caseで行う想定）
        """
        pass

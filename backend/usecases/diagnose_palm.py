"""
Use cases層: 手相診断ユースケース
LLMはPort経由で注入され、Controllerから直接Geminiを呼ばない。
"""
import json
import re
from typing import Optional

from backend.domain.entities import PalmReadingResult
from backend.interfaces.llm_port import LLMPort


class DiagnosePalmUseCase:
    """
    手相画像を受け取り、LLMで診断し、PalmReadingResultを返す。
    ビジネスルール（プロンプト設計・パース）はここに集約。
    """

    def __init__(self, llm: LLMPort) -> None:
        self._llm = llm

    def execute(
        self,
        image_base64: str,
        mime_type: str,
        user_prompt: Optional[str] = None,
    ) -> PalmReadingResult:
        """
        診断を実行する。

        Args:
            image_base64: Base64エンコードされた手のひら画像
            mime_type: 画像のMIMEタイプ（例: image/jpeg）
            user_prompt: ユーザーからのオプション質問

        Returns:
            診断結果エンティティ

        Raises:
            ValueError: 画像が不正またはLLMが不正な形式を返した場合
        """
        if not image_base64 or not image_base64.strip():
            raise ValueError("画像データがありません")
        if not mime_type or not str(mime_type).strip():
            raise ValueError("画像形式が不明です")

        raw_response = self._llm.generate_palm_reading(image_base64, str(mime_type).strip(), user_prompt)
        return self._parse_response(raw_response)

    def _parse_response(self, raw: str) -> PalmReadingResult:
        """
        LLMの生テキストをパースしてPalmReadingResultにする。
        ビジネスルール: 必須項目とオプション項目の扱い。
        """
        raw = raw.strip()
        # JSONブロックを抽出（```json ... ``` や { ... } に対応）
        json_str = self._extract_json(raw)
        data = json.loads(json_str)

        return PalmReadingResult(
            summary=self._get_str(data, "summary", "要約がありません"),
            life_line=self._get_str(data, "life_line", "生命線の情報がありません"),
            head_line=self._get_str(data, "head_line", "知能線の情報がありません"),
            heart_line=self._get_str(data, "heart_line", "感情線の情報がありません"),
            fate_line=self._get_str_optional(data, "fate_line"),
            advice=self._get_str_optional(data, "advice"),
        )

    @staticmethod
    def _extract_json(text: str) -> str:
        """MarkdownのコードブロックやプレーンJSONからJSON文字列を抽出。"""
        # ```json ... ``` を優先
        code_block = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
        if code_block:
            return code_block.group(1).strip()
        # { ... } を探す
        brace = re.search(r"\{[\s\S]*\}", text)
        if brace:
            return brace.group(0)
        return text

    @staticmethod
    def _get_str(data: dict, key: str, default: str) -> str:
        v = data.get(key)
        if v is None:
            return default
        return str(v).strip() or default

    @staticmethod
    def _get_str_optional(data: dict, key: str) -> Optional[str]:
        v = data.get(key)
        if v is None:
            return None
        s = str(v).strip()
        return s if s else None

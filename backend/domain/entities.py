"""
Domain層: 診断結果エンティティ
ビジネスルールと不変の構造を保持する。
"""
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class PalmReadingResult:
    """
    手相診断の結果を表すエンティティ。
    外部フレームワークに依存しない純粋なデータ構造。
    """
    summary: str
    life_line: str
    head_line: str
    heart_line: str
    fate_line: Optional[str] = None
    advice: Optional[str] = None

    def to_dict(self) -> dict:
        """APIレスポンス用の辞書に変換（Presenter層で使う想定）。"""
        return {
            "summary": self.summary,
            "life_line": self.life_line,
            "head_line": self.head_line,
            "heart_line": self.heart_line,
            "fate_line": self.fate_line,
            "advice": self.advice,
        }

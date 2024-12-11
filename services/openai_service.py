# paper_harvester/services/openai_service.py

from openai import OpenAI
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_PARAMS
from services.paper_processor import PaperProcessor
import time
from typing import Dict, Any, Optional

class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_summary(self, paper_info: Dict[str, Any]) -> Optional[str]:
        """論文の要約を生成"""
        print(f"Generating summary for paper: {paper_info['title'][:50]}...")
        try:
            prompt = self._create_summary_prompt(paper_info)
            
            response = self.client.chat.completions.create(
                model=OPENAI_MODEL,
                messages=[
                    {
                        "role": "system",
                        "content": "あなたは研究論文を深く理解し、技術的な詳細を分かりやすく解説する専門家です。"
                                "論文の全体像を把握し、重要なポイントを簡潔かつ正確に説明してください。"
                    },
                    {"role": "user", "content": prompt}
                ],
                **OPENAI_PARAMS
            )
            
            summary = response.choices[0].message.content.strip()
            print("Summary generated successfully")
            return summary

        except Exception as e:
            print(f"Error generating summary: {e}")
            import traceback
            print(traceback.format_exc())
            return f"要約の生成に失敗しました。\n論文タイトル: {paper_info['title']}"

    def _create_summary_prompt(self, paper_info: Dict[str, Any]) -> str:
        """要約生成用のプロンプトを作成"""
        source_text = paper_info.get('full_text', paper_info['abstract'])
        source_type = "本文" if paper_info.get('full_text') else "アブストラクト"
        
        return f"""以下の論文の{source_type}を分析し、詳細な要約を日本語で作成してください。

        【論文情報】
        タイトル: {paper_info['title']}
        著者: {paper_info['authors']}
        
        {source_type}:
        {source_text}

        以下の形式で出力してください：

        📌 *研究の要点*
        • 目的：
        • 背景：
        • 課題：

        🔍 *提案手法*
        • 新規性：
        • アプローチ：
        • 特徴：

        🛠️ *技術詳細*
        • 実装方法：
        • アーキテクチャ：
        • 使用技術：
        • データセット：

        📊 *主な結果*
        • 性能評価：
        • 比較結果：
        • 改善点：

        💡 *実装・利用のポイント*
        • 推奨環境：
        • 必要リソース：
        • 注意事項：

        📚 *関連研究との比較*
        • 類似研究：
        • 主な違い：
        • 優位点：

        ⚠️ *制限事項・課題*
        • 技術的制限：
        • 実用面での課題：
        • 改善の余地：

        🔮 *今後の展望*
        • 発展可能性：
        • 応用分野：
        • 将来課題：

        🔧 *実装例・疑似コード*
        • 主要な実装ポイント：
        • アルゴリズムの概要：
        • 実装時の注意点：

        注意事項：
        - 数値や具体例を積極的に含めてください
        - 特に重要な点は`バッククォート`で強調してください
        - この要約は{source_type}に基づいていることを考慮してください
        - 実験結果や評価指標は可能な限り具体的な数値で示してください
        """

def generate_summary(paper_info: Dict[str, Any]) -> str:
    """要約生成の便利関数"""
    service = OpenAIService()
    return service.generate_summary(paper_info) or f"要約の生成に失敗しました。\n論文タイトル: {paper_info['title']}"
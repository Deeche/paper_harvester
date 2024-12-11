# paper_harvester/utils/message_builder.py

from typing import List, Dict, Any, Optional

def create_paper_message_blocks(paper, keyword: Optional[str] = None) -> List[Dict[str, Any]]:
    """論文情報のメッセージブロックを作成"""
    arxiv_url = f"https://arxiv.org/abs/{paper.arxiv_id}"  # arXiv URLを生成
    
    blocks = [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{paper.title}*\n"
                        f"Authors: {paper.authors}\n"
                        f"Keywords: `{keyword}`\n"
                        f"Source: <{arxiv_url}|arXiv>"  # URLを追加
            }
        }
    ]
    return blocks

def create_summary_blocks(paper) -> List[Dict[str, Any]]:
    """スレッド用の要約とアブストラクトのブロックを生成"""
    blocks = []
    
    # 要約セクション
    if paper.summary:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📝 日本語要約*\n" + _escape_text(paper.summary)
            }
        })
    
    # アブストラクトセクション
    if paper.abstract:
        blocks.append({
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*📄 Original Abstract*\n" + _escape_text(paper.abstract)
            }
        })

    # セパレータ
    blocks.append({
        "type": "divider"
    })
    
    # フッター
    blocks.append({
        "type": "context",
        "elements": [
            {
                "type": "mrkdwn",
                "text": "このスレッドで論文について議論できます 💭"
            }
        ]
    })
    
    return blocks

def _escape_text(text: str) -> str:
    """Slack用のテキストエスケープ処理"""
    if not text:
        return ""
    
    # 特殊文字のエスケープ
    escapable_chars = ['&', '<', '>', '"', "'"]
    escaped_text = text
    for char in escapable_chars:
        if char == '&':
            escaped_text = escaped_text.replace(char, '&amp;')
        elif char == '<':
            escaped_text = escaped_text.replace(char, '&lt;')
        elif char == '>':
            escaped_text = escaped_text.replace(char, '&gt;')
        elif char == '"':
            escaped_text = escaped_text.replace(char, '&quot;')
        elif char == "'":
            escaped_text = escaped_text.replace(char, '&apos;')
    
    return escaped_text

def create_error_blocks(error_message: str) -> List[Dict[str, Any]]:
    """エラーメッセージ用のブロックを生成"""
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"⚠️ *エラーが発生しました*\n{error_message}"
            }
        }
    ]
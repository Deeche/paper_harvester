# paper_harvester/handlers/action_handlers.py

from config import SessionLocal
from models.database import Paper
from utils.message_builder import create_error_blocks
from slack_sdk.errors import SlackApiError
from typing import Any, Dict

def setup_action_handlers(app):
    @app.action("toggle_abstract")
    def handle_toggle_abstract(ack: Any, body: Dict[str, Any], client: Any):
        """アブストラクトの表示/非表示を切り替え"""
        ack()
        
        try:
            blocks = body['message']['blocks']
            abstract_block_id = body['actions'][0]['block_id']
            
            # 現在の表示状態をチェック
            for i, block in enumerate(blocks):
                if block.get('block_id') == abstract_block_id + '_content':
                    # アブストラクトが表示中なので非表示にする
                    blocks.pop(i)
                    button_text = "📖 アブストラクトを表示"
                    break
            else:
                # アブストラクトを表示する
                abstract_text = body['actions'][0]['value']
                abstract_block = {
                    "type": "section",
                    "block_id": abstract_block_id + '_content',
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*アブストラクト*\n{abstract_text}"
                    }
                }
                button_index = next(i for i, block in enumerate(blocks) 
                                  if block.get('block_id') == abstract_block_id)
                blocks.insert(button_index + 1, abstract_block)
                button_text = "📖 アブストラクトを隠す"
            
            # ボタンのテキストを更新
            for block in blocks:
                if block.get('block_id') == abstract_block_id:
                    block['elements'][0]['text']['text'] = button_text
            
            # メッセージを更新
            client.chat_update(
                channel=body['channel']['id'],
                ts=body['message']['ts'],
                blocks=blocks,
                text=body['message']['text']
            )
            
        except Exception as e:
            print(f"Error in toggle_abstract: {e}")
            try:
                client.chat_postEphemeral(
                    channel=body['channel']['id'],
                    user=body['user']['id'],
                    blocks=create_error_blocks("アブストラクトの表示切り替えに失敗しました。")
                )
            except SlackApiError:
                print(f"Failed to send error message: {e}")

    @app.action("paper_interest")
    def handle_paper_interest(ack: Any, body: Dict[str, Any], client: Any):
        """論文への興味を表明"""
        ack()
        user = body['user']['id']
        
        try:
            # スレッドにメッセージを投稿
            client.chat_postMessage(
                channel=body['channel']['id'],
                thread_ts=body['message']['ts'],
                text=f"<@{user}> がこの論文に興味を持っています 👍"
            )
            
            # ユーザーにフィードバック（一時メッセージ）
            client.chat_postEphemeral(
                channel=body['channel']['id'],
                user=user,
                text="論文に興味があることを記録しました 👍"
            )
            
            # データベースに記録（オプション）
            db = SessionLocal()
            try:
                # TODO: 興味を持った論文の記録を実装
                pass
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error in paper_interest: {e}")
            try:
                client.chat_postEphemeral(
                    channel=body['channel']['id'],
                    user=user,
                    blocks=create_error_blocks("アクションの記録に失敗しました。")
                )
            except SlackApiError:
                print(f"Failed to send error message: {e}")

    @app.action("paper_read_later")
    def handle_paper_read_later(ack: Any, body: Dict[str, Any], client: Any):
        """後で読むリストに追加"""
        ack()
        user = body['user']['id']
        
        try:
            # スレッドにメッセージを投稿
            client.chat_postMessage(
                channel=body['channel']['id'],
                thread_ts=body['message']['ts'],
                text=f"<@{user}> がこの論文を後で読むリストに追加しました 📌"
            )
            
            # ユーザーにフィードバック
            client.chat_postEphemeral(
                channel=body['channel']['id'],
                user=user,
                text="論文を後で読むリストに追加しました 📌"
            )
            
            # データベースに記録（オプション）
            db = SessionLocal()
            try:
                # TODO: 後で読む論文の記録を実装
                pass
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error in paper_read_later: {e}")
            try:
                client.chat_postEphemeral(
                    channel=body['channel']['id'],
                    user=user,
                    blocks=create_error_blocks("アクションの記録に失敗しました。")
                )
            except SlackApiError:
                print(f"Failed to send error message: {e}")

    @app.action("paper_read")
    def handle_paper_read(ack: Any, body: Dict[str, Any], client: Any):
        """論文を読むボタンのクリックを記録"""
        ack()
        # このアクションは直接URLを開くだけなので、
        # 必要に応じてログ記録などを追加できます
        pass

    return app

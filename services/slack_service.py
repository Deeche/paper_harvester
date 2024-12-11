# paper_harvester/services/slack_service.py

from slack_bolt import App
from slack_sdk.errors import SlackApiError
from typing import Optional
from config import SLACK_BOT_TOKEN
from utils.message_builder import create_paper_message_blocks, create_summary_blocks
import time

class SlackService:
    def __init__(self):
        """Slackサービスの初期化"""
        print("\nInitializing Slack Service...")
        self.app = App(token=SLACK_BOT_TOKEN)
        self.setup_handlers()
    
    def setup_handlers(self):
        """ハンドラーのセットアップ"""
        print("Setting up command handlers...")
        from handlers.command_handlers import setup_command_handlers
        setup_command_handlers(self.app)
        
        # アクションハンドラは一時的に無効化
        # print("Setting up action handlers...")
        # from handlers.action_handlers import setup_action_handlers
        # setup_action_handlers(self.app)
    
    def send_paper_message(self, channel_id: str, paper, keyword: Optional[str] = None, max_retries: int = 3):
        """論文メッセージの送信"""
        retry_count = 0
        while retry_count < max_retries:
            try:
                print(f"\nSending message for paper: {paper.title}")
                
                # メインメッセージを送信
                print("Posting main message...")
                main_message = self.app.client.chat_postMessage(
                    channel=channel_id,
                    blocks=create_paper_message_blocks(paper, keyword),
                    text=f"新着論文: {paper.title}"
                )
                
                # スレッドに要約を送信
                print("Posting summary in thread...")
                thread_message = self.app.client.chat_postMessage(
                    channel=channel_id,
                    thread_ts=main_message['ts'],
                    blocks=create_summary_blocks(paper),
                    text=f"論文の要約とアブストラクト"
                )
                
                print("Messages posted successfully")
                return True
                
            except SlackApiError as e:
                retry_count += 1
                print(f"Slack API error (attempt {retry_count}): {e}")
                if e.response['error'] == 'ratelimited':
                    # レートリミットの場合、指定された時間待機
                    retry_after = int(e.response.headers.get('Retry-After', 30))
                    print(f"Rate limited. Waiting {retry_after} seconds...")
                    time.sleep(retry_after)
                else:
                    # その他のエラーの場合は5秒待機
                    time.sleep(5)
                
                if retry_count >= max_retries:
                    print(f"Failed to send message after {max_retries} attempts")
                    return False
                
            except Exception as e:
                print(f"Error sending message: {e}")
                import traceback
                print(traceback.format_exc())
                return False
    
    def update_message(self, channel_id: str, message_ts: str, blocks, text: str):
        """メッセージの更新"""
        try:
            self.app.client.chat_update(
                channel=channel_id,
                ts=message_ts,
                blocks=blocks,
                text=text
            )
            return True
        except SlackApiError as e:
            print(f"Error updating message: {e}")
            return False
    
    def delete_message(self, channel_id: str, message_ts: str):
        """メッセージの削除"""
        try:
            self.app.client.chat_delete(
                channel=channel_id,
                ts=message_ts
            )
            return True
        except SlackApiError as e:
            print(f"Error deleting message: {e}")
            return False
    
    def get_channel_info(self, channel_id: str):
        """チャンネル情報の取得"""
        try:
            response = self.app.client.conversations_info(channel=channel_id)
            return response['channel']
        except SlackApiError as e:
            print(f"Error getting channel info: {e}")
            return None
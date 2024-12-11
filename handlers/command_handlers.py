# paper_harvester/handlers/command_handlers.py
from config import (
    SessionLocal, 
    DEFAULT_DAYS_BACK,
    DEFAULT_MAX_RESULTS,
    SLACK_BOT_TOKEN
)
from models.database import Channel, Keyword, ChannelConfig
from services.arxiv import ArxivService
from services.paper_processor import PaperProcessor
from utils.message_builder import create_paper_message_blocks, create_summary_blocks
from sqlalchemy.orm import joinedload
from slack_bolt import App
from slack_sdk import WebClient
import time
from services.openai_service import OpenAIService

client = WebClient(token=SLACK_BOT_TOKEN)

def setup_command_handlers(app):
    # ... 既存のコード ...
    @app.command("/paper_subscribe")
    def handle_paper_subscribe(ack, respond, command):
        """キーワードを登録"""
        # Slackからの即時応答要求に対して空で応答
        ack()
        
        try:
            if not command.get('text'):
                respond("キーワードを指定してください。例：`/paper_subscribe LLM`")
                return
            
            keyword_text = command["text"].strip()
            db = SessionLocal()
            
            try:
                success_message = PaperProcessor.setup_keywords(db, command["channel_id"], keyword_text)
                if success_message:
                    respond(success_message)
                else:
                    respond("キーワードの登録に失敗しました。")
                    
            finally:
                db.close()
                
        except Exception as e:
            print(f"Error in handle_paper_subscribe: {e}")
            import traceback
            print(traceback.format_exc())
            respond("エラーが発生しました。")

    @app.command("/paper_list_keywords")
    def handle_paper_list_keywords(ack, respond, command):
        """現在の購読キーワード一覧を表示"""
        ack()
        
        db = SessionLocal()
        try:
            channel = db.query(Channel).filter_by(
                slack_channel_id=command["channel_id"]
            ).options(
                joinedload(Channel.keywords)
            ).first()
            
            if channel and channel.keywords:
                keywords = [k.word for k in channel.keywords]
                # メッセージ形式を統一
                keyword_list = "、".join([f"「{k}」" for k in keywords])
                respond(f"現在登録されているキーワード: {keyword_list}")
            else:
                respond("このチャンネルには購読キーワードが設定されていません。")
        finally:
            db.close()

    @app.command("/paper_remove_keyword")
    def handle_remove_keyword(ack, respond, command):
        """キーワードの購読を解除"""
        ack()
        
        word = command["text"].strip()
        if not word:
            respond("削除するキーワードを指定してください。")
            return
        
        db = SessionLocal()
        try:
            channel = db.query(Channel).filter_by(slack_channel_id=command["channel_id"]).first()
            keyword = db.query(Keyword).filter_by(word=word).first()
            
            if channel and keyword and keyword in channel.keywords:
                channel.keywords.remove(keyword)
                db.commit()
                respond(f"キーワード `{word}` の購読を解除しました。")
            else:
                respond(f"キーワード `{word}` は購読されていません。")
        finally:
            db.close()

    @app.command("/paper_check_now")
    def handle_paper_check_now(ack, respond, command):
        """今すぐ論文をチェック"""
        ack()
        
        db = SessionLocal()
        try:
            print(f"\n=== Starting paper_check_now for channel: {command['channel_id']} ===")
            
            # チャンネルとキーワードの取得
            channel = db.query(Channel).filter_by(
                slack_channel_id=command["channel_id"]
            ).options(
                joinedload(Channel.keywords),
                joinedload(Channel.config)
            ).first()
            
            print(f"Channel found: {channel is not None}")
            if channel:
                print(f"Keywords count: {len(channel.keywords) if channel.keywords else 0}")
                print(f"Keywords: {[k.word for k in channel.keywords] if channel.keywords else []}")
                print(f"Config: days_back={channel.config.days_back if channel.config else 'None'}")
            
            if not channel or not channel.keywords:
                print("No channel or keywords found")
                respond("このチャンネルにはキーワードが設定されていません。`/paper_subscribe`で設定してください。")
                return
            
            openai_service = OpenAIService()
            total_new_papers = 0
            
            for keyword in channel.keywords:
                print(f"\nProcessing keyword: {keyword.word}")
                new_papers = ArxivService.fetch_and_process_papers(db, keyword.word, command["channel_id"])
                print(f"Found {len(new_papers)} new papers for keyword: {keyword.word}")
                total_new_papers += len(new_papers)
                
                for paper in new_papers:
                    print(f"Creating message blocks for paper: {paper.title}")
                    blocks = create_paper_message_blocks(paper, keyword.word)
                    
                    response = client.chat_postMessage(
                        channel=command["channel_id"],
                        blocks=blocks,
                        text=f"New paper: {paper.title}"
                    )
                    time.sleep(1)
                    
                    if response and 'ts' in response:
                        paper_info = {
                            'title': paper.title,
                            'authors': paper.authors,
                            'abstract': paper.abstract
                        }
                        summary = openai_service.generate_summary(paper_info)
                        
                        client.chat_postMessage(
                            channel=command["channel_id"],
                            thread_ts=response['ts'],
                            text=summary
                        )
                        time.sleep(1)
            
            print(f"\nTotal new papers found: {total_new_papers}")
            if total_new_papers == 0:
                respond(f"検索期間（過去{channel.config.days_back}日間）に新着論文は見つかりませんでした。")
            else:
                respond(f"✅ {total_new_papers}件の新着論文が見つかりました。")
            
        except Exception as e:
            print(f"Error in handle_paper_check_now: {e}")
            import traceback
            print(traceback.format_exc())
            respond("論文チェック中にエラーが発生しました。")
        finally:
            db.close()

    @app.command("/paper_set_days")
    def handle_set_days(ack, respond, command):
        """論文検索の対象期間を設定"""
        ack()
        
        try:
            days = int(command["text"].strip())
            if days <= 0 or days > 30:
                respond("検索対象期間は1-30日の範囲で指定してください。")
                return
        except ValueError:
            respond("正しい日数を指定してください（例: `/paper_set_days 2`）")
            return
        
        db = SessionLocal()
        try:
            channel = db.query(Channel).filter_by(slack_channel_id=command["channel_id"]).first()
            if not channel:
                channel = Channel(slack_channel_id=command["channel_id"], name=command["channel_name"])
                db.add(channel)
                db.commit()
            
            config = db.query(ChannelConfig).filter_by(channel_id=channel.id).first()
            if not config:
                config = ChannelConfig(channel_id=channel.id)
                db.add(config)
            
            config.days_back = days
            db.commit()
            
            respond(f"論文検索の対象期間を{days}日前までに設定しました。")
        finally:
            db.close()

    @app.command("/paper_settings")
    def handle_show_settings(ack, respond, command):
        """現在の設定を表示"""
        ack()
        db = SessionLocal()
        try:
            channel = db.query(Channel).filter_by(slack_channel_id=command["channel_id"]).first()
            if channel and channel.config:
                respond(
                    f"現在の設定:\n"
                    f"• 検索対象期間: {channel.config.days_back}日前まで\n"
                    f"• 最大検索件数: {channel.config.max_results}件\n"
                    f"• 登録キーワード数: {len(channel.keywords)}個"
                )
            else:
                respond("設定が見つかりません。デフォルト値が使用されます。")
        finally:
            db.close()

    return app

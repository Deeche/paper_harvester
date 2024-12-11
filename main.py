# paper_harvester/main.py
import os
import sys
from pathlib import Path

# paper_harvesterディレクトリをPythonパスに追加
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.append(str(current_dir))

from slack_bolt.adapter.socket_mode import SocketModeHandler
from config import SLACK_APP_TOKEN, engine, DB_PATH, BASE_DIR, SessionLocal
from services.slack_service import SlackService
from services.scheduler import SchedulerService
from models.database import Base, Channel

def init_db():
    """データベースの初期化"""
    print(f"Initializing database at: {DB_PATH}")
    
    # データベースディレクトリの権限設定
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    os.chmod(os.path.dirname(DB_PATH), 0o777)
    
    if os.path.exists(DB_PATH):
        if os.getenv("ENVIRONMENT") == "development":
            os.remove(DB_PATH)
            print("Removed existing database")
        else:
            print("Database already exists, skipping initialization")
            return
    
    # データベース作成
    Base.metadata.create_all(engine)
    
    # データベースファイルの権限設定
    os.chmod(DB_PATH, 0o666)
    print("Database initialized successfully!")

def main():
    print(f"Project root directory: {BASE_DIR}")
    
    # データベース初期化
    init_db()
    
    # Slackサービスの初期化
    slack_service = SlackService()
    
    # スケジューラーサービスの初期化と開始
    scheduler_service = SchedulerService(slack_service)
    scheduler_service.start()
    
    # SocketModeでアプリを起動
    print("⚡️ Bolt app is running!")
    handler = SocketModeHandler(slack_service.app, SLACK_APP_TOKEN)
    handler.start()

if __name__ == "__main__":
    main()
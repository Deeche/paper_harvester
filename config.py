import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import pytz

# .envファイルから環境変数を読み込む
load_dotenv()

# paper_harvesterディレクトリをルートとして設定
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# データベースファイルのパスを設定
DB_PATH = os.path.join(BASE_DIR, "paperbot.db")

# データベース設定
DATABASE_URL = f"sqlite:///{DB_PATH}"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

print(f"Database path: {DB_PATH}")  # デバッグ用

# Slack設定
SLACK_BOT_TOKEN = os.getenv('SLACK_BOT_TOKEN')
SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')

# OpenAI設定
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
OPENAI_MODEL = "gpt-4o-mini-2024-07-18"  # 使用するモデルを指定
OPENAI_PARAMS = {
    "temperature": 0.7,     # 出力の多様性（0.0-2.0）
    # "max_tokens": 2000,      # 最大出力トークン数
    "top_p": 1.0,          # 出力のランダム性
    "frequency_penalty": 0, # 単語の重複を減らす（-2.0-2.0）
    "presence_penalty": 0   # 新しいトピックの導入（-2.0-2.0）
}

# アプリケーション設定
DEFAULT_DAYS_BACK = 7         # デフォルトの検索対象期間（日数）
DEFAULT_MAX_RESULTS = 10      # デフォルトの検索結果最大件数
MAX_DAYS_LIMIT = 30          # 検索対象期間の最大値
MIN_DAYS_LIMIT = 1           # 検索対象期間の最小値
MAX_RESULTS_LIMIT = 10       # 検索結果件数の最大値
MIN_RESULTS_LIMIT = 1        # 検索結果件数の最小値

# タイムゾーンとスケジュール設定
TIMEZONE = "Asia/Tokyo"
SCHEDULE_TIMES = [
    "09:00",
    "15:00",
    "21:00",
]

# PDF処理設定
PDF_DOWNLOAD_TIMEOUT = 10    # PDFダウンロードのタイムアウト（秒）
PDF_MAX_PAGES = 50          # 処理する最大ページ数

# ログ設定
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = 'INFO'

# エラーハンドリング設定
MAX_RETRIES = 3             # APIリクエストの最大リトライ回数
RETRY_DELAY = 1             # リトライ間の待機時間（秒）
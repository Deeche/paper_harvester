# Paper Harvester 🤖📚

最新の研究論文を自動収集・要約するSlackボット

## 概要 📋

Paper Harvesterは、研究者やエンジニアのための高度な論文管理・共有ツールです。arXivから最新の研究論文を自動的に収集し、OpenAI GPTを活用して詳細な要約を生成します。Slackを通じてチーム全体で最新の研究動向を効率的に把握することができます。

### なぜPaper Harvesterが必要か？

- 📚 日々大量に公開される研究論文をキャッチアップするのが困難
- 🕒 論文の内容を理解するのに時間がかかる
- 👥 チーム内での研究知見の共有が非効率
- 🔍 興味のある研究分野の最新動向を追跡するのが大変

これらの課題を、Paper Harvesterは自動化とAIの力で解決します。

## 主な機能 🌟

### 1. 論文検索・収集機能
- 🔍 arXivからのキーワードベースの論文検索
- 📅 設定可能な検索期間（1-30日）
- 🎯 複数キーワードの同時監視
- 🔄 重複論文の自動フィルタリング

### 2. AI要約機能
- 🤖 GPT-4による高度な論文要約生成
- 📊 研究の目的、手法、結果を構造化して提示
- 💡 技術的なポイントの抽出
- 🔮 将来の展望や課題の分析

### 3. Slack連携機能
- ⏰ 定期的な新着論文の自動通知（9:00, 15:00, 21:00）
- 👍 論文への興味表明ボタン
- 💬 スレッドでのディスカッション機能
- 📖 アブストラクトの表示/非表示切り替え

### 4. カスタマイズ機能
- ⚙️ 検索期間のカスタマイズ
- 📈 検索結果数の調整
- 🕐 通知スケジュールの設定
- 🎨 要約フォーマットの調整

## セットアップガイド 🛠️

### システム要件

- Python 3.7以上
- SQLite3
- インターネット接続
- Slack Workspace管理者権限
- OpenAI APIアカウントとキー

### 1. 事前準備

#### Slackアプリの設定
1. [Slack API](https://api.slack.com/apps)にアクセス
2. 「Create New App」→「From scratch」を選択
3. 必要な権限を付与:
   - chat:write
   - commands
   - channels:history
   - channels:read
   - channels:join

#### OpenAI APIの準備
1. [OpenAI](https://openai.com/)でアカウント作成
2. APIキーを生成
3. 利用制限と課金設定を確認

### 2. インストール手順

1. リポジトリのクローン
```bash
git clone https://github.com/yourusername/paper_harvester.git
cd paper_harvester
```

2. 仮想環境の作成（推奨）
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# または
.\venv\Scripts\activate  # Windows
```

3. 依存パッケージのインストール
```bash
pip install -r requirements.txt
```

### 3. 環境設定

1. 環境変数の設定
`.env`ファイルを作成し、以下の内容を設定：
```
SLACK_BOT_TOKEN=xoxb-your-bot-token    # Slackボットトークン
SLACK_APP_TOKEN=xapp-your-app-token    # Slackアプリトークン
OPENAI_API_KEY=your-openai-api-key     # OpenAI APIキー
```

2. データベースの初期化
```bash
python main.py
```

## Slackコマンド一覧 💻

### 基本コマンド
- `/paper_subscribe [キーワード]`
  - 論文検索キーワードを登録
  - 例: `/paper_subscribe "machine learning"`

- `/paper_check_now`
  - 即時に論文をチェック
  - 登録されているすべてのキーワードで検索実行

- `/paper_set_days [日数]`
  - 検索対象期間を設定
  - 有効範囲: 1-30日
  - 例: `/paper_set_days 7`

- `/paper_settings`
  - 現在の設定を表示
  - キーワード一覧
  - 検索期間
  - 通知設定

### 応用コマンド
- `/paper_unsubscribe [キーワード]`
  - 登録キーワードの削除
  - 例: `/paper_unsubscribe "machine learning"`

- `/paper_list`
  - 登録済みキーワード一覧の表示

## 設定カスタマイズ ⚙️

`config.py`で以下の設定をカスタマイズできます：

### 検索設定
```python
DEFAULT_DAYS_BACK = 7         # デフォルトの検索対象期間
DEFAULT_MAX_RESULTS = 10      # デフォルトの検索結果最大件数
MAX_DAYS_LIMIT = 30          # 検索対象期間の最大値
MIN_DAYS_LIMIT = 1           # 検索対象期間の最小値
```

### スケジュール設定
```python
SCHEDULE_TIMES = [
    "09:00",
    "15:00",
    "21:00"
]
```

### OpenAI設定
```python
OPENAI_MODEL = "gpt-4"
OPENAI_PARAMS = {
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0,
    "presence_penalty": 0
}
```

### PDF処理設定
```python
PDF_DOWNLOAD_TIMEOUT = 10    # ダウンロードタイムアウト（秒）
PDF_MAX_PAGES = 50          # 処理する最大ページ数
```

## アーキテクチャ詳細 🏗️

### ディレクトリ構造
```
paper_harvester/
├── main.py                 # エントリーポイント
├── config.py              # 設定ファイル
├── services/              # 主要サービス
│   ├── arxiv.py          # arXiv API連携
│   ├── openai_service.py # OpenAI API連携
│   ├── slack_service.py  # Slack API連携
│   └── scheduler.py      # 定期実行管理
├── handlers/              # イベントハンドラ
│   ├── command_handlers.py  # Slackコマンド処理
│   └── action_handlers.py   # ボタンアクション処理
├── models/               # データモデル
│   └── database.py      # SQLiteモデル定義
└── utils/               # ユーティリティ
    └── message_builder.py  # メッセージ整形
```

### データベース構造

#### Channelテーブル
- チャンネルID
- チャンネル名
- 作成日時
- 更新日時

#### Keywordテーブル
- キーワード
- チャンネルID（外部キー）
- 作成日時

#### ChannelConfigテーブル
- チャンネルID（外部キー）
- 検索対象期間
- 最大結果件数
- 更新日時

#### Paperテーブル
- 論文ID
- タイトル
- 著者
- アブストラクト
- URL
- 公開日
- 処理日時

## パフォーマンスと制限事項 ⚠️

### API制限
- OpenAI API
  - レートリミット: モデルによって異なる
  - コスト: トークン数に応じた課金
  - 推奨: 使用量の監視と予算設定

- arXiv API
  - リクエスト間隔: 3秒以上
  - 1回あたりの最大結果数: 100件

### システム制限
- PDF処理
  - 最大ページ数: 50ページ
  - タイムアウト: 10秒
  - 対応フォーマット: PDF

- データベース
  - 使用DB: SQLite
  - 推奨最大キーワード数: チャンネルあたり10個
  - 保持期間: 設定なし（手動クリーンアップ）

## トラブルシューティング 🔧

### よくある問題と解決方法

1. ボットが応答しない
   - Slackトークンの確認
   - ボットのオンライン状態確認
   - ログの確認

2. 論文が取得できない
   - キーワードの確認
   - 検索期間の確認
   - arXiv APIの状態確認

3. 要約が生成されない
   - OpenAI APIキーの確認
   - クレジット残高の確認
   - エラーログの確認

## ライセンス 📜

MIT License

Copyright (c) 2023 Your Name

## 貢献とサポート 🤝

### 貢献方法
1. Issueの作成
   - バグ報告
   - 機能リクエスト
   - 改善提案

2. プルリクエスト
   - コーディング規約の遵守
   - テストの追加
   - ドキュメントの更新

### サポート
- GitHubのIssueにて受付
- 重要な更新は[Releases](https://github.com/yourusername/paper_harvester/releases)をご確認ください

## 更新履歴 📝

### Version 1.0.0
- 初回リリース
- 基本機能の実装
- Slack連携機能の実装
- AI要約機能の実装





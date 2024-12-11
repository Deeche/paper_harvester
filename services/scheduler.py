# paper_harvester/services/scheduler.py

import schedule
import time
import threading
import pytz
from datetime import datetime
from typing import Optional
from config import SessionLocal, TIMEZONE, SCHEDULE_TIMES
from models.database import Channel
from services.arxiv import ArxivService

class SchedulerService:
    def __init__(self, slack_service):
        """スケジューラーサービスの初期化"""
        self.slack_service = slack_service
        self.timezone = pytz.timezone(TIMEZONE)
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()

    def check_new_papers(self):
        """全チャンネルの新着論文をチェック"""
        current_time = datetime.now(self.timezone)
        print(f"\n=== Starting paper check at {current_time.strftime('%Y-%m-%d %H:%M:%S %Z')} ===")
        
        db = SessionLocal()
        try:
            # チャンネル取得
            channels = db.query(Channel).all()
            print(f"Found {len(channels)} channels to check")
            
            for channel in channels:
                print(f"\nChecking channel: {channel.name} (ID: {channel.slack_channel_id})")
                
                if not channel.keywords:
                    print("No keywords set for this channel, skipping...")
                    continue
                
                print(f"Keywords for this channel: {[k.word for k in channel.keywords]}")
                
                for keyword in channel.keywords:
                    if not self._running:
                        print("Scheduler stopping, interrupting paper check")
                        return
                    
                    print(f"\nSearching papers for keyword: {keyword.word}")
                    try:
                        papers = ArxivService.fetch_and_process_papers(
                            db,
                            keyword.word,
                            channel.slack_channel_id
                        )
                        
                        if papers:
                            print(f"Found {len(papers)} new papers for keyword '{keyword.word}'")
                            for paper in papers:
                                try:
                                    print(f"Sending notification for paper: {paper.title}")
                                    with self._lock:
                                        self.slack_service.send_paper_message(
                                            channel.slack_channel_id,
                                            paper,
                                            keyword.word
                                        )
                                    print("Notification sent successfully")
                                except Exception as e:
                                    print(f"Error sending notification for paper {paper.title}: {e}")
                                    continue
                        else:
                            print(f"No new papers found for keyword '{keyword.word}'")
                    
                    except Exception as e:
                        print(f"Error processing keyword {keyword.word}: {e}")
                        continue
            
            print(f"\n=== Completed paper check at {datetime.now(self.timezone).strftime('%Y-%m-%d %H:%M:%S %Z')} ===\n")
        
        except Exception as e:
            print(f"Error in scheduled check: {e}")
            import traceback
            print(traceback.format_exc())
        finally:
            db.close()

    def start(self):
        """スケジューラーの開始"""
        if self._running:
            print("Scheduler is already running")
            return
        
        print("\n=== Initializing Scheduler ===")
        self._running = True
        
        # 設定された全ての時刻でスケジュール実行を設定
        for schedule_time in SCHEDULE_TIMES:
            schedule.every().day.at(schedule_time).do(self.check_new_papers)
            print(f"📅 Scheduled paper check at {schedule_time} {TIMEZONE}")
        
        # 次回の実行時刻を表示
        next_run = schedule.next_run()
        if next_run:
            next_run_local = pytz.utc.localize(next_run).astimezone(self.timezone)
            print(f"Next check scheduled for: {next_run_local.strftime('%Y-%m-%d %H:%M:%S %Z')}")
        
        def run_scheduler():
            """スケジューラーのメインループ"""
            while self._running:
                try:
                    schedule.run_pending()
                    time.sleep(1)
                except Exception as e:
                    print(f"Error in scheduler loop: {e}")
                    time.sleep(5)  # エラー時は少し長めに待機
        
        # 別スレッドでスケジューラーを実行
        self._thread = threading.Thread(target=run_scheduler, daemon=True)
        self._thread.start()
        print("=== Scheduler thread started ===\n")
        
        # 初回の実行
        print("\n=== Running initial paper check ===")
        self.check_new_papers()

    def stop(self):
        """スケジューラーの停止"""
        print("\n=== Stopping Scheduler ===")
        self._running = False
        if self._thread:
            self._thread.join(timeout=30)  # 最大30秒待機
            if self._thread.is_alive():
                print("Warning: Scheduler thread did not stop gracefully")
            else:
                print("Scheduler stopped successfully")
        schedule.clear()
        print("=== Scheduler shutdown complete ===\n")

    @property
    def is_running(self) -> bool:
        """スケジューラーの実行状態を取得"""
        return self._running and (self._thread and self._thread.is_alive())
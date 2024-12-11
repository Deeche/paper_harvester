# paper_harvester/services/arxiv.py

import arxiv
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import pytz
from models.database import Paper, Channel
from config import DEFAULT_DAYS_BACK, DEFAULT_MAX_RESULTS
from services.paper_processor import PaperProcessor
from .openai_service import generate_summary
import time
from sqlalchemy.orm import joinedload

class ArxivService:
    @classmethod
    def search_papers(cls, keyword: str, days_back: int = 2, max_results: int = 20):
        """arXivから論文を検索"""
        try:
            end_date = datetime.now(pytz.UTC)
            start_date = end_date - timedelta(days=days_back)
            
            print(f"\nSearching papers for keyword '{keyword}'")
            print(f"Date range: {start_date.strftime('%Y-%m-%d %H:%M:%S UTC')} to {end_date.strftime('%Y-%m-%d %H:%M:%S UTC')}")
            
            # 期間内の論文を確実に取得するため、より多くの論文を取得
            search_max_results = max_results * 3  # 余裕を持って取得
            
            query = arxiv.Search(
                query=f'all:"{keyword}"',
                max_results=search_max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate,
                sort_order=arxiv.SortOrder.Descending
            )
            
            papers = []
            print("Fetching results from arXiv...")
            
            for result in query.results():
                print(f"Checking paper: {result.title} (published: {result.published})")
                if start_date <= result.published <= end_date:
                    paper_info = {
                        'arxiv_id': result.entry_id.split('/')[-1],
                        'title': result.title,
                        'authors': ', '.join([author.name for author in result.authors]),
                        'abstract': result.summary,
                        'url': result.pdf_url,
                        'published_date': result.published
                    }
                    papers.append(paper_info)
                    print(f"📝 Found matching paper: {paper_info['title']}")
                else:
                    print(f"❌ Skipped paper (out of date range): {result.title}")
            
            print(f"Found {len(papers)} papers within date range")
            return papers
            
        except Exception as e:
            print(f"Error searching papers: {e}")
            import traceback
            print(traceback.format_exc())
            return []

    @classmethod
    def fetch_and_process_papers(cls, db, keyword, channel_id):
        """論文を取得して処理"""
        try:
            channel = db.query(Channel).filter_by(slack_channel_id=channel_id).first()
            days_back = channel.config.days_back if channel and channel.config else DEFAULT_DAYS_BACK
            max_results = channel.config.max_results if channel and channel.config else DEFAULT_MAX_RESULTS
            
            print(f"\nProcessing papers for keyword: {keyword} in channel: {channel_id}")
            print(f"Search parameters - days_back: {days_back}, max_results: {max_results}")
            
            papers = ArxivService.search_papers(keyword, days_back, max_results)
            if not papers:
                print("ℹ️ No papers found")
                return []
            
            new_papers = []
            print(f"\nChecking {len(papers)} papers for duplicates...")
            
            for paper_info in papers:
                existing_paper = db.query(Paper).filter_by(
                    arxiv_id=paper_info['arxiv_id']
                ).first()
                
                if not existing_paper:
                    print(f"✨ New paper found: {paper_info['title']}")
                    paper = Paper(
                        arxiv_id=paper_info['arxiv_id'],
                        title=paper_info['title'],
                        authors=paper_info['authors'],
                        abstract=paper_info['abstract'],
                        url=paper_info['url'],
                        published_date=paper_info['published_date']
                    )
                    db.add(paper)
                    new_papers.append(paper)
                    
                    if len(new_papers) >= max_results:
                        break
                else:
                    print(f"📎 Paper already exists: {paper_info['title']}")
            
            if new_papers:
                db.commit()
                print(f"✅ Successfully processed {len(new_papers)} new papers")
            else:
                print("ℹ️ No new papers found")
            
            return new_papers
            
        except Exception as e:
            print(f"❌ Error in fetch_and_process_papers: {e}")
            import traceback
            print(traceback.format_exc())
            return []

    @staticmethod
    def get_paper_by_id(db, arxiv_id: str) -> Optional[Paper]:
        """指定したarXiv IDの論文を取得"""
        return db.query(Paper).filter_by(arxiv_id=arxiv_id).first()

    @staticmethod
    def get_recent_papers(db, days: int = 7) -> List[Paper]:
        """最近の論文を取得"""
        cutoff_date = datetime.now(pytz.UTC) - timedelta(days=days)
        return db.query(Paper)\
            .filter(Paper.published_date >= cutoff_date)\
            .order_by(Paper.published_date.desc())\
            .all()
# paper_harvester/services/paper_processor.py

import arxiv
import PyPDF2
import io
import requests
from urllib.parse import urlparse
from typing import Dict, Any, Optional
from config import PDF_DOWNLOAD_TIMEOUT, PDF_MAX_PAGES, DEFAULT_DAYS_BACK, DEFAULT_MAX_RESULTS
import time
from models.database import Channel, Keyword, ChannelConfig

class PaperProcessor:
    @staticmethod
    def is_arxiv_paper(url: str) -> bool:
        """URLがarXivのものかチェック"""
        return 'arxiv.org' in url.lower()

    @staticmethod
    def check_paper_accessibility(url: str) -> bool:
        """論文のアクセス可能性をチェック"""
        try:
            response = requests.head(url, timeout=5)
            return response.status_code == 200
        except Exception as e:
            print(f"Error checking accessibility for {url}: {e}")
            return False

    @staticmethod
    def extract_text_from_pdf(pdf_content: bytes) -> Optional[str]:
        """PDFから本文を抽出"""
        try:
            reader = PyPDF2.PdfReader(io.BytesIO(pdf_content))
            
            # ページ数制限の確認
            num_pages = len(reader.pages)
            if num_pages > PDF_MAX_PAGES:
                print(f"Warning: PDF has {num_pages} pages, limiting to {PDF_MAX_PAGES}")
                num_pages = PDF_MAX_PAGES
            
            # テキスト抽出
            full_text = []
            for i in range(num_pages):
                try:
                    page = reader.pages[i]
                    text = page.extract_text()
                    if text.strip():  # 空のページをスキップ
                        full_text.append(text)
                except Exception as e:
                    print(f"Error extracting text from page {i}: {e}")
                    continue
            
            return "\n".join(full_text) if full_text else None
            
        except Exception as e:
            print(f"Error processing PDF: {e}")
            return None

    @classmethod
    def get_paper_content(cls, arxiv_id: str) -> Optional[Dict[str, Any]]:
        """論文の内容を取得（arXivの論文のみ）"""
        try:
            print(f"Fetching paper content for arXiv ID: {arxiv_id}")
            
            # arXivから論文情報を取得
            client = arxiv.Client()
            search = arxiv.Search(id_list=[arxiv_id])
            paper = next(client.results(search))
            
            # arXivの論文かチェック
            if not cls.is_arxiv_paper(paper.pdf_url):
                print(f"Skipping non-arXiv paper: {paper.title}")
                return None
            
            # アクセス可能性をチェック
            if not cls.check_paper_accessibility(paper.pdf_url):
                print(f"Paper is not accessible: {paper.title}")
                return {
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'abstract': paper.summary,
                    'full_text': None,
                    'pdf_url': paper.pdf_url,
                    'source': 'arxiv_abstract_only'
                }
            
            try:
                # PDFをダウンロード
                print("Downloading PDF...")
                response = requests.get(paper.pdf_url, timeout=PDF_DOWNLOAD_TIMEOUT)
                if response.status_code != 200:
                    raise Exception(f"Failed to download PDF: {response.status_code}")
                
                # テキスト抽出
                print("Extracting text from PDF...")
                full_text = cls.extract_text_from_pdf(response.content)
                
                if full_text:
                    print("Successfully extracted text from PDF")
                    source_type = 'arxiv_full_text'
                else:
                    print("Failed to extract text from PDF, using abstract only")
                    full_text = paper.summary
                    source_type = 'arxiv_abstract_only'
                
                return {
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'abstract': paper.summary,
                    'full_text': full_text,
                    'pdf_url': paper.pdf_url,
                    'source': source_type
                }
                
            except Exception as e:
                print(f"Error processing PDF for {paper.title}: {e}")
                return {
                    'title': paper.title,
                    'authors': [author.name for author in paper.authors],
                    'abstract': paper.summary,
                    'full_text': paper.summary,
                    'pdf_url': paper.pdf_url,
                    'source': 'arxiv_abstract_only'
                }
                
        except Exception as e:
            print(f"Error accessing paper: {e}")
            import traceback
            print(traceback.format_exc())
            return None

    @staticmethod
    def clean_text(text: str) -> str:
        """テキストのクリーニング"""
        if not text:
            return ""
        
        # 基本的なクリーニング
        text = text.replace('\x00', '')  # nullバイトの除去
        text = ' '.join(text.split())    # 余分な空白の正規化
        
        return text.strip()

    @staticmethod
    def setup_keywords(db, channel_id, keyword_text):
        """キーワードを設定"""
        try:
            # チャンネルの取得または作成
            channel = db.query(Channel).filter_by(slack_channel_id=channel_id).first()
            if not channel:
                print(f"Creating new channel: {channel_id}")
                channel = Channel(
                    slack_channel_id=channel_id,
                    name=channel_id
                )
                db.add(channel)
                channel.config = ChannelConfig(
                    days_back=DEFAULT_DAYS_BACK,
                    max_results=DEFAULT_MAX_RESULTS
                )
                db.commit()
            
            # キーワードの取得または作成
            keyword = db.query(Keyword).filter_by(word=keyword_text).first()
            if not keyword:
                print(f"Creating new keyword: {keyword_text}")
                keyword = Keyword(word=keyword_text)
                db.add(keyword)
            
            # キーワードをチャンネルに関連付け
            if keyword not in channel.keywords:
                channel.keywords.append(keyword)
                print(f"Adding keyword '{keyword_text}' to channel")
            
            db.commit()
            print("Changes committed successfully")
            return f"キーワード「{keyword_text}」を登録しました。"
            
        except Exception as e:
            print(f"Error in setup_keywords: {e}")
            import traceback
            print(traceback.format_exc())
            return None
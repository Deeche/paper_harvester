# paper_harvester/models/database.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Table, Text
from sqlalchemy.orm import relationship, declarative_base
from datetime import datetime
import pytz

Base = declarative_base()

# 中間テーブル
channel_keywords = Table(
    'channel_keywords',
    Base.metadata,
    Column('channel_id', Integer, ForeignKey('channels.id', ondelete='CASCADE'), primary_key=True),
    Column('keyword_id', Integer, ForeignKey('keywords.id', ondelete='CASCADE'), primary_key=True)
)

class Channel(Base):
    __tablename__ = 'channels'
    
    id = Column(Integer, primary_key=True)
    slack_channel_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    
    keywords = relationship(
        'Keyword',
        secondary=channel_keywords,
        back_populates='channels',
        lazy='joined',
        cascade="all, delete"
    )
    config = relationship(
        'ChannelConfig',
        backref='channel',
        uselist=False,
        lazy='joined',
        cascade="all, delete-orphan"
    )

class Keyword(Base):
    __tablename__ = 'keywords'
    
    id = Column(Integer, primary_key=True)
    word = Column(String, unique=True, nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    
    channels = relationship(
        'Channel',
        secondary=channel_keywords,
        back_populates='keywords',
        lazy='joined'
    )

class ChannelConfig(Base):
    __tablename__ = 'channel_configs'
    
    id = Column(Integer, primary_key=True)
    channel_id = Column(Integer, ForeignKey('channels.id', ondelete='CASCADE'), nullable=False)
    days_back = Column(Integer, default=2, nullable=False)
    max_results = Column(Integer, default=3, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    updated_at = Column(DateTime(timezone=True), 
                       default=lambda: datetime.now(pytz.UTC), 
                       onupdate=lambda: datetime.now(pytz.UTC))

class Paper(Base):
    __tablename__ = 'papers'
    
    id = Column(Integer, primary_key=True)
    arxiv_id = Column(String, unique=True, nullable=False, index=True)
    title = Column(String, nullable=False)
    authors = Column(String, nullable=False)
    abstract = Column(Text)
    full_text = Column(Text)
    url = Column(String, nullable=False)
    summary = Column(Text)
    source_type = Column(String)  # 'arxiv' or 'arxiv_abstract_only'
    published_date = Column(DateTime(timezone=True), nullable=False, index=True)
    notified_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC))
    error_count = Column(Integer, default=0)  # 処理エラーの回数
    last_error = Column(String)  # 最後に発生したエラーメッセージ

    def __repr__(self):
        return f"<Paper(title='{self.title}', arxiv_id='{self.arxiv_id}')>"
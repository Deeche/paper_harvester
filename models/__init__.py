# paper_harvester/models/__init__.py
from .database import Base, Channel, Keyword, Paper, ChannelConfig, channel_keywords

__all__ = [
    'Base',
    'Channel',
    'Keyword',
    'Paper',
    'ChannelConfig',
    'channel_keywords'
]
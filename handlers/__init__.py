# paper_harvester/handlers/__init__.py
from handlers.command_handlers import setup_command_handlers
from handlers.action_handlers import setup_action_handlers

__all__ = [
    'setup_command_handlers',
    'setup_action_handlers'
]
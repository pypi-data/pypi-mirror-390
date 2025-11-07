"""
Trello API client wrapper
"""

from trello import TrelloClient as PyTrelloClient
from .config import load_config


class TrelloClient:
    """Wrapper around py-trello client with error handling"""

    _instance = None

    def __new__(cls):
        """Singleton pattern to reuse client instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize Trello client with credentials from config"""
        if self._initialized:
            return

        config = load_config()
        self.client = PyTrelloClient(
            api_key=config['api_key'],
            token=config['token']
        )
        self._initialized = True

    def get_board(self, board_id):
        """Get board by ID"""
        try:
            return self.client.get_board(board_id)
        except Exception as e:
            raise Exception(f"Failed to get board {board_id}: {str(e)}")

    def get_list(self, list_id):
        """Get list by ID"""
        try:
            return self.client.get_list(list_id)
        except Exception as e:
            raise Exception(f"Failed to get list {list_id}: {str(e)}")

    def get_card(self, card_id):
        """Get card by ID"""
        try:
            return self.client.get_card(card_id)
        except Exception as e:
            raise Exception(f"Failed to get card {card_id}: {str(e)}")

    def list_boards(self):
        """List all boards"""
        try:
            return self.client.list_boards()
        except Exception as e:
            raise Exception(f"Failed to list boards: {str(e)}")

    def add_board(self, name):
        """Create new board"""
        try:
            return self.client.add_board(name)
        except Exception as e:
            raise Exception(f"Failed to create board '{name}': {str(e)}")


def get_client():
    """Get singleton TrelloClient instance"""
    return TrelloClient()

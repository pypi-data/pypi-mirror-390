"""
Board-related commands
"""

from ..client import get_client
from ..utils import format_table


def cmd_boards():
    """List all boards"""
    client = get_client()
    boards = client.list_boards()

    if not boards:
        print("No boards found")
        return

    format_table(
        boards,
        columns=[("ID", "id"), ("Name", "name")],
        widths={"ID": 25, "Name": 40}
    )


def cmd_create_board(board_name):
    """Create a new board"""
    client = get_client()
    new_board = client.add_board(board_name)

    print(f"✅ Board created: {new_board.name}")
    print(f"   ID: {new_board.id}")
    print(f"   URL: {new_board.url}")

"""
Label-related commands
"""

from ..client import get_client
from ..utils import validate_color


def cmd_add_label(card_id, color, name=""):
    """Add a label to a card"""
    client = get_client()
    card = client.get_card(card_id)

    # Validate color
    validate_color(color)

    # Get board and find or create label
    board = card.board
    label = None

    for l in board.get_labels():
        if l.name == name and l.color == color:
            label = l
            break

    if not label:
        label = board.add_label(name, color)

    card.add_label(label)
    print(f"✅ Label '{name}' ({color}) added to card {card.name}")


def cmd_remove_label(card_id, label_identifier):
    """
    Remove a label from a card

    Args:
        card_id: Card ID
        label_identifier: Label name, color, or ID
    """
    client = get_client()
    card = client.get_card(card_id)

    # Find the label to remove
    label_to_remove = None

    for label in card.labels:
        # Match by ID, name, or color
        if (label.id == label_identifier or
            label.name == label_identifier or
            label.color == label_identifier):
            label_to_remove = label
            break

    if not label_to_remove:
        print(f"❌ Label '{label_identifier}' not found on card")
        print(f"\nAvailable labels on this card:")
        if card.labels:
            for l in card.labels:
                display_name = l.name or f"[{l.color}]"
                print(f"  • {display_name} ({l.color}) - ID: {l.id}")
        else:
            print("  (no labels)")
        return

    card.remove_label(label_to_remove)
    display_name = label_to_remove.name or f"[{label_to_remove.color}]"
    print(f"✅ Label '{display_name}' ({label_to_remove.color}) removed from card {card.name}")


def cmd_delete_label(board_id, label_identifier):
    """
    Delete a label from the board entirely

    Args:
        board_id: Board ID
        label_identifier: Label name, color, or ID
    """
    client = get_client()
    board = client.get_board(board_id)

    # Find the label
    board_labels = board.get_labels()
    label_to_delete = None

    for label in board_labels:
        if (label.id == label_identifier or
            label.name == label_identifier or
            label.color == label_identifier):
            label_to_delete = label
            break

    if not label_to_delete:
        print(f"❌ Label '{label_identifier}' not found on board")
        print(f"\nAvailable labels:")
        for l in board_labels[:20]:
            display_name = l.name or f"[unnamed {l.color}]"
            print(f"  • {display_name:30} │ {l.color:10} │ ID: {l.id}")
        if len(board_labels) > 20:
            print(f"  ... and {len(board_labels) - 20} more")
        return

    # Delete the label using REST API
    display_name = label_to_delete.name or f"[unnamed {label_to_delete.color}]"

    # Use the py-trello client's fetch_json method to make DELETE request
    client.client.fetch_json(
        f'/labels/{label_to_delete.id}',
        http_method='DELETE'
    )

    print(f"✅ Label '{display_name}' ({label_to_delete.color}) deleted from board")
    print(f"   This label has been removed from all cards")


def cmd_rename_label(board_id, label_identifier, new_name):
    """
    Rename a label on the board

    Args:
        board_id: Board ID
        label_identifier: Current label name, color, or ID
        new_name: New name for the label
    """
    client = get_client()
    board = client.get_board(board_id)

    # Find the label
    board_labels = board.get_labels()
    label_to_rename = None

    for label in board_labels:
        if (label.id == label_identifier or
            label.name == label_identifier or
            label.color == label_identifier):
            label_to_rename = label
            break

    if not label_to_rename:
        print(f"❌ Label '{label_identifier}' not found on board")
        print(f"\nAvailable labels:")
        for l in board_labels[:20]:
            display_name = l.name or f"[unnamed {l.color}]"
            print(f"  • {display_name:30} │ {l.color:10} │ ID: {l.id}")
        if len(board_labels) > 20:
            print(f"  ... and {len(board_labels) - 20} more")
        return

    old_name = label_to_rename.name or f"[unnamed {label_to_rename.color}]"

    # Rename the label using REST API
    client.client.fetch_json(
        f'/labels/{label_to_rename.id}',
        http_method='PUT',
        post_args={'name': new_name}
    )

    print(f"✅ Label renamed:")
    print(f"   Old: {old_name} ({label_to_rename.color})")
    print(f"   New: {new_name} ({label_to_rename.color})")
    print(f"   ID:  {label_to_rename.id}")
    print(f"   This change affects all cards with this label")

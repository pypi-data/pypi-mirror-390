"""
Card-related commands
"""

from ..client import get_client
from ..utils import format_table, format_card_details, validate_date
from ..validators import (
    card_creation_validator,
    card_movement_validator,
    ValidationError,
    get_config
)


def cmd_cards(list_id):
    """List all cards in a list"""
    client = get_client()
    lst = client.get_list(list_id)
    cards = lst.list_cards()

    if not cards:
        print(f"No cards found in list {lst.name}")
        return

    format_table(
        cards,
        columns=[("ID", "id"), ("Name", "name")],
        widths={"ID": 25, "Name": 40}
    )


def cmd_add_card(list_id, title, description=""):
    """Add a new card to a list"""
    # Detect common argument order mistake
    # Case 1: Long string followed by 24-char hex (likely title then list_id)
    if (len(list_id) > 24 and len(title) == 24 and
        all(c in '0123456789abcdef' for c in title.lower())):
        print("❌ ERROR: Arguments appear to be in wrong order")
        print(f"   You provided: \"{list_id[:50]}...\" {title}")
        print(f"   Expected: <list_id> \"<title>\"")
        print()
        print("💡 Correct usage:")
        print(f"   trello add-card {title} \"{list_id[:40]}...\" --description \"...\"")
        print()
        print("💡 Run 'trello help' to see detailed usage and examples")
        print()
        return

    # Case 2: Title looks like card format but list_id doesn't look like hex ID
    if (list_id.startswith(('FI-', 'PROJ-')) and ':' in list_id and
        len(title) == 24 and all(c in '0123456789abcdef' for c in title.lower())):
        print("❌ ERROR: Arguments are in wrong order")
        print(f"   You provided: \"{list_id}\" {title}")
        print(f"   Expected: <list_id> \"<title>\"")
        print()
        print("💡 Correct usage:")
        print(f"   trello add-card {title} \"{list_id}\" --description \"...\"")
        print()
        print("💡 Run 'trello help' to see detailed usage and examples")
        print()
        return

    # Validate list_id format (24 hex chars)
    if len(list_id) != 24 or not all(c in '0123456789abcdef' for c in list_id.lower()):
        print("❌ ERROR: Invalid list_id format")
        print(f"   Provided: '{list_id}'")
        print(f"   Expected: 24-character hexadecimal ID")
        print()
        print("💡 To find list IDs:")
        print("   trello lists <board_id>")
        print("   trello board-ids <board_id>")
        print()
        print("💡 Run 'trello help' to see detailed usage and examples")
        print()
        return

    # Validate if validation system is enabled
    config = get_config()
    if config.is_enabled():
        try:
            card_creation_validator.validate(
                title=title,
                description=description
            )
        except ValidationError as e:
            print(f"\n{e.message}\n")
            if e.help_command:
                print(f"💡 Run '{e.help_command}' for more information\n")

            # Show relevant help section automatically
            print("=" * 70)
            print("📖 QUICK HELP FOR add-card:")
            print("=" * 70)
            print()
            print("CORRECT FORMAT:")
            print("  trello add-card <list_id> \"title\" --description \"description\"")
            print()
            print("ARGUMENTS:")
            print("  <list_id>      24-character hexadecimal list ID (NOT board_id)")
            print("  \"title\"        Card title (minimum 10 characters)")
            print("  --description  Card description (minimum 50 characters)")
            print()
            print("TO FIND list_id:")
            print("  trello lists <board_id>")
            print("  trello board-ids <board_id>")
            print()
            print("EXAMPLE:")
            print("  trello add-card 68fc01108ce7d8a2c22fa8e0 \\")
            print("    \"FI-FEAT-001: New Feature\" \\")
            print("    --description \"This is a detailed description that is at least 50 characters long\"")
            print()
            print("=" * 70)
            print()
            return

    try:
        client = get_client()
        lst = client.get_list(list_id)
        card = lst.add_card(name=title, desc=description)

        print(f"✅ Card created: {card.name}")
        print(f"   ID: {card.id}")
        print(f"   List: {lst.name}")
    except Exception as e:
        if "invalid id" in str(e).lower():
            print("❌ ERROR: Invalid list_id")
            print(f"   The ID '{list_id}' does not exist or is not a valid list")
            print()
            print("💡 To find the correct list_id:")
            print("   trello lists <board_id>")
            print("   trello board-overview <board_id>")
        else:
            print(f"❌ ERROR: {e}")
            print()
            print("💡 Run 'trello help' for usage information")
        return


def cmd_show_card(card_id):
    """Show detailed card information"""
    client = get_client()
    card = client.get_card(card_id)
    format_card_details(card)


def cmd_update_card(card_id, description):
    """Update card description"""
    client = get_client()
    card = client.get_card(card_id)
    card.set_description(description)

    print(f"✅ Updated description for: {card.name}")


def cmd_move_card(card_id, list_id, explicit_done=False):
    """Move card to another list"""
    client = get_client()
    card = client.get_card(card_id)
    target_list = client.get_list(list_id)

    # Validate if validation system is enabled
    config = get_config()
    if config.is_enabled():
        try:
            card_movement_validator.validate(
                card=card,
                target_list=target_list,
                explicit_done=explicit_done
            )
        except ValidationError as e:
            print(f"\n{e.message}\n")
            if e.help_command:
                print(f"💡 Run '{e.help_command}' for more information\n")
            return

    card.change_list(list_id)
    print(f"✅ Moved card '{card.name}' to list '{target_list.name}'")


def cmd_add_checklist(card_id, checklist_name):
    """Add a checklist to a card"""
    client = get_client()
    card = client.get_card(card_id)
    checklist = card.add_checklist(checklist_name, [])

    print(f"✅ Checklist '{checklist_name}' added to card {card.name}")


def cmd_add_checkitem(card_id, checklist_name, item_name):
    """Add an item to a checklist"""
    client = get_client()
    card = client.get_card(card_id)

    # Find or create checklist
    checklist = None
    for cl in card.checklists:
        if cl.name == checklist_name:
            checklist = cl
            break

    if not checklist:
        print(f"ℹ️  Checklist '{checklist_name}' not found. Creating it...")
        checklist = card.add_checklist(checklist_name, [])

    checklist.add_checklist_item(item_name)
    print(f"✅ Added '{item_name}' to checklist '{checklist_name}'")


def cmd_set_due(card_id, due_date):
    """Set due date for a card"""
    client = get_client()
    card = client.get_card(card_id)

    dt = validate_date(due_date)
    card.set_due(dt)

    print(f"✅ Set due date to {dt.strftime('%Y-%m-%d %H:%M')} for card {card.name}")


def cmd_add_comment(card_id, comment):
    """Add a comment to a card"""
    client = get_client()
    card = client.get_card(card_id)
    card.comment(comment)

    print(f"✅ Added comment to card {card.name}")


def cmd_delete_card(card_id):
    """Delete a card permanently"""
    client = get_client()
    card = client.get_card(card_id)
    card_name = card.name

    card.delete()
    print(f"✅ Card deleted: {card_name}")


def cmd_rename_card(card_id, new_name):
    """Rename a card (update title)"""
    client = get_client()
    card = client.get_card(card_id)
    old_name = card.name

    card.set_name(new_name)
    print(f"✅ Card renamed:")
    print(f"   Old: {old_name}")
    print(f"   New: {new_name}")
    print(f"   ID:  {card_id}")

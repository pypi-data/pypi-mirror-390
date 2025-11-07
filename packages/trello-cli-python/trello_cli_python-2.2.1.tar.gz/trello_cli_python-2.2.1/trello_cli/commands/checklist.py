"""
Checklist Commands - Mark individual checklist items as complete
Commands: check, uncheck, checklist-status

Smart commands that understand item-level progress and prevent fraud.
"""

from typing import Tuple, Optional
from ..client import get_client


def cmd_check(card_id: str, checklist_name: str, item_name: str, validate_fraud: bool = True):
    """
    Mark a checklist item as complete.

    Usage: trello check <card_id> "Checklist Name" "Item Name"

    With fraud validation: Requires card to have description + PR/commit reference
    to prevent fake completion.
    """
    client = get_client()
    card = client.get_card(card_id)

    if not card:
        print(f"❌ Card not found: {card_id}")
        return False

    # Find the checklist
    checklist = _find_checklist(card, checklist_name)
    if not checklist:
        print(f"❌ Checklist not found: {checklist_name}")
        print(f"   Available checklists: {[cl.name if hasattr(cl, 'name') else cl.get('name') for cl in card.checklists]}")
        return False

    # Find the item
    item = _find_item(checklist, item_name)
    if not item:
        print(f"❌ Item not found: {item_name}")
        items_list = checklist.get('items', []) if isinstance(checklist, dict) else (checklist.items if hasattr(checklist, 'items') else [])
        print(f"   Available items: {[it.get('name') if isinstance(it, dict) else it.name for it in items_list]}")
        return False

    # FRAUD CHECK: If completing last item, validate card integrity
    if validate_fraud:
        total, completed = _count_progress(checklist)
        is_last_item = (completed + 1 == total)  # This will be the last

        if is_last_item:
            valid, reason = _validate_card_completion(card)
            if not valid:
                print(f"❌ Cannot complete last item: {reason}")
                print(f"\n   Recommendations:")
                print(f"   • Add PR/commit reference to card description")
                print(f"   • Or add deployment notes")
                print(f"   • Or add explicit \"Completed: [date]\" with proof")
                return False

    # Mark as complete in Trello
    try:
        # Get the actual Checklist object from py-trello
        checklist_obj = None
        checklist_name_val = checklist.get('name', '') if isinstance(checklist, dict) else (checklist.name if hasattr(checklist, 'name') else '')

        for cl in card.checklists:
            cl_name = cl.get('name', '') if isinstance(cl, dict) else (cl.name if hasattr(cl, 'name') else '')
            if cl_name == checklist_name_val:
                checklist_obj = cl
                break

        if not checklist_obj:
            print(f"❌ Could not find checklist object: {checklist.get('name')}")
            return False

        # Mark item as complete using the correct method
        checklist_obj.set_checklist_item(item_name, True)

        # Show progress
        total, completed = _count_progress(checklist)
        new_completed = completed + 1
        completion_rate = (new_completed / total) * 100

        print(f"✅ Checked: {item_name}")
        print(f"   Progress: {new_completed}/{total} items ({completion_rate:.0f}%)")

        if new_completed == total:
            print(f"\n🎉 Checklist complete! Card is ready for Done.")

        return True

    except Exception as e:
        print(f"❌ Error updating Trello: {e}")
        return False


def cmd_uncheck(card_id: str, checklist_name: str, item_name: str):
    """
    Mark a checklist item as incomplete.

    Usage: trello uncheck <card_id> "Checklist Name" "Item Name"
    """
    client = get_client()
    card = client.get_card(card_id)

    if not card:
        print(f"❌ Card not found: {card_id}")
        return False

    # Find the checklist
    checklist = _find_checklist(card, checklist_name)
    if not checklist:
        print(f"❌ Checklist not found: {checklist_name}")
        return False

    # Find the item
    item = _find_item(checklist, item_name)
    if not item:
        print(f"❌ Item not found: {item_name}")
        return False

    # Mark as incomplete
    try:
        # Get the actual Checklist object from py-trello
        checklist_obj = None
        checklist_name_val = checklist.get('name', '') if isinstance(checklist, dict) else (checklist.name if hasattr(checklist, 'name') else '')

        for cl in card.checklists:
            cl_name = cl.get('name', '') if isinstance(cl, dict) else (cl.name if hasattr(cl, 'name') else '')
            if cl_name == checklist_name_val:
                checklist_obj = cl
                break

        if not checklist_obj:
            print(f"❌ Could not find checklist object: {checklist.get('name')}")
            return False

        # Mark item as incomplete using the correct method
        checklist_obj.set_checklist_item(item_name, False)

        total, completed = _count_progress(checklist)
        new_completed = completed - 1
        completion_rate = (new_completed / total) * 100 if total > 0 else 0

        print(f"↩️  Unchecked: {item_name}")
        print(f"   Progress: {new_completed}/{total} items ({completion_rate:.0f}%)")

        return True

    except Exception as e:
        print(f"❌ Error updating Trello: {e}")
        return False


def cmd_checklist_status(card_id: str):
    """
    Show detailed checklist progress for a card.

    Usage: trello checklist-status <card_id>
    """
    client = get_client()
    card = client.get_card(card_id)

    if not card:
        print(f"❌ Card not found: {card_id}")
        return False

    if not card.checklists:
        print(f"Card has no checklists")
        return True

    print(f"\n📋 CHECKLIST STATUS: {card.name}")
    print("=" * 80)

    for checklist in card.checklists:
        total, completed = _count_progress(checklist)
        completion_rate = (completed / total) * 100 if total > 0 else 0

        # Progress bar
        filled = int(completion_rate / 10)
        empty = 10 - filled
        bar = "█" * filled + "░" * empty

        print(f"\n{checklist.get('name')}")
        print(f"  {bar} {completed}/{total} ({completion_rate:.0f}%)")

        items = checklist.get('items', [])
        for item in items:
            state = "✅" if item.get('state') == 'complete' else "⭕"
            print(f"    {state} {item.get('name')}")

    print("\n" + "=" * 80)
    return True


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def _find_checklist(card, checklist_name: str):
    """Find checklist by name (case-insensitive partial match)."""
    name_lower = checklist_name.lower()

    for checklist in card.checklists:
        # Handle both dict and object formats from py-trello
        cl_name = checklist.get('name', '') if isinstance(checklist, dict) else (checklist.name if hasattr(checklist, 'name') else '')
        if name_lower in cl_name.lower():
            return checklist

    return None


def _find_item(checklist, item_name: str):
    """Find item by name (case-insensitive partial match)."""
    name_lower = item_name.lower()

    # Handle both dict and object formats from py-trello
    items = checklist.get('items', []) if isinstance(checklist, dict) else (checklist.items if hasattr(checklist, 'items') else [])

    for item in items:
        # Handle both dict and object item formats
        item_name_val = item.get('name', '') if isinstance(item, dict) else (item.name if hasattr(item, 'name') else '')
        if name_lower in item_name_val.lower():
            return item

    return None


def _count_progress(checklist) -> Tuple[int, int]:
    """
    Count total and completed items in checklist.
    Returns: (total, completed)
    """
    # Handle both dict and object formats from py-trello
    items = checklist.get('items', []) if isinstance(checklist, dict) else (checklist.items if hasattr(checklist, 'items') else [])

    total = len(items)
    completed = 0
    for item in items:
        # Handle both dict and object item formats
        state = item.get('state') if isinstance(item, dict) else (item.state if hasattr(item, 'state') else '')
        if state == 'complete':
            completed += 1

    return total, completed


def _validate_card_completion(card) -> Tuple[bool, str]:
    """
    Validate if card can be marked complete.
    Returns: (is_valid, reason_if_invalid)

    Rules:
    - Must have description (proof of work)
    - Must have PR/commit/deployment reference
    """
    desc = (card.description or "").lower()

    # Check for description
    if not desc or len(desc) < 20:
        return False, "Card needs description (proof of what was done)"

    # Check for execution evidence
    has_pr = "pr" in desc or "pull" in desc
    has_commit = "commit" in desc or "merge" in desc
    has_deploy = "deploy" in desc or "release" in desc or "shipped" in desc

    if not (has_pr or has_commit or has_deploy):
        return False, "Card needs PR/commit/deployment reference in description"

    return True, ""


def _format_item_name(name: str) -> str:
    """Format item name for display."""
    return name.strip()

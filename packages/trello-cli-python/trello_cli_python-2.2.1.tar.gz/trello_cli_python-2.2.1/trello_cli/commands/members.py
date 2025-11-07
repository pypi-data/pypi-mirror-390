"""
Member management commands
"""

import json
from pathlib import Path
from ..client import get_client


def get_current_user():
    """Get current user ID from config"""
    config_file = Path.home() / '.trello_cli_config.json'
    if not config_file.exists():
        return None

    try:
        with open(config_file) as f:
            config = json.load(f)
            return config.get('user_id')
    except:
        return None


def cmd_assign_card(card_id, member_identifier):
    """
    Assign a member to a card

    Args:
        card_id: Card ID
        member_identifier: Member username, name, or 'me'
    """
    client = get_client()
    card = client.get_card(card_id)
    board = card.board

    # Handle 'me' shortcut
    if member_identifier.lower() == 'me':
        user_id = get_current_user()
        if not user_id:
            print("❌ Cannot determine current user")
            print("   Run 'trello config' to set user_id")
            return
        member_identifier = user_id

    # Get board members
    board_members = board.get_members()

    # Find the member
    member_to_assign = None
    for member in board_members:
        if (member.id == member_identifier or
            member.username == member_identifier or
            member.full_name == member_identifier):
            member_to_assign = member
            break

    if not member_to_assign:
        print(f"❌ Member '{member_identifier}' not found on board")
        print(f"\nAvailable members:")
        for m in board_members[:20]:
            print(f"  • {m.full_name:25} (@{m.username}) - ID: {m.id}")
        if len(board_members) > 20:
            print(f"  ... and {len(board_members) - 20} more")
        return

    # Assign member
    card.add_member(member_to_assign)
    print(f"✅ Assigned {member_to_assign.full_name} (@{member_to_assign.username}) to card")
    print(f"   Card: {card.name}")
    print(f"   Member ID: {member_to_assign.id}")


def cmd_unassign_card(card_id, member_identifier):
    """
    Remove a member from a card

    Args:
        card_id: Card ID
        member_identifier: Member username, name, ID, or 'me'
    """
    client = get_client()
    card = client.get_card(card_id)

    # Handle 'me' shortcut
    if member_identifier.lower() == 'me':
        user_id = get_current_user()
        if not user_id:
            print("❌ Cannot determine current user")
            print("   Run 'trello config' to set user_id")
            return
        member_identifier = user_id

    # Get card members
    card_members = card.get_members()

    # Find the member
    member_to_remove = None
    for member in card_members:
        if (member.id == member_identifier or
            member.username == member_identifier or
            member.full_name == member_identifier):
            member_to_remove = member
            break

    if not member_to_remove:
        print(f"❌ Member '{member_identifier}' not assigned to this card")
        print(f"\nCurrently assigned members:")
        if card_members:
            for m in card_members:
                print(f"  • {m.full_name:25} (@{m.username}) - ID: {m.id}")
        else:
            print("  (no members assigned)")
        return

    # Remove member
    card.remove_member(member_to_remove)
    print(f"✅ Unassigned {member_to_remove.full_name} (@{member_to_remove.username}) from card")
    print(f"   Card: {card.name}")


def cmd_card_log(card_id, limit=50):
    """
    Show action history for a card

    Args:
        card_id: Card ID
        limit: Number of actions to show (default 50)
    """
    from datetime import datetime

    client = get_client()
    card = client.get_card(card_id)

    print(f"\n{'='*80}")
    print(f"CARD ACTION HISTORY - {card.name}")
    print(f"Card ID: {card_id}")
    print(f"{'='*80}\n")

    # Get actions
    actions = card.fetch_actions(action_filter='all', limit=limit)

    if not actions:
        print("No actions found for this card")
        return

    print(f"Showing last {len(actions)} action(s):\n")

    for action in actions:
        # Parse date
        try:
            date_str = action.get('date', '')
            if date_str:
                date = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                date_formatted = date.strftime('%Y-%m-%d %H:%M:%S')
            else:
                date_formatted = 'Unknown date'
        except:
            date_formatted = 'Unknown date'

        # Get member
        member_data = action.get('memberCreator', {})
        member_name = member_data.get('fullName', 'Unknown')
        member_username = member_data.get('username', '')

        # Get action type
        action_type = action.get('type', 'unknown')

        # Format action description
        data = action.get('data', {})

        if action_type == 'createCard':
            description = "📝 Created card"
            list_name = data.get('list', {}).get('name', 'Unknown list')
            description += f" in '{list_name}'"

        elif action_type == 'updateCard':
            description = "✏️  Updated card"
            old_data = data.get('old', {})
            card_data = data.get('card', {})

            if 'name' in old_data:
                description += f"\n         Renamed: '{old_data['name']}' → '{card_data.get('name')}'"
            elif 'desc' in old_data:
                description += " (description)"
            elif 'idList' in old_data:
                list_before = data.get('listBefore', {}).get('name', 'Unknown')
                list_after = data.get('listAfter', {}).get('name', 'Unknown')
                description += f"\n         Moved: '{list_before}' → '{list_after}'"
            elif 'due' in old_data:
                old_due = old_data.get('due', 'None')
                new_due = card_data.get('due', 'None')
                description += f"\n         Due date: {old_due} → {new_due}"
            elif 'closed' in old_data:
                if card_data.get('closed'):
                    description += " (archived)"
                else:
                    description += " (unarchived)"

        elif action_type == 'commentCard':
            comment_text = data.get('text', '')
            description = f"💬 Commented: {comment_text[:60]}"
            if len(comment_text) > 60:
                description += "..."

        elif action_type == 'addMemberToCard':
            added_member = data.get('member', {}).get('name', 'Unknown')
            description = f"👤 Added member: {added_member}"

        elif action_type == 'removeMemberFromCard':
            removed_member = data.get('member', {}).get('name', 'Unknown')
            description = f"👋 Removed member: {removed_member}"

        elif action_type == 'addLabelToCard':
            label = data.get('label', {})
            label_name = label.get('name', f"[{label.get('color', 'unknown')}]")
            description = f"🏷️  Added label: {label_name}"

        elif action_type == 'removeLabelFromCard':
            label = data.get('label', {})
            label_name = label.get('name', f"[{label.get('color', 'unknown')}]")
            description = f"🗑️  Removed label: {label_name}"

        elif action_type == 'addChecklistToCard':
            checklist_name = data.get('checklist', {}).get('name', 'Unknown')
            description = f"☑️  Added checklist: {checklist_name}"

        elif action_type == 'updateCheckItemStateOnCard':
            checkitem = data.get('checkItem', {})
            state = checkitem.get('state', 'unknown')
            name = checkitem.get('name', 'Unknown item')
            if state == 'complete':
                description = f"✅ Completed: {name}"
            else:
                description = f"⬜ Unchecked: {name}"

        elif action_type == 'addAttachmentToCard':
            attachment = data.get('attachment', {})
            att_name = attachment.get('name', 'Unknown')
            description = f"📎 Added attachment: {att_name}"

        else:
            description = f"• {action_type}"

        # Print action
        print(f"{date_formatted} │ {member_name} (@{member_username})")
        print(f"{'':19} │ {description}")
        print()

    print(f"{'='*80}\n")

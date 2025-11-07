"""
Bulk operations commands for batch processing
"""

import json
import csv
from ..client import get_client
from ..utils import validate_date


def cmd_bulk_move_cards(source_list_id, target_list_id, filter_query=""):
    """
    Move multiple cards from one list to another.
    Optionally filter by query string.
    """
    client = get_client()
    source_list = client.get_list(source_list_id)
    target_list = client.get_list(target_list_id)
    cards = source_list.list_cards()

    if not cards:
        print(f"No cards found in list '{source_list.name}'")
        return

    # Filter cards if query provided
    if filter_query:
        query_lower = filter_query.lower()
        cards = [c for c in cards if query_lower in c.name.lower() or
                 (c.desc and query_lower in c.desc.lower())]

    if not cards:
        print(f"No cards matching '{filter_query}' found")
        return

    print(f"\n{'='*70}")
    print(f"BULK MOVE: {len(cards)} card(s)")
    print(f"FROM: {source_list.name}")
    print(f"TO:   {target_list.name}")
    print(f"{'='*70}\n")

    moved_count = 0
    for card in cards:
        try:
            card.change_list(target_list_id)
            print(f"✅ Moved: {card.name[:60]}")
            moved_count += 1
        except Exception as e:
            print(f"❌ Failed to move '{card.name[:60]}': {str(e)}")

    print(f"\n{'='*70}")
    print(f"✅ Successfully moved {moved_count}/{len(cards)} cards")
    print(f"{'='*70}\n")


def cmd_bulk_add_label(card_ids_file, label_color, label_name=""):
    """
    Add label to multiple cards.
    card_ids_file: File with one card ID per line
    """
    client = get_client()

    # Read card IDs from file
    try:
        with open(card_ids_file, 'r') as f:
            card_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ File not found: {card_ids_file}")
        return

    if not card_ids:
        print(f"❌ No card IDs found in file")
        return

    print(f"\n{'='*70}")
    print(f"BULK ADD LABEL: {len(card_ids)} card(s)")
    print(f"Label: {label_name} ({label_color})")
    print(f"{'='*70}\n")

    success_count = 0
    for card_id in card_ids:
        try:
            card = client.get_card(card_id)
            board = client.get_board(card.board_id)

            # Find or create label
            label = None
            for l in board.get_labels():
                if l.color == label_color and (not label_name or l.name == label_name):
                    label = l
                    break

            if not label:
                label = board.add_label(label_name, label_color)

            card.add_label(label)
            print(f"✅ Added label to: {card.name[:50]}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed for card {card_id}: {str(e)}")

    print(f"\n{'='*70}")
    print(f"✅ Successfully labeled {success_count}/{len(card_ids)} cards")
    print(f"{'='*70}\n")


def cmd_bulk_set_due(card_ids_file, due_date):
    """
    Set due date for multiple cards.
    card_ids_file: File with one card ID per line
    due_date: Date in YYYY-MM-DD format
    """
    client = get_client()
    dt = validate_date(due_date)

    # Read card IDs from file
    try:
        with open(card_ids_file, 'r') as f:
            card_ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"❌ File not found: {card_ids_file}")
        return

    if not card_ids:
        print(f"❌ No card IDs found in file")
        return

    print(f"\n{'='*70}")
    print(f"BULK SET DUE DATE: {len(card_ids)} card(s)")
    print(f"Due Date: {dt.strftime('%Y-%m-%d %H:%M')}")
    print(f"{'='*70}\n")

    success_count = 0
    for card_id in card_ids:
        try:
            card = client.get_card(card_id)
            card.set_due(dt)
            print(f"✅ Set due date for: {card.name[:50]}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed for card {card_id}: {str(e)}")

    print(f"\n{'='*70}")
    print(f"✅ Successfully set due date for {success_count}/{len(card_ids)} cards")
    print(f"{'='*70}\n")


def cmd_bulk_archive_cards(list_id, filter_query=""):
    """
    Archive multiple cards in a list.
    Optionally filter by query string.
    """
    client = get_client()
    lst = client.get_list(list_id)
    cards = lst.list_cards()

    if not cards:
        print(f"No cards found in list '{lst.name}'")
        return

    # Filter cards if query provided
    if filter_query:
        query_lower = filter_query.lower()
        cards = [c for c in cards if query_lower in c.name.lower() or
                 (c.desc and query_lower in c.desc.lower())]

    if not cards:
        print(f"No cards matching '{filter_query}' found")
        return

    print(f"\n{'='*70}")
    print(f"BULK ARCHIVE: {len(cards)} card(s) from '{lst.name}'")
    print(f"{'='*70}\n")

    for card in cards:
        print(f"  • {card.name[:60]}")

    confirm = input(f"\n⚠️  Archive these {len(cards)} cards? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled")
        return

    archived_count = 0
    for card in cards:
        try:
            card.set_closed(True)
            print(f"✅ Archived: {card.name[:60]}")
            archived_count += 1
        except Exception as e:
            print(f"❌ Failed to archive '{card.name[:60]}': {str(e)}")

    print(f"\n{'='*70}")
    print(f"✅ Successfully archived {archived_count}/{len(cards)} cards")
    print(f"{'='*70}\n")


def cmd_bulk_create_cards(list_id, input_file):
    """
    Create multiple cards from CSV or JSON file.

    CSV format: title,description,due_date,labels
    JSON format: [{"title": "...", "description": "...", "due_date": "...", "labels": ["color:name", ...]}, ...]
    """
    client = get_client()
    lst = client.get_list(list_id)

    # Determine file type
    if input_file.endswith('.json'):
        cards_data = _read_json_file(input_file)
    elif input_file.endswith('.csv'):
        cards_data = _read_csv_file(input_file)
    else:
        print("❌ Unsupported file format. Use .csv or .json")
        return

    if not cards_data:
        print("❌ No card data found in file")
        return

    print(f"\n{'='*70}")
    print(f"BULK CREATE: {len(cards_data)} card(s) in '{lst.name}'")
    print(f"{'='*70}\n")

    created_count = 0
    for card_data in cards_data:
        try:
            title = card_data.get('title', '')
            description = card_data.get('description', '')
            due_date = card_data.get('due_date', '')
            labels = card_data.get('labels', [])

            if not title:
                print(f"⚠️  Skipping card with no title")
                continue

            # Create card
            card = lst.add_card(name=title, desc=description)

            # Set due date if provided
            if due_date:
                try:
                    dt = validate_date(due_date)
                    card.set_due(dt)
                except:
                    print(f"⚠️  Invalid due date for '{title[:40]}': {due_date}")

            # Add labels if provided
            if labels:
                board = client.get_board(card.board_id)
                for label_spec in labels:
                    try:
                        if ':' in label_spec:
                            color, name = label_spec.split(':', 1)
                        else:
                            color, name = label_spec, ""

                        # Find or create label
                        label = None
                        for l in board.get_labels():
                            if l.color == color and (not name or l.name == name):
                                label = l
                                break

                        if not label:
                            label = board.add_label(name, color)

                        card.add_label(label)
                    except Exception as e:
                        print(f"⚠️  Failed to add label '{label_spec}' to '{title[:40]}': {str(e)}")

            print(f"✅ Created: {title[:60]}")
            created_count += 1
        except Exception as e:
            print(f"❌ Failed to create card: {str(e)}")

    print(f"\n{'='*70}")
    print(f"✅ Successfully created {created_count}/{len(cards_data)} cards")
    print(f"{'='*70}\n")


def _read_json_file(filepath):
    """Read cards data from JSON file"""
    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON file: {str(e)}")
        return []


def _read_csv_file(filepath):
    """Read cards data from CSV file"""
    try:
        cards = []
        with open(filepath, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                card_data = {
                    'title': row.get('title', ''),
                    'description': row.get('description', ''),
                    'due_date': row.get('due_date', ''),
                    'labels': row.get('labels', '').split(',') if row.get('labels') else []
                }
                cards.append(card_data)
        return cards
    except Exception as e:
        print(f"❌ Error reading CSV file: {str(e)}")
        return []


def cmd_bulk_relabel(board_id, from_label, to_label, dry_run=False):
    """
    Re-assign all cards from one label to another.
    Useful for recovering from accidental label deletions.

    Args:
        board_id: Board ID
        from_label: Source label (name, color, or ID) - cards currently with this label
        to_label: Target label (name, color, or ID) - label to apply instead
        dry_run: If True, only show what would be done without making changes
    """
    client = get_client()
    board = client.get_board(board_id)

    # Find source and target labels
    board_labels = board.get_labels()
    source_label = None
    target_label = None

    for label in board_labels:
        if (label.id == from_label or label.name == from_label or label.color == from_label):
            source_label = label
        if (label.id == to_label or label.name == to_label or label.color == to_label):
            target_label = label

    if not source_label:
        print(f"❌ Source label '{from_label}' not found on board")
        return

    if not target_label:
        print(f"❌ Target label '{to_label}' not found on board")
        print(f"\n💡 Tip: Create the target label first using:")
        print(f"   trello add-label <card_id> <color> \"{to_label}\"")
        return

    source_name = source_label.name or f"[{source_label.color}]"
    target_name = target_label.name or f"[{target_label.color}]"

    # Get all cards on board and filter by source label
    all_cards = board.all_cards()
    cards_with_label = [card for card in all_cards
                       if any(l.id == source_label.id for l in card.labels)]

    if not cards_with_label:
        print(f"✅ No cards found with label '{source_name}'")
        return

    print(f"\n{'='*80}")
    if dry_run:
        print(f"🔍 DRY RUN - BULK RELABEL")
    else:
        print(f"🏷️  BULK RELABEL")
    print(f"{'='*80}")
    print(f"Source Label: {source_name} ({source_label.color})")
    print(f"Target Label: {target_name} ({target_label.color})")
    print(f"Cards Found:  {len(cards_with_label)}")
    print(f"{'='*80}\n")

    if dry_run:
        print(f"📋 Cards that would be relabeled:\n")
        for i, card in enumerate(cards_with_label[:20], 1):
            print(f"  {i}. {card.name[:65]}")
        if len(cards_with_label) > 20:
            print(f"  ... and {len(cards_with_label) - 20} more")
        print(f"\n💡 Remove --dry-run flag to execute the relabeling")
        return

    # Confirm action
    confirm = input(f"\n⚠️  Relabel {len(cards_with_label)} cards? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Operation cancelled")
        return

    success_count = 0
    for card in cards_with_label:
        try:
            # Remove old label and add new label
            card.remove_label(source_label)
            card.add_label(target_label)
            print(f"✅ Relabeled: {card.name[:60]}")
            success_count += 1
        except Exception as e:
            print(f"❌ Failed for '{card.name[:60]}': {str(e)}")

    print(f"\n{'='*80}")
    print(f"✅ Successfully relabeled {success_count}/{len(cards_with_label)} cards")
    print(f"{'='*80}\n")


def cmd_label_backup(board_id, output_file="label_backup.json"):
    """
    Backup all label assignments for a board to JSON file.
    Useful for disaster recovery.

    Args:
        board_id: Board ID
        output_file: Output JSON file path
    """
    client = get_client()
    board = client.get_board(board_id)

    print(f"\n{'='*80}")
    print(f"📦 LABEL BACKUP")
    print(f"{'='*80}")
    print(f"Board: {board.name}")
    print(f"{'='*80}\n")

    # Get all labels
    board_labels = board.get_labels()
    labels_map = {label.id: {'name': label.name, 'color': label.color}
                  for label in board_labels}

    print(f"📊 Found {len(board_labels)} label(s) on board")

    # Get all cards and their labels
    all_cards = board.all_cards()
    backup_data = {
        'board_id': board_id,
        'board_name': board.name,
        'backup_date': json.dumps(None),  # Will be serialized by json.dump
        'labels': labels_map,
        'card_labels': {}
    }

    card_count = 0
    for card in all_cards:
        if card.labels:
            backup_data['card_labels'][card.id] = {
                'name': card.name,
                'labels': [{'id': l.id, 'name': l.name, 'color': l.color}
                          for l in card.labels]
            }
            card_count += 1

    print(f"📊 Found {card_count} card(s) with labels")

    # Write to file
    try:
        with open(output_file, 'w') as f:
            json.dump(backup_data, f, indent=2)
        print(f"\n✅ Backup saved to: {output_file}")
        print(f"   Labels: {len(board_labels)}")
        print(f"   Cards with labels: {card_count}")
        print(f"\n💡 To restore: trello label-restore <board_id> {output_file}")
    except Exception as e:
        print(f"\n❌ Failed to save backup: {str(e)}")


def cmd_label_restore(board_id, backup_file):
    """
    Restore label assignments from backup file.

    Args:
        board_id: Board ID
        backup_file: Backup JSON file path
    """
    client = get_client()
    board = client.get_board(board_id)

    # Read backup file
    try:
        with open(backup_file, 'r') as f:
            backup_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Backup file not found: {backup_file}")
        return
    except Exception as e:
        print(f"❌ Error reading backup file: {str(e)}")
        return

    print(f"\n{'='*80}")
    print(f"📥 LABEL RESTORE")
    print(f"{'='*80}")
    print(f"Backup from: {backup_data.get('board_name', 'Unknown')}")
    print(f"Target board: {board.name}")
    print(f"{'='*80}\n")

    # Get current labels
    current_labels = board.get_labels()
    label_map = {}

    # Recreate missing labels
    for label_id, label_info in backup_data.get('labels', {}).items():
        # Find existing label by name and color
        existing = None
        for l in current_labels:
            if l.name == label_info['name'] and l.color == label_info['color']:
                existing = l
                break

        if existing:
            label_map[label_id] = existing
            print(f"✅ Found existing label: {label_info['name']} ({label_info['color']})")
        else:
            # Create new label
            new_label = board.add_label(label_info['name'], label_info['color'])
            label_map[label_id] = new_label
            print(f"➕ Created label: {label_info['name']} ({label_info['color']})")

    # Restore card labels
    card_labels_data = backup_data.get('card_labels', {})
    if not card_labels_data:
        print(f"\n⚠️  No card label data in backup")
        return

    print(f"\n📋 Restoring labels to {len(card_labels_data)} card(s)...\n")

    success_count = 0
    for card_id, card_data in card_labels_data.items():
        try:
            card = client.get_card(card_id)

            for label_info in card_data.get('labels', []):
                if label_info['id'] in label_map:
                    target_label = label_map[label_info['id']]
                    card.add_label(target_label)

            print(f"✅ Restored labels for: {card_data['name'][:50]}")
            success_count += 1
        except Exception as e:
            print(f"⚠️  Failed for card {card_id}: {str(e)}")

    print(f"\n{'='*80}")
    print(f"✅ Successfully restored labels for {success_count}/{len(card_labels_data)} cards")
    print(f"{'='*80}\n")

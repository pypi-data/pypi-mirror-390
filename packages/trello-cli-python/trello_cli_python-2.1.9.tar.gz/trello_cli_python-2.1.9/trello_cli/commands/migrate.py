"""
Board migration commands - Move all cards from one board to another
"""

from ..client import get_client


# List mapping templates for common board structures
LIST_MAPPINGS = {
    "agile": {
        # Standard Agile board structure mapping
        "philosophy": ["📚 Philosophy & Architecture", "Philosophy & Architecture"],
        "done": ["✅ Done", "Done"],
        "testing": ["🧪 Testing", "Testing"],
        "in_progress": ["⚙️ In Progress", "In Progress"],
        "sprint": ["📝 To Do (Sprint)", "Sprint", "To Do (Sprint)"],
        "ready": ["✅ Ready", "Ready"],
        "design": ["📐 Design/Specs", "Design/Specs", "Design"],
        "refinement": ["🔍 Refinement", "Refinement"],
        "prioritize": ["📋 To Prioritize", "To Prioritize", "Backlog"],
        "ideas": ["💡 Ideas/Discussion", "Ideas/Discussion", "Ideas"],
        "inbox": ["📥 Inbox", "Inbox"],
    }
}


def find_matching_list(source_list_name, target_lists, mapping_type="agile"):
    """
    Find the matching list in target board based on name similarity

    Args:
        source_list_name: Name of the source list
        target_lists: List of target board lists
        mapping_type: Type of mapping to use (default: agile)

    Returns:
        Target list object or None
    """
    mapping = LIST_MAPPINGS.get(mapping_type, LIST_MAPPINGS["agile"])

    # Try exact match first
    for target_list in target_lists:
        if target_list.name == source_list_name:
            return target_list

    # Try fuzzy match using mapping
    for category, variants in mapping.items():
        if source_list_name in variants:
            # Find target list that matches this category
            for target_list in target_lists:
                if target_list.name in variants:
                    return target_list

    return None


def cmd_migrate_board(source_board_id, target_board_id, dry_run=False):
    """
    Migrate all cards from source board to target board

    Args:
        source_board_id: ID of the source board
        target_board_id: ID of the target board
        dry_run: If True, only show what would be migrated without actually moving cards
    """
    client = get_client()

    source_board = client.get_board(source_board_id)
    target_board = client.get_board(target_board_id)

    print(f"🔄 {'[DRY RUN] ' if dry_run else ''}Migrating cards:")
    print(f"   Source: {source_board.name} ({source_board_id})")
    print(f"   Target: {target_board.name} ({target_board_id})")
    print()

    source_lists = source_board.list_lists()
    target_lists = target_board.list_lists()

    total_cards = 0
    moved_cards = 0
    skipped_cards = 0

    for source_list in source_lists:
        cards = source_list.list_cards()

        if not cards:
            continue

        total_cards += len(cards)

        # Find matching list in target board
        target_list = find_matching_list(source_list.name, target_lists)

        if not target_list:
            print(f"⚠️  No matching list found for '{source_list.name}' - skipping {len(cards)} cards")
            skipped_cards += len(cards)
            continue

        print(f"📋 {source_list.name} → {target_list.name} ({len(cards)} cards)")

        for card in cards:
            if dry_run:
                print(f"   [DRY RUN] Would move: {card.name}")
            else:
                try:
                    # Move card to target board and list
                    card.change_board(target_board_id, target_list.id)
                    print(f"   ✅ Moved: {card.name}")
                    moved_cards += 1
                except Exception as e:
                    print(f"   ❌ Error moving {card.name}: {e}")
                    skipped_cards += 1

        print()

    print(f"{'='*60}")
    if dry_run:
        print(f"[DRY RUN] Migration summary:")
        print(f"   Total cards found: {total_cards}")
        print(f"   Would be moved: {total_cards - skipped_cards}")
        print(f"   Would be skipped: {skipped_cards}")
        print()
        print("Run without --dry-run to perform actual migration")
    else:
        print(f"✅ Migration complete!")
        print(f"   Total cards: {total_cards}")
        print(f"   Moved: {moved_cards}")
        print(f"   Skipped: {skipped_cards}")
    print()


def cmd_archive_board(board_id):
    """Archive a board after migration"""
    client = get_client()
    board = client.get_board(board_id)

    print(f"⚠️  About to archive board: {board.name}")
    confirm = input("Are you sure? (yes/no): ").strip().lower()

    if confirm == "yes":
        board.close()
        print(f"✅ Board '{board.name}' has been archived")
    else:
        print("❌ Archive cancelled")

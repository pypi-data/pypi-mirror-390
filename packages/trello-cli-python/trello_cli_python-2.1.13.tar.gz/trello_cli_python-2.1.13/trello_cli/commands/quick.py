"""
Quick commands for common workflows - shortcuts for frequent operations
"""

from ..client import get_client


def cmd_quick_start(card_id, comment="Started working on this"):
    """
    Quick start: Move card to "In Progress" list and add comment.
    Automatically finds the "In Progress" list.
    """
    client = get_client()
    card = client.get_card(card_id)
    board = client.get_board(card.board_id)
    lists = board.list_lists()

    # Find "In Progress" list (flexible matching)
    in_progress_list = None
    for lst in lists:
        name_lower = lst.name.lower()
        if any(keyword in name_lower for keyword in ['in progress', 'doing', 'en proceso', 'wip']):
            in_progress_list = lst
            break

    if not in_progress_list:
        print("❌ Could not find 'In Progress' list")
        print("💡 Available lists:")
        for lst in lists:
            print(f"   • {lst.name}")
        return

    # Move card and add comment
    card.change_list(in_progress_list.id)
    card.comment(comment)

    print(f"✅ Card moved to '{in_progress_list.name}'")
    print(f"📝 Comment added: {comment}")
    print(f"🔗 {card.url}")


def cmd_quick_test(card_id, comment="Ready for testing"):
    """
    Quick test: Move card to "Testing" list and add comment.
    Automatically finds the "Testing" list.
    """
    client = get_client()
    card = client.get_card(card_id)
    board = client.get_board(card.board_id)
    lists = board.list_lists()

    # Find "Testing" list (flexible matching)
    testing_list = None
    for lst in lists:
        name_lower = lst.name.lower()
        if any(keyword in name_lower for keyword in ['testing', 'test', 'qa', 'review', 'prueba']):
            testing_list = lst
            break

    if not testing_list:
        print("❌ Could not find 'Testing' list")
        print("💡 Available lists:")
        for lst in lists:
            print(f"   • {lst.name}")
        return

    # Move card and add comment
    card.change_list(testing_list.id)
    card.comment(comment)

    print(f"✅ Card moved to '{testing_list.name}'")
    print(f"📝 Comment added: {comment}")
    print(f"🔗 {card.url}")


def cmd_quick_done(card_id, comment="Completed and verified"):
    """
    Quick done: Move card to "Done" list and add comment.
    Automatically finds the "Done" list.
    """
    client = get_client()
    card = client.get_card(card_id)
    board = client.get_board(card.board_id)
    lists = board.list_lists()

    # Find "Done" list (flexible matching)
    done_list = None
    for lst in lists:
        name_lower = lst.name.lower()
        if any(keyword in name_lower for keyword in ['done', 'completed', 'finished', 'hecho', 'completa']):
            done_list = lst
            break

    if not done_list:
        print("❌ Could not find 'Done' list")
        print("💡 Available lists:")
        for lst in lists:
            print(f"   • {lst.name}")
        return

    # Move card and add comment
    card.change_list(done_list.id)
    card.comment(comment)

    print(f"✅ Card moved to '{done_list.name}'")
    print(f"📝 Comment added: {comment}")
    print(f"🔗 {card.url}")


def cmd_my_cards(board_id, member_name=""):
    """
    Show all cards assigned to a specific member (or current user).
    If member_name is empty, shows all assigned cards.
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    print(f"\n{'='*70}")
    print(f"MY CARDS: {board.name}")
    if member_name:
        print(f"Member: {member_name}")
    print(f"{'='*70}\n")

    total_cards = 0
    for lst in lists:
        if lst.closed:
            continue

        cards = lst.list_cards()
        # Filter by member if specified
        if member_name:
            cards = [c for c in cards if any(member_name.lower() in m.full_name.lower()
                                            for m in c.member_ids)]

        if not cards:
            continue

        print(f"\n📋 {lst.name} ({len(cards)} card(s))")
        print(f"{'─'*70}")

        for card in cards:
            due_str = f" [Due: {card.due.strftime('%Y-%m-%d')}]" if card.due else ""
            labels_str = f" [{', '.join([l.name or l.color for l in card.labels])}]" if card.labels else ""
            print(f"  • {card.name}{due_str}{labels_str}")
            print(f"    ID: {card.id}")
            total_cards += 1

    print(f"\n{'='*70}")
    print(f"Total: {total_cards} card(s)")
    print(f"{'='*70}\n")


def cmd_card_age(list_id):
    """
    Show how long cards have been in a specific list.
    Useful for identifying stale cards or bottlenecks.
    """
    from datetime import datetime

    client = get_client()
    lst = client.get_list(list_id)
    cards = lst.list_cards()

    if not cards:
        print(f"No cards found in list '{lst.name}'")
        return

    print(f"\n{'='*70}")
    print(f"CARD AGE REPORT: {lst.name}")
    print(f"{'='*70}\n")

    # Calculate age for each card (using card ID timestamp)
    card_ages = []
    for card in cards:
        # Trello card IDs contain a timestamp (first 8 hex chars)
        try:
            timestamp = int(card.id[:8], 16)
            created_date = datetime.fromtimestamp(timestamp)
            age_days = (datetime.now() - created_date).days
            card_ages.append((card, age_days, created_date))
        except:
            card_ages.append((card, None, None))

    # Sort by age (oldest first)
    card_ages.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)

    for card, age_days, created_date in card_ages:
        if age_days is not None:
            age_str = f"{age_days} day(s) old"
            if age_days > 30:
                age_icon = "🔴"  # Very old
            elif age_days > 14:
                age_icon = "🟡"  # Getting old
            else:
                age_icon = "🟢"  # Fresh

            created_str = created_date.strftime('%Y-%m-%d')
            print(f"{age_icon} {age_str:15} | Created: {created_str} | {card.name[:40]}")
            print(f"   ID: {card.id}")
        else:
            print(f"⚪ Unknown age     | {card.name[:40]}")
            print(f"   ID: {card.id}")

    # Show statistics
    if card_ages:
        valid_ages = [age for _, age, _ in card_ages if age is not None]
        if valid_ages:
            avg_age = sum(valid_ages) / len(valid_ages)
            oldest = max(valid_ages)
            newest = min(valid_ages)

            print(f"\n{'='*70}")
            print(f"STATISTICS")
            print(f"{'='*70}")
            print(f"Total Cards: {len(cards)}")
            print(f"Average Age: {avg_age:.1f} days")
            print(f"Oldest Card: {oldest} days")
            print(f"Newest Card: {newest} days")
            print(f"{'='*70}\n")

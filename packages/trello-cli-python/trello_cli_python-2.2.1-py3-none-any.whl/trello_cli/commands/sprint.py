"""
Sprint planning and management commands
"""

from datetime import datetime
from ..client import get_client


def cmd_sprint_start(board_id, sprint_list_name="To Do (Sprint)", ready_list_name="Ready"):
    """
    Start a sprint by moving cards from Ready to Sprint list.
    Interactive selection of cards to include.
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    # Find Ready and Sprint lists
    ready_list = _find_list(lists, ready_list_name, ['ready', 'backlog prioritizado'])
    sprint_list = _find_list(lists, sprint_list_name, ['to do', 'sprint', 'todo'])

    if not ready_list or not sprint_list:
        print("❌ Could not find required lists")
        print(f"Looking for: '{ready_list_name}' and '{sprint_list_name}'")
        print("\n💡 Available lists:")
        for lst in lists:
            print(f"   • {lst.name}")
        return

    # Get cards from Ready list
    cards = ready_list.list_cards()
    if not cards:
        print(f"No cards found in '{ready_list.name}'")
        return

    print(f"\n{'='*70}")
    print(f"SPRINT START - {board.name}")
    print(f"{'='*70}")
    print(f"From: {ready_list.name}")
    print(f"To:   {sprint_list.name}")
    print(f"\nAvailable cards ({len(cards)}):\n")

    for i, card in enumerate(cards, 1):
        labels_str = f" [{', '.join([l.name or l.color for l in card.labels])}]" if card.labels else ""
        print(f"{i:2}. {card.name}{labels_str}")

    print(f"\n{'='*70}")
    selection = input("Enter card numbers to include (e.g., 1,2,3 or 1-5 or 'all'): ")

    if selection.lower() == 'all':
        selected_cards = cards
    else:
        try:
            selected_indices = _parse_selection(selection)
            selected_cards = [cards[i-1] for i in selected_indices if 0 < i <= len(cards)]
        except:
            print("❌ Invalid selection format")
            return

    if not selected_cards:
        print("❌ No cards selected")
        return

    print(f"\n{'='*70}")
    print(f"Moving {len(selected_cards)} card(s) to sprint...")
    print(f"{'='*70}\n")

    moved_count = 0
    for card in selected_cards:
        try:
            card.change_list(sprint_list.id)
            card.comment("Moved to sprint")
            print(f"✅ {card.name[:60]}")
            moved_count += 1
        except Exception as e:
            print(f"❌ Failed: {card.name[:60]} - {str(e)}")

    print(f"\n{'='*70}")
    print(f"✅ Sprint started with {moved_count} card(s)")
    print(f"{'='*70}\n")


def cmd_sprint_status(board_id):
    """
    Show current sprint status with cards per workflow stage.
    Shows: Ready, To Do, In Progress, Testing, Done
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    # Define sprint workflow stages
    stages = {
        'Ready': ['ready', 'listo'],
        'To Do (Sprint)': ['to do', 'sprint', 'todo', 'por hacer'],
        'In Progress': ['in progress', 'doing', 'en proceso', 'wip'],
        'Testing': ['testing', 'test', 'qa', 'review', 'prueba'],
        'Done': ['done', 'completed', 'hecho', 'completa']
    }

    print(f"\n{'='*70}")
    print(f"SPRINT STATUS - {board.name}")
    print(f"{'='*70}\n")

    total_cards = 0
    stage_data = []

    for stage_name, keywords in stages.items():
        lst = _find_list(lists, stage_name, keywords)
        if lst:
            cards = lst.list_cards()
            card_count = len(cards)
            total_cards += card_count

            # Count cards by label/priority
            p0_count = sum(1 for c in cards if any(l.color == 'red' for l in c.labels))
            p1_count = sum(1 for c in cards if any(l.color == 'orange' for l in c.labels))
            p2_count = sum(1 for c in cards if any(l.color == 'yellow' for l in c.labels))

            stage_data.append({
                'name': lst.name,
                'total': card_count,
                'p0': p0_count,
                'p1': p1_count,
                'p2': p2_count
            })

    # Display status
    for stage in stage_data:
        priority_str = f"P0:{stage['p0']} P1:{stage['p1']} P2:{stage['p2']}" if stage['total'] > 0 else ""
        bar_length = min(40, stage['total'] * 2)
        bar = '█' * bar_length

        print(f"{stage['name']:<20} │ {stage['total']:3} cards │ {bar}")
        if priority_str:
            print(f"{'':<20} │ {priority_str:<9} │")
        print()

    print(f"{'='*70}")
    print(f"Total Sprint Cards: {total_cards}")
    print(f"{'='*70}\n")

    # Show bottleneck warning
    in_progress_data = next((s for s in stage_data if 'progress' in s['name'].lower()), None)
    if in_progress_data and in_progress_data['total'] > 5:
        print("⚠️  WARNING: High number of cards in progress - possible bottleneck")

    testing_data = next((s for s in stage_data if 'test' in s['name'].lower()), None)
    if testing_data and testing_data['total'] > 3:
        print("⚠️  WARNING: Testing queue building up")


def cmd_sprint_close(board_id, sprint_list_name="To Do (Sprint)", backlog_list_name="Backlog"):
    """
    Close sprint: Move unfinished cards back to backlog and generate report.
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    # Find sprint workflow lists
    sprint_list = _find_list(lists, sprint_list_name, ['to do', 'sprint', 'todo'])
    backlog_list = _find_list(lists, backlog_list_name, ['backlog'])
    done_list = _find_list(lists, 'Done', ['done', 'completed', 'hecho'])
    testing_list = _find_list(lists, 'Testing', ['testing', 'test', 'qa'])
    in_progress_list = _find_list(lists, 'In Progress', ['in progress', 'doing'])

    if not sprint_list or not backlog_list:
        print("❌ Could not find required lists")
        return

    # Count completed cards
    completed_count = len(done_list.list_cards()) if done_list else 0

    # Get unfinished cards
    unfinished_cards = []
    if sprint_list:
        unfinished_cards.extend(sprint_list.list_cards())
    if in_progress_list:
        unfinished_cards.extend(in_progress_list.list_cards())
    if testing_list:
        unfinished_cards.extend(testing_list.list_cards())

    print(f"\n{'='*70}")
    print(f"SPRINT CLOSE - {board.name}")
    print(f"{'='*70}")
    print(f"\n📊 Sprint Summary:")
    print(f"   Completed: {completed_count} card(s)")
    print(f"   Unfinished: {len(unfinished_cards)} card(s)")
    print(f"\n{'='*70}\n")

    if unfinished_cards:
        print(f"Unfinished cards to move back to {backlog_list.name}:\n")
        for card in unfinished_cards:
            print(f"  • {card.name[:60]}")

        confirm = input(f"\n⚠️  Move {len(unfinished_cards)} unfinished cards to backlog? (yes/no): ")
        if confirm.lower() != 'yes':
            print("❌ Sprint close cancelled")
            return

        moved_count = 0
        for card in unfinished_cards:
            try:
                card.change_list(backlog_list.id)
                card.comment("Moved back to backlog - not completed in sprint")
                moved_count += 1
            except Exception as e:
                print(f"❌ Failed to move: {card.name[:60]}")

        print(f"\n✅ Moved {moved_count} card(s) back to backlog")

    print(f"\n{'='*70}")
    print(f"✅ Sprint closed successfully")
    print(f"   Completed: {completed_count} card(s)")
    print(f"   Moved to backlog: {len(unfinished_cards)} card(s)")
    print(f"{'='*70}\n")


def cmd_sprint_velocity(board_id, num_sprints=3):
    """
    Calculate sprint velocity based on completed cards.
    Note: This is a simple estimate based on card count in Done list.
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    done_list = _find_list(lists, 'Done', ['done', 'completed', 'hecho'])

    if not done_list:
        print("❌ Could not find 'Done' list")
        return

    cards = done_list.list_cards()

    if not cards:
        print("No completed cards found")
        return

    print(f"\n{'='*70}")
    print(f"SPRINT VELOCITY - {board.name}")
    print(f"{'='*70}\n")

    # Group cards by month (rough sprint approximation)
    from datetime import datetime
    from collections import defaultdict

    cards_by_month = defaultdict(list)

    for card in cards:
        try:
            # Use card ID timestamp
            timestamp = int(card.id[:8], 16)
            created_date = datetime.fromtimestamp(timestamp)
            month_key = created_date.strftime('%Y-%m')
            cards_by_month[month_key].append(card)
        except:
            pass

    # Show recent sprints (months)
    sorted_months = sorted(cards_by_month.keys(), reverse=True)[:num_sprints]

    total_completed = 0
    for month in sorted_months:
        count = len(cards_by_month[month])
        total_completed += count
        bar = '█' * (count // 2)
        print(f"{month} │ {count:3} cards │ {bar}")

    if sorted_months:
        avg_velocity = total_completed / len(sorted_months)
        print(f"\n{'='*70}")
        print(f"Average Velocity: {avg_velocity:.1f} cards/sprint")
        print(f"Total Completed: {total_completed} cards")
        print(f"{'='*70}\n")


def _find_list(lists, preferred_name, keywords):
    """Helper to find list by name or keywords"""
    # Try exact match first
    for lst in lists:
        if lst.name == preferred_name:
            return lst

    # Try keyword match
    for lst in lists:
        name_lower = lst.name.lower()
        for keyword in keywords:
            if keyword in name_lower:
                return lst

    return None


def _parse_selection(selection):
    """Parse selection string like '1,2,3' or '1-5' into list of indices"""
    indices = []
    parts = selection.split(',')

    for part in parts:
        part = part.strip()
        if '-' in part:
            start, end = map(int, part.split('-'))
            indices.extend(range(start, end + 1))
        else:
            indices.append(int(part))

    return indices

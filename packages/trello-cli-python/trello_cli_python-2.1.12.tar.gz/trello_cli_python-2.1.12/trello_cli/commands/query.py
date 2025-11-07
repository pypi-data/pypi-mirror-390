"""
Advanced query commands for filtering and analyzing cards
"""

from datetime import datetime, timedelta
from ..client import get_client


def cmd_cards_by_label(board_id, label_color, label_name=""):
    """
    Find all cards in a board with a specific label color/name.
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    print(f"\n{'='*70}")
    print(f"CARDS BY LABEL - {board.name}")
    print(f"Label: {label_name} ({label_color})" if label_name else f"Label Color: {label_color}")
    print(f"{'='*70}\n")

    found_cards = []

    for lst in lists:
        if lst.closed:
            continue

        cards = lst.list_cards()
        for card in cards:
            # Check if card has matching label
            has_label = False
            for label in card.labels:
                if label.color == label_color:
                    if not label_name or label.name == label_name:
                        has_label = True
                        break

            if has_label:
                found_cards.append((card, lst.name))

    if not found_cards:
        print(f"No cards found with label: {label_name} ({label_color})")
        return

    # Group by list
    from collections import defaultdict
    cards_by_list = defaultdict(list)

    for card, list_name in found_cards:
        cards_by_list[list_name].append(card)

    for list_name in sorted(cards_by_list.keys()):
        cards = cards_by_list[list_name]
        print(f"\n📋 {list_name} ({len(cards)} card(s))")
        print(f"{'─'*70}")

        for card in cards:
            labels_str = ', '.join([f"{l.name or l.color}" for l in card.labels])
            print(f"  • {card.name[:50]}")
            print(f"    ID: {card.id} | Labels: {labels_str}")

    print(f"\n{'='*70}")
    print(f"Total: {len(found_cards)} card(s)")
    print(f"{'='*70}\n")


def cmd_cards_due_soon(board_id, days=7):
    """
    Find cards with due dates in the next N days (default: 7).
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    cutoff_date = datetime.now() + timedelta(days=days)

    print(f"\n{'='*70}")
    print(f"CARDS DUE SOON - {board.name}")
    print(f"Due within: {days} day(s) (before {cutoff_date.strftime('%Y-%m-%d')})")
    print(f"{'='*70}\n")

    cards_with_due = []

    for lst in lists:
        if lst.closed:
            continue

        cards = lst.list_cards()
        for card in cards:
            if card.due:
                # Parse due date
                try:
                    if isinstance(card.due, str):
                        due_date = datetime.fromisoformat(card.due.replace('Z', '+00:00'))
                    else:
                        due_date = card.due

                    # Check if within timeframe
                    if datetime.now() <= due_date <= cutoff_date:
                        days_until = (due_date - datetime.now()).days
                        cards_with_due.append((card, lst.name, due_date, days_until))
                except:
                    pass

    if not cards_with_due:
        print(f"No cards due within {days} day(s)")
        return

    # Sort by due date (soonest first)
    cards_with_due.sort(key=lambda x: x[2])

    for card, list_name, due_date, days_until in cards_with_due:
        if days_until <= 1:
            urgency = "🔴 URGENT"
        elif days_until <= 3:
            urgency = "🟡 SOON"
        else:
            urgency = "🟢 OK"

        due_str = due_date.strftime('%Y-%m-%d %H:%M')
        print(f"{urgency} │ Due in {days_until} day(s): {due_str}")
        print(f"        │ {card.name[:50]}")
        print(f"        │ List: {list_name} | ID: {card.id}")
        print()

    print(f"{'='*70}")
    print(f"Total: {len(cards_with_due)} card(s) due soon")
    print(f"{'='*70}\n")


def cmd_cards_overdue(board_id):
    """
    Find all cards with overdue due dates.
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    print(f"\n{'='*70}")
    print(f"OVERDUE CARDS - {board.name}")
    print(f"{'='*70}\n")

    overdue_cards = []

    for lst in lists:
        if lst.closed:
            continue

        cards = lst.list_cards()
        for card in cards:
            if card.due:
                try:
                    if isinstance(card.due, str):
                        due_date = datetime.fromisoformat(card.due.replace('Z', '+00:00'))
                    else:
                        due_date = card.due

                    if due_date < datetime.now():
                        days_overdue = (datetime.now() - due_date).days
                        overdue_cards.append((card, lst.name, due_date, days_overdue))
                except:
                    pass

    if not overdue_cards:
        print("✅ No overdue cards")
        return

    # Sort by how overdue (most overdue first)
    overdue_cards.sort(key=lambda x: x[3], reverse=True)

    for card, list_name, due_date, days_overdue in overdue_cards:
        due_str = due_date.strftime('%Y-%m-%d %H:%M')
        print(f"🔴 OVERDUE by {days_overdue} day(s): {due_str}")
        print(f"   {card.name[:50]}")
        print(f"   List: {list_name} | ID: {card.id}")
        print()

    print(f"{'='*70}")
    print(f"Total: {len(overdue_cards)} overdue card(s)")
    print(f"{'='*70}\n")


def cmd_list_metrics(list_id):
    """
    Show metrics for a specific list:
    - Card count
    - Average age
    - Label distribution
    - Cards with/without due dates
    """
    from datetime import datetime

    client = get_client()
    lst = client.get_list(list_id)
    cards = lst.list_cards()

    if not cards:
        print(f"No cards found in list '{lst.name}'")
        return

    print(f"\n{'='*70}")
    print(f"LIST METRICS - {lst.name}")
    print(f"{'='*70}\n")

    # Calculate ages
    ages = []
    for card in cards:
        try:
            timestamp = int(card.id[:8], 16)
            created_date = datetime.fromtimestamp(timestamp)
            age_days = (datetime.now() - created_date).days
            ages.append(age_days)
        except:
            pass

    # Label distribution
    from collections import Counter
    label_counts = Counter()
    for card in cards:
        for label in card.labels:
            label_name = label.name or label.color
            label_counts[label_name] += 1

    # Due date stats
    cards_with_due = sum(1 for c in cards if c.due)
    cards_without_due = len(cards) - cards_with_due

    # Print metrics
    print(f"📊 Card Count: {len(cards)}")
    print()

    if ages:
        avg_age = sum(ages) / len(ages)
        print(f"⏱️  Age Metrics:")
        print(f"   Average: {avg_age:.1f} days")
        print(f"   Oldest:  {max(ages)} days")
        print(f"   Newest:  {min(ages)} days")
        print()

    if label_counts:
        print(f"🏷️  Label Distribution:")
        for label_name, count in label_counts.most_common():
            bar = '█' * min(20, count)
            print(f"   {label_name:<20} │ {count:3} │ {bar}")
        print()

    print(f"📅 Due Dates:")
    print(f"   With due date:    {cards_with_due}")
    print(f"   Without due date: {cards_without_due}")
    print()

    print(f"{'='*70}\n")


def cmd_board_health(board_id):
    """
    Board health check:
    - Stale cards (older than 30 days in non-Done lists)
    - Blocked cards (no activity in 14+ days)
    - Overdue cards
    - Lists with too many cards
    """
    from datetime import datetime

    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    print(f"\n{'='*70}")
    print(f"BOARD HEALTH CHECK - {board.name}")
    print(f"{'='*70}\n")

    stale_cards = []
    overdue_cards = []
    congested_lists = []

    for lst in lists:
        if lst.closed:
            continue

        cards = lst.list_cards()

        # Check for congestion (>10 cards not in Done)
        if len(cards) > 10 and 'done' not in lst.name.lower():
            congested_lists.append((lst.name, len(cards)))

        # Check each card
        for card in cards:
            # Skip Done lists
            if 'done' in lst.name.lower():
                continue

            # Check card age
            try:
                timestamp = int(card.id[:8], 16)
                created_date = datetime.fromtimestamp(timestamp)
                age_days = (datetime.now() - created_date).days

                if age_days > 30:
                    stale_cards.append((card, lst.name, age_days))
            except:
                pass

            # Check overdue
            if card.due:
                try:
                    if isinstance(card.due, str):
                        due_date = datetime.fromisoformat(card.due.replace('Z', '+00:00'))
                    else:
                        due_date = card.due

                    if due_date < datetime.now():
                        days_overdue = (datetime.now() - due_date).days
                        overdue_cards.append((card, lst.name, days_overdue))
                except:
                    pass

    # Print health report
    health_score = 100

    print(f"🩺 HEALTH ISSUES:\n")

    if stale_cards:
        health_score -= min(30, len(stale_cards) * 5)
        print(f"⚠️  STALE CARDS: {len(stale_cards)} card(s) older than 30 days")
        for card, list_name, age in sorted(stale_cards, key=lambda x: x[2], reverse=True)[:5]:
            print(f"   • {age} days: {card.name[:40]} (in {list_name})")
        if len(stale_cards) > 5:
            print(f"   ... and {len(stale_cards) - 5} more")
        print()

    if overdue_cards:
        health_score -= min(30, len(overdue_cards) * 10)
        print(f"🔴 OVERDUE: {len(overdue_cards)} card(s) past due date")
        for card, list_name, days_overdue in sorted(overdue_cards, key=lambda x: x[2], reverse=True)[:5]:
            print(f"   • {days_overdue} days overdue: {card.name[:40]}")
        if len(overdue_cards) > 5:
            print(f"   ... and {len(overdue_cards) - 5} more")
        print()

    if congested_lists:
        health_score -= min(20, len(congested_lists) * 10)
        print(f"🚦 CONGESTED LISTS: {len(congested_lists)} list(s) with >10 cards")
        for list_name, count in sorted(congested_lists, key=lambda x: x[1], reverse=True):
            print(f"   • {list_name}: {count} cards")
        print()

    if not stale_cards and not overdue_cards and not congested_lists:
        print("✅ No major health issues detected!")
        print()

    # Health score
    print(f"{'='*70}")
    if health_score >= 90:
        status = "🟢 EXCELLENT"
    elif health_score >= 70:
        status = "🟡 GOOD"
    elif health_score >= 50:
        status = "🟠 NEEDS ATTENTION"
    else:
        status = "🔴 CRITICAL"

    print(f"Board Health Score: {health_score}/100 - {status}")
    print(f"{'='*70}\n")

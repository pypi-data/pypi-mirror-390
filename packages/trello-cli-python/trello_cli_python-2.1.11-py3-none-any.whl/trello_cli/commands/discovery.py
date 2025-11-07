"""
Discovery and overview commands for exploring Trello boards
"""

from ..client import get_client
from ..utils import format_table


def cmd_board_overview(board_id):
    """
    Get a complete overview of a board including all lists and card counts.
    This is useful for understanding board structure at a glance.
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    print(f"\n{'='*70}")
    print(f"BOARD OVERVIEW: {board.name}")
    print(f"{'='*70}")
    print(f"Board ID: {board.id}")
    print(f"URL: {board.url}")
    print(f"\n{'LISTS':-^70}")

    if not lists:
        print("\nNo lists found in this board")
        return

    # Prepare data for table with card counts
    list_data = []
    for lst in lists:
        cards = lst.list_cards()
        card_count = len(cards)
        list_data.append({
            'id': lst.id,
            'name': lst.name,
            'cards': card_count,
            'closed': lst.closed
        })

    # Display lists with card counts
    format_table(
        list_data,
        columns=[
            ("ID", "id"),
            ("Name", "name"),
            ("Cards", "cards"),
            ("Status", lambda x: "Archived" if x.get('closed') else "Active")
        ],
        widths={"ID": 25, "Name": 30, "Cards": 8, "Status": 10}
    )

    # Summary statistics
    total_cards = sum(item['cards'] for item in list_data)
    active_lists = sum(1 for item in list_data if not item['closed'])

    print(f"\n{'SUMMARY':-^70}")
    print(f"Total Lists: {len(list_data)} ({active_lists} active)")
    print(f"Total Cards: {total_cards}")
    print(f"{'='*70}\n")


def cmd_board_ids(board_id):
    """
    Get a quick reference guide of all useful IDs in a board.
    Shows board ID, list IDs, and recent card IDs for easy copying.
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    print(f"\n{'='*70}")
    print(f"ID QUICK REFERENCE: {board.name}")
    print(f"{'='*70}")
    print(f"\nBOARD ID: {board.id}")
    print(f"Board URL: {board.url}")

    if not lists:
        print("\nNo lists found in this board")
        return

    print(f"\n{'LIST IDs':-^70}\n")

    for lst in lists:
        status = " [ARCHIVED]" if lst.closed else ""
        print(f"  {lst.name}{status}")
        print(f"  ID: {lst.id}")

        # Get cards in this list
        cards = lst.list_cards()
        if cards:
            print(f"  Cards ({len(cards)}):")
            # Show first 5 cards as a quick reference
            for card in cards[:5]:
                short_name = card.name[:50] + "..." if len(card.name) > 50 else card.name
                print(f"    • {short_name}")
                print(f"      ID: {card.id}")
            if len(cards) > 5:
                print(f"    ... and {len(cards) - 5} more cards")
        else:
            print(f"  Cards: (empty)")
        print()

    print(f"{'='*70}")
    print(f"💡 TIP: Use 'trello cards <list_id>' to see all cards in a list")
    print(f"💡 TIP: Use 'trello show-card <card_id>' for detailed card info")
    print(f"{'='*70}\n")


def cmd_search_cards(board_id, query):
    """
    Search for cards across all lists in a board by title or description.
    Shows which list each card belongs to.
    """
    # Validate board_id format (24 hex chars)
    if len(board_id) != 24 or not all(c in '0123456789abcdef' for c in board_id.lower()):
        print("❌ ERROR: Invalid board_id format")
        print(f"   Provided: '{board_id}'")
        print(f"   Expected: 24-character hexadecimal ID")
        print()
        print("💡 Correct usage:")
        print("   trello search-cards <board_id> \"search query\"")
        print()
        print("   Note: First argument is board_id, second is query")
        print("   Example: trello search-cards 68fbfeeb7f8614df2eb61e42 \"FI-API-FEAT\"")
        print()
        print("💡 To find board_id:")
        print("   trello boards")
        print()
        print("💡 Run 'trello help' to see detailed usage and examples")
        print()
        return

    try:
        client = get_client()
        board = client.get_board(board_id)
    except Exception as e:
        print(f"❌ ERROR: Failed to get board {board_id}: {e}")
        print()
        print("💡 Make sure you're using the correct board_id")
        print("   Run 'trello boards' to see available boards")
        print()
        print("💡 Run 'trello help' to see detailed usage and examples")
        print()
        return
    lists = board.list_lists()

    query_lower = query.lower()
    results = []

    print(f"\n{'='*70}")
    print(f"SEARCHING FOR: '{query}' in board '{board.name}'")
    print(f"{'='*70}\n")

    # Search through all lists
    for lst in lists:
        if lst.closed:  # Skip archived lists
            continue

        cards = lst.list_cards()
        for card in cards:
            # Search in card name and description
            if (query_lower in card.name.lower() or
                (card.desc and query_lower in card.desc.lower())):
                results.append({
                    'id': card.id,
                    'name': card.name,
                    'list_name': lst.name,
                    'list_id': lst.id,
                    'url': card.url
                })

    if not results:
        print(f"No cards found matching '{query}'")
        print(f"\n{'='*70}\n")
        return

    print(f"Found {len(results)} card(s):\n")

    for result in results:
        print(f"{'─'*70}")
        print(f"Card: {result['name']}")
        print(f"  ID: {result['id']}")
        print(f"  List: {result['list_name']} (ID: {result['list_id']})")
        print(f"  URL: {result['url']}")

    print(f"{'─'*70}")
    print(f"\n💡 TIP: Use 'trello show-card <card_id>' for full card details")
    print(f"{'='*70}\n")

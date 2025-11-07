"""
Export commands for boards
"""

import csv
import json
from datetime import datetime
from ..client import get_client


def cmd_export_board(board_id, format_type='json', output_file=None):
    """
    Export board to various formats

    Args:
        board_id: Board ID
        format_type: Export format (json, csv, md)
        output_file: Output file path (optional, prints to stdout if not provided)
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    # Collect all data
    board_data = {
        'board_id': board.id,
        'board_name': board.name,
        'exported_at': datetime.now().isoformat(),
        'lists': []
    }

    total_cards = 0

    for lst in lists:
        if lst.closed:
            continue

        list_data = {
            'list_id': lst.id,
            'list_name': lst.name,
            'cards': []
        }

        cards = lst.list_cards()
        total_cards += len(cards)

        for card in cards:
            # Get card age
            try:
                timestamp = int(card.id[:8], 16)
                created_date = datetime.fromtimestamp(timestamp)
                age_days = (datetime.now() - created_date).days
            except:
                created_date = None
                age_days = None

            # Get labels
            labels = [{'name': l.name, 'color': l.color} for l in card.labels]

            # Get members
            members = [{'name': m.full_name, 'username': m.username} for m in card.get_members()] if hasattr(card, 'get_members') else []

            # Get checklists
            checklists = []
            for checklist in card.checklists:
                items = []
                for item in checklist.items:
                    items.append({
                        'name': item.get('name', ''),
                        'checked': item.get('state', 'incomplete') == 'complete'
                    })

                checklists.append({
                    'name': checklist.name,
                    'items': items,
                    'completed': sum(1 for item in items if item['checked']),
                    'total': len(items)
                })

            card_data = {
                'card_id': card.id,
                'name': card.name,
                'description': card.desc or '',
                'url': card.url,
                'labels': labels,
                'members': members,
                'due_date': card.due.isoformat() if card.due else None,
                'created_date': created_date.isoformat() if created_date else None,
                'age_days': age_days,
                'checklists': checklists,
                'is_archived': card.closed
            }

            list_data['cards'].append(card_data)

        board_data['lists'].append(list_data)

    # Export based on format
    if format_type == 'json':
        output = json.dumps(board_data, indent=2, ensure_ascii=False)

    elif format_type == 'csv':
        output = _export_to_csv(board_data)

    elif format_type == 'md':
        output = _export_to_markdown(board_data)

    else:
        print(f"❌ Unknown format: {format_type}")
        print("   Supported formats: json, csv, md")
        return

    # Output
    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output)
        print(f"✅ Board exported to: {output_file}")
        print(f"   Board: {board.name}")
        print(f"   Format: {format_type}")
        print(f"   Lists: {len(board_data['lists'])}")
        print(f"   Cards: {total_cards}")
    else:
        print(output)


def _export_to_csv(board_data):
    """Convert board data to CSV format"""
    import io

    output = io.StringIO()
    writer = csv.writer(output)

    # Write header
    writer.writerow([
        'List', 'Card Name', 'Card ID', 'Description',
        'Labels', 'Members', 'Due Date', 'Age (days)',
        'Checklists Complete', 'Checklists Total', 'URL', 'Archived'
    ])

    # Write cards
    for list_data in board_data['lists']:
        list_name = list_data['list_name']

        for card in list_data['cards']:
            labels_str = ', '.join([l['name'] or l['color'] for l in card['labels']])
            members_str = ', '.join([m['name'] for m in card['members']])

            checklists_complete = sum(cl['completed'] for cl in card['checklists'])
            checklists_total = sum(cl['total'] for cl in card['checklists'])

            writer.writerow([
                list_name,
                card['name'],
                card['card_id'],
                card['description'][:100],  # Truncate long descriptions
                labels_str,
                members_str,
                card['due_date'] or '',
                card['age_days'] or '',
                checklists_complete,
                checklists_total,
                card['url'],
                'Yes' if card['is_archived'] else 'No'
            ])

    return output.getvalue()


def _export_to_markdown(board_data):
    """Convert board data to Markdown format"""
    lines = []

    lines.append(f"# {board_data['board_name']}")
    lines.append(f"\n**Exported:** {board_data['exported_at']}")
    lines.append(f"**Board ID:** {board_data['board_id']}\n")

    total_cards = sum(len(lst['cards']) for lst in board_data['lists'])
    lines.append(f"**Lists:** {len(board_data['lists'])} | **Cards:** {total_cards}\n")

    lines.append("---\n")

    # Export each list
    for list_data in board_data['lists']:
        lines.append(f"## {list_data['list_name']}")
        lines.append(f"\n*Cards: {len(list_data['cards'])}*\n")

        if not list_data['cards']:
            lines.append("*(empty)*\n")
            continue

        for card in list_data['cards']:
            lines.append(f"### {card['name']}")

            # Labels
            if card['labels']:
                labels_str = ', '.join([f"`{l['name'] or l['color']}`" for l in card['labels']])
                lines.append(f"\n**Labels:** {labels_str}")

            # Members
            if card['members']:
                members_str = ', '.join([f"@{m['username']}" for m in card['members']])
                lines.append(f"**Assigned:** {members_str}")

            # Due date
            if card['due_date']:
                lines.append(f"**Due:** {card['due_date']}")

            # Age
            if card['age_days'] is not None:
                lines.append(f"**Age:** {card['age_days']} days")

            # Description
            if card['description']:
                lines.append(f"\n{card['description']}\n")

            # Checklists
            if card['checklists']:
                lines.append("\n**Checklists:**\n")
                for checklist in card['checklists']:
                    lines.append(f"- **{checklist['name']}** ({checklist['completed']}/{checklist['total']})")
                    for item in checklist['items']:
                        checkbox = '[x]' if item['checked'] else '[ ]'
                        lines.append(f"  - {checkbox} {item['name']}")

            # URL
            lines.append(f"\n[View on Trello]({card['url']})\n")
            lines.append("---\n")

    return '\n'.join(lines)

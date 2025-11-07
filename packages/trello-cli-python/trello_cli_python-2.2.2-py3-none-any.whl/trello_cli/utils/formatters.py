"""
Output formatting utilities
"""


def format_table(items, columns, widths=None):
    """
    Format items as a table

    Args:
        items: List of objects or dicts to display
        columns: List of (header, attribute/key) tuples or (header, callable) tuples
        widths: Optional dict of column widths
    """
    if not widths:
        widths = {col[0]: 40 for col in columns}

    # Print header
    header = " ".join(f"{col[0]:<{widths.get(col[0], 40)}}" for col in columns)
    print(header)
    print("-" * len(header))

    # Print rows
    for item in items:
        row_parts = []
        for col in columns:
            # Handle callable (lambda function)
            if callable(col[1]):
                value = str(col[1](item))
            # Handle dict
            elif isinstance(item, dict):
                value = str(item.get(col[1], ''))
            # Handle object attribute
            else:
                value = str(getattr(item, col[1], ''))

            row_parts.append(f"{value:<{widths.get(col[0], 40)}}")

        row = " ".join(row_parts)
        print(row)


def format_card_details(card):
    """Format card details for display"""
    print(f"📝 Card: {card.name}")
    print(f"   ID: {card.id}")
    print(f"   URL: {card.url}")
    print()
    print(f"Description:")
    print(f"   {card.desc or '(none)'}")
    print()
    print(f"Due Date: {card.due or '(none)'}")
    print(f"Labels: {', '.join([l.name for l in card.labels]) or '(none)'}")

    if card.checklists:
        print()
        print("Checklists:")
        for checklist in card.checklists:
            print(f"   ☑️  {checklist.name}")
            for item in checklist.items:
                status = "✅" if item['checked'] else "⬜"
                print(f"      {status} {item['name']}")

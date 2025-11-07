"""
Audit commands for board and list analysis
"""

import json
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from ..client import get_client


def cmd_board_audit(board_id, pattern=None, fix_labels=False, report_json=False):
    """
    Comprehensive board audit - exposes structural chaos and workflow inconsistencies:

    CRITICAL VALIDATIONS:
    1. Cards in "Done" without due date (traceability failure)
    2. Cards in "Done" with incomplete checklists (premature completion)
    3. Cards without due dates in active lists (Sprint, Testing, In Progress)
    4. Overdue cards not marked as complete (zombie tasks)
    5. Cards without assigned members in execution lists (orphaned work)
    6. Duplicate/unused labels (label chaos)
    7. Empty checklists (fake productivity)
    8. Cards without descriptions in critical lists
    9. Naming pattern violations (inconsistent nomenclature)
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    # Compile pattern if provided
    id_pattern = re.compile(pattern) if pattern else None

    # Initialize critical issue trackers
    done_cards_no_due = []
    done_cards_incomplete_checklist = []
    active_cards_no_due = []
    overdue_not_complete = []
    execution_cards_no_members = []
    empty_checklists = []
    cards_without_pattern = []
    cards_without_description_critical = []

    # Additional trackers
    cards_without_labels = []
    empty_lists = []
    stale_lists = []

    total_cards = 0
    total_active_lists = 0

    # Define list categories
    DONE_KEYWORDS = ['done', 'completed', 'finished', 'closed', 'archive']
    ACTIVE_KEYWORDS = ['sprint', 'doing', 'in progress', 'testing', 'ready', 'wip', 'development']
    EXECUTION_KEYWORDS = ['sprint', 'doing', 'in progress', 'testing', 'development']
    CRITICAL_KEYWORDS = ['sprint', 'testing', 'in progress', 'doing', 'review']

    for lst in lists:
        if lst.closed:
            continue

        total_active_lists += 1
        cards = lst.list_cards()

        # Check for empty lists
        if len(cards) == 0:
            empty_lists.append(lst.name)
            continue

        total_cards += len(cards)

        # Categorize list
        list_name_lower = lst.name.lower()
        is_done_list = any(keyword in list_name_lower for keyword in DONE_KEYWORDS)
        is_active_list = any(keyword in list_name_lower for keyword in ACTIVE_KEYWORDS)
        is_execution_list = any(keyword in list_name_lower for keyword in EXECUTION_KEYWORDS)
        is_critical_list = any(keyword in list_name_lower for keyword in CRITICAL_KEYWORDS)

        # Check if list is stale
        is_stale = True
        newest_card_age = None

        for card in cards:
            try:
                timestamp = int(card.id[:8], 16)
                created_date = datetime.fromtimestamp(timestamp)
                age_days = (datetime.now() - created_date).days

                if newest_card_age is None or age_days < newest_card_age:
                    newest_card_age = age_days

                if age_days < 30:
                    is_stale = False
            except:
                pass

        if is_stale and newest_card_age and not is_done_list:
            stale_lists.append((lst.name, newest_card_age))

        # Audit each card
        for card in cards:
            # Get card age
            try:
                timestamp = int(card.id[:8], 16)
                created_date = datetime.fromtimestamp(timestamp)
                age_days = (datetime.now() - created_date).days
            except:
                age_days = None

            # Parse due date
            due_date = None
            is_overdue = False
            days_overdue = 0
            if card.due:
                try:
                    if isinstance(card.due, str):
                        due_date = datetime.fromisoformat(card.due.replace('Z', '+00:00'))
                    else:
                        due_date = card.due

                    if due_date < datetime.now():
                        is_overdue = True
                        days_overdue = (datetime.now() - due_date).days
                except:
                    pass

            # Get checklist status
            has_checklist = len(card.checklists) > 0
            checklist_complete = True
            checklist_empty = False
            total_items = 0
            completed_items = 0

            if has_checklist:
                for checklist in card.checklists:
                    items = checklist.items
                    if len(items) == 0:
                        checklist_empty = True

                    for item in items:
                        total_items += 1
                        if item.get('state', 'incomplete') == 'complete':
                            completed_items += 1

                if total_items > 0 and completed_items < total_items:
                    checklist_complete = False

            # Get member status
            has_members = False
            if hasattr(card, 'idMembers') and card.idMembers:
                has_members = True
            elif hasattr(card, 'member_id') and card.member_id:
                has_members = True

            # CRITICAL VALIDATION 1: Cards in Done without due date
            if is_done_list and not card.due:
                done_cards_no_due.append({
                    'card': card,
                    'list': lst.name,
                    'age': age_days
                })

            # CRITICAL VALIDATION 2: Cards in Done with incomplete checklists
            if is_done_list and has_checklist and not checklist_complete:
                done_cards_incomplete_checklist.append({
                    'card': card,
                    'list': lst.name,
                    'total': total_items,
                    'completed': completed_items
                })

            # CRITICAL VALIDATION 3: Active cards without due dates
            if is_active_list and not card.due:
                active_cards_no_due.append({
                    'card': card,
                    'list': lst.name
                })

            # CRITICAL VALIDATION 4: Overdue cards not marked complete
            if is_overdue and not is_done_list:
                overdue_not_complete.append({
                    'card': card,
                    'list': lst.name,
                    'due_date': due_date,
                    'days_overdue': days_overdue
                })

            # CRITICAL VALIDATION 5: Execution cards without members
            if is_execution_list and not has_members:
                execution_cards_no_members.append({
                    'card': card,
                    'list': lst.name
                })

            # CRITICAL VALIDATION 7: Empty checklists
            if checklist_empty:
                empty_checklists.append({
                    'card': card,
                    'list': lst.name
                })

            # Additional validations
            if id_pattern and not id_pattern.search(card.name):
                cards_without_pattern.append({
                    'card': card,
                    'list': lst.name
                })

            if is_critical_list and (not card.desc or card.desc.strip() == ""):
                cards_without_description_critical.append({
                    'card': card,
                    'list': lst.name
                })

            if not card.labels or len(card.labels) == 0:
                cards_without_labels.append({
                    'card': card,
                    'list': lst.name
                })

    # Calculate severity scores
    critical_issues = 0
    high_issues = 0
    medium_issues = 0

    if done_cards_no_due: critical_issues += 1
    if done_cards_incomplete_checklist: critical_issues += 1
    if active_cards_no_due: high_issues += 1
    if overdue_not_complete: critical_issues += 1
    if execution_cards_no_members: high_issues += 1
    if empty_checklists: medium_issues += 1
    if cards_without_pattern and id_pattern: medium_issues += 1
    if cards_without_description_critical: medium_issues += 1

    total_issues = critical_issues + high_issues + medium_issues

    # If JSON report requested
    if report_json:
        report = {
            "board_id": board_id,
            "board_name": board.name,
            "audit_timestamp": datetime.now().isoformat(),
            "summary": {
                "total_lists": total_active_lists,
                "total_cards": total_cards,
                "critical_issues": critical_issues,
                "high_issues": high_issues,
                "medium_issues": medium_issues,
                "total_issues": total_issues
            },
            "critical_findings": {
                "done_no_due": len(done_cards_no_due),
                "done_incomplete_checklist": len(done_cards_incomplete_checklist),
                "overdue_not_complete": len(overdue_not_complete)
            },
            "high_findings": {
                "active_no_due": len(active_cards_no_due),
                "execution_no_members": len(execution_cards_no_members)
            },
            "medium_findings": {
                "empty_checklists": len(empty_checklists),
                "pattern_violations": len(cards_without_pattern),
                "critical_no_description": len(cards_without_description_critical)
            },
            "health_score": max(0, 100 - (critical_issues * 20) - (high_issues * 10) - (medium_issues * 5))
        }
        print(json.dumps(report, indent=2))
        return

    # Human-readable output
    print(f"\n{'='*80}")
    print(f"🔍 BOARD AUDIT REPORT - {board.name}")
    print(f"Board ID: {board_id}")
    print(f"Audit Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*80}\n")

    # Summary
    print(f"📊 BOARD SUMMARY:")
    print(f"   Total Active Lists: {total_active_lists}")
    print(f"   Total Cards: {total_cards}")
    print(f"   Critical Issues: {critical_issues}")
    print(f"   High Priority Issues: {high_issues}")
    print(f"   Medium Priority Issues: {medium_issues}")
    print()

    # CRITICAL ISSUES
    print(f"{'='*80}")
    print(f"🔴 CRITICAL ISSUES (Workflow Killers)")
    print(f"{'='*80}\n")

    # Issue 1: Done without due date
    if done_cards_no_due:
        print(f"❌ CARDS IN 'DONE' WITHOUT DUE DATE: {len(done_cards_no_due)} card(s)")
        print(f"   Problem: No traceability - when was this completed?")
        print(f"   Impact: Cannot measure velocity or predict future work\n")

        for item in done_cards_no_due[:10]:
            card = item['card']
            print(f"   • {card.name[:55]}")
            print(f"     List: {item['list']} | ID: {card.id}")
            print(f"     Fix: trello set-due {card.id} \"YYYY-MM-DD\"")

        if len(done_cards_no_due) > 10:
            print(f"   ... and {len(done_cards_no_due) - 10} more\n")
        print()
    else:
        print(f"✅ All 'Done' cards have due dates\n")

    # Issue 2: Done with incomplete checklists
    if done_cards_incomplete_checklist:
        print(f"❌ CARDS IN 'DONE' WITH INCOMPLETE CHECKLISTS: {len(done_cards_incomplete_checklist)} card(s)")
        print(f"   Problem: Marked complete but checklist says otherwise")
        print(f"   Impact: False sense of completion, missing deliverables\n")

        for item in done_cards_incomplete_checklist[:10]:
            card = item['card']
            completion = f"{item['completed']}/{item['total']}"
            print(f"   • {card.name[:55]}")
            print(f"     List: {item['list']} | Checklist: {completion} items")
            print(f"     ID: {card.id}")

        if len(done_cards_incomplete_checklist) > 10:
            print(f"   ... and {len(done_cards_incomplete_checklist) - 10} more\n")
        print()
    else:
        print(f"✅ All 'Done' cards have complete checklists\n")

    # Issue 4: Overdue cards not marked complete
    if overdue_not_complete:
        print(f"❌ OVERDUE CARDS NOT MARKED COMPLETE: {len(overdue_not_complete)} card(s)")
        print(f"   Problem: Past due date but still in active workflow")
        print(f"   Impact: Zombie tasks that kill sprint health\n")

        # Sort by most overdue
        sorted_overdue = sorted(overdue_not_complete, key=lambda x: x['days_overdue'], reverse=True)

        for item in sorted_overdue[:10]:
            card = item['card']
            days = item['days_overdue']
            due_str = item['due_date'].strftime('%Y-%m-%d')

            if days > 7:
                urgency = "🔴 CRITICAL"
            elif days > 3:
                urgency = "🟠 HIGH"
            else:
                urgency = "🟡 MEDIUM"

            print(f"   {urgency} │ {days} days overdue (due: {due_str})")
            print(f"           │ {card.name[:50]}")
            print(f"           │ List: {item['list']} | ID: {card.id}")
            print()

        if len(overdue_not_complete) > 10:
            print(f"   ... and {len(overdue_not_complete) - 10} more\n")
        print()
    else:
        print(f"✅ No overdue cards in active workflow\n")

    # HIGH PRIORITY ISSUES
    print(f"{'='*80}")
    print(f"🟠 HIGH PRIORITY ISSUES (Execution Blockers)")
    print(f"{'='*80}\n")

    # Issue 3: Active cards without due dates
    if active_cards_no_due:
        print(f"⚠️  ACTIVE CARDS WITHOUT DUE DATES: {len(active_cards_no_due)} card(s)")
        print(f"   Problem: How do you know if they're late?")
        print(f"   Impact: No accountability, no sprint planning possible\n")

        # Group by list
        by_list = defaultdict(list)
        for item in active_cards_no_due:
            by_list[item['list']].append(item['card'])

        for list_name in sorted(by_list.keys()):
            cards = by_list[list_name]
            print(f"   📋 {list_name} ({len(cards)} card(s)):")
            for card in cards[:5]:
                print(f"      • {card.name[:55]}")
                print(f"        ID: {card.id}")
            if len(cards) > 5:
                print(f"      ... and {len(cards) - 5} more")
            print()
        print()
    else:
        print(f"✅ All active cards have due dates\n")

    # Issue 5: Execution cards without members
    if execution_cards_no_members:
        print(f"⚠️  EXECUTION CARDS WITHOUT ASSIGNED MEMBERS: {len(execution_cards_no_members)} card(s)")
        print(f"   Problem: Who's doing this work?")
        print(f"   Impact: Orphaned tasks that nobody owns\n")

        # Group by list
        by_list = defaultdict(list)
        for item in execution_cards_no_members:
            by_list[item['list']].append(item['card'])

        for list_name in sorted(by_list.keys()):
            cards = by_list[list_name]
            print(f"   📋 {list_name} ({len(cards)} card(s)):")
            for card in cards[:5]:
                print(f"      • {card.name[:55]}")
                print(f"        ID: {card.id}")
                print(f"        Fix: trello assign-card {card.id} <member_id>")
            if len(cards) > 5:
                print(f"      ... and {len(cards) - 5} more")
            print()
        print()
    else:
        print(f"✅ All execution cards have assigned members\n")

    # MEDIUM PRIORITY ISSUES
    print(f"{'='*80}")
    print(f"🟡 MEDIUM PRIORITY ISSUES (Quality & Consistency)")
    print(f"{'='*80}\n")

    # Issue 7: Empty checklists
    if empty_checklists:
        print(f"⚠️  EMPTY CHECKLISTS: {len(empty_checklists)} card(s)")
        print(f"   Problem: Checklist created but never filled")
        print(f"   Impact: False productivity signal\n")

        for item in empty_checklists[:10]:
            card = item['card']
            print(f"   • {card.name[:60]}")
            print(f"     List: {item['list']} | ID: {card.id}")

        if len(empty_checklists) > 10:
            print(f"   ... and {len(empty_checklists) - 10} more\n")
        print()
    else:
        print(f"✅ No empty checklists found\n")

    # Pattern violations
    if id_pattern and cards_without_pattern:
        print(f"⚠️  NAMING PATTERN VIOLATIONS: {len(cards_without_pattern)} card(s)")
        print(f"   Pattern: {pattern}")
        print(f"   Problem: Inconsistent nomenclature")
        print(f"   Impact: Hard to search, filter, and organize\n")

        for item in cards_without_pattern[:10]:
            card = item['card']
            print(f"   • {card.name[:60]}")
            print(f"     List: {item['list']} | ID: {card.id}")

        if len(cards_without_pattern) > 10:
            print(f"   ... and {len(cards_without_pattern) - 10} more\n")
        print()

    # Critical lists without descriptions
    if cards_without_description_critical:
        print(f"⚠️  CARDS WITHOUT DESCRIPTIONS (in critical lists): {len(cards_without_description_critical)} card(s)")
        print(f"   Problem: No context for implementation")
        print(f"   Impact: Team members guessing requirements\n")

        for item in cards_without_description_critical[:10]:
            card = item['card']
            print(f"   • {card.name[:60]}")
            print(f"     List: {item['list']} | ID: {card.id}")

        if len(cards_without_description_critical) > 10:
            print(f"   ... and {len(cards_without_description_critical) - 10} more\n")
        print()

    # Health Score
    print(f"{'='*80}")
    print(f"📊 BOARD HEALTH SCORE")
    print(f"{'='*80}\n")

    health_score = max(0, 100 - (critical_issues * 20) - (high_issues * 10) - (medium_issues * 5))

    if health_score >= 90:
        status = "🟢 EXCELLENT"
        message = "Your board is well-maintained and ready for production"
    elif health_score >= 70:
        status = "🟡 GOOD"
        message = "Minor issues detected, but generally healthy"
    elif health_score >= 50:
        status = "🟠 NEEDS ATTENTION"
        message = "Significant workflow issues detected"
    else:
        status = "🔴 CRITICAL"
        message = "Board has severe structural problems affecting delivery"

    print(f"Health Score: {health_score}/100 - {status}")
    print(f"Assessment: {message}")
    print()
    print(f"Issue Breakdown:")
    print(f"  Critical Issues:  {critical_issues} (workflow killers)")
    print(f"  High Priority:    {high_issues} (execution blockers)")
    print(f"  Medium Priority:  {medium_issues} (quality issues)")
    print(f"  Total Issues:     {total_issues}")
    print()

    # Recommendations
    if total_issues > 0:
        print(f"{'='*80}")
        print(f"💡 RECOMMENDATIONS")
        print(f"{'='*80}\n")

        if critical_issues > 0:
            print(f"🔴 IMMEDIATE ACTION REQUIRED:")
            if done_cards_no_due:
                print(f"   • Add due dates to {len(done_cards_no_due)} 'Done' cards for traceability")
            if done_cards_incomplete_checklist:
                print(f"   • Complete or remove {len(done_cards_incomplete_checklist)} incomplete checklists")
            if overdue_not_complete:
                print(f"   • Address {len(overdue_not_complete)} overdue cards (move to Done or update dates)")
            print()

        if high_issues > 0:
            print(f"🟠 HIGH PRIORITY:")
            if active_cards_no_due:
                print(f"   • Set due dates for {len(active_cards_no_due)} active cards")
            if execution_cards_no_members:
                print(f"   • Assign members to {len(execution_cards_no_members)} orphaned cards")
            print()

        if medium_issues > 0:
            print(f"🟡 CLEANUP TASKS:")
            if empty_checklists:
                print(f"   • Remove or populate {len(empty_checklists)} empty checklists")
            if cards_without_pattern:
                print(f"   • Rename {len(cards_without_pattern)} cards to follow naming pattern")
            if cards_without_description_critical:
                print(f"   • Add descriptions to {len(cards_without_description_critical)} critical cards")
            print()

    print(f"{'='*80}\n")


def cmd_list_snapshot(list_id, output_file=None):
    """
    Export complete snapshot of a list to JSON.
    Includes all card details: ID, name, description, labels, members, checklists, etc.
    """
    client = get_client()
    lst = client.get_list(list_id)
    cards = lst.list_cards()

    snapshot = {
        "list_id": lst.id,
        "list_name": lst.name,
        "exported_at": datetime.now().isoformat(),
        "card_count": len(cards),
        "cards": []
    }

    for card in cards:
        # Extract card age
        try:
            timestamp = int(card.id[:8], 16)
            created_date = datetime.fromtimestamp(timestamp)
            age_days = (datetime.now() - created_date).days
        except:
            created_date = None
            age_days = None

        # Extract labels
        labels = []
        for label in card.labels:
            labels.append({
                "name": label.name,
                "color": label.color
            })

        # Extract checklists
        checklists = []
        for checklist in card.checklists:
            items = []
            for item in checklist.items:
                items.append({
                    "name": item.get('name', ''),
                    "checked": item.get('state', 'incomplete') == 'complete'
                })

            checklists.append({
                "name": checklist.name,
                "items": items,
                "completed": sum(1 for item in items if item['checked']),
                "total": len(items)
            })

        # Extract due date
        due_date = None
        if card.due:
            try:
                if isinstance(card.due, str):
                    due_date = card.due
                else:
                    due_date = card.due.isoformat()
            except:
                pass

        card_data = {
            "id": card.id,
            "name": card.name,
            "description": card.desc or "",
            "url": card.url,
            "labels": labels,
            "due_date": due_date,
            "created_date": created_date.isoformat() if created_date else None,
            "age_days": age_days,
            "checklists": checklists,
            "checklist_summary": {
                "total_checklists": len(checklists),
                "total_items": sum(cl['total'] for cl in checklists),
                "completed_items": sum(cl['completed'] for cl in checklists)
            },
            "has_description": bool(card.desc and card.desc.strip()),
            "has_labels": len(labels) > 0,
            "has_due_date": due_date is not None
        }

        snapshot["cards"].append(card_data)

    # Output
    json_output = json.dumps(snapshot, indent=2, ensure_ascii=False)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(json_output)
        print(f"✅ List snapshot exported to: {output_file}")
        print(f"   List: {lst.name}")
        print(f"   Cards: {len(cards)}")
    else:
        print(json_output)


def cmd_list_audit(list_id, pattern=None):
    """
    Detailed audit of a specific list.
    Similar to board audit but focused on a single list.
    """
    client = get_client()
    lst = client.get_list(list_id)
    cards = lst.list_cards()

    print(f"\n{'='*80}")
    print(f"LIST AUDIT REPORT - {lst.name}")
    print(f"List ID: {list_id}")
    print(f"{'='*80}\n")

    if not cards:
        print("📭 This list is empty")
        return

    # Compile pattern if provided
    id_pattern = re.compile(pattern) if pattern else None

    # Initialize trackers
    cards_without_pattern = []
    cards_without_members = []
    cards_without_labels = []
    cards_without_description = []
    cards_with_due = 0
    cards_overdue = 0

    # Age statistics
    ages = []

    for card in cards:
        # Check age
        try:
            timestamp = int(card.id[:8], 16)
            created_date = datetime.fromtimestamp(timestamp)
            age_days = (datetime.now() - created_date).days
            ages.append(age_days)
        except:
            pass

        # Check ID pattern
        if id_pattern and not id_pattern.search(card.name):
            cards_without_pattern.append((card.name, card.id))

        # Check for assigned members
        if not card.member_id and not hasattr(card, 'idMembers'):
            cards_without_members.append((card.name, card.id))

        # Check for labels
        if not card.labels or len(card.labels) == 0:
            cards_without_labels.append((card.name, card.id))

        # Check for description
        if not card.desc or card.desc.strip() == "":
            cards_without_description.append((card.name, card.id))

        # Check due dates
        if card.due:
            cards_with_due += 1
            try:
                if isinstance(card.due, str):
                    due_date = datetime.fromisoformat(card.due.replace('Z', '+00:00'))
                else:
                    due_date = card.due

                if due_date < datetime.now():
                    cards_overdue += 1
            except:
                pass

    # Print summary
    print(f"📊 LIST SUMMARY:")
    print(f"   Total Cards: {len(cards)}")
    print(f"   Cards with due dates: {cards_with_due}")
    print(f"   Overdue cards: {cards_overdue}")

    if ages:
        print(f"\n⏱️  AGE STATISTICS:")
        print(f"   Average age: {sum(ages) / len(ages):.1f} days")
        print(f"   Oldest card: {max(ages)} days")
        print(f"   Newest card: {min(ages)} days")

    print()

    # Print issues
    print(f"{'='*80}")
    print(f"AUDIT FINDINGS:")
    print(f"{'='*80}\n")

    issues = 0

    # Pattern violations
    if id_pattern:
        if cards_without_pattern:
            issues += 1
            print(f"⚠️  NAMING PATTERN VIOLATIONS: {len(cards_without_pattern)} card(s)")
            print(f"   Pattern: {pattern}")
            for card_name, card_id in cards_without_pattern[:10]:
                print(f"   • {card_name[:60]}")
                print(f"     ID: {card_id}")
            if len(cards_without_pattern) > 10:
                print(f"   ... and {len(cards_without_pattern) - 10} more")
            print()

    # Missing members
    if cards_without_members:
        issues += 1
        print(f"⚠️  CARDS WITHOUT ASSIGNED MEMBERS: {len(cards_without_members)} card(s)")
        for card_name, card_id in cards_without_members[:10]:
            print(f"   • {card_name[:60]}")
            print(f"     ID: {card_id}")
        if len(cards_without_members) > 10:
            print(f"   ... and {len(cards_without_members) - 10} more")
        print()

    # Missing labels
    if cards_without_labels:
        issues += 1
        print(f"⚠️  CARDS WITHOUT LABELS: {len(cards_without_labels)} card(s)")
        for card_name, card_id in cards_without_labels[:10]:
            print(f"   • {card_name[:60]}")
            print(f"     ID: {card_id}")
        if len(cards_without_labels) > 10:
            print(f"   ... and {len(cards_without_labels) - 10} more")
        print()

    # Missing descriptions
    if cards_without_description:
        issues += 1
        print(f"⚠️  CARDS WITHOUT DESCRIPTION: {len(cards_without_description)} card(s)")
        for card_name, card_id in cards_without_description[:10]:
            print(f"   • {card_name[:60]}")
            print(f"     ID: {card_id}")
        if len(cards_without_description) > 10:
            print(f"   ... and {len(cards_without_description) - 10} more")
        print()

    if issues == 0:
        print("✅ No issues found! This list is well maintained.\n")

    # Score
    print(f"{'='*80}")
    audit_score = max(0, 100 - (issues * 20))

    if audit_score >= 90:
        status = "🟢 EXCELLENT"
    elif audit_score >= 70:
        status = "🟡 GOOD"
    elif audit_score >= 50:
        status = "🟠 NEEDS ATTENTION"
    else:
        status = "🔴 CRITICAL"

    print(f"List Audit Score: {audit_score}/100 - {status}")
    print(f"Issues Found: {issues}")
    print(f"{'='*80}\n")


def cmd_sprint_audit(board_id, sprint_label=None):
    """
    Sprint-specific audit:
    - Cards with sprint labels that don't have due dates
    - Cards with overdue dates in active sprints
    - Sprint label distribution
    - Cards in sprint lists without sprint labels
    - Due date consistency within sprints
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    print(f"\n{'='*80}")
    print(f"SPRINT AUDIT REPORT - {board.name}")
    print(f"Board ID: {board_id}")
    if sprint_label:
        print(f"Filtering by label: {sprint_label}")
    print(f"{'='*80}\n")

    # Initialize trackers
    sprint_cards = []
    sprint_cards_without_dates = []
    overdue_sprint_cards = []
    cards_in_sprint_list_without_label = []
    sprint_labels_found = set()

    # Track cards by sprint label
    cards_by_sprint = defaultdict(list)

    # Keywords for sprint-related lists
    sprint_list_keywords = ['sprint', 'doing', 'in progress', 'testing', 'ready']

    for lst in lists:
        if lst.closed:
            continue

        cards = lst.list_cards()
        is_sprint_list = any(keyword in lst.name.lower() for keyword in sprint_list_keywords)

        for card in cards:
            # Find sprint labels
            card_sprint_labels = []
            for label in card.labels:
                label_name = (label.name or "").lower()

                # Check if it's a sprint label
                is_sprint_label = False
                if sprint_label:
                    # User specified a specific sprint label
                    if sprint_label.lower() in label_name:
                        is_sprint_label = True
                else:
                    # Auto-detect sprint labels (containing "sprint", "s1", "s2", etc)
                    if 'sprint' in label_name or re.match(r's\d+', label_name):
                        is_sprint_label = True

                if is_sprint_label:
                    card_sprint_labels.append(label.name or label.color)
                    sprint_labels_found.add(label.name or label.color)

            # Card has sprint label
            if card_sprint_labels:
                sprint_cards.append((card, lst.name, card_sprint_labels))

                # Group by sprint
                for sprint in card_sprint_labels:
                    cards_by_sprint[sprint].append((card, lst.name))

                # Check if has due date
                if not card.due:
                    sprint_cards_without_dates.append((card, lst.name, card_sprint_labels))
                else:
                    # Check if overdue
                    try:
                        if isinstance(card.due, str):
                            due_date = datetime.fromisoformat(card.due.replace('Z', '+00:00'))
                        else:
                            due_date = card.due

                        if due_date < datetime.now():
                            days_overdue = (datetime.now() - due_date).days
                            overdue_sprint_cards.append((card, lst.name, card_sprint_labels, due_date, days_overdue))
                    except:
                        pass

            # Card in sprint list but no sprint label
            elif is_sprint_list:
                # Skip Done lists
                if 'done' not in lst.name.lower():
                    cards_in_sprint_list_without_label.append((card, lst.name))

    # Print summary
    print(f"📊 SPRINT SUMMARY:")
    print(f"   Sprint labels found: {len(sprint_labels_found)}")
    if sprint_labels_found:
        for label in sorted(sprint_labels_found):
            count = len(cards_by_sprint[label])
            print(f"      • {label}: {count} card(s)")
    print(f"   Total cards in sprints: {len(sprint_cards)}")
    print()

    # Print issues
    print(f"{'='*80}")
    print(f"SPRINT AUDIT FINDINGS:")
    print(f"{'='*80}\n")

    issues = 0

    # Cards with sprint labels but no due dates
    if sprint_cards_without_dates:
        issues += 1
        print(f"⚠️  SPRINT CARDS WITHOUT DUE DATES: {len(sprint_cards_without_dates)} card(s)")
        print(f"   Sprint cards should have due dates for proper planning\n")

        # Group by sprint
        by_sprint = defaultdict(list)
        for card, list_name, sprints in sprint_cards_without_dates:
            for sprint in sprints:
                by_sprint[sprint].append((card, list_name))

        for sprint in sorted(by_sprint.keys()):
            cards = by_sprint[sprint]
            print(f"   📅 {sprint} ({len(cards)} card(s) missing dates):")
            for card, list_name in cards[:10]:
                print(f"      • {card.name[:55]}")
                print(f"        ID: {card.id} | List: {list_name}")
                print(f"        Fix: trello set-due {card.id} \"YYYY-MM-DD\"")
            if len(cards) > 10:
                print(f"      ... and {len(cards) - 10} more")
            print()
    else:
        print(f"✅ All sprint cards have due dates\n")

    # Overdue sprint cards
    if overdue_sprint_cards:
        issues += 1
        print(f"🔴 OVERDUE SPRINT CARDS: {len(overdue_sprint_cards)} card(s)")
        print(f"   These cards are past their due date and need attention\n")

        # Sort by most overdue
        overdue_sprint_cards.sort(key=lambda x: x[4], reverse=True)

        for card, list_name, sprints, due_date, days_overdue in overdue_sprint_cards[:15]:
            sprint_str = ", ".join(sprints)
            due_str = due_date.strftime('%Y-%m-%d')

            if days_overdue > 7:
                urgency = "🔴 CRITICAL"
            elif days_overdue > 3:
                urgency = "🟠 HIGH"
            else:
                urgency = "🟡 MEDIUM"

            print(f"   {urgency} │ {days_overdue} days overdue (due: {due_str})")
            print(f"           │ {card.name[:50]}")
            print(f"           │ Sprint: {sprint_str} | List: {list_name}")
            print(f"           │ ID: {card.id}")
            print()

        if len(overdue_sprint_cards) > 15:
            print(f"   ... and {len(overdue_sprint_cards) - 15} more\n")
    else:
        print(f"✅ No overdue sprint cards\n")

    # Cards in sprint lists without sprint labels
    if cards_in_sprint_list_without_label:
        issues += 1
        print(f"⚠️  CARDS IN SPRINT LISTS WITHOUT SPRINT LABELS: {len(cards_in_sprint_list_without_label)} card(s)")
        print(f"   These cards are in sprint-related lists but lack sprint labels\n")

        # Group by list
        by_list = defaultdict(list)
        for card, list_name in cards_in_sprint_list_without_label:
            by_list[list_name].append(card)

        for list_name in sorted(by_list.keys()):
            cards = by_list[list_name]
            print(f"   📋 {list_name} ({len(cards)} card(s)):")
            for card in cards[:10]:
                print(f"      • {card.name[:55]}")
                print(f"        ID: {card.id}")
                print(f"        Fix: trello add-label {card.id} \"color\" \"Sprint X\"")
            if len(cards) > 10:
                print(f"      ... and {len(cards) - 10} more")
            print()
    else:
        print(f"✅ All cards in sprint lists have sprint labels\n")

    # Sprint consistency analysis
    print(f"{'='*80}")
    print(f"SPRINT HEALTH ANALYSIS:")
    print(f"{'='*80}\n")

    for sprint in sorted(cards_by_sprint.keys()):
        cards_info = cards_by_sprint[sprint]
        total = len(cards_info)

        # Calculate stats
        with_dates = 0
        overdue = 0
        due_soon = 0
        on_track = 0

        for card, list_name in cards_info:
            if card.due:
                with_dates += 1
                try:
                    if isinstance(card.due, str):
                        due_date = datetime.fromisoformat(card.due.replace('Z', '+00:00'))
                    else:
                        due_date = card.due

                    days_until = (due_date - datetime.now()).days

                    if days_until < 0:
                        overdue += 1
                    elif days_until <= 3:
                        due_soon += 1
                    else:
                        on_track += 1
                except:
                    pass

        without_dates = total - with_dates
        completion_rate = (with_dates / total * 100) if total > 0 else 0

        # Health indicator
        if overdue > total * 0.3:
            health = "🔴 CRITICAL"
        elif overdue > total * 0.1 or without_dates > total * 0.2:
            health = "🟠 NEEDS ATTENTION"
        elif due_soon > total * 0.5:
            health = "🟡 WATCH"
        else:
            health = "🟢 HEALTHY"

        print(f"📌 {sprint}: {health}")
        print(f"   Total cards:        {total}")
        print(f"   With due dates:     {with_dates} ({completion_rate:.1f}%)")
        print(f"   Without due dates:  {without_dates}")
        if with_dates > 0:
            print(f"   Overdue:            {overdue}")
            print(f"   Due soon (≤3 days): {due_soon}")
            print(f"   On track:           {on_track}")
        print()

    # Audit score
    print(f"{'='*80}")
    audit_score = max(0, 100 - (issues * 25) - (len(overdue_sprint_cards) * 2))

    if audit_score >= 90:
        status = "🟢 EXCELLENT"
    elif audit_score >= 70:
        status = "🟡 GOOD"
    elif audit_score >= 50:
        status = "🟠 NEEDS ATTENTION"
    else:
        status = "🔴 CRITICAL"

    print(f"Sprint Audit Score: {audit_score}/100 - {status}")
    print(f"Critical Issues: {issues}")
    print(f"Overdue Cards: {len(overdue_sprint_cards)}")
    print(f"{'='*80}\n")


def cmd_label_audit(board_id):
    """
    Label audit:
    - Detect duplicate labels (same name, different color)
    - Detect similar labels (typos, case differences)
    - Unused labels (defined but not used on any card)
    - Label usage statistics
    - Naming inconsistencies
    """
    client = get_client()
    board = client.get_board(board_id)

    # Get all board labels
    board_labels = board.get_labels()

    # Get all lists and cards
    lists = board.list_lists()

    print(f"\n{'='*80}")
    print(f"LABEL AUDIT REPORT - {board.name}")
    print(f"Board ID: {board_id}")
    print(f"{'='*80}\n")

    # Track label usage
    label_usage = defaultdict(int)
    label_details = {}  # id -> {name, color, count}

    # Initialize all board labels
    for label in board_labels:
        label_id = label.id
        label_name = label.name or f"[{label.color}]"
        label_details[label_id] = {
            'id': label_id,
            'name': label.name,
            'color': label.color,
            'count': 0
        }

    # Count label usage
    total_cards = 0
    for lst in lists:
        if lst.closed:
            continue

        cards = lst.list_cards()
        total_cards += len(cards)

        for card in cards:
            for label in card.labels:
                if label.id in label_details:
                    label_details[label.id]['count'] += 1
                    label_usage[label.id] += 1

    # Analysis
    print(f"📊 LABEL SUMMARY:")
    print(f"   Total labels defined: {len(board_labels)}")
    print(f"   Total cards: {total_cards}")
    print()

    # Group labels by name (case-insensitive)
    labels_by_name = defaultdict(list)
    for label in board_labels:
        name_key = (label.name or "").lower().strip()
        if name_key:
            labels_by_name[name_key].append(label)

    # Detect issues
    print(f"{'='*80}")
    print(f"LABEL AUDIT FINDINGS:")
    print(f"{'='*80}\n")

    issues = 0

    # 1. Duplicate names (same name, different colors)
    duplicates = {name: labels for name, labels in labels_by_name.items() if len(labels) > 1}

    if duplicates:
        issues += 1
        print(f"⚠️  DUPLICATE LABEL NAMES: {len(duplicates)} name(s) with multiple colors")
        print(f"   Same name but different colors - may cause confusion\n")

        for name, labels in sorted(duplicates.items()):
            print(f"   📛 \"{name}\" ({len(labels)} versions):")
            for label in labels:
                usage = label_details.get(label.id, {}).get('count', 0)
                print(f"      • Color: {label.color:12} | Used: {usage:3} times | ID: {label.id}")
            print()
    else:
        print(f"✅ No duplicate label names\n")

    # 2. Similar labels (potential typos)
    similar_labels = []
    label_names = [(label.name.lower().strip(), label) for label in board_labels if label.name]

    for i, (name1, label1) in enumerate(label_names):
        for name2, label2 in label_names[i+1:]:
            # Check for very similar names (edit distance, common prefixes, etc.)
            if name1 != name2:
                # Simple similarity: same words in different order, or one contains the other
                words1 = set(name1.split())
                words2 = set(name2.split())

                # Check if one contains the other or significant overlap
                if (words1.issubset(words2) or words2.issubset(words1) or
                    len(words1.intersection(words2)) >= min(len(words1), len(words2)) * 0.7):
                    similar_labels.append((label1, label2))

    if similar_labels:
        issues += 1
        print(f"⚠️  SIMILAR LABELS: {len(similar_labels)} pair(s) detected")
        print(f"   These labels have similar names - possible typos or redundancy\n")

        for label1, label2 in similar_labels[:10]:
            usage1 = label_details.get(label1.id, {}).get('count', 0)
            usage2 = label_details.get(label2.id, {}).get('count', 0)
            print(f"   📛 Similar pair:")
            print(f"      • \"{label1.name}\" ({label1.color}) - Used {usage1} times")
            print(f"      • \"{label2.name}\" ({label2.color}) - Used {usage2} times")
            print()

        if len(similar_labels) > 10:
            print(f"   ... and {len(similar_labels) - 10} more pairs\n")
    else:
        print(f"✅ No similar label names detected\n")

    # 3. Unused labels
    unused_labels = [label for label in board_labels
                    if label_details.get(label.id, {}).get('count', 0) == 0]

    if unused_labels:
        issues += 1
        print(f"⚠️  UNUSED LABELS: {len(unused_labels)} label(s) not used on any card")
        print(f"   Consider removing these to reduce clutter\n")

        for label in unused_labels[:15]:
            name = label.name or f"[unnamed {label.color}]"
            print(f"   • {name:30} │ Color: {label.color:10} │ ID: {label.id}")

        if len(unused_labels) > 15:
            print(f"   ... and {len(unused_labels) - 15} more\n")
    else:
        print(f"✅ All labels are in use\n")

    # 4. Unnamed labels
    unnamed_labels = [label for label in board_labels if not label.name or label.name.strip() == ""]

    if unnamed_labels:
        issues += 1
        print(f"⚠️  UNNAMED LABELS: {len(unnamed_labels)} label(s) without names")
        print(f"   Labels should have descriptive names\n")

        for label in unnamed_labels:
            usage = label_details.get(label.id, {}).get('count', 0)
            print(f"   • Color: {label.color:12} | Used: {usage:3} times | ID: {label.id}")
        print()
    else:
        print(f"✅ All labels have names\n")

    # Label usage statistics
    print(f"{'='*80}")
    print(f"LABEL USAGE STATISTICS:")
    print(f"{'='*80}\n")

    # Sort by usage
    labels_sorted = sorted(label_details.values(), key=lambda x: x['count'], reverse=True)

    print(f"Top 20 Most Used Labels:\n")
    for i, label in enumerate(labels_sorted[:20], 1):
        name = label['name'] or f"[unnamed {label['color']}]"
        count = label['count']
        color = label['color']

        # Usage bar
        max_count = labels_sorted[0]['count'] if labels_sorted else 1
        bar_length = int((count / max_count) * 40) if max_count > 0 else 0
        bar = '█' * bar_length

        print(f"{i:2}. {name:30} │ {color:10} │ {count:4} │ {bar}")

    print()

    # Label distribution by color
    color_counts = Counter(label['color'] for label in label_details.values())
    print(f"Label Distribution by Color:\n")
    for color, count in sorted(color_counts.items()):
        bar = '█' * min(30, count)
        print(f"   {color:12} │ {count:3} label(s) │ {bar}")

    print()

    # Recommendations
    print(f"{'='*80}")
    print(f"RECOMMENDATIONS:")
    print(f"{'='*80}\n")

    if duplicates:
        print(f"🔧 Consolidate duplicate labels:")
        print(f"   Choose one color per label name and migrate cards to it\n")

    if unused_labels:
        print(f"🗑️  Delete unused labels to reduce clutter:")
        print(f"   Review the {len(unused_labels)} unused label(s) and remove if not needed\n")

    if unnamed_labels:
        print(f"✏️  Add names to unnamed labels:")
        print(f"   Give descriptive names to {len(unnamed_labels)} color-only label(s)\n")

    if similar_labels:
        print(f"🔍 Review similar labels for typos or redundancy:")
        print(f"   Check {len(similar_labels)} similar pair(s) and consolidate if appropriate\n")

    if issues == 0:
        print(f"✅ Your labels are well organized! No issues found.\n")

    # Audit score
    print(f"{'='*80}")
    audit_score = max(0, 100 - (len(duplicates) * 10) - (len(unused_labels) * 2) -
                     (len(unnamed_labels) * 5) - (len(similar_labels) * 5))

    if audit_score >= 90:
        status = "🟢 EXCELLENT"
    elif audit_score >= 70:
        status = "🟡 GOOD"
    elif audit_score >= 50:
        status = "🟠 NEEDS ATTENTION"
    else:
        status = "🔴 CRITICAL"

    print(f"Label Audit Score: {audit_score}/100 - {status}")
    print(f"Issues Found: {issues}")
    print(f"Duplicate names: {len(duplicates)}")
    print(f"Unused labels: {len(unused_labels)}")
    print(f"Unnamed labels: {len(unnamed_labels)}")
    print(f"Similar labels: {len(similar_labels)} pairs")
    print(f"{'='*80}\n")

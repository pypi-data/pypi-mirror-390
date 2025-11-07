"""
Board standardization and Agile/Scrum conformity commands
"""

from ..client import get_client


# Standard Agile/Scrum list structure
STANDARD_LISTS = [
    {"name": "💡 Ideas/Discussion", "description": "Ideas and discussion topics"},
    {"name": "📥 Inbox", "description": "Unprocessed items"},
    {"name": "📋 Backlog", "description": "All pending work"},
    {"name": "📋 To Prioritize", "description": "Items ready for prioritization"},
    {"name": "🔍 Refinement", "description": "Items being refined"},
    {"name": "✅ Ready", "description": "Items ready for sprint"},
    {"name": "📐 Design/Specs", "description": "Design and specifications"},
    {"name": "📝 To Do (Sprint)", "description": "Sprint backlog"},
    {"name": "⚙️ In Progress", "description": "Work in progress (WIP limit: 3)"},
    {"name": "🧪 Testing", "description": "Ready for testing/review"},
    {"name": "✅ Done", "description": "Completed work"},
    {"name": "📚 Philosophy & Architecture", "description": "Architectural decisions and philosophy"},
]


def cmd_standardize_lists(board_id, template="agile", dry_run=False):
    """
    Standardize board lists according to a template.

    Templates:
    - agile: Full Agile/Scrum workflow
    - kanban: Simple Kanban (To Do, In Progress, Done)
    - basic: Basic workflow (Backlog, To Do, In Progress, Done)
    """
    client = get_client()
    board = client.get_board(board_id)
    current_lists = board.list_lists()

    # Get template
    if template == "agile":
        target_lists = STANDARD_LISTS
    elif template == "kanban":
        target_lists = [
            {"name": "📝 To Do", "description": "Work to be done"},
            {"name": "⚙️ In Progress", "description": "Work in progress"},
            {"name": "✅ Done", "description": "Completed work"},
        ]
    elif template == "basic":
        target_lists = [
            {"name": "📋 Backlog", "description": "All pending work"},
            {"name": "📝 To Do", "description": "Ready to work"},
            {"name": "⚙️ In Progress", "description": "Work in progress"},
            {"name": "✅ Done", "description": "Completed work"},
        ]
    else:
        print(f"❌ Unknown template: {template}")
        print("Available templates: agile, kanban, basic")
        return

    print(f"\n{'='*70}")
    print(f"STANDARDIZE LISTS - {board.name}")
    print(f"Template: {template.upper()}")
    print(f"{'='*70}\n")

    # Analyze current state
    current_names = [lst.name for lst in current_lists if not lst.closed]
    target_names = [lst["name"] for lst in target_lists]

    missing_lists = [lst for lst in target_lists if lst["name"] not in current_names]
    extra_lists = [lst for lst in current_lists if lst.name not in target_names and not lst.closed]

    print(f"📊 ANALYSIS:")
    print(f"   Current lists: {len(current_names)}")
    print(f"   Target lists: {len(target_names)}")
    print(f"   Missing lists: {len(missing_lists)}")
    print(f"   Extra lists: {len(extra_lists)}")
    print()

    if missing_lists:
        print(f"📝 MISSING LISTS (will be created):")
        for lst in missing_lists:
            print(f"   • {lst['name']}")
        print()

    if extra_lists:
        print(f"⚠️  EXTRA LISTS (not in template):")
        for lst in extra_lists:
            cards_count = len(lst.list_cards())
            print(f"   • {lst.name} ({cards_count} cards)")
        print()

    if not missing_lists and not extra_lists:
        print("✅ Board already follows the standard!")
        return

    if dry_run:
        print(f"{'='*70}")
        print("DRY RUN - No changes made")
        print(f"{'='*70}\n")
        return

    # Confirm
    print(f"{'='*70}")
    confirm = input(f"Apply standardization? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Standardization cancelled")
        return

    # Create missing lists
    created_count = 0
    for lst in missing_lists:
        try:
            board.add_list(lst["name"])
            print(f"✅ Created: {lst['name']}")
            created_count += 1
        except Exception as e:
            print(f"❌ Failed to create {lst['name']}: {str(e)}")

    print(f"\n{'='*70}")
    print(f"✅ Standardization complete!")
    print(f"   Created: {created_count} list(s)")
    print(f"   Extra lists: {len(extra_lists)} (not modified)")
    print(f"\n💡 Use 'trello scrum-check {board_id}' to validate Agile conformity")
    print(f"{'='*70}\n")


def cmd_scrum_check(board_id):
    """
    Check board conformity with Agile/Scrum best practices.

    Validates:
    - Required lists exist
    - WIP limits
    - Sprint size
    - Card distribution
    - Workflow health
    """
    client = get_client()
    board = client.get_board(board_id)
    lists = board.list_lists()

    print(f"\n{'='*70}")
    print(f"AGILE/SCRUM CONFORMITY CHECK - {board.name}")
    print(f"{'='*70}\n")

    issues = []
    score = 100

    # Required lists check
    required_keywords = {
        "Backlog": ["backlog", "📋"],
        "Ready": ["ready", "listo", "✅"],
        "Sprint/To Do": ["sprint", "to do", "todo", "📝"],
        "In Progress": ["in progress", "doing", "wip", "⚙️"],
        "Testing": ["testing", "test", "qa", "🧪"],
        "Done": ["done", "completed", "✅"],
    }

    print("📋 REQUIRED LISTS CHECK:\n")
    for list_type, keywords in required_keywords.items():
        found = False
        for lst in lists:
            if any(keyword in lst.name.lower() for keyword in keywords):
                found = True
                cards_count = len(lst.list_cards())
                print(f"✅ {list_type}: '{lst.name}' ({cards_count} cards)")
                break

        if not found:
            print(f"❌ {list_type}: MISSING")
            issues.append(f"Missing required list: {list_type}")
            score -= 15

    # WIP limit check (In Progress should have ≤3-5 cards)
    print(f"\n⚙️  WIP LIMITS CHECK:\n")
    for lst in lists:
        if any(keyword in lst.name.lower() for keyword in ["in progress", "doing", "wip"]):
            cards = lst.list_cards()
            card_count = len(cards)

            if card_count == 0:
                print(f"⚠️  {lst.name}: No cards (consider pulling work)")
            elif card_count <= 3:
                print(f"✅ {lst.name}: {card_count} cards (GOOD - within WIP limit)")
            elif card_count <= 5:
                print(f"🟡 {lst.name}: {card_count} cards (WARNING - near WIP limit)")
                issues.append(f"WIP near limit in '{lst.name}': {card_count}/5")
                score -= 5
            else:
                print(f"🔴 {lst.name}: {card_count} cards (CRITICAL - exceeds WIP limit)")
                issues.append(f"WIP exceeded in '{lst.name}': {card_count} (recommended: ≤5)")
                score -= 15

    # Sprint size check (Sprint/To Do should have 5-15 cards)
    print(f"\n📝 SPRINT SIZE CHECK:\n")
    for lst in lists:
        if any(keyword in lst.name.lower() for keyword in ["sprint", "to do"]) and \
           any(keyword in lst.name.lower() for keyword in ["sprint", "doing"]):
            cards = lst.list_cards()
            card_count = len(cards)

            if card_count == 0:
                print(f"⚠️  {lst.name}: Empty sprint")
            elif 5 <= card_count <= 15:
                print(f"✅ {lst.name}: {card_count} cards (GOOD sprint size)")
            elif card_count < 5:
                print(f"🟡 {lst.name}: {card_count} cards (Small sprint)")
                issues.append(f"Sprint too small: {card_count} cards (recommended: 5-15)")
                score -= 5
            else:
                print(f"🔴 {lst.name}: {card_count} cards (Overloaded sprint)")
                issues.append(f"Sprint too large: {card_count} cards (recommended: 5-15)")
                score -= 10

    # Testing queue check
    print(f"\n🧪 TESTING QUEUE CHECK:\n")
    for lst in lists:
        if any(keyword in lst.name.lower() for keyword in ["testing", "test", "qa", "review"]):
            cards = lst.list_cards()
            card_count = len(cards)

            if card_count == 0:
                print(f"✅ {lst.name}: No bottleneck")
            elif card_count <= 3:
                print(f"✅ {lst.name}: {card_count} cards (Healthy)")
            elif card_count <= 5:
                print(f"🟡 {lst.name}: {card_count} cards (Building up)")
                issues.append(f"Testing queue building: {card_count} cards")
                score -= 5
            else:
                print(f"🔴 {lst.name}: {card_count} cards (BOTTLENECK)")
                issues.append(f"Testing bottleneck: {card_count} cards")
                score -= 15

    # Backlog health check
    print(f"\n📋 BACKLOG HEALTH:\n")
    for lst in lists:
        if "backlog" in lst.name.lower():
            cards = lst.list_cards()
            card_count = len(cards)

            if card_count == 0:
                print(f"⚠️  {lst.name}: Empty backlog (no future work)")
                issues.append("Empty backlog")
                score -= 10
            elif card_count < 10:
                print(f"🟡 {lst.name}: {card_count} cards (Low - needs grooming)")
                issues.append(f"Low backlog: {card_count} cards")
                score -= 5
            elif card_count <= 50:
                print(f"✅ {lst.name}: {card_count} cards (Healthy)")
            else:
                print(f"🟡 {lst.name}: {card_count} cards (Large - consider prioritization)")

    # Summary
    print(f"\n{'='*70}")
    print(f"CONFORMITY SCORE: {score}/100")

    if score >= 90:
        status = "🟢 EXCELLENT - Following Agile best practices"
    elif score >= 70:
        status = "🟡 GOOD - Minor improvements needed"
    elif score >= 50:
        status = "🟠 NEEDS WORK - Several issues found"
    else:
        status = "🔴 CRITICAL - Major conformity issues"

    print(f"Status: {status}")

    if issues:
        print(f"\n⚠️  ISSUES FOUND ({len(issues)}):")
        for issue in issues:
            print(f"   • {issue}")

    print(f"\n💡 Recommendations:")
    if score < 90:
        print(f"   • Run 'trello standardize-lists {board_id}' to create missing lists")
    if any("WIP" in issue for issue in issues):
        print(f"   • Move cards from 'In Progress' to reduce WIP")
    if any("bottleneck" in issue.lower() for issue in issues):
        print(f"   • Address testing bottleneck - allocate more QA resources")
    if any("Sprint" in issue for issue in issues):
        print(f"   • Adjust sprint planning - aim for 5-15 cards per sprint")

    print(f"{'='*70}\n")


def cmd_migrate_cards(source_list_id, target_board_id, target_list_name=""):
    """
    Migrate cards from one list to another board.
    Useful for reorganizing boards or splitting projects.
    """
    client = get_client()
    source_list = client.get_list(source_list_id)
    target_board = client.get_board(target_board_id)

    cards = source_list.list_cards()

    if not cards:
        print(f"No cards found in list '{source_list.name}'")
        return

    # Find target list
    target_list = None
    if target_list_name:
        for lst in target_board.list_lists():
            if lst.name == target_list_name or target_list_name.lower() in lst.name.lower():
                target_list = lst
                break

    if not target_list:
        # Use first list if not specified
        lists = target_board.list_lists()
        target_list = lists[0] if lists else None

    if not target_list:
        print(f"❌ Could not find target list in board '{target_board.name}'")
        return

    print(f"\n{'='*70}")
    print(f"MIGRATE CARDS")
    print(f"{'='*70}")
    print(f"From: {source_list.name}")
    print(f"To:   {target_board.name} → {target_list.name}")
    print(f"Cards: {len(cards)}")
    print(f"{'='*70}\n")

    for card in cards:
        print(f"  • {card.name[:60]}")

    confirm = input(f"\n⚠️  Migrate {len(cards)} cards? (yes/no): ")
    if confirm.lower() != 'yes':
        print("❌ Migration cancelled")
        return

    migrated_count = 0
    for card in cards:
        try:
            card.change_board(target_board.id, target_list.id)
            print(f"✅ Migrated: {card.name[:60]}")
            migrated_count += 1
        except Exception as e:
            print(f"❌ Failed to migrate '{card.name[:60]}': {str(e)}")

    print(f"\n{'='*70}")
    print(f"✅ Migration complete: {migrated_count}/{len(cards)} cards")
    print(f"{'='*70}\n")


def cmd_list_templates():
    """
    Show available board templates and their list structures.
    """
    templates = {
        "agile": {
            "name": "Agile/Scrum (Full)",
            "description": "Complete Agile workflow with refinement and ready stages",
            "lists": STANDARD_LISTS
        },
        "kanban": {
            "name": "Kanban (Simple)",
            "description": "Simple three-column Kanban board",
            "lists": [
                {"name": "📝 To Do", "description": "Work to be done"},
                {"name": "⚙️ In Progress", "description": "Work in progress"},
                {"name": "✅ Done", "description": "Completed work"},
            ]
        },
        "basic": {
            "name": "Basic Workflow",
            "description": "Four-stage workflow for simple projects",
            "lists": [
                {"name": "📋 Backlog", "description": "All pending work"},
                {"name": "📝 To Do", "description": "Ready to work"},
                {"name": "⚙️ In Progress", "description": "Work in progress"},
                {"name": "✅ Done", "description": "Completed work"},
            ]
        }
    }

    print(f"\n{'='*70}")
    print(f"AVAILABLE BOARD TEMPLATES")
    print(f"{'='*70}\n")

    for template_id, template in templates.items():
        print(f"📋 {template['name']} (ID: {template_id})")
        print(f"   {template['description']}")
        print(f"   Lists ({len(template['lists'])}):")
        for lst in template['lists']:
            print(f"      • {lst['name']}")
        print()

    print(f"{'='*70}")
    print(f"Usage:")
    print(f"  trello standardize-lists <board_id> <template_id>")
    print(f"  trello standardize-lists <board_id> agile --dry-run")
    print(f"{'='*70}\n")

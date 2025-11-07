#!/usr/bin/env python3
"""
Trello CLI - Main command-line interface
"""

import sys
import warnings

# Suppress urllib3 NotOpenSSLWarning - this is a system-level SSL library issue
# that doesn't affect Trello CLI functionality with HTTPS requests
warnings.filterwarnings('ignore', message='.*urllib3 v2 only supports OpenSSL.*')

from . import __version__
from .config import configure_interactive
from .plugins import cmd_plugin_list, cmd_plugin_info, cmd_plugin_run
from .client import get_client
from .commands import (
    # Basic commands
    cmd_boards, cmd_create_board,
    cmd_lists, cmd_create_list, cmd_archive_list,
    cmd_cards, cmd_add_card, cmd_show_card,
    cmd_update_card, cmd_move_card, cmd_rename_card,
    cmd_add_checklist, cmd_add_checkitem,
    cmd_set_due, cmd_add_comment, cmd_delete_card,
    cmd_add_label, cmd_remove_label, cmd_delete_label, cmd_rename_label,
    # Help & Discovery
    cmd_help, cmd_help_json,
    cmd_board_overview, cmd_board_ids, cmd_search_cards,
    # Bulk operations
    cmd_bulk_move_cards, cmd_bulk_add_label, cmd_bulk_set_due,
    cmd_bulk_archive_cards, cmd_bulk_create_cards,
    cmd_bulk_relabel, cmd_label_backup, cmd_label_restore,
    # Quick commands
    cmd_quick_start, cmd_quick_test, cmd_quick_done,
    cmd_my_cards, cmd_card_age,
    # Sprint planning
    cmd_sprint_start, cmd_sprint_status, cmd_sprint_close, cmd_sprint_velocity,
    # Advanced queries
    cmd_cards_by_label, cmd_cards_due_soon, cmd_cards_overdue,
    cmd_list_metrics, cmd_board_health,
    # Board standardization
    cmd_standardize_lists, cmd_scrum_check, cmd_migrate_cards, cmd_list_templates,
    # Board migration
    cmd_migrate_board, cmd_archive_board,
    # Audit commands
    cmd_board_audit, cmd_list_audit, cmd_list_snapshot, cmd_sprint_audit, cmd_label_audit,
    # Member management
    cmd_assign_card, cmd_unassign_card, cmd_card_log,
    # Export
    cmd_export_board,
    # Validation
    cmd_validation_status, cmd_validation_enable, cmd_validation_disable,
    cmd_validation_config, cmd_validation_reload, cmd_validation_reset,
    # Reporting
    BoardReporter,
    # Checklist operations
    cmd_check, cmd_uncheck, cmd_checklist_status
)

HELP_TEXT = """
Trello CLI v{version} - Official Python command-line interface for Trello
AI-powered project intelligence with Claude daemon integration

🎯 FOR AI USERS - QUICK START:
  1. trello feedback <board_id>          🧠 Get intelligent board analysis (Claude AI)
  2. trello report <board_id>            📊 Detailed report (duplicates, orphans, frozen cards, fake done)
  3. trello score <board_id>             📈 Board integrity score (0-100)
  4. trello checklist-status <card_id>   📋 See item-by-item progress
  5. trello check <card_id> "List" "Item" ✅ Complete items with anti-fraud validation

Usage: trello <command> [arguments]

HELP & CONFIGURATION:
  config                      Configure API credentials
  help                        Show this help message
  help-json                   Get all commands in JSON format (for Claude Code)
  daemon-status               Show Claude Daemon status & capabilities

DISCOVERY COMMANDS (for exploration):
  board-overview <board_id>   Complete board structure with card counts
  board-ids <board_id>        Quick reference of all IDs in a board
  search-cards <board_id> "query"   Search cards across all lists

QUICK COMMANDS (shortcuts):
  quick-start <card_id>       Move to "In Progress" + add comment
  quick-test <card_id>        Move to "Testing" + add comment
  quick-done <card_id>        Move to "Done" + add comment
  my-cards <board_id>         Show all your assigned cards
  card-age <list_id>          Show how long cards have been in list

SPRINT PLANNING:
  sprint-start <board_id>     Start sprint (move Ready → Sprint)
  sprint-status <board_id>    Show current sprint status
  sprint-close <board_id>     Close sprint and move unfinished cards
  sprint-velocity <board_id>  Calculate sprint velocity

BULK OPERATIONS:
  bulk-move-cards <source_list> <target_list> ["filter"]
  bulk-add-label <file> <color> ["name"]
  bulk-set-due <file> <date>
  bulk-archive-cards <list_id> ["filter"]
  bulk-create-cards <list_id> <csv/json_file>
  bulk-relabel <board_id> <from_label> <to_label> [--dry-run]

LABEL BACKUP & RECOVERY:
  label-backup <board_id> [output_file]         Backup all label assignments
  label-restore <board_id> <backup_file>        Restore labels from backup

ADVANCED QUERIES:
  cards-by-label <board_id> <color> ["name"]
  cards-due-soon <board_id> [days]
  cards-overdue <board_id>
  list-metrics <list_id>
  board-health <board_id>

BOARD STANDARDIZATION (Agile/Scrum):
  list-templates              Show available board templates
  standardize-lists <board_id> <template> [--dry-run]
  scrum-check <board_id>      Validate Agile/Scrum conformity
  migrate-cards <list_id> <target_board_id> ["target_list"]

MEMBER MANAGEMENT:
  assign-card <card_id> <member>        Assign member to card (use 'me' for self)
  unassign-card <card_id> <member>      Remove member from card
  card-log <card_id> [limit]            Show card action history

AUDIT & ANALYSIS (Expose Structural Chaos):
  board-audit <board_id> ["pattern"] [--report-json] [--fix-labels]
                                        🔍 Comprehensive workflow audit:
                                        - Cards in Done without due dates
                                        - Cards in Done with incomplete checklists
                                        - Active cards without due dates
                                        - Overdue zombie tasks
                                        - Execution cards without owners
                                        - Empty checklists (fake productivity)
                                        - Pattern violations & missing descriptions
                                        Flags: --report-json (JSON output)
                                               --fix-labels (auto-fix duplicates)
  list-audit <list_id> ["pattern"]      Detailed list audit
  list-snapshot <list_id> ["file.json"] Export list to JSON snapshot
  sprint-audit <board_id> ["sprint"]    Sprint-specific audit (dates, overdue)
  label-audit <board_id>                Label audit (duplicates, unused, typos)

BOARD INTELLIGENCE (Claude Daemon + AI Analysis):
  report <board_id>               📊 Detailed board report showing:
                                     - Duplicated cards (similitude ≥33%)
                                     - Orphaned tasks (no description, no subtasks)
                                     - Frozen progress (>7 days without movement)
                                     - Fake completion (Done but items incomplete)
                                     - Missing evidence (no PR/commit/deployment)
                                     Example: trello report 68fcf05e481843db13204397

  feedback <board_id>             🧠 AI-powered qualitative analysis (requires Claude SDK):
                                     - Current board health status (Healthy/Fragile/Chaotic/Broken)
                                     - Top critical issues identified
                                     - Specific actionable recommendations
                                     - Insights about team workflow patterns
                                     Set ANTHROPIC_API_KEY for Claude AI feedback
                                     Fallback: heuristic analysis if API unavailable

  score <board_id>                📈 Integrity score (0-100) based on 5 weighted axes:
                                     • Structure (25%): Lists organized, clear states
                                     • Clarity (20%): Cards have descriptions, scope defined
                                     • Progress (20%): Tasks moving, no stuck cards
                                     • Evidence (20%): PRs, commits, deployments referenced
                                     • Health (15%): No duplicates, no orphans, no chaos

CHECKLIST ITEM OPERATIONS (Item-level progress tracking):
  check <card_id> "List" "Item"   ✅ Mark checklist item complete with anti-fraud validation:
                                     - If completing last item, requires card description + PR/commit
                                     - Shows real-time progress (3/7 items done)
                                     - Prevents fake completion (can't mark Done without proof)
                                     Example: trello check 68fd24640bf4 \"Implementation\" \"Setup\"

  uncheck <card_id> "List" "Item" ↩️  Mark checklist item incomplete (undo check)
                                     Example: trello uncheck 68fd24640bf4 \"Implementation\" \"Setup\"

  checklist-status <card_id>      📋 Show ALL checklist items with progress bars:
                                     ████████░░ 8/10 items (80%)
                                     ✅ Completed items listed first
                                     ⭕ Incomplete items with count remaining
                                     Example: trello checklist-status 68fd24640bf4

EXPORT & REPORTING:
  export-board <board_id> <format> ["file"]  Export board (json/csv/md)

PLUGINS (EXTENSIBILITY):
  plugin list [--plugin-dir DIR]             List available plugins
  plugin info <name> [--plugin-dir DIR]      Show plugin details
  plugin run <name> [args] [--plugin-dir DIR] Execute a plugin

VALIDATION RULES (ENFORCE SCRUM PRACTICES):
  validation-status                Show validation rules status
  validation-enable                Enable validation system
  validation-disable               Disable validation system
  validation-config                Show/edit configuration
  validation-reload                Reload config from file
  validation-reset                 Reset to default rules

BASIC BOARD/LIST/CARD COMMANDS:
  boards                      List all boards
  lists <board_id>            List all lists
  cards <list_id>             List cards in list
  add-card <list_id> "title" ["desc"]
  show-card <card_id>
  update-card <card_id> "desc"
  rename-card <card_id> "title"         Rename card (update title)
  move-card <card_id> <list_id>
  delete-card <card_id>                 Delete a card permanently
  add-label <card_id> "color" ["name"]
  remove-label <card_id> "label"        Remove label from card
  delete-label <board_id> "label"       Delete label from board
  rename-label <board_id> "label" "new" Rename label on board
  add-checklist <card_id> "name"
  set-due <card_id> "YYYY-MM-DD"
  add-comment <card_id> "text"

═══════════════════════════════════════════════════════════════════════════════

⚡ WORKFLOW EXAMPLES FOR AI USERS:

1. UNDERSTAND YOUR BOARD'S HEALTH
   trello feedback board_123
   → Get Claude's assessment of what's wrong

   Then zoom in:
   trello report board_123
   → See exactly what cards are problematic

2. COMPLETE WORK ITEM BY ITEM
   trello checklist-status card_456
   → See what's left to do

   trello check card_456 "Implementation" "Write tests"
   → Mark done with validation

   System validates: \"Can't mark done without PR reference\"

   Fix description → trello check again → ✅ Complete

3. GET INTEGRITY METRICS
   trello score board_123
   → See 5 axes breakdown
   → Identify weakest areas
   → Know what to prioritize

═══════════════════════════════════════════════════════════════════════════════

🔐 ANTI-FRAUD FEATURES (Prevent Fake Completion):

The system BLOCKS these patterns:
  ❌ Marking card Done without PR/commit reference
  ❌ Completing last checklist item without proof of work
  ❌ Creating duplicate cards repeatedly (fraud detection)
  ❌ Jumping from To Do → Done (skipping workflow states)

The system EDUCATES:
  ✅ Shows exactly what's missing (\"Needs PR reference\")
  ✅ Recommends what to add (\"Add deployment notes\")
  ✅ Suggests next actions (\"Complete remaining 3 items\")

═══════════════════════════════════════════════════════════════════════════════

🧠 CLAUDE AI INTEGRATION:

For intelligent feedback, set your API key:
  export ANTHROPIC_API_KEY=\"sk-...\"

Then use:
  trello feedback board_123

Claude will analyze:
  • Board patterns (healthy vs chaotic)
  • Specific problems ranked by severity
  • Actionable next steps (not generic advice)
  • Team workflow insights

Without API key: falls back to heuristic analysis (still useful)

═══════════════════════════════════════════════════════════════════════════════

📖 ENVIRONMENT VARIABLES:

ANTHROPIC_API_KEY        Claude AI integration (for intelligent feedback)
                         Example: export ANTHROPIC_API_KEY=\"sk-ant-...\"

═══════════════════════════════════════════════════════════════════════════════

For detailed help, run: trello help-json
For more information, see: README.md and CLAUDE.md
For Claude Daemon docs, see: claude-daemon/README.md
""".format(version=__version__)


def main():
    """Main CLI entry point"""
    if len(sys.argv) < 2:
        print(HELP_TEXT)
        sys.exit(1)

    command = sys.argv[1]

    try:
        if command == 'config':
            configure_interactive()

        elif command in ['-h', '--help', 'help']:
            cmd_help()

        elif command == 'help-json':
            cmd_help_json()

        elif command == 'board-overview':
            if len(sys.argv) < 3:
                print("❌ Usage: trello board-overview <board_id>")
                sys.exit(1)
            cmd_board_overview(sys.argv[2])

        elif command == 'board-ids':
            if len(sys.argv) < 3:
                print("❌ Usage: trello board-ids <board_id>")
                sys.exit(1)
            cmd_board_ids(sys.argv[2])

        elif command == 'search-cards':
            if len(sys.argv) < 4:
                print("❌ Usage: trello search-cards <board_id> \"query\"")
                sys.exit(1)
            cmd_search_cards(sys.argv[2], sys.argv[3])

        elif command == 'boards':
            cmd_boards()

        elif command == 'create-board':
            if len(sys.argv) < 3:
                print("❌ Usage: trello create-board \"name\"")
                sys.exit(1)
            cmd_create_board(sys.argv[2])

        elif command == 'lists':
            if len(sys.argv) < 3:
                print("❌ Usage: trello lists <board_id>")
                sys.exit(1)
            cmd_lists(sys.argv[2])

        elif command == 'create-list':
            if len(sys.argv) < 4:
                print("❌ Usage: trello create-list <board_id> \"name\"")
                sys.exit(1)
            cmd_create_list(sys.argv[2], sys.argv[3])

        elif command == 'archive-list':
            if len(sys.argv) < 3:
                print("❌ Usage: trello archive-list <list_id>")
                sys.exit(1)
            cmd_archive_list(sys.argv[2])

        elif command == 'cards':
            if len(sys.argv) < 3:
                print("❌ Usage: trello cards <list_id>")
                sys.exit(1)
            cmd_cards(sys.argv[2])

        elif command == 'add-card':
            if len(sys.argv) < 4:
                print("❌ Usage: trello add-card <list_id> \"title\" [--description \"description\"]")
                sys.exit(1)

            # Parse description - support both positional and --description flag
            description = ""
            if len(sys.argv) > 4:
                if sys.argv[4] == '--description' and len(sys.argv) > 5:
                    description = sys.argv[5]
                else:
                    # Legacy support: positional description argument
                    description = sys.argv[4]

            cmd_add_card(sys.argv[2], sys.argv[3], description)

        elif command == 'show-card':
            if len(sys.argv) < 3:
                print("❌ Usage: trello show-card <card_id>")
                sys.exit(1)
            cmd_show_card(sys.argv[2])

        elif command == 'update-card':
            if len(sys.argv) < 4:
                print("❌ Usage: trello update-card <card_id> [--description] \"description\"")
                sys.exit(1)

            # Parse description - support both positional and --description flag
            description = ""
            if sys.argv[3] == '--description' and len(sys.argv) > 4:
                description = sys.argv[4]
            else:
                # Legacy support: positional description argument
                description = sys.argv[3]

            cmd_update_card(sys.argv[2], description)

        elif command == 'rename-card':
            if len(sys.argv) < 4:
                print("❌ Usage: trello rename-card <card_id> \"new_title\"")
                sys.exit(1)
            cmd_rename_card(sys.argv[2], sys.argv[3])

        elif command == 'move-card':
            if len(sys.argv) < 4:
                print("❌ Usage: trello move-card <card_id> <list_id> [--done]")
                sys.exit(1)
            explicit_done = '--done' in sys.argv
            cmd_move_card(sys.argv[2], sys.argv[3], explicit_done)

        elif command == 'add-label':
            if len(sys.argv) < 4:
                print("❌ Usage: trello add-label <card_id> \"color\" [\"name\"]")
                sys.exit(1)
            label_name = sys.argv[4] if len(sys.argv) > 4 else ""
            cmd_add_label(sys.argv[2], sys.argv[3], label_name)

        elif command == 'remove-label':
            if len(sys.argv) < 4:
                print("❌ Usage: trello remove-label <card_id> \"label_name|color|id\"")
                sys.exit(1)
            cmd_remove_label(sys.argv[2], sys.argv[3])

        elif command == 'delete-label':
            if len(sys.argv) < 4:
                print("❌ Usage: trello delete-label <board_id> \"label_name|color|id\"")
                sys.exit(1)
            cmd_delete_label(sys.argv[2], sys.argv[3])

        elif command == 'rename-label':
            if len(sys.argv) < 5:
                print("❌ Usage: trello rename-label <board_id> \"current_label\" \"new_name\"")
                sys.exit(1)
            cmd_rename_label(sys.argv[2], sys.argv[3], sys.argv[4])

        elif command == 'add-checklist':
            if len(sys.argv) < 4:
                print("❌ Usage: trello add-checklist <card_id> \"name\"")
                sys.exit(1)
            cmd_add_checklist(sys.argv[2], sys.argv[3])

        elif command == 'add-checkitem':
            if len(sys.argv) < 5:
                print("❌ Usage: trello add-checkitem <card_id> \"checklist\" \"item\"")
                sys.exit(1)
            cmd_add_checkitem(sys.argv[2], sys.argv[3], sys.argv[4])

        elif command == 'set-due':
            if len(sys.argv) < 4:
                print("❌ Usage: trello set-due <card_id> \"YYYY-MM-DD\"")
                sys.exit(1)
            cmd_set_due(sys.argv[2], sys.argv[3])

        elif command == 'add-comment':
            if len(sys.argv) < 4:
                print("❌ Usage: trello add-comment <card_id> \"comment\"")
                sys.exit(1)
            cmd_add_comment(sys.argv[2], sys.argv[3])

        elif command == 'delete-card':
            if len(sys.argv) < 3:
                print("❌ Usage: trello delete-card <card_id>")
                sys.exit(1)
            cmd_delete_card(sys.argv[2])

        # Quick Commands
        elif command == 'quick-start':
            if len(sys.argv) < 3:
                print("❌ Usage: trello quick-start <card_id> [\"comment\"]")
                sys.exit(1)
            comment = sys.argv[3] if len(sys.argv) > 3 else "Started working on this"
            cmd_quick_start(sys.argv[2], comment)

        elif command == 'quick-test':
            if len(sys.argv) < 3:
                print("❌ Usage: trello quick-test <card_id> [\"comment\"]")
                sys.exit(1)
            comment = sys.argv[3] if len(sys.argv) > 3 else "Ready for testing"
            cmd_quick_test(sys.argv[2], comment)

        elif command == 'quick-done':
            if len(sys.argv) < 3:
                print("❌ Usage: trello quick-done <card_id> [\"comment\"]")
                sys.exit(1)
            comment = sys.argv[3] if len(sys.argv) > 3 else "Completed and verified"
            cmd_quick_done(sys.argv[2], comment)

        elif command == 'my-cards':
            if len(sys.argv) < 3:
                print("❌ Usage: trello my-cards <board_id> [\"member_name\"]")
                sys.exit(1)
            member_name = sys.argv[3] if len(sys.argv) > 3 else ""
            cmd_my_cards(sys.argv[2], member_name)

        elif command == 'card-age':
            if len(sys.argv) < 3:
                print("❌ Usage: trello card-age <list_id>")
                sys.exit(1)
            cmd_card_age(sys.argv[2])

        # Sprint Planning Commands
        elif command == 'sprint-start':
            if len(sys.argv) < 3:
                print("❌ Usage: trello sprint-start <board_id>")
                sys.exit(1)
            cmd_sprint_start(sys.argv[2])

        elif command == 'sprint-status':
            if len(sys.argv) < 3:
                print("❌ Usage: trello sprint-status <board_id>")
                sys.exit(1)
            cmd_sprint_status(sys.argv[2])

        elif command == 'sprint-close':
            if len(sys.argv) < 3:
                print("❌ Usage: trello sprint-close <board_id>")
                sys.exit(1)
            cmd_sprint_close(sys.argv[2])

        elif command == 'sprint-velocity':
            if len(sys.argv) < 3:
                print("❌ Usage: trello sprint-velocity <board_id> [num_sprints]")
                sys.exit(1)
            num_sprints = int(sys.argv[3]) if len(sys.argv) > 3 else 3
            cmd_sprint_velocity(sys.argv[2], num_sprints)

        # Bulk Operations
        elif command == 'bulk-move-cards':
            if len(sys.argv) < 4:
                print("❌ Usage: trello bulk-move-cards <source_list_id> <target_list_id> [\"filter\"]")
                sys.exit(1)
            filter_query = sys.argv[4] if len(sys.argv) > 4 else ""
            cmd_bulk_move_cards(sys.argv[2], sys.argv[3], filter_query)

        elif command == 'bulk-add-label':
            if len(sys.argv) < 4:
                print("❌ Usage: trello bulk-add-label <card_ids_file> <color> [\"name\"]")
                sys.exit(1)
            label_name = sys.argv[4] if len(sys.argv) > 4 else ""
            cmd_bulk_add_label(sys.argv[2], sys.argv[3], label_name)

        elif command == 'bulk-set-due':
            if len(sys.argv) < 4:
                print("❌ Usage: trello bulk-set-due <card_ids_file> <date>")
                sys.exit(1)
            cmd_bulk_set_due(sys.argv[2], sys.argv[3])

        elif command == 'bulk-archive-cards':
            if len(sys.argv) < 3:
                print("❌ Usage: trello bulk-archive-cards <list_id> [\"filter\"]")
                sys.exit(1)
            filter_query = sys.argv[3] if len(sys.argv) > 3 else ""
            cmd_bulk_archive_cards(sys.argv[2], filter_query)

        elif command == 'bulk-create-cards':
            if len(sys.argv) < 4:
                print("❌ Usage: trello bulk-create-cards <list_id> <csv/json_file>")
                sys.exit(1)
            cmd_bulk_create_cards(sys.argv[2], sys.argv[3])

        elif command == 'bulk-relabel':
            if len(sys.argv) < 5:
                print("❌ Usage: trello bulk-relabel <board_id> <from_label> <to_label> [--dry-run]")
                sys.exit(1)
            dry_run = '--dry-run' in sys.argv
            cmd_bulk_relabel(sys.argv[2], sys.argv[3], sys.argv[4], dry_run)

        elif command == 'label-backup':
            if len(sys.argv) < 3:
                print("❌ Usage: trello label-backup <board_id> [output_file]")
                sys.exit(1)
            output_file = sys.argv[3] if len(sys.argv) > 3 else "label_backup.json"
            cmd_label_backup(sys.argv[2], output_file)

        elif command == 'label-restore':
            if len(sys.argv) < 4:
                print("❌ Usage: trello label-restore <board_id> <backup_file>")
                sys.exit(1)
            cmd_label_restore(sys.argv[2], sys.argv[3])

        # Advanced Query Commands
        elif command == 'cards-by-label':
            if len(sys.argv) < 4:
                print("❌ Usage: trello cards-by-label <board_id> <color> [\"name\"]")
                sys.exit(1)
            label_name = sys.argv[4] if len(sys.argv) > 4 else ""
            cmd_cards_by_label(sys.argv[2], sys.argv[3], label_name)

        elif command == 'cards-due-soon':
            if len(sys.argv) < 3:
                print("❌ Usage: trello cards-due-soon <board_id> [days]")
                sys.exit(1)
            days = int(sys.argv[3]) if len(sys.argv) > 3 else 7
            cmd_cards_due_soon(sys.argv[2], days)

        elif command == 'cards-overdue':
            if len(sys.argv) < 3:
                print("❌ Usage: trello cards-overdue <board_id>")
                sys.exit(1)
            cmd_cards_overdue(sys.argv[2])

        elif command == 'list-metrics':
            if len(sys.argv) < 3:
                print("❌ Usage: trello list-metrics <list_id>")
                sys.exit(1)
            cmd_list_metrics(sys.argv[2])

        elif command == 'board-health':
            if len(sys.argv) < 3:
                print("❌ Usage: trello board-health <board_id>")
                sys.exit(1)
            cmd_board_health(sys.argv[2])

        # Board Standardization Commands
        elif command == 'list-templates':
            cmd_list_templates()

        elif command == 'standardize-lists':
            if len(sys.argv) < 3:
                print("❌ Usage: trello standardize-lists <board_id> [template] [--dry-run]")
                sys.exit(1)
            template = sys.argv[3] if len(sys.argv) > 3 else "agile"
            dry_run = "--dry-run" in sys.argv or "-n" in sys.argv
            cmd_standardize_lists(sys.argv[2], template, dry_run)

        elif command == 'scrum-check':
            if len(sys.argv) < 3:
                print("❌ Usage: trello scrum-check <board_id>")
                sys.exit(1)
            cmd_scrum_check(sys.argv[2])

        elif command == 'migrate-cards':
            if len(sys.argv) < 4:
                print("❌ Usage: trello migrate-cards <source_list_id> <target_board_id> [\"target_list\"]")
                sys.exit(1)
            target_list = sys.argv[4] if len(sys.argv) > 4 else ""
            cmd_migrate_cards(sys.argv[2], sys.argv[3], target_list)

        elif command == 'migrate-board':
            if len(sys.argv) < 4:
                print("❌ Usage: trello migrate-board <source_board_id> <target_board_id> [--dry-run]")
                sys.exit(1)
            dry_run = '--dry-run' in sys.argv
            cmd_migrate_board(sys.argv[2], sys.argv[3], dry_run)

        elif command == 'archive-board':
            if len(sys.argv) < 3:
                print("❌ Usage: trello archive-board <board_id>")
                sys.exit(1)
            cmd_archive_board(sys.argv[2])

        # Audit Commands
        elif command == 'board-audit':
            if len(sys.argv) < 3:
                print("❌ Usage: trello board-audit <board_id> [\"pattern\"] [--report-json] [--fix-labels]")
                print("\nFlags:")
                print("  --report-json    Output audit results in JSON format")
                print("  --fix-labels     Automatically fix duplicate labels")
                sys.exit(1)

            # Parse arguments and flags
            board_id = sys.argv[2]
            pattern = None
            report_json = False
            fix_labels = False

            for i in range(3, len(sys.argv)):
                arg = sys.argv[i]
                if arg == '--report-json':
                    report_json = True
                elif arg == '--fix-labels':
                    fix_labels = True
                elif not pattern and not arg.startswith('--'):
                    pattern = arg

            cmd_board_audit(board_id, pattern, fix_labels, report_json)

        elif command == 'list-audit':
            if len(sys.argv) < 3:
                print("❌ Usage: trello list-audit <list_id> [\"pattern\"]")
                sys.exit(1)
            pattern = sys.argv[3] if len(sys.argv) > 3 else None
            cmd_list_audit(sys.argv[2], pattern)

        elif command == 'list-snapshot':
            if len(sys.argv) < 3:
                print("❌ Usage: trello list-snapshot <list_id> [\"output_file.json\"]")
                sys.exit(1)
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            cmd_list_snapshot(sys.argv[2], output_file)

        elif command == 'sprint-audit':
            if len(sys.argv) < 3:
                print("❌ Usage: trello sprint-audit <board_id> [\"sprint_label\"]")
                sys.exit(1)
            sprint_label = sys.argv[3] if len(sys.argv) > 3 else None
            cmd_sprint_audit(sys.argv[2], sprint_label)

        elif command == 'label-audit':
            if len(sys.argv) < 3:
                print("❌ Usage: trello label-audit <board_id>")
                sys.exit(1)
            cmd_label_audit(sys.argv[2])

        # Member Management Commands
        elif command == 'assign-card':
            if len(sys.argv) < 4:
                print("❌ Usage: trello assign-card <card_id> <member_username|name|'me'>")
                sys.exit(1)
            cmd_assign_card(sys.argv[2], sys.argv[3])

        elif command == 'unassign-card':
            if len(sys.argv) < 4:
                print("❌ Usage: trello unassign-card <card_id> <member_username|name|'me'>")
                sys.exit(1)
            cmd_unassign_card(sys.argv[2], sys.argv[3])

        elif command == 'card-log':
            if len(sys.argv) < 3:
                print("❌ Usage: trello card-log <card_id> [limit]")
                sys.exit(1)
            limit = int(sys.argv[3]) if len(sys.argv) > 3 else 50
            cmd_card_log(sys.argv[2], limit)

        # Export Commands
        elif command == 'export-board':
            if len(sys.argv) < 4:
                print("❌ Usage: trello export-board <board_id> <json|csv|md> [\"output_file\"]")
                sys.exit(1)
            output_file = sys.argv[4] if len(sys.argv) > 4 else None
            cmd_export_board(sys.argv[2], sys.argv[3], output_file)

        # Checklist Item Operations
        elif command == 'check':
            if len(sys.argv) < 5:
                print('❌ Usage: trello check <card_id> "Checklist Name" "Item Name"')
                sys.exit(1)
            checklist_name = sys.argv[3]
            item_name = sys.argv[4]
            cmd_check(sys.argv[2], checklist_name, item_name)

        elif command == 'uncheck':
            if len(sys.argv) < 5:
                print('❌ Usage: trello uncheck <card_id> "Checklist Name" "Item Name"')
                sys.exit(1)
            checklist_name = sys.argv[3]
            item_name = sys.argv[4]
            cmd_uncheck(sys.argv[2], checklist_name, item_name)

        elif command == 'checklist-status':
            if len(sys.argv) < 3:
                print("❌ Usage: trello checklist-status <card_id>")
                sys.exit(1)
            cmd_checklist_status(sys.argv[2])

        # Board Intelligence (Claude Daemon - Reporting)
        elif command == 'report':
            if len(sys.argv) < 3:
                print("❌ Usage: trello report <board_id>")
                sys.exit(1)
            trello_client = get_client()
            reporter = BoardReporter(trello_client)
            print(reporter.get_board_report(sys.argv[2]))

        elif command == 'feedback':
            if len(sys.argv) < 3:
                print("❌ Usage: trello feedback <board_id>")
                sys.exit(1)
            trello_client = get_client()
            reporter = BoardReporter(trello_client)
            print(reporter.get_board_feedback(sys.argv[2]))

        elif command == 'score':
            if len(sys.argv) < 3:
                print("❌ Usage: trello score <board_id>")
                sys.exit(1)
            trello_client = get_client()
            reporter = BoardReporter(trello_client)
            print(reporter.get_board_score(sys.argv[2]))

        # Validation Commands
        elif command == 'validation-status':
            cmd_validation_status()

        elif command == 'validation-enable':
            cmd_validation_enable()

        elif command == 'validation-disable':
            cmd_validation_disable()

        elif command == 'validation-config':
            cmd_validation_config()

        elif command == 'validation-reload':
            cmd_validation_reload()

        elif command == 'validation-reset':
            cmd_validation_reset()

        # Plugin Commands
        elif command == 'plugin':
            if len(sys.argv) < 3:
                print("❌ Usage: trello plugin <list|info|run> [args]")
                print("\n  plugin list                    - List all plugins")
                print("  plugin info <name>             - Show plugin details")
                print("  plugin run <name> [args]       - Execute a plugin")
                print("\n  Optional: --plugin-dir <path>  - Use custom plugin directory")
                sys.exit(1)

            subcommand = sys.argv[2]

            # Extract --plugin-dir if present
            plugin_dir = None
            if '--plugin-dir' in sys.argv:
                idx = sys.argv.index('--plugin-dir')
                if idx + 1 < len(sys.argv):
                    plugin_dir = sys.argv[idx + 1]
                    # Remove --plugin-dir and its value from argv
                    sys.argv.pop(idx)
                    sys.argv.pop(idx)

            if subcommand == 'list':
                cmd_plugin_list(plugin_dir)

            elif subcommand == 'info':
                if len(sys.argv) < 4:
                    print("❌ Usage: trello plugin info <name>")
                    sys.exit(1)
                cmd_plugin_info(sys.argv[3], plugin_dir)

            elif subcommand == 'run':
                if len(sys.argv) < 4:
                    print("❌ Usage: trello plugin run <name> [args]")
                    sys.exit(1)
                plugin_name = sys.argv[3]
                plugin_args = sys.argv[4:]
                cmd_plugin_run(plugin_name, plugin_args, plugin_dir)

            else:
                print(f"❌ Unknown plugin subcommand: {subcommand}")
                print("   Valid subcommands: list, info, run")
                sys.exit(1)

        elif command in ['-v', '--version', 'version']:
            print(f"Trello CLI v{__version__}")

        else:
            print(f"❌ Unknown command: {command}")
            print()
            print(HELP_TEXT)
            sys.exit(1)

        # Show help reminder after successful command execution
        # (only for non-help, non-version commands)
        if command not in ['help', '-h', '--help', 'help-json', 'version', '-v', '--version']:
            print("\n💡 Run 'trello help' to see all capabilities")

    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(130)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)


if __name__ == '__main__':
    main()

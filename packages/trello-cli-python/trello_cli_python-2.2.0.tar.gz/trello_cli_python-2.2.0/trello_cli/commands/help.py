"""
Help and documentation commands
"""

import json


def cmd_help_json():
    """
    Output all available commands in JSON format for Claude Code consumption.
    This helps Claude Code understand what commands are available.
    """
    commands = {
        "cli_name": "trello",
        "description": "Trello CLI - Command-line interface for Trello",
        "commands": {
            "config": {
                "description": "Configure API credentials",
                "usage": "trello config",
                "args": []
            },
            "help-json": {
                "description": "Output all available commands in JSON format",
                "usage": "trello help-json",
                "args": []
            },
            "boards": {
                "description": "List all accessible boards",
                "usage": "trello boards",
                "args": [],
                "output": "Table with board IDs and names"
            },
            "create-board": {
                "description": "Create a new board",
                "usage": "trello create-board \"name\"",
                "args": [
                    {"name": "board_name", "type": "string", "required": True}
                ]
            },
            "board-overview": {
                "description": "Get complete overview of a board with all lists and card counts",
                "usage": "trello board-overview <board_id>",
                "args": [
                    {"name": "board_id", "type": "string", "required": True}
                ],
                "output": "Board details with lists and card counts"
            },
            "board-ids": {
                "description": "Get quick reference of all useful IDs in a board (lists, cards)",
                "usage": "trello board-ids <board_id>",
                "args": [
                    {"name": "board_id", "type": "string", "required": True}
                ],
                "output": "Comprehensive list of IDs for boards, lists, and recent cards"
            },
            "lists": {
                "description": "List all lists in a board",
                "usage": "trello lists <board_id>",
                "args": [
                    {"name": "board_id", "type": "string", "required": True}
                ]
            },
            "create-list": {
                "description": "Create a new list in a board",
                "usage": "trello create-list <board_id> \"name\"",
                "args": [
                    {"name": "board_id", "type": "string", "required": True},
                    {"name": "list_name", "type": "string", "required": True}
                ]
            },
            "archive-list": {
                "description": "Archive (close) a list",
                "usage": "trello archive-list <list_id>",
                "args": [
                    {"name": "list_id", "type": "string", "required": True}
                ]
            },
            "cards": {
                "description": "List all cards in a list",
                "usage": "trello cards <list_id>",
                "args": [
                    {"name": "list_id", "type": "string", "required": True}
                ]
            },
            "search-cards": {
                "description": "Search for cards in a board by title/description with list information",
                "usage": "trello search-cards <board_id> \"query\"",
                "args": [
                    {"name": "board_id", "type": "string", "required": True},
                    {"name": "query", "type": "string", "required": True}
                ],
                "output": "Cards matching query with their list names"
            },
            "add-card": {
                "description": "Add a new card to a list",
                "usage": "trello add-card <list_id> \"title\" --description \"description\"",
                "args": [
                    {"name": "list_id", "type": "string", "required": True, "description": "24-character hexadecimal list ID (NOT board_id)"},
                    {"name": "title", "type": "string", "required": True, "description": "Card title (minimum 10 characters)"},
                    {"name": "--description", "type": "string", "required": True, "description": "Card description (minimum 50 characters)"}
                ],
                "examples": [
                    "# CORRECT: list_id first, then title",
                    "trello add-card 68fc01108ce7d8a2c22fa8e0 \"FI-FEAT-001: New Feature\" --description \"This is a detailed description of at least 50 characters...\"",
                    "",
                    "# WRONG: Do NOT pass board_id",
                    "# trello add-card <board_id> <list_id> \"title\"  # ❌ INCORRECT",
                    "",
                    "# To find list_id:",
                    "trello lists <board_id>",
                    "trello board-ids <board_id>"
                ],
                "common_errors": [
                    "❌ Using board_id instead of list_id",
                    "❌ Passing arguments in wrong order (title before list_id)",
                    "❌ Title too short (< 10 characters)",
                    "❌ Description too short (< 50 characters)"
                ]
            },
            "show-card": {
                "description": "Show detailed card information",
                "usage": "trello show-card <card_id>",
                "args": [
                    {"name": "card_id", "type": "string", "required": True}
                ]
            },
            "update-card": {
                "description": "Update card description",
                "usage": "trello update-card <card_id> \"description\"",
                "args": [
                    {"name": "card_id", "type": "string", "required": True},
                    {"name": "description", "type": "string", "required": True}
                ]
            },
            "move-card": {
                "description": "Move card to another list",
                "usage": "trello move-card <card_id> <list_id>",
                "args": [
                    {"name": "card_id", "type": "string", "required": True},
                    {"name": "list_id", "type": "string", "required": True}
                ]
            },
            "add-label": {
                "description": "Add label to card",
                "usage": "trello add-label <card_id> \"color\" [\"name\"]",
                "args": [
                    {"name": "card_id", "type": "string", "required": True},
                    {"name": "color", "type": "string", "required": True, "values": ["yellow", "purple", "blue", "red", "green", "orange", "black", "sky", "pink", "lime"]},
                    {"name": "name", "type": "string", "required": False}
                ]
            },
            "add-checklist": {
                "description": "Add checklist to card",
                "usage": "trello add-checklist <card_id> \"name\"",
                "args": [
                    {"name": "card_id", "type": "string", "required": True},
                    {"name": "checklist_name", "type": "string", "required": True}
                ]
            },
            "add-checkitem": {
                "description": "Add item to checklist (creates checklist if it doesn't exist)",
                "usage": "trello add-checkitem <card_id> \"checklist\" \"item\"",
                "args": [
                    {"name": "card_id", "type": "string", "required": True},
                    {"name": "checklist_name", "type": "string", "required": True},
                    {"name": "item_name", "type": "string", "required": True}
                ]
            },
            "set-due": {
                "description": "Set due date for a card",
                "usage": "trello set-due <card_id> \"YYYY-MM-DD\"",
                "args": [
                    {"name": "card_id", "type": "string", "required": True},
                    {"name": "due_date", "type": "string", "required": True, "format": "YYYY-MM-DD"}
                ]
            },
            "add-comment": {
                "description": "Add comment to card",
                "usage": "trello add-comment <card_id> \"comment\"",
                "args": [
                    {"name": "card_id", "type": "string", "required": True},
                    {"name": "comment", "type": "string", "required": True}
                ]
            },
            "delete-card": {
                "description": "Delete a card permanently",
                "usage": "trello delete-card <card_id>",
                "args": [
                    {"name": "card_id", "type": "string", "required": True}
                ]
            },
            "board-audit": {
                "description": "Comprehensive board audit: naming patterns, missing members/labels, empty lists, deletion candidates",
                "usage": "trello board-audit <board_id> [\"pattern\"]",
                "args": [
                    {"name": "board_id", "type": "string", "required": True},
                    {"name": "pattern", "type": "string", "required": False, "description": "Regex pattern for card naming validation (e.g., 'PF-[A-Z]+-\\d+')"}
                ]
            },
            "list-audit": {
                "description": "Detailed audit of a specific list with pattern validation",
                "usage": "trello list-audit <list_id> [\"pattern\"]",
                "args": [
                    {"name": "list_id", "type": "string", "required": True},
                    {"name": "pattern", "type": "string", "required": False, "description": "Regex pattern for card naming validation"}
                ]
            },
            "list-snapshot": {
                "description": "Export complete list snapshot to JSON with all card details",
                "usage": "trello list-snapshot <list_id> [\"output_file.json\"]",
                "args": [
                    {"name": "list_id", "type": "string", "required": True},
                    {"name": "output_file", "type": "string", "required": False, "description": "Output JSON file (prints to stdout if not provided)"}
                ]
            },
            "sprint-audit": {
                "description": "Sprint-specific audit: validates sprint labels have due dates, detects overdue cards, checks label consistency",
                "usage": "trello sprint-audit <board_id> [\"sprint_label\"]",
                "args": [
                    {"name": "board_id", "type": "string", "required": True},
                    {"name": "sprint_label", "type": "string", "required": False, "description": "Filter by specific sprint label (e.g., 'Sprint 1'). Auto-detects if not provided."}
                ]
            },
            "rename-card": {
                "description": "Rename a card (update title/name)",
                "usage": "trello rename-card <card_id> \"new_title\"",
                "args": [
                    {"name": "card_id", "type": "string", "required": True},
                    {"name": "new_title", "type": "string", "required": True}
                ]
            },
            "label-audit": {
                "description": "Label audit: detect duplicates, similar names, unused labels, and naming inconsistencies",
                "usage": "trello label-audit <board_id>",
                "args": [
                    {"name": "board_id", "type": "string", "required": True}
                ]
            },
            "remove-label": {
                "description": "Remove a label from a card (label stays on board)",
                "usage": "trello remove-label <card_id> \"label_name|color|id\"",
                "args": [
                    {"name": "card_id", "type": "string", "required": True},
                    {"name": "label_identifier", "type": "string", "required": True, "description": "Label name, color, or ID"}
                ]
            },
            "delete-label": {
                "description": "Delete a label from the board entirely (removes from all cards)",
                "usage": "trello delete-label <board_id> \"label_name|color|id\"",
                "args": [
                    {"name": "board_id", "type": "string", "required": True},
                    {"name": "label_identifier", "type": "string", "required": True, "description": "Label name, color, or ID"}
                ]
            },
            "rename-label": {
                "description": "Rename a label on the board (affects all cards with this label)",
                "usage": "trello rename-label <board_id> \"current_label\" \"new_name\"",
                "args": [
                    {"name": "board_id", "type": "string", "required": True},
                    {"name": "current_label", "type": "string", "required": True, "description": "Current label name, color, or ID"},
                    {"name": "new_name", "type": "string", "required": True}
                ]
            },
            "plugin-list": {
                "description": "List all available plugins",
                "usage": "trello plugin list [--plugin-dir DIR]",
                "args": [
                    {"name": "--plugin-dir", "type": "string", "required": False, "description": "Custom plugin directory"}
                ],
                "output": "Table with plugin names, descriptions, versions, and authors"
            },
            "plugin-info": {
                "description": "Show detailed information about a plugin",
                "usage": "trello plugin info <name> [--plugin-dir DIR]",
                "args": [
                    {"name": "plugin_name", "type": "string", "required": True},
                    {"name": "--plugin-dir", "type": "string", "required": False, "description": "Custom plugin directory"}
                ],
                "output": "Detailed plugin metadata and available environment variables"
            },
            "plugin-run": {
                "description": "Execute a plugin with arguments",
                "usage": "trello plugin run <name> [args] [--plugin-dir DIR]",
                "args": [
                    {"name": "plugin_name", "type": "string", "required": True},
                    {"name": "args", "type": "array", "required": False, "description": "Arguments to pass to the plugin"}
                ],
                "output": "Plugin-specific output",
                "examples": [
                    "trello plugin run board-audit <board_id>",
                    "trello plugin run board-audit <board_id> --json",
                    "trello plugin run board-audit <board_id> --pattern \"PF-[A-Z]+-\\d+\""
                ]
            }
        },
        "usage_notes": [
            "Use 'trello help-json' to get command information in JSON format for programmatic use",
            "Use 'trello board-overview <board_id>' to see all lists and their card counts",
            "Use 'trello board-ids <board_id>' to get a quick reference of all IDs in a board",
            "Use 'trello search-cards <board_id> \"query\"' to find cards across all lists"
        ]
    }

    print(json.dumps(commands, indent=2))


def cmd_help():
    """Display help information in human-readable format"""
    # Import here to avoid circular imports
    from .. import __version__ as pkg_version

    help_text = f"""Trello CLI v{pkg_version} - Official Python command-line interface for Trello
AI-powered project intelligence with Claude daemon integration

🎯 FOR AI USERS - QUICK START:
  1. trello feedback <board_id>          🧠 Get intelligent board analysis (Claude AI)
  2. trello report <board_id>            📊 Detailed report (duplicates, orphans, frozen cards, fake done)
  3. trello score <board_id>             📈 Board integrity score (0-100)
  4. trello checklist-status <card_id>   📋 See item-by-item progress
  5. trello check <card_id> "List" "Item" ✅ Complete items with anti-fraud validation

DISCOVERY COMMANDS (useful for Claude Code):
  help-json                         Get all commands in JSON format
  board-overview <board_id>         Complete board overview with lists and counts
  board-ids <board_id>              Quick reference of all IDs in a board
  search-cards <board_id> "query"   Search cards across board

QUICK COMMANDS (shortcuts):
  quick-start <card_id>             Move to "In Progress" + add comment
  quick-test <card_id>              Move to "Testing" + add comment
  quick-done <card_id>              Move to "Done" + add comment
  my-cards <board_id>               Show all your assigned cards
  card-age <list_id>                Show how long cards have been in list

SPRINT PLANNING:
  sprint-start <board_id>           Start sprint (move Ready → Sprint)
  sprint-status <board_id>          Show current sprint status
  sprint-close <board_id>           Close sprint and move unfinished cards
  sprint-velocity <board_id>        Calculate sprint velocity

BULK OPERATIONS:
  bulk-move-cards <source> <target>     Move multiple cards
  bulk-add-label <file> <color>         Label multiple cards
  bulk-set-due <file> <date>            Set due dates in bulk
  bulk-archive-cards <list_id>          Archive multiple cards
  bulk-create-cards <list_id> <file>    Create from CSV/JSON

BOARD COMMANDS:
  boards                            List all boards
  create-board "name"               Create a new board

LIST COMMANDS:
  lists <board_id>                  List all lists in a board
  create-list <board_id> "name"     Create a new list
  archive-list <list_id>            Archive (close) a list

CARD COMMANDS:
  cards <list_id>                           List all cards in a list
  add-card <list_id> "title" --description "desc"   Add a new card
  show-card <card_id>                       Show card details
  update-card <card_id> "desc"              Update card description
  rename-card <card_id> "title"             Rename card (update title)
  move-card <card_id> <list_id>             Move card to another list
  delete-card <card_id>                     Delete a card permanently

  ⚠️  IMPORTANT for add-card:
      - First argument is list_id (24-char hex), NOT board_id
      - Use 'trello lists <board_id>' to find list IDs
      - Title must be 10+ characters
      - Description must be 50+ characters
      - Format: trello add-card <list_id> "title" --description "desc"

CARD ENHANCEMENT COMMANDS:
  add-label <card_id> "color" ["name"]   Add label to card
  remove-label <card_id> "label"         Remove label from card
  add-checklist <card_id> "name"         Add checklist to card
  add-checkitem <card_id> "checklist" "item"   Add item to checklist
  set-due <card_id> "YYYY-MM-DD"         Set due date
  add-comment <card_id> "comment"        Add comment to card

CHECKLIST ITEM OPERATIONS (Item-Level Tracking):
  checklist-status <card_id>        Show detailed checklist progress (item-by-item)
  check <card_id> "List" "Item"     ✅ Mark checklist item complete
                                       (with anti-fraud validation)
  uncheck <card_id> "List" "Item"   ↩️  Mark checklist item incomplete

  ✅ Anti-Fraud Validation:
     - Prevents fake completion (items without PR/commit/deployment proof)
     - When completing the last item, card description must include:
       • PR/commit reference, OR
       • Deployment note, OR
       • Explicit completion proof
     - Use: trello check <card_id> "checklist" "item_name"

LABEL MANAGEMENT (BOARD-LEVEL):
  delete-label <board_id> "label"        Delete label from board
  rename-label <board_id> "label" "new"  Rename label on board

BOARD INTELLIGENCE (Claude Daemon + AI Analysis):
  report <board_id>               📊 Detailed board report showing:
                                     - Duplicated cards (similitude ≥33%)
                                     - Orphaned tasks (no description, no subtasks)
                                     - Frozen progress (>7 days without movement)
                                     - Fake completion (Done but items incomplete)
                                     - Missing evidence (no PR/commit/deployment)

  feedback <board_id>             🧠 Intelligent board feedback (requires Claude API key):
                                     - Uses Claude AI for pedagogical analysis
                                     - Explains structural issues in board
                                     - Suggests improvements for team workflow
                                     - Falls back to heuristics if API unavailable
                                     Set: export ANTHROPIC_API_KEY="sk-ant-..."

  score <board_id>                📈 Board integrity score (0-100):
                                     - Architecture clarity (25%)
                                     - Phase definition (15%)
                                     - Dependency documentation (20%)
                                     - Scope definition (20%)
                                     - Risk assessment (20%)

AUDIT & ANALYSIS COMMANDS:
  board-audit <board_id> ["pattern"]     Comprehensive board audit
  list-audit <list_id> ["pattern"]       Detailed list audit
  list-snapshot <list_id> ["file.json"]  Export list to JSON
  sprint-audit <board_id> ["sprint"]     Sprint audit (dates, overdue)
  label-audit <board_id>                 Label audit (duplicates, unused)

MEMBER MANAGEMENT:
  assign-card <card_id> <member>         Assign member to card (use 'me' for self)
  unassign-card <card_id> <member>       Remove member from card
  card-log <card_id>                     Show card action history

CONFIGURATION:
  config                            Configure API credentials
  daemon-status                     Show Claude Daemon status

Valid label colors: yellow, purple, blue, red, green, orange, black, sky, pink, lime

═══════════════════════════════════════════════════════════════════════════════

WORKFLOW EXAMPLES FOR AI USERS:

1. Understanding Board Health (Recommended workflow):
   trello feedback <board_id>      # Get Claude AI analysis
   trello report <board_id>        # See specific issues
   trello score <board_id>         # View integrity metrics

2. Completing Work Item-by-Item (With anti-fraud validation):
   trello checklist-status <card_id>    # See progress
   trello check <card_id> "List" "Item" # Complete items (validated)
   trello report <board_id>             # Verify no fake completions

3. Board Structure & Organization:
   trello board-overview <board_id>  # Understand layout
   trello board-ids <board_id>       # Get IDs for operations
   trello search-cards <board_id> "query"  # Find specific cards

═══════════════════════════════════════════════════════════════════════════════

ANTI-FRAUD FEATURES (Prevent Fake Work):

The CLI validates project integrity to prevent:
  ❌ Fake completion (tasks marked done without proof)
  ❌ Invalid transitions (TODO→DONE without intermediate steps)
  ❌ Duplication (multiple identical cards created rapidly)

When you mark the final checklist item complete:
  ✅ Card description is checked for PR/commit reference
  ✅ Deployment or shipping note required
  ✅ Explicit completion proof with date

This ensures every "Done" card represents real work.

═══════════════════════════════════════════════════════════════════════════════

CLAUDE AI INTEGRATION:

To enable intelligent board analysis with Claude AI:

1. Get API key from: https://console.anthropic.com/
2. Set environment variable:
   export ANTHROPIC_API_KEY="sk-ant-..."
3. Use feedback command:
   trello feedback <board_id>

Benefits:
  • Conversational analysis of board structure
  • Pedagogical feedback on project planning
  • Suggestions for agile/scrum conformity
  • Risk assessment and mitigation strategies

Without ANTHROPIC_API_KEY:
  • Commands still work with heuristic analysis
  • No Claude AI coaching
  • Graceful degradation - no blocking

═══════════════════════════════════════════════════════════════════════════════

📖 ENVIRONMENT VARIABLES:

ANTHROPIC_API_KEY        Claude AI integration (for intelligent feedback)
                         Example: export ANTHROPIC_API_KEY="sk-ant-..."

═══════════════════════════════════════════════════════════════════════════════

Examples:
  # Discovery commands
  trello help-json
  trello board-overview 68fcf05e481843db13204397
  trello board-ids 68fcf05e481843db13204397
  trello search-cards 68fcf05e481843db13204397 "feature"

  # AI Analysis
  trello feedback 68fcf05e481843db13204397
  trello report 68fcf05e481843db13204397
  trello score 68fcf05e481843db13204397

  # Create a card (CORRECT way)
  trello lists 68fcf05e481843db13204397  # First get list_id
  trello add-card 68fcff46fa7dbc9cc069eaef "FI-FEAT-001: New Feature" --description "Implement OAuth2 for user authentication..."

  # Work with checklists (item-level)
  trello checklist-status 68fd24640bf4
  trello check 68fd24640bf4 "Implementation" "Setup environment"

  # Board intelligence
  trello report 68fcf05e481843db13204397

For detailed help, run: trello help-json
For more information, see: README.md and CLAUDE.md
For Claude Daemon docs, see: claude-daemon/README.md
"""
    print(help_text)

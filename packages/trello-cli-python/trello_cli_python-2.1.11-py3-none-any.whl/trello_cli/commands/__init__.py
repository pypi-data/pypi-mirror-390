"""
Command modules for Trello CLI
"""

from .board import cmd_boards, cmd_create_board
from .list import cmd_lists, cmd_create_list, cmd_archive_list
from .card import (
    cmd_cards, cmd_add_card, cmd_show_card,
    cmd_update_card, cmd_move_card,
    cmd_add_checklist, cmd_add_checkitem,
    cmd_set_due, cmd_add_comment, cmd_delete_card, cmd_rename_card
)
from .label import cmd_add_label, cmd_remove_label, cmd_delete_label, cmd_rename_label
from .help import cmd_help, cmd_help_json
from .discovery import cmd_board_overview, cmd_board_ids, cmd_search_cards
from .bulk import (
    cmd_bulk_move_cards, cmd_bulk_add_label, cmd_bulk_set_due,
    cmd_bulk_archive_cards, cmd_bulk_create_cards,
    cmd_bulk_relabel, cmd_label_backup, cmd_label_restore
)
from .quick import (
    cmd_quick_start, cmd_quick_test, cmd_quick_done,
    cmd_my_cards, cmd_card_age
)
from .sprint import (
    cmd_sprint_start, cmd_sprint_status, cmd_sprint_close, cmd_sprint_velocity
)
from .query import (
    cmd_cards_by_label, cmd_cards_due_soon, cmd_cards_overdue,
    cmd_list_metrics, cmd_board_health
)
from .standardize import (
    cmd_standardize_lists, cmd_scrum_check, cmd_migrate_cards, cmd_list_templates
)
from .migrate import cmd_migrate_board, cmd_archive_board
from .audit import cmd_board_audit, cmd_list_audit, cmd_list_snapshot, cmd_sprint_audit, cmd_label_audit
from .members import cmd_assign_card, cmd_unassign_card, cmd_card_log
from .export import cmd_export_board
from .validation import (
    cmd_validation_status, cmd_validation_enable, cmd_validation_disable,
    cmd_validation_config, cmd_validation_reload, cmd_validation_reset
)
from .reporting import BoardReporter
from .checklist import cmd_check, cmd_uncheck, cmd_checklist_status

__all__ = [
    # Basic commands
    'cmd_boards', 'cmd_create_board',
    'cmd_lists', 'cmd_create_list', 'cmd_archive_list',
    'cmd_cards', 'cmd_add_card', 'cmd_show_card',
    'cmd_update_card', 'cmd_move_card', 'cmd_rename_card',
    'cmd_add_checklist', 'cmd_add_checkitem',
    'cmd_set_due', 'cmd_add_comment', 'cmd_delete_card',
    'cmd_add_label', 'cmd_remove_label', 'cmd_delete_label', 'cmd_rename_label',
    # Help & Discovery
    'cmd_help', 'cmd_help_json',
    'cmd_board_overview', 'cmd_board_ids', 'cmd_search_cards',
    # Bulk operations
    'cmd_bulk_move_cards', 'cmd_bulk_add_label', 'cmd_bulk_set_due',
    'cmd_bulk_archive_cards', 'cmd_bulk_create_cards',
    'cmd_bulk_relabel', 'cmd_label_backup', 'cmd_label_restore',
    # Quick commands
    'cmd_quick_start', 'cmd_quick_test', 'cmd_quick_done',
    'cmd_my_cards', 'cmd_card_age',
    # Sprint planning
    'cmd_sprint_start', 'cmd_sprint_status', 'cmd_sprint_close', 'cmd_sprint_velocity',
    # Advanced queries
    'cmd_cards_by_label', 'cmd_cards_due_soon', 'cmd_cards_overdue',
    'cmd_list_metrics', 'cmd_board_health',
    # Board standardization
    'cmd_standardize_lists', 'cmd_scrum_check', 'cmd_migrate_cards', 'cmd_list_templates',
    # Board migration
    'cmd_migrate_board', 'cmd_archive_board',
    # Audit commands
    'cmd_board_audit', 'cmd_list_audit', 'cmd_list_snapshot', 'cmd_sprint_audit', 'cmd_label_audit',
    # Member management
    'cmd_assign_card', 'cmd_unassign_card', 'cmd_card_log',
    # Export
    'cmd_export_board',
    # Validation
    'cmd_validation_status', 'cmd_validation_enable', 'cmd_validation_disable',
    'cmd_validation_config', 'cmd_validation_reload', 'cmd_validation_reset',
    # Reporting
    'BoardReporter',
    # Checklist operations
    'cmd_check', 'cmd_uncheck', 'cmd_checklist_status'
]

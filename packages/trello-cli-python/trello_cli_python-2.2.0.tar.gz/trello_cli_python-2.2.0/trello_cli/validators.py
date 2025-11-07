"""
Validation rules system for enforcing Scrum best practices.

This module provides a configurable validation system that can be extended
via plugins. Validators check card creation, updates, and movements to ensure
compliance with team workflows.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Callable
from datetime import datetime


class ValidationError(Exception):
    """Raised when a validation rule fails."""
    def __init__(self, message: str, help_command: Optional[str] = None):
        self.message = message
        self.help_command = help_command
        super().__init__(message)


class ValidationRule:
    """Base class for validation rules."""

    def __init__(self, name: str, enabled: bool = True, severity: str = "error"):
        self.name = name
        self.enabled = enabled
        self.severity = severity  # "error", "warning"

    def validate(self, **kwargs) -> tuple[bool, Optional[str]]:
        """
        Validate the given context.

        Returns:
            (is_valid, error_message)
        """
        raise NotImplementedError


class CardCreationValidator:
    """Validates card creation operations."""

    def __init__(self, config: Dict):
        self.config = config
        self.rules = []
        self._setup_rules()

    def _setup_rules(self):
        """Initialize validation rules from config."""
        cfg = self.config.get('card_creation', {})

        # Title validation
        if cfg.get('require_title', True):
            self.rules.append(
                RequireTitleRule(
                    min_length=cfg.get('title_min_length', 10)
                )
            )

        # Description validation
        if cfg.get('require_description', True):
            self.rules.append(
                RequireDescriptionRule(
                    min_length=cfg.get('description_min_length', 50)
                )
            )

        # Label validation
        if cfg.get('require_labels', True):
            self.rules.append(
                RequireLabelsRule(
                    min_labels=cfg.get('min_labels', 1)
                )
            )

        # Due date validation
        if cfg.get('require_due_date', False):
            self.rules.append(RequireDueDateRule())

        # Card ID format validation
        if cfg.get('require_card_id_format', True):
            self.rules.append(
                RequireCardIDFormatRule(
                    pattern=cfg.get('card_id_pattern', r'^[A-Z]+-[A-Z0-9]+-[A-Z]+-\d+:')
                )
            )

    def validate(self, title: str, description: str = "", labels: List = None,
                 due_date: Optional[datetime] = None) -> None:
        """
        Validate card creation parameters.

        Raises:
            ValidationError: If validation fails
        """
        labels = labels or []

        for rule in self.rules:
            if not rule.enabled:
                continue

            is_valid, error_msg = rule.validate(
                title=title,
                description=description,
                labels=labels,
                due_date=due_date
            )

            if not is_valid:
                if rule.severity == "error":
                    raise ValidationError(
                        error_msg,
                        help_command="trello help"
                    )
                else:
                    print(f"⚠️  WARNING: {error_msg}")


class CardMovementValidator:
    """Validates card movement operations."""

    def __init__(self, config: Dict):
        self.config = config
        self.rules = []
        self._setup_rules()

    def _setup_rules(self):
        """Initialize validation rules from config."""
        cfg = self.config.get('card_movement', {})

        # Done list validation
        if cfg.get('require_explicit_done', True):
            self.rules.append(
                RequireExplicitDoneRule(
                    done_list_names=cfg.get('done_list_names', ['Done', '✅ Done', 'Hecho'])
                )
            )

        # Checklist completion for Done
        if cfg.get('require_checklist_completion', True):
            self.rules.append(RequireChecklistCompletionRule())

        # Labels required before testing
        if cfg.get('require_labels_before_testing', True):
            self.rules.append(
                RequireLabelsBeforeTestingRule(
                    testing_list_names=cfg.get('testing_list_names', ['Testing', '🧪 Testing'])
                )
            )

    def validate(self, card, target_list, explicit_done: bool = False) -> None:
        """
        Validate card movement.

        Args:
            card: Card object
            target_list: Target list object
            explicit_done: Whether user explicitly confirmed moving to Done

        Raises:
            ValidationError: If validation fails
        """
        for rule in self.rules:
            if not rule.enabled:
                continue

            is_valid, error_msg = rule.validate(
                card=card,
                target_list=target_list,
                explicit_done=explicit_done
            )

            if not is_valid:
                if rule.severity == "error":
                    raise ValidationError(
                        error_msg,
                        help_command="trello help"
                    )
                else:
                    print(f"⚠️  WARNING: {error_msg}")


# Specific validation rules

class RequireTitleRule(ValidationRule):
    """Validates card title requirements."""

    def __init__(self, min_length: int = 10):
        super().__init__("require_title")
        self.min_length = min_length

    def validate(self, title: str = "", **kwargs) -> tuple[bool, Optional[str]]:
        if not title or len(title.strip()) < self.min_length:
            return False, (
                f"❌ Card title must be at least {self.min_length} characters.\n"
                f"   Current length: {len(title.strip())}\n"
                f"   💡 Use descriptive titles like: 'FI-FEAT-001: Implement user authentication'"
            )
        return True, None


class RequireDescriptionRule(ValidationRule):
    """Validates card description requirements."""

    def __init__(self, min_length: int = 50):
        super().__init__("require_description")
        self.min_length = min_length

    def validate(self, description: str = "", **kwargs) -> tuple[bool, Optional[str]]:
        if not description or len(description.strip()) < self.min_length:
            return False, (
                f"❌ Card description must be at least {self.min_length} characters.\n"
                f"   Current length: {len(description.strip())}\n"
                f"   💡 Use --description flag:\n"
                f"   trello add-card <list_id> \"title\" --description \"detailed description\""
            )
        return True, None


class RequireLabelsRule(ValidationRule):
    """Validates that cards have required labels."""

    def __init__(self, min_labels: int = 1):
        super().__init__("require_labels")
        self.min_labels = min_labels

    def validate(self, labels: List = None, **kwargs) -> tuple[bool, Optional[str]]:
        labels = labels or []
        if len(labels) < self.min_labels:
            return False, (
                f"❌ Card must have at least {self.min_labels} label(s).\n"
                f"   Current: {len(labels)} labels\n"
                f"   💡 Add labels after creation:\n"
                f"   trello add-label <card_id> \"color\" \"name\""
            )
        return True, None


class RequireDueDateRule(ValidationRule):
    """Validates that cards have a due date."""

    def __init__(self):
        super().__init__("require_due_date")

    def validate(self, due_date: Optional[datetime] = None, **kwargs) -> tuple[bool, Optional[str]]:
        if not due_date:
            return False, (
                "❌ Card must have a due date.\n"
                "   💡 Set due date after creation:\n"
                "   trello set-due <card_id> \"YYYY-MM-DD\""
            )
        return True, None


class RequireCardIDFormatRule(ValidationRule):
    """Validates card title follows ID format convention."""

    def __init__(self, pattern: str):
        super().__init__("require_card_id_format")
        self.pattern = pattern

    def validate(self, title: str = "", **kwargs) -> tuple[bool, Optional[str]]:
        import re
        if not re.match(self.pattern, title):
            return False, (
                f"❌ Card title must follow format: {self.pattern}\n"
                f"   Examples:\n"
                f"   - 'FI-BACKEND-REF-005: Exponential Backoff + Circuit Breaker'\n"
                f"   - 'FI-UI-FEAT-202: Dashboard Metrics Panel'\n"
                f"   - 'FI-API-FEAT-010: Authentication Endpoint'\n"
                f"   💡 Use convention: PROJECT-AREA-TYPE-###"
            )
        return True, None


class RequireExplicitDoneRule(ValidationRule):
    """Validates that cards moved to Done are explicitly marked."""

    def __init__(self, done_list_names: List[str]):
        super().__init__("require_explicit_done")
        self.done_list_names = done_list_names

    def validate(self, target_list, explicit_done: bool = False, **kwargs) -> tuple[bool, Optional[str]]:
        if target_list.name in self.done_list_names and not explicit_done:
            return False, (
                "❌ Cannot move card to Done without explicit confirmation.\n"
                "   💡 Use the --done flag:\n"
                "   trello move-card <card_id> <done_list_id> --done"
            )
        return True, None


class RequireChecklistCompletionRule(ValidationRule):
    """Validates that all checklists are complete before moving to Done."""

    def __init__(self):
        super().__init__("require_checklist_completion")

    def validate(self, card, target_list, **kwargs) -> tuple[bool, Optional[str]]:
        done_list_names = ['Done', '✅ Done', 'Hecho']
        if target_list.name not in done_list_names:
            return True, None

        # Check if card has incomplete checklists
        if hasattr(card, 'checklists') and card.checklists:
            for checklist in card.checklists:
                total = len(checklist.items) if hasattr(checklist, 'items') else 0
                completed = sum(1 for item in checklist.items if item.get('state') == 'complete') if hasattr(checklist, 'items') else 0

                if total > 0 and completed < total:
                    return False, (
                        f"❌ Cannot move to Done: Checklist '{checklist.name}' incomplete.\n"
                        f"   Completed: {completed}/{total}\n"
                        f"   💡 Complete all checklist items first"
                    )

        return True, None


class RequireLabelsBeforeTestingRule(ValidationRule):
    """Validates that cards have labels before moving to Testing."""

    def __init__(self, testing_list_names: List[str]):
        super().__init__("require_labels_before_testing")
        self.testing_list_names = testing_list_names

    def validate(self, card, target_list, **kwargs) -> tuple[bool, Optional[str]]:
        if target_list.name in self.testing_list_names:
            if not hasattr(card, 'labels') or not card.labels:
                return False, (
                    "❌ Cannot move to Testing: Card has no labels.\n"
                    "   💡 Add at least a priority label:\n"
                    "   trello add-label <card_id> \"red\" \"P0\""
                )
        return True, None


class ValidationConfig:
    """Manages validation configuration."""

    DEFAULT_CONFIG = {
        "enabled": True,
        "card_creation": {
            "require_title": True,
            "title_min_length": 10,
            "require_description": True,
            "description_min_length": 50,
            "require_labels": False,  # Start lenient, can be enabled per-board
            "min_labels": 1,
            "require_due_date": False,
            "require_card_id_format": False,  # Disabled by default - too strict
            "card_id_pattern": r'^[A-Z]+-[A-Z0-9]+-[A-Z]+-\d+:'  # Pattern expects colon after number
        },
        "card_movement": {
            "require_explicit_done": True,
            "done_list_names": ["Done", "✅ Done", "Hecho"],
            "require_checklist_completion": True,
            "require_labels_before_testing": True,
            "testing_list_names": ["Testing", "🧪 Testing"]
        }
    }

    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or Path.home() / ".trello_validation_rules.json"
        self.config = self._load_config()

    def _load_config(self) -> Dict:
        """Load configuration from file or use defaults."""
        if self.config_path.exists():
            try:
                with open(self.config_path) as f:
                    return json.load(f)
            except Exception as e:
                print(f"⚠️  Warning: Could not load validation config: {e}")
                return self.DEFAULT_CONFIG.copy()
        return self.DEFAULT_CONFIG.copy()

    def save_config(self) -> None:
        """Save configuration to file."""
        with open(self.config_path, 'w') as f:
            json.dump(self.config, f, indent=2)

    def is_enabled(self) -> bool:
        """Check if validation system is enabled."""
        return self.config.get('enabled', True)


# Global validators
_config = ValidationConfig()
card_creation_validator = CardCreationValidator(_config.config)
card_movement_validator = CardMovementValidator(_config.config)


def get_config() -> ValidationConfig:
    """Get the global validation configuration."""
    return _config


def reload_config():
    """Reload configuration from file."""
    global _config, card_creation_validator, card_movement_validator
    _config = ValidationConfig()
    card_creation_validator = CardCreationValidator(_config.config)
    card_movement_validator = CardMovementValidator(_config.config)

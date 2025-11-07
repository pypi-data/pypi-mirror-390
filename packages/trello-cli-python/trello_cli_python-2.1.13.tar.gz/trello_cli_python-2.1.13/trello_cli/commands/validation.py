"""
Validation configuration commands
"""

import json
from ..validators import get_config, reload_config


def cmd_validation_status():
    """Show current validation configuration status"""
    config = get_config()

    print("\n" + "=" * 60)
    print("🛡️  VALIDATION RULES STATUS")
    print("=" * 60)

    print(f"\nSystem: {'✅ ENABLED' if config.is_enabled() else '❌ DISABLED'}")
    print(f"Config file: {config.config_path}")

    if config.is_enabled():
        print("\n📋 CARD CREATION RULES:")
        cc = config.config.get('card_creation', {})
        print(f"  • Require title (min {cc.get('title_min_length', 10)} chars): {'✅' if cc.get('require_title') else '❌'}")
        print(f"  • Require description (min {cc.get('description_min_length', 50)} chars): {'✅' if cc.get('require_description') else '❌'}")
        print(f"  • Require labels (min {cc.get('min_labels', 1)}): {'✅' if cc.get('require_labels') else '❌'}")
        print(f"  • Require due date: {'✅' if cc.get('require_due_date') else '❌'}")
        print(f"  • Require card ID format: {'✅' if cc.get('require_card_id_format') else '❌'}")

        print("\n📦 CARD MOVEMENT RULES:")
        cm = config.config.get('card_movement', {})
        print(f"  • Require explicit --done flag: {'✅' if cm.get('require_explicit_done') else '❌'}")
        print(f"  • Require checklist completion: {'✅' if cm.get('require_checklist_completion') else '❌'}")
        print(f"  • Require labels before testing: {'✅' if cm.get('require_labels_before_testing') else '❌'}")

    print("\n" + "=" * 60)
    print("💡 Run 'trello validation-config' to modify settings")
    print("=" * 60 + "\n")


def cmd_validation_enable():
    """Enable validation system"""
    config = get_config()
    config.config['enabled'] = True
    config.save_config()
    reload_config()

    print("✅ Validation system ENABLED")
    print("💡 Run 'trello validation-status' to see current rules")


def cmd_validation_disable():
    """Disable validation system"""
    config = get_config()
    config.config['enabled'] = False
    config.save_config()
    reload_config()

    print("❌ Validation system DISABLED")
    print("⚠️  Warning: Cards can now be created without validation")


def cmd_validation_config():
    """Show and optionally edit validation configuration"""
    config = get_config()

    print("\n" + "=" * 60)
    print("⚙️  VALIDATION CONFIGURATION")
    print("=" * 60)
    print(f"\nConfig file: {config.config_path}\n")

    print(json.dumps(config.config, indent=2))

    print("\n" + "=" * 60)
    print("💡 To modify settings:")
    print(f"   1. Edit: {config.config_path}")
    print("   2. Run: trello validation-reload")
    print("=" * 60 + "\n")


def cmd_validation_reload():
    """Reload validation configuration from file"""
    reload_config()
    print("✅ Validation configuration reloaded")
    print("💡 Run 'trello validation-status' to see current rules")


def cmd_validation_reset():
    """Reset validation configuration to defaults"""
    from ..validators import ValidationConfig

    config = get_config()
    config.config = ValidationConfig.DEFAULT_CONFIG.copy()
    config.save_config()
    reload_config()

    print("✅ Validation configuration reset to defaults")
    print("💡 Run 'trello validation-status' to see current rules")

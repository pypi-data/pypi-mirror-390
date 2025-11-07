"""
Configuration management for Trello CLI
"""

import json
import sys
from pathlib import Path

CONFIG_FILE = Path.home() / '.trello_config.json'


def load_config():
    """Load Trello API credentials from config file"""
    if not CONFIG_FILE.exists():
        print("❌ Configuration file not found.")
        print("   Run 'trello config' to set up API credentials.")
        sys.exit(1)

    try:
        with open(CONFIG_FILE) as f:
            config = json.load(f)

        if 'api_key' not in config or 'token' not in config:
            print("❌ Invalid configuration file.")
            print("   Run 'trello config' to reconfigure.")
            sys.exit(1)

        return config
    except json.JSONDecodeError:
        print("❌ Corrupted configuration file.")
        print("   Run 'trello config' to reconfigure.")
        sys.exit(1)


def save_config(api_key, api_token):
    """Save Trello API credentials to config file"""
    config = {
        'api_key': api_key,
        'token': api_token
    }

    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)

    # Set secure permissions (read/write for user only)
    CONFIG_FILE.chmod(0o600)

    print(f"✅ Configuration saved to {CONFIG_FILE}")
    print("   Credentials are stored securely with 600 permissions.")


def configure_interactive():
    """Interactive configuration wizard"""
    print("=" * 70)
    print("🔧 Trello API Configuration")
    print("=" * 70)
    print()
    print("Step 1: Get your API key")
    print("   → https://trello.com/app-key")
    print()

    api_key = input("Enter API Key: ").strip()

    if not api_key:
        print("❌ API key cannot be empty")
        sys.exit(1)

    print()
    print("Step 2: Get your API token")
    print(f"   → https://trello.com/1/authorize?expiration=never&scope=read,write&response_type=token&key={api_key}")
    print()

    api_token = input("Enter API Token: ").strip()

    if not api_token:
        print("❌ API token cannot be empty")
        sys.exit(1)

    print()
    save_config(api_key, api_token)

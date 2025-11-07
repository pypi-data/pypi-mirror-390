"""
Plugin system for Trello CLI
"""

import os
import subprocess
import sys
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple


PLUGIN_DIR = Path.home() / '.trellocli' / 'plugins'
CONFIG_FILE = Path.home() / '.trello_config.json'


def ensure_plugin_dir():
    """Ensure plugin directory exists"""
    PLUGIN_DIR.mkdir(parents=True, exist_ok=True)


def get_plugin_path(plugin_name: str, plugin_dir: Optional[Path] = None) -> Optional[Path]:
    """
    Find plugin file by name

    Args:
        plugin_name: Plugin name (without extension)
        plugin_dir: Optional custom plugin directory

    Returns:
        Path to plugin file or None if not found
    """
    search_dir = plugin_dir or PLUGIN_DIR

    if not search_dir.exists():
        return None

    # Try common extensions
    extensions = ['.py', '.sh', '.js', '.rb', '.go', '']

    for ext in extensions:
        plugin_path = search_dir / f"{plugin_name}{ext}"
        if plugin_path.exists() and plugin_path.is_file():
            # Check if executable (for extensionless files)
            if ext == '' and not os.access(plugin_path, os.X_OK):
                continue
            return plugin_path

    return None


def parse_plugin_metadata(plugin_path: Path) -> Dict[str, str]:
    """
    Parse plugin metadata from file header

    Expected format:
    # trello-plugin
    # name: Plugin Name
    # description: Plugin description
    # usage: plugin run name [args]
    # author: Name
    # version: 1.0.0

    Args:
        plugin_path: Path to plugin file

    Returns:
        Dictionary with metadata
    """
    metadata = {
        'name': plugin_path.stem,
        'description': 'No description provided',
        'usage': f'plugin run {plugin_path.stem}',
        'author': 'Unknown',
        'version': '0.0.0',
        'is_valid': False
    }

    try:
        with open(plugin_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()[:30]  # Only scan first 30 lines

            found_marker = False
            for line in lines:
                line = line.strip()

                # Check for plugin marker
                if 'trello-plugin' in line.lower():
                    found_marker = True
                    metadata['is_valid'] = True
                    continue

                # Parse metadata lines
                if found_marker and '#' in line:
                    # Remove comment markers
                    line = line.lstrip('#').strip()

                    if ':' in line:
                        key, value = line.split(':', 1)
                        key = key.strip().lower()
                        value = value.strip()

                        if key in metadata:
                            metadata[key] = value

    except Exception as e:
        metadata['error'] = str(e)

    return metadata


def discover_plugins(plugin_dir: Optional[Path] = None) -> List[Tuple[str, Path, Dict]]:
    """
    Discover all plugins in plugin directory

    Args:
        plugin_dir: Optional custom plugin directory

    Returns:
        List of tuples: (plugin_name, plugin_path, metadata)
    """
    search_dir = plugin_dir or PLUGIN_DIR

    if not search_dir.exists():
        return []

    plugins = []

    for item in search_dir.iterdir():
        if not item.is_file():
            continue

        # Skip hidden files and backups
        if item.name.startswith('.') or item.name.endswith('~'):
            continue

        # Check if executable or recognized extension
        recognized_extensions = {'.py', '.sh', '.js', '.rb', '.go'}
        is_executable = os.access(item, os.X_OK)
        has_valid_ext = item.suffix in recognized_extensions

        if is_executable or has_valid_ext:
            metadata = parse_plugin_metadata(item)
            plugins.append((item.stem, item, metadata))

    return sorted(plugins, key=lambda x: x[0])


def get_plugin_env(custom_env: Optional[Dict] = None) -> Dict[str, str]:
    """
    Get environment variables for plugin execution

    Args:
        custom_env: Optional custom environment variables

    Returns:
        Dictionary with environment variables
    """
    from . import __version__

    env = os.environ.copy()

    # Load config
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE) as f:
                config = json.load(f)
                env['TRELLO_API_KEY'] = config.get('api_key', '')
                env['TRELLO_TOKEN'] = config.get('token', '')
                env['TRELLO_USER_ID'] = config.get('user_id', '')
        except:
            pass

    # Set additional variables
    env['TRELLO_CONFIG_DIR'] = str(Path.home() / '.trellocli')
    env['TRELLO_CLI_VERSION'] = __version__
    env['TRELLO_BASE_URL'] = 'https://api.trello.com/1'
    env['TRELLO_PLUGIN_DIR'] = str(PLUGIN_DIR)

    # Add custom env if provided
    if custom_env:
        env.update(custom_env)

    return env


def run_plugin(plugin_name: str, args: List[str], plugin_dir: Optional[Path] = None, timeout: int = 300) -> int:
    """
    Execute a plugin

    Args:
        plugin_name: Plugin name
        args: Arguments to pass to plugin
        plugin_dir: Optional custom plugin directory
        timeout: Execution timeout in seconds (default 5 minutes)

    Returns:
        Exit code
    """
    plugin_path = get_plugin_path(plugin_name, plugin_dir)

    if not plugin_path:
        print(f"❌ Plugin '{plugin_name}' not found")
        print(f"\nSearch path: {plugin_dir or PLUGIN_DIR}")
        print(f"Run 'trello plugin list' to see available plugins")
        return 1

    # Validate plugin
    metadata = parse_plugin_metadata(plugin_path)
    if not metadata['is_valid']:
        print(f"⚠️  Warning: Plugin '{plugin_name}' is missing trello-plugin marker")
        print(f"   This plugin may not be a valid Trello CLI plugin")
        print()

    # Determine how to execute
    if plugin_path.suffix == '.py':
        cmd = [sys.executable, str(plugin_path)] + args
    elif plugin_path.suffix == '.sh':
        cmd = ['bash', str(plugin_path)] + args
    elif plugin_path.suffix == '.js':
        cmd = ['node', str(plugin_path)] + args
    elif os.access(plugin_path, os.X_OK):
        cmd = [str(plugin_path)] + args
    else:
        print(f"❌ Plugin '{plugin_name}' is not executable and has no recognized extension")
        print(f"   Make it executable: chmod +x {plugin_path}")
        return 1

    # Execute plugin
    env = get_plugin_env()

    try:
        result = subprocess.run(
            cmd,
            env=env,
            timeout=timeout,
            capture_output=False,  # Let output go directly to terminal
        )
        return result.returncode

    except subprocess.TimeoutExpired:
        print(f"\n❌ Plugin '{plugin_name}' timed out after {timeout} seconds", file=sys.stderr)
        return 124

    except FileNotFoundError as e:
        print(f"\n❌ Failed to execute plugin '{plugin_name}': {e}", file=sys.stderr)
        print(f"   Make sure required interpreter is installed", file=sys.stderr)
        return 127

    except Exception as e:
        print(f"\n❌ Plugin '{plugin_name}' failed: {e}", file=sys.stderr)
        return 1


def cmd_plugin_list(plugin_dir: Optional[str] = None):
    """List all available plugins"""
    custom_dir = Path(plugin_dir) if plugin_dir else None
    search_dir = custom_dir or PLUGIN_DIR

    ensure_plugin_dir()

    print(f"\n{'='*80}")
    print(f"AVAILABLE PLUGINS")
    print(f"Plugin Directory: {search_dir}")
    print(f"{'='*80}\n")

    plugins = discover_plugins(custom_dir)

    if not plugins:
        print("No plugins found")
        print(f"\nTo create a plugin:")
        print(f"  1. Create a file in {search_dir}")
        print(f"  2. Make it executable (chmod +x)")
        print(f"  3. Add metadata header with '# trello-plugin'")
        print(f"  4. Run 'trello plugin list' to verify")
        return

    for plugin_name, plugin_path, metadata in plugins:
        is_valid = metadata.get('is_valid', False)
        status = '✅' if is_valid else '⚠️ '

        print(f"{status} {plugin_name}")
        print(f"   {metadata.get('description', 'No description')}")

        if is_valid:
            print(f"   Version: {metadata.get('version', '0.0.0')}")
            if metadata.get('author') != 'Unknown':
                print(f"   Author: {metadata.get('author')}")

        print(f"   File: {plugin_path.name}")
        print()

    print(f"{'='*80}")
    print(f"Total: {len(plugins)} plugin(s)")
    print(f"\nRun 'trello plugin info <name>' for details")
    print(f"Run 'trello plugin run <name> [args]' to execute")
    print(f"{'='*80}\n")


def cmd_plugin_info(plugin_name: str, plugin_dir: Optional[str] = None):
    """Show detailed information about a plugin"""
    custom_dir = Path(plugin_dir) if plugin_dir else None
    plugin_path = get_plugin_path(plugin_name, custom_dir)

    if not plugin_path:
        print(f"❌ Plugin '{plugin_name}' not found")
        return

    metadata = parse_plugin_metadata(plugin_path)

    print(f"\n{'='*80}")
    print(f"PLUGIN INFO: {plugin_name}")
    print(f"{'='*80}\n")

    print(f"Name:        {metadata['name']}")
    print(f"Version:     {metadata['version']}")
    print(f"Author:      {metadata['author']}")
    print(f"Valid:       {'Yes' if metadata['is_valid'] else 'No (missing trello-plugin marker)'}")
    print()
    print(f"Description: {metadata['description']}")
    print()
    print(f"Usage:       {metadata['usage']}")
    print()
    print(f"File:        {plugin_path}")
    print(f"Executable:  {'Yes' if os.access(plugin_path, os.X_OK) else 'No'}")
    print(f"Size:        {plugin_path.stat().st_size} bytes")
    print()

    # Show available environment variables
    print("Available Environment Variables:")
    print("  TRELLO_API_KEY       - Your API key")
    print("  TRELLO_TOKEN         - Your API token")
    print("  TRELLO_USER_ID       - Your user ID")
    print("  TRELLO_CONFIG_DIR    - Config directory path")
    print("  TRELLO_CLI_VERSION   - CLI version")
    print("  TRELLO_BASE_URL      - Trello API base URL")
    print("  TRELLO_PLUGIN_DIR    - Plugin directory path")
    print()

    print(f"{'='*80}\n")


def cmd_plugin_run(plugin_name: str, args: List[str], plugin_dir: Optional[str] = None):
    """Run a plugin"""
    custom_dir = Path(plugin_dir) if plugin_dir else None
    exit_code = run_plugin(plugin_name, args, custom_dir)
    sys.exit(exit_code)

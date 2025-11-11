"""
Setup utilities for NIA MCP Server configuration
"""
import os
import json
import platform
import shutil
import subprocess
from pathlib import Path
from typing import Dict, Optional, Any


def find_mcp_config_path(ide: str = "cursor") -> Path:
    """
    Find the MCP configuration file path based on OS and IDE.

    Args:
        ide: IDE to configure (cursor, vscode, continue, windsurf, cline, claude-code, codex)

    Returns:
        Path to the MCP configuration file
    """
    system = platform.system()
    home = Path.home()

    if ide == "cursor":
        if system == "Darwin":  # macOS
            return home / ".cursor" / "mcp.json"
        elif system == "Windows":
            appdata = os.environ.get("APPDATA", home / "AppData" / "Roaming")
            return Path(appdata) / "Cursor" / "mcp.json"
        else:  # Linux and others
            return home / ".config" / "cursor" / "mcp.json"

    elif ide == "vscode":
        # VS Code uses different config locations
        if system == "Darwin":
            return home / "Library" / "Application Support" / "Code" / "User" / "mcp.json"
        elif system == "Windows":
            appdata = os.environ.get("APPDATA", home / "AppData" / "Roaming")
            return Path(appdata) / "Code" / "User" / "mcp.json"
        else:
            return home / ".config" / "Code" / "User" / "mcp.json"

    elif ide == "continue":
        # Continue.dev uses .continue directory
        return home / ".continue" / "config.json"

    elif ide == "windsurf":
        # Windsurf uses similar structure to Cursor
        if system == "Darwin":
            return home / ".windsurf" / "mcp.json"
        elif system == "Windows":
            appdata = os.environ.get("APPDATA", home / "AppData" / "Roaming")
            return Path(appdata) / "Windsurf" / "mcp.json"
        else:
            return home / ".config" / "windsurf" / "mcp.json"

    elif ide == "cline":
        # Cline uses VS Code extension directory
        if system == "Darwin":
            return home / "Library" / "Application Support" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
        elif system == "Windows":
            appdata = os.environ.get("APPDATA", home / "AppData" / "Roaming")
            return Path(appdata) / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"
        else:
            return home / ".config" / "Code" / "User" / "globalStorage" / "saoudrizwan.claude-dev" / "settings" / "cline_mcp_settings.json"

    elif ide == "claude-code":
        # Claude Code uses command-based setup, no config file needed
        return None

    elif ide == "codex":
        # Codex uses command-based setup, no config file needed
        return None

    else:
        raise ValueError(f"Unsupported IDE: {ide}")


def backup_config(config_path: Path) -> Optional[Path]:
    """
    Create a backup of existing configuration file.
    
    Args:
        config_path: Path to the configuration file
    
    Returns:
        Path to the backup file if created, None otherwise
    """
    if config_path.exists():
        backup_path = config_path.with_suffix(".json.backup")
        # If backup already exists, add timestamp
        if backup_path.exists():
            import time
            timestamp = int(time.time())
            backup_path = config_path.with_suffix(f".json.backup.{timestamp}")
        
        shutil.copy2(config_path, backup_path)
        return backup_path
    return None


def create_nia_config(api_key: str, ide: str = "cursor") -> Dict[str, Any]:
    """
    Create NIA MCP server configuration.

    Args:
        api_key: NIA API key
        ide: IDE to configure (affects config format)

    Returns:
        Dictionary with NIA server configuration
    """
    base_config = {
        "command": "pipx",
        "args": ["run", "nia-mcp-server"],
        "env": {
            "NIA_API_KEY": api_key,
            "NIA_API_URL": "https://apigcp.trynia.ai/"
        }
    }

    # Cline requires alwaysAllow permissions
    if ide == "cline":
        base_config["alwaysAllow"] = [
            "index_repository",
            "search_codebase",
            "search_documentation",
            "list_repositories",
            "check_repository_status",
            "index_documentation",
            "list_documentation",
            "check_documentation_status",
            "delete_documentation",
            "delete_repository",
            "rename_repository",
            "rename_documentation",
            "nia_web_search",
            "nia_deep_research_agent",
            "initialize_project",
            "read_source_content",
            "index_local_filesystem",
            "scan_local_filesystem",
            "check_local_filesystem_status",
            "search_local_filesystem",
            "visualize_codebase",
        ]
        base_config["disabled"] = False

    return base_config


def update_mcp_config(config_path: Path, api_key: str, ide: str = "cursor") -> bool:
    """
    Update or create MCP configuration file with NIA server.

    Args:
        config_path: Path to the MCP configuration file
        api_key: NIA API key
        ide: IDE to configure

    Returns:
        True if successful, False otherwise
    """
    try:
        # Ensure directory exists
        config_path.parent.mkdir(parents=True, exist_ok=True)

        # Load existing config or create new one
        if config_path.exists():
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {}

        # Ensure mcpServers section exists
        if "mcpServers" not in config:
            config["mcpServers"] = {}

        # Add or update NIA server configuration
        config["mcpServers"]["nia"] = create_nia_config(api_key, ide)

        # Write updated configuration
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)

        return True

    except Exception as e:
        print(f"❌ Error updating configuration: {e}")
        return False


def setup_command_based_ide(api_key: str, ide: str) -> bool:
    """
    Setup NIA MCP Server for command-based IDEs (claude-code, codex).

    Args:
        api_key: NIA API key
        ide: IDE to configure

    Returns:
        True if successful, False otherwise
    """

    # Build the command based on IDE
    if ide == "claude-code":
        cmd = [
            "claude", "mcp", "add", "nia",
            "-e", f"NIA_API_KEY={api_key}",
            "-e", "NIA_API_URL=https://apigcp.trynia.ai/",
            "--", "pipx", "run", "--no-cache", "nia-mcp-server"
        ]
        ide_name = "Claude Code"
    elif ide == "codex":
        cmd = [
            "codex", "mcp", "add", "nia",
            "--env", f"NIA_API_KEY={api_key}",
            "--env", "NIA_API_URL=https://apigcp.trynia.ai/",
            "--", "pipx", "run", "--no-cache", "nia-mcp-server"
        ]
        ide_name = "Codex"
    else:
        print(f"❌ Unsupported command-based IDE: {ide}")
        return False

    try:
        # Run the command
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"\n✅ Setup complete!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"\n❌ Setup failed with error: {e}")
        if e.stderr:
            print(f"Error details: {e.stderr}")
        return False
    except FileNotFoundError:
        print(f"\n❌ {ide_name} CLI not found. Please ensure {ide_name} is installed and in your PATH.")
        return False


def setup_mcp_config(api_key: str, ide: str = "cursor") -> bool:
    """
    Main setup function to configure NIA MCP Server.

    Args:
        api_key: NIA API key
        ide: IDE to configure

    Returns:
        True if successful, False otherwise
    """
    # Handle command-based IDEs differently
    if ide in ["claude-code", "codex"]:
        return setup_command_based_ide(api_key, ide)

    # For file-based configuration IDEs
    # Find config path
    config_path = find_mcp_config_path(ide)

    # Backup existing config
    backup_path = backup_config(config_path)
    if backup_path:
        print(f"📦 Backed up existing config to: {backup_path}")

    # Update configuration
    if update_mcp_config(config_path, api_key, ide):
        print(f"\n✅ Setup complete!")
        print(f"📝 Configuration written to: {config_path}")
        return True
    else:
        print(f"\n❌ Setup failed. Please check the error messages above.")
        if backup_path:
            print(f"   Your original config is safe at: {backup_path}")
        return False
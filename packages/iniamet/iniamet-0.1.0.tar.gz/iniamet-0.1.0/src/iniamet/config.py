"""
Configuration utility for INIAMET library.

Helps users configure their API key easily.
"""

import sys
import os
from pathlib import Path


def get_config_file() -> Path:
    """Get the path to the configuration file."""
    return Path.home() / '.iniamet' / 'config'


def set_api_key(api_key: str) -> None:
    """
    Save API key to config file.
    
    Args:
        api_key: The INIA API key to save
    """
    config_file = get_config_file()
    config_dir = config_file.parent
    
    # Create directory if it doesn't exist
    config_dir.mkdir(parents=True, exist_ok=True)
    
    # Write config file
    with open(config_file, 'w') as f:
        f.write(f"api_key={api_key}\n")
    
    # Set restrictive permissions (Unix-like systems)
    try:
        os.chmod(config_file, 0o600)
    except Exception:
        pass  # Windows doesn't support chmod
    
    print(f"✅ API key saved successfully to: {config_file}")
    print("\nYou can now use INIAMET:")
    print("  from iniamet import INIAClient")
    print("  client = INIAClient()")


def show_api_key() -> None:
    """Show the currently configured API key (masked)."""
    config_file = get_config_file()
    
    if not config_file.exists():
        print(f"❌ No config file found at: {config_file}")
        print("\nConfigure your API key with:")
        print("  python -m iniamet.config set-key YOUR-API-KEY")
        return
    
    try:
        with open(config_file, 'r') as f:
            for line in f:
                if line.startswith('api_key='):
                    key = line.split('=', 1)[1].strip()
                    if len(key) > 10:
                        masked = key[:4] + '*' * (len(key) - 8) + key[-4:]
                    else:
                        masked = '*' * len(key)
                    print(f"✅ API key configured: {masked}")
                    print(f"📁 Config file: {config_file}")
                    return
        
        print(f"⚠️ No API key found in config file: {config_file}")
    except Exception as e:
        print(f"❌ Error reading config file: {e}")


def remove_api_key() -> None:
    """Remove the configured API key."""
    config_file = get_config_file()
    
    if config_file.exists():
        config_file.unlink()
        print(f"✅ API key removed from: {config_file}")
    else:
        print(f"ℹ️ No config file found at: {config_file}")


def show_help():
    """Show help message."""
    print("""
INIAMET Configuration Utility

Usage:
  python -m iniamet.config <command> [arguments]

Commands:
  set-key <api-key>   Save your INIA API key
  show                Display current API key (masked)
  remove              Remove saved API key
  help                Show this help message

Examples:
  # Save your API key
  python -m iniamet.config set-key YOUR_API_KEY_HERE

  # Check current configuration
  python -m iniamet.config show

  # Remove API key
  python -m iniamet.config remove

Alternative methods:
  1. Environment variable:
     export INIA_API_KEY='your-api-key'        # Linux/Mac
     set INIA_API_KEY=your-api-key             # Windows CMD
     $env:INIA_API_KEY='your-api-key'          # Windows PowerShell

  2. Pass directly in code:
     from iniamet import INIAClient
     client = INIAClient(api_key='your-api-key')

Get your API key from: https://agromet.inia.cl/api/v2/
""")


def main():
    """Main entry point for config utility."""
    if len(sys.argv) < 2:
        show_help()
        sys.exit(1)
    
    command = sys.argv[1].lower()
    
    if command in ['set-key', 'set']:
        if len(sys.argv) < 3:
            print("❌ Error: API key required")
            print("\nUsage: python -m iniamet.config set-key YOUR-API-KEY")
            sys.exit(1)
        api_key = sys.argv[2]
        set_api_key(api_key)
    
    elif command == 'show':
        show_api_key()
    
    elif command == 'remove':
        remove_api_key()
    
    elif command in ['help', '-h', '--help']:
        show_help()
    
    else:
        print(f"❌ Unknown command: {command}")
        print("\nRun 'python -m iniamet.config help' for usage information")
        sys.exit(1)


if __name__ == '__main__':
    main()

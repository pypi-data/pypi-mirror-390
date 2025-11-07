#!/usr/bin/env python3
"""
Command-line interface for managing per-datasets API keys
"""

import os
import json
import sys
import argparse
import getpass
from pathlib import Path
from typing import Optional, Dict, Any

def get_config_file() -> Path:
    """Get the path to the configuration file"""
    # Use user's home directory for cross-platform compatibility
    home = Path.home()
    config_dir = home / ".per_datasets"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.json"

def load_config() -> Dict[str, Any]:
    """Load configuration from file"""
    config_file = get_config_file()
    if config_file.exists():
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return {}
    return {}

def save_config(config: Dict[str, Any]) -> bool:
    """Save configuration to file"""
    config_file = get_config_file()
    try:
        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)
        return True
    except IOError:
        return False

def set_api_key(api_key: str) -> bool:
    """Set the global API key"""
    config = load_config()
    config['api_key'] = api_key.strip()
    
    if save_config(config):
        print("✅ API key stored successfully!")
        print(f"🔑 API Key: pk...{api_key[-4:] if len(api_key) > 4 else api_key}")
        return True
    else:
        print("❌ Failed to save API key")
        return False

def get_api_key() -> Optional[str]:
    """Get the stored API key"""
    config = load_config()
    return config.get('api_key')


def remove_api_key() -> bool:
    """Remove the stored API key"""
    config = load_config()
    if 'api_key' in config:
        del config['api_key']
        if save_config(config):
            print("✅ API key removed successfully!")
            return True
        else:
            print("❌ Failed to remove API key")
            return False
    else:
        print("⚠️  No API key found to remove")
        return False

def show_status() -> None:
    """Show current configuration status"""
    config = load_config()
    
    if 'api_key' in config:
        api_key = config['api_key']
        print("🔑 API Key Status: CONFIGURED")
        print(f"   Key: pk...{api_key[-4:] if len(api_key) > 4 else api_key}")
        print(f"   Config File: {get_config_file()}")
        
        # Test the API key
        try:
            import requests
            headers = {'X-API-Key': api_key}
            response = requests.get('https://perd-server.onrender.com/datasets', headers=headers, timeout=5)
            if response.status_code == 200:
                print("🌐 API Status: ACTIVE")
            else:
                print(f"🌐 API Status: INACTIVE (HTTP {response.status_code})")
        except Exception as e:
            print(f"🌐 API Status: ERROR ({type(e).__name__})")
    else:
        print("🔑 API Key Status: NOT CONFIGURED")
        print(f"   Config File: {get_config_file()}")
        print("   Use 'per-datasets set-key <api_key>' to configure")

def clear_config() -> bool:
    """Clear all configuration"""
    config_file = get_config_file()
    if config_file.exists():
        try:
            config_file.unlink()
            print("✅ Configuration cleared successfully!")
            return True
        except IOError:
            print("❌ Failed to clear configuration")
            return False
    else:
        print("⚠️  No configuration found to clear")
        return False

def main():
    parser = argparse.ArgumentParser(
        description="Manage per-datasets API keys globally",
        prog="per-datasets"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Set API key command
    set_parser = subparsers.add_parser('set-key', help='Set the API key')
    set_parser.add_argument('api_key', help='Your API key')
    
    # Get API key command
    get_parser = subparsers.add_parser('get-key', help='Get the stored API key')
    
    # Remove API key command
    remove_parser = subparsers.add_parser('remove-key', help='Remove the API key')
    
    # Status command
    status_parser = subparsers.add_parser('status', help='Show configuration status')
    
    # Clear command
    clear_parser = subparsers.add_parser('clear', help='Clear all configuration')
    
    # Interactive mode
    interactive_parser = subparsers.add_parser('interactive', help='Interactive setup')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == 'set-key':
        set_api_key(args.api_key)
    
    elif args.command == 'get-key':
        api_key = get_api_key()
        if api_key:
            print(f"pk...{api_key[-4:] if len(api_key) > 4 else api_key}")
        else:
            print("No API key configured")
    
    elif args.command == 'remove-key':
        remove_api_key()
    
    elif args.command == 'status':
        show_status()
    
    elif args.command == 'clear':
        clear_config()
    
    elif args.command == 'interactive':
        print("🔧 Interactive API Key Setup")
        print("=" * 40)
        
        # Check if key already exists
        existing_key = get_api_key()
        if existing_key:
            print(f"Current API key: pk...{existing_key[-4:] if len(existing_key) > 4 else existing_key}")
            response = input("Do you want to replace it? (y/N): ").strip().lower()
            if response != 'y':
                print("Setup cancelled")
                return
        
        # Get new API key
        print("\nEnter your API key:")
        api_key = getpass.getpass("API Key: ").strip()
        
        if not api_key:
            print("❌ API key cannot be empty")
            return
        
        # Save configuration
        if set_api_key(api_key):
            print("\n🎉 Setup complete!")
            print("You can now use per-datasets in any project without specifying the API key.")

if __name__ == "__main__":
    main()

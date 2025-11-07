# -*- coding: utf-8 -*-

"""Environment configuration loader for RC CLI.

This module provides utilities to load environment variables from .env file.
Supports multiple configuration locations:
1. .env in current directory
2. ~/.rc-cli.env in user's home directory
3. Environment variables already set in shell

Usage:
    from rc_cli.env_loader import load_env
    load_env()  # Load .env file if it exists
"""

import os
from pathlib import Path


def get_config_paths() -> list:
    """
    Get list of possible configuration file paths in priority order.
    
    Returns:
        List of Path objects to check for configuration
    """
    paths = []
    
    # 1. Current directory .env
    paths.append(Path.cwd() / ".env")
    
    # 2. User home directory ~/.rc-cli.env
    home = Path.home()
    paths.append(home / ".rc-cli.env")
    
    # 3. Project root .env (where this file is located)
    current_file = Path(__file__).resolve()
    project_root = current_file.parent.parent
    paths.append(project_root / ".env")
    
    return paths


def load_env(env_file: str = None) -> tuple:
    """
    Load environment variables from a .env file.
    
    Args:
        env_file: Optional specific path to .env file
        
    Returns:
        Tuple of (success: bool, config_path: str or None)
    """
    paths_to_try = [Path(env_file)] if env_file else get_config_paths()
    
    for env_path in paths_to_try:
        if not env_path.exists():
            continue
        
        try:
            with open(env_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Skip comments and empty lines
                    if not line or line.startswith('#'):
                        continue
                    
                    # Parse KEY=VALUE
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        
                        # Only set if not already in environment
                        if key and not os.environ.get(key):
                            os.environ[key] = value
            
            return (True, str(env_path))
        except Exception as e:
            print(f"Warning: Failed to load {env_path}: {e}")
            continue
    
    return (False, None)


def get_env_status() -> dict:
    """
    Get status of required environment variables.
    
    Returns:
        Dictionary with variable names and their status
    """
    required_vars = {
        'SP_GITLAB_BASE_URL': os.environ.get('SP_GITLAB_BASE_URL'),
        'SP_GITLAB_PROJECT_ID': os.environ.get('SP_GITLAB_PROJECT_ID'),
        'GITLAB_TOKEN': '***' if os.environ.get('GITLAB_TOKEN') else None,
    }
    return required_vars


def check_configuration() -> tuple:
    """
    Check if configuration is properly set up.
    
    Returns:
        Tuple of (is_configured: bool, missing_vars: list)
    """
    status = get_env_status()
    missing = []
    
    # Check if using default placeholder values
    if status['SP_GITLAB_BASE_URL'] == 'https://git.example.com/api/v4':
        missing.append('SP_GITLAB_BASE_URL (using placeholder)')
    elif not status['SP_GITLAB_BASE_URL']:
        missing.append('SP_GITLAB_BASE_URL')
    
    if not status['GITLAB_TOKEN'] or status['GITLAB_TOKEN'] == 'your-token-here':
        missing.append('GITLAB_TOKEN')
    
    return (len(missing) == 0, missing)


# Auto-load .env file when module is imported
_loaded, _config_path = load_env()
if _loaded:
    # Silently loaded, only show in verbose mode
    pass



"""Path-related utility functions for RealtimeX ecosystem."""

import os


def get_realtimex_user_dir() -> str:
    """Returns the path to the .realtimex.ai user directory.

    Returns:
        Path to the user directory (e.g., ~/.realtimex.ai)
    """
    return os.path.join(os.path.expanduser("~"), ".realtimex.ai")


def get_shared_env_path() -> str:
    """Returns the fixed path to the shared environment file.

    Returns:
        Path to the shared .env.development file
    """
    user_dir = get_realtimex_user_dir()
    return os.path.join(user_dir, "Resources", "server", ".env.development")

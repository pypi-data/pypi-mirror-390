"""Agent flow management utilities."""
import os
import sys
import json
from typing import Any

def get_flow_variable(
    variable_name:str = None,
    default_value:Any = None
) -> Any:
    """Retrieve flow variable"""
    try:
        run_id = sys.argv[1]
        payload_file_path = sys.argv[2]
        payload = None

        if not os.path.exists(payload_file_path):
            return None

        with open(payload_file_path, 'r') as f:
            payload = json.load(f)

        if not payload:
            return None

        if variable_name:
            if variable_name in payload:
                return payload[variable_name]
            return default_value
            
        return payload
        
    except Exception:
        return None


def get_workspace_slug(
    default_value:Any = None
) -> Any:
    """Retrieve current workspace slug"""
    try:
        return get_flow_variable("workspace_slug",default_value=default_value)
    except Exception:
        return default_value

def get_thread_id(
    default_value:Any = None
) -> Any:
    """Retrieve current thread id"""
    try:
        return get_flow_variable("thread_id",default_value=default_value)
    except Exception:
        return default_value

def get_workspace_data_dir(
    variable_name:str = None,
    default_workspace_slug:Any = None
) -> Any:
    """Retrieve flow variable"""
    try:
        import os

        workspace_slug = get_workspace_slug(default_value=default_workspace_slug)
        realtimex_dir = os.path.join(os.path.expanduser("~"),".realtimex.ai")
        realtimex_storage_dir = os.path.realpath(os.path.join(realtimex_dir,"Resources","server","storage"))

        if not os.path.exists(realtimex_storage_dir):
            return None

        workspace_data_dir = os.path.join(realtimex_storage_dir,"working-data",workspace_slug)

        if not os.path.exists(workspace_data_dir):
            os.makedirs(workspace_data_dir,exist_ok=True)
        
        return workspace_data_dir

        
    except Exception:
        return None


__all__ = [
    "get_flow_variable",
    "get_workspace_data_dir",
    "get_thread_id",
    "get_workspace_slug"
]

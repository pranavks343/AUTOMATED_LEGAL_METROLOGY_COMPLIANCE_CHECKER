"""
JSON Utilities Module
Provides consistent JSON serialization with datetime handling
"""

import json
from datetime import datetime
from typing import Any, Dict, List

class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects"""
    
    def default(self, obj: Any) -> Any:
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def safe_json_dumps(obj: Any, **kwargs) -> str:
    """
    Safely serialize objects to JSON, handling datetime objects
    
    Args:
        obj: Object to serialize
        **kwargs: Additional arguments for json.dumps
    
    Returns:
        JSON string
    """
    return json.dumps(obj, cls=DateTimeEncoder, **kwargs)

def safe_json_dump(obj: Any, fp, **kwargs) -> None:
    """
    Safely serialize objects to JSON file, handling datetime objects
    
    Args:
        obj: Object to serialize
        fp: File pointer to write to
        **kwargs: Additional arguments for json.dump
    """
    json.dump(obj, fp, cls=DateTimeEncoder, **kwargs)

def clean_for_json(obj: Any) -> Any:
    """
    Clean objects for JSON serialization by converting datetime to string
    
    Args:
        obj: Object to clean
    
    Returns:
        Cleaned object safe for JSON serialization
    """
    if isinstance(obj, dict):
        return {key: clean_for_json(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [clean_for_json(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    else:
        return obj

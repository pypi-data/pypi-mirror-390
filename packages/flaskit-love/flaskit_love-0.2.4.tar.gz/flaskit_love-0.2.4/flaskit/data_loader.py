"""
FlaskIt Data Loader - Simple JSON data loader for public data
Load data from data.json file
"""
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional


class DataLoader:
    """Simple loader for public data from data.json"""
    
    _instance: Optional['DataLoader'] = None
    _data: Dict[str, Any] = {}
    _file_path: Optional[Path] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._data:
            self.load()
    
    def load(self, file_path: Optional[str] = None) -> None:
        """Load data from data.json"""
        if file_path:
            self._file_path = Path(file_path)
        else:
            # Search for data.json in current directory or parent directories
            current = Path.cwd()
            for _ in range(5):
                data_file = current / "data.json"
                if data_file.exists():
                    self._file_path = data_file
                    break
                current = current.parent
            
            if not self._file_path:
                # No data.json found, use empty dict
                self._data = {}
                return
        
        try:
            with open(self._file_path, 'r', encoding='utf-8') as f:
                self._data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self._data = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value with dot notation (e.g., 'app.name' or 'web.social.whatsapp')"""
        keys = key.split('.')
        value = self._data
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def all(self) -> Dict[str, Any]:
        """Get all data"""
        return self._data.copy()
    
    def reload(self) -> None:
        """Reload data from file"""
        self._data = {}
        self.load()


# Create singleton instance
_loader = DataLoader()

# Helper function for easy access
def get_data(key: str, default: Any = None) -> Any:
    """
    Get public data from data.json
    
    Example:
        from flaskit.data_loader import get_data
        
        app_name = get_data('app.name')
        whatsapp = get_data('web.social.whatsapp')
        email = get_data('contact.email')
    """
    return _loader.get(key, default)


def all_data() -> Dict[str, Any]:
    """Get all public data"""
    return _loader.all()


__all__ = ['get_data', 'all_data', 'DataLoader']

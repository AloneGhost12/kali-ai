"""
Configuration file management for KaliAI
"""

import json
from pathlib import Path
from typing import Optional
from rich.console import Console

console = Console()

class ConfigManager:
    """Manage KaliAI configuration file"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        if config_dir is None:
            self.config_dir = Path.home() / ".kaliagent"
        else:
            self.config_dir = config_dir
        
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "config.json"
        self.config = self._load_config()
    
    def _load_config(self) -> dict:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                console.print(f"[yellow]Warning: Could not load config file: {str(e)}[/yellow]")
                return {}
        return {}
    
    def _save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            console.print(f"[red]Error saving config: {str(e)}[/red]")
    
    def set(self, key: str, value):
        """Set a configuration value"""
        self.config[key] = value
        self._save_config()
    
    def get(self, key: str, default=None):
        """Get a configuration value"""
        return self.config.get(key, default)
    
    def delete(self, key: str):
        """Delete a configuration value"""
        if key in self.config:
            del self.config[key]
            self._save_config()
    
    def get_all(self) -> dict:
        """Get all configuration"""
        return self.config.copy()
    
    def clear(self):
        """Clear all configuration"""
        self.config = {}
        self._save_config()

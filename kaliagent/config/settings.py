from pydantic_settings import BaseSettings
from typing import Optional, Dict, Any, List
from pathlib import Path
import os

class Settings(BaseSettings):
    """KaliAgent Configuration Settings"""
    
    # API Configuration
    OPENAI_API_KEY: Optional[str] = None
    MODEL_ID: str = "gpt-3.5-turbo"  # Changed from gpt-4 to reduce costs
    
    # Application Settings
    APP_NAME: str = "KaliAI"
    APP_VERSION: str = "2.0.0"
    
    # Storage Settings
    DATA_DIR: Path = Path.home() / ".kaliagent"
    LOG_DIR: Path = DATA_DIR / "logs"
    HISTORY_DIR: Path = DATA_DIR / "history"
    
    # Logging Settings
    ENABLE_LOGGING: bool = True
    LOG_LEVEL: str = "INFO"
    
    # Security Settings
    ALLOWED_TOOLS: List[str] = [
        "nmap", "nikto", "dirb", "gobuster", "wpscan", "sqlmap", 
        "wireshark", "metasploit", "hydra", "john", "hashcat",
        "burpsuite", "aircrack-ng", "maltego", "beef", "zaproxy"
    ]
    
    # Command Execution
    SAFE_MODE: bool = True  # If True, will only display commands but not execute them
    REQUIRE_CONFIRMATION: bool = True  # If True, requires user confirmation before executing commands
    
    class Config:
        # Allow mutation of settings
        frozen = False
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Create necessary directories
        self.DATA_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_DIR.mkdir(parents=True, exist_ok=True)
        self.HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        
        # Load from config file if available
        self._load_from_config()
    
    def _load_from_config(self):
        """Load settings from config file"""
        try:
            from .config_manager import ConfigManager
            config_mgr = ConfigManager(self.DATA_DIR)
            
            # Update settings from config file
            api_key = config_mgr.get('OPENAI_API_KEY')
            if api_key and isinstance(api_key, str):
                self.OPENAI_API_KEY = api_key
                os.environ['OPENAI_API_KEY'] = api_key
            
            model_id = config_mgr.get('MODEL_ID')
            if model_id and isinstance(model_id, str):
                self.MODEL_ID = model_id
            
            safe_mode = config_mgr.get('SAFE_MODE')
            if safe_mode is not None and isinstance(safe_mode, bool):
                self.SAFE_MODE = safe_mode
            
            require_conf = config_mgr.get('REQUIRE_CONFIRMATION')
            if require_conf is not None and isinstance(require_conf, bool):
                self.REQUIRE_CONFIRMATION = require_conf
        except Exception:
            # If config loading fails, use defaults
            pass

# Create global settings instance
settings = Settings()

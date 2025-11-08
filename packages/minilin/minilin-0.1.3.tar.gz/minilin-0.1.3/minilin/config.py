"""
Global configuration management for MiniLin
"""

import os
from pathlib import Path
from typing import Dict, Any, Optional
import json


class Config:
    """Global configuration manager."""
    
    _instance = None
    _config = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_config()
        return cls._instance
    
    def _load_config(self):
        """Load configuration from file or environment."""
        # Try to load from config file
        config_paths = [
            Path.home() / ".minilin" / "config.json",
            Path("minilin_config.json"),
            Path(".minilin_config.json")
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                with open(config_path, 'r') as f:
                    self._config = json.load(f)
                break
        
        # Override with environment variables
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration from environment variables."""
        env_mappings = {
            'MINILIN_TRANSLATION_API_KEY': 'translation_api_key',
            'MINILIN_TRANSLATION_API_URL': 'translation_api_url',
            'MINILIN_HUGGINGFACE_TOKEN': 'huggingface_token',
            'MINILIN_CACHE_DIR': 'cache_dir',
            'MINILIN_LOG_LEVEL': 'log_level',
        }
        
        for env_var, config_key in env_mappings.items():
            value = os.getenv(env_var)
            if value:
                self._config[config_key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        return self._config.get(key, default)
    
    def set(self, key: str, value: Any):
        """Set configuration value."""
        self._config[key] = value
    
    def save(self, path: Optional[Path] = None):
        """Save configuration to file."""
        if path is None:
            path = Path.home() / ".minilin" / "config.json"
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            json.dump(self._config, f, indent=2)
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()


# Global config instance
config = Config()

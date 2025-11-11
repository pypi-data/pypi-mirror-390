#!/usr/bin/env python3
"""
Configuration Management for VersaLaw2
"""

import os
from pathlib import Path
from typing import Optional
import json

class Config:
    """Configuration manager"""
    
    def __init__(self, config_file: Optional[str] = None):
        self.config_file = config_file
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Load configuration"""
        default_config = {
            'mayalaw_path': '/root/dragon/global/mayalaw',
            'ai_provider': 'mock',
            'ai_api_key': os.getenv('AI_API_KEY', ''),
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY', ''),
            'qodo_api_key': os.getenv('QODO_API_KEY', ''),  # NEW: Qodo.ai support
            'qodo_base_url': os.getenv('QODO_BASE_URL', 'https://api.qodo.ai/v1'),  # NEW
            'cache_enabled': True,
            'cache_dir': '/root/dragon/global/lab/.cache',
            'log_level': 'INFO',
            'log_file': '/root/dragon/global/lab/versalaw2.log',
            'max_search_results': 3,
            'ai_temperature': 0.3,
            'ai_max_tokens': 2000,
        }
        
        if self.config_file and Path(self.config_file).exists():
            try:
                with open(self.config_file, 'r') as f:
                    user_config = json.load(f)
                default_config.update(user_config)
            except Exception as e:
                print(f"Warning: Could not load config file: {e}")
        
        return default_config
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value):
        """Set configuration value"""
        self.config[key] = value
    
    def save(self, filepath: Optional[str] = None):
        """Save configuration to file"""
        save_path = filepath or self.config_file
        if save_path:
            with open(save_path, 'w') as f:
                json.dump(self.config, f, indent=2)
    
    def __getitem__(self, key):
        return self.config[key]
    
    def __setitem__(self, key, value):
        self.config[key] = value

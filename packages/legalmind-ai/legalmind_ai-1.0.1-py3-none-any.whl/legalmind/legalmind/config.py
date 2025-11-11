#!/usr/bin/env python3
"""
LegalMind Configuration
"""

import os
from pathlib import Path

class LegalMindConfig:
    """Configuration for LegalMind system"""
    
    def __init__(self):
        self.config = {
            # Paths
            'mayalaw_path': '/root/dragon/global/mayalaw',
            'cache_dir': '/root/dragon/global/lab/.cache',
            
            # AI Providers
            'ai_provider': 'mock',  # mock, openai, deepseek, qodo
            'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
            'deepseek_api_key': os.getenv('DEEPSEEK_API_KEY', ''),
            'qodo_api_key': os.getenv('QODO_API_KEY', ''),
            
            # Settings
            'cache_enabled': True,
            'max_search_results': 3,
            'ai_temperature': 0.3,
            'ai_max_tokens': 2000,
        }
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def set(self, key, value):
        self.config[key] = value
    
    def __getitem__(self, key):
        return self.config[key]
    
    def __setitem__(self, key, value):
        self.config[key] = value

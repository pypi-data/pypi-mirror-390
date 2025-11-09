import os
import json
from typing import Dict, Any, Optional
from pathlib import Path


class AIConfig:
    """Simple AI configuration manager"""
    
    def __init__(self):
        self.config_file = Path.home() / ".ax_config.json"
        self.config = self.load_config()
    
    def load_config(self) -> Dict[str, Any]:
        """Load configuration from file"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except:
                pass
        return {}
    
    def save_config(self, config: Optional[Dict[str, Any]] = None):
        """Save configuration to file"""
        if config is not None:
            self.config = config
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Error saving config: {e}")
    
    def set_ai_config(self, api_key: str, provider: str = "openai", model: str = None, endpoint: str = None):
        """Set AI configuration"""
        self.config.update({
            "ai_api_key": api_key,
            "ai_provider": provider.lower(),
            "ai_model": model or self.get_default_model(provider),
            "ai_endpoint": endpoint or self.get_default_endpoint(provider)
        })
        self.save_config()
    
    def get_default_model(self, provider: str) -> str:
        """Get default model for provider"""
        defaults = {
            "openai": "gpt-5",
            "anthropic": "claude-4.5-sonnet-20240229",
            "qwen": "qwen-max",
            "gemini": "gemini-pro"
        }
        return defaults.get(provider.lower(), "gpt-4")
    
    def get_default_endpoint(self, provider: str) -> str:
        """Get default endpoint for provider"""
        endpoints = {
            "openai": "https://api.openai.com/v1/chat/completions",
            "anthropic": "https://api.anthropic.com/v1/messages",
            "qwen": "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation",
            "gemini": "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro:generateContent"
        }
        return endpoints.get(provider.lower(), "")
    
    def is_configured(self) -> bool:
        """Check if AI is properly configured"""
        return bool(self.config.get("api_key") and self.config.get("provider"))
    
    def get_config(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.config.copy()
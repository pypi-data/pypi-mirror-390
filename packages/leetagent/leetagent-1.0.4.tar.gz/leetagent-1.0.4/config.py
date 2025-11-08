"""
Configuration management for LeetCode Agent Automation
Loads environment variables and defines project constants
"""

import os
import json
from pathlib import Path
from typing import List, Optional
from dotenv import load_dotenv

# Load environment variables
BASE_DIR = Path(__file__).resolve().parent  # LeetcodeAgentAutomation folder
load_dotenv(BASE_DIR / ".env")


def _load_user_config() -> dict:
    """Load user configuration from ~/.leetagent/config.json"""
    config_path = Path.home() / ".leetagent" / "config.json"
    if config_path.exists():
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}


# Load user config once at import
_user_config = _load_user_config()


class Settings:
    """Centralized configuration management with dynamic credential loading"""
    
    def __init__(self):
        """Initialize settings and load user config"""
        self._load_credentials()
    
    def _load_credentials(self):
        """Load credentials from config.json, keyring, or environment"""
        config = _load_user_config()
        
        # Load API keys with priority: config.json > keyring > env
        self._gemini_key = config.get("GEMINI_API_KEY") or self._try_keyring("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY", "")
        self._telegram_token = config.get("TELEGRAM_TOKEN") or self._try_keyring("TELEGRAM_TOKEN") or os.getenv("TELEGRAM_BOT_TOKEN", "")
        self._chat_id1 = config.get("CHAT_ID") or self._try_keyring("CHAT_ID") or os.getenv("CHAT_ID1", "")
        self._chat_id2 = os.getenv("CHAT_ID2", "")
        self._preferred_language = config.get("PREFERRED_LANGUAGE") or os.getenv("PREFERRED_LANGUAGE", "Python")
    
    def _try_keyring(self, key: str) -> Optional[str]:
        """Try to get value from keyring, return None if not available"""
        try:
            import keyring
            value = keyring.get_password("leetagent", key)
            return value if value else None
        except:
            return None
    
    @property
    def GEMINI_API_KEY(self) -> str:
        """Get Gemini API key (reloads from config if needed)"""
        if not self._gemini_key:
            self._load_credentials()
        return self._gemini_key
    
    @property
    def TELEGRAM_BOT_TOKEN(self) -> str:
        """Get Telegram bot token"""
        return self._telegram_token
    
    @property
    def CHAT_ID1(self) -> str:
        """Get primary chat ID"""
        return self._chat_id1
    
    @property
    def CHAT_ID2(self) -> str:
        """Get secondary chat ID"""
        return self._chat_id2
    
    @property
    def PREFERRED_LANGUAGE(self) -> str:
        """Get preferred coding language"""
        return self._preferred_language
    
    # LeetCode Settings
    LEETCODE_GRAPHQL_URL: str = os.getenv("LEETCODE_GRAPHQL_URL", "https://leetcode.com/graphql")
    LEETCODE_BASE_URL: str = os.getenv("LEETCODE_BASE_URL", "https://leetcode.com")
    
    # Gemini Model Configuration
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-2.0-flash-exp")
    MAX_AI_ATTEMPTS: int = int(os.getenv("MAX_AI_ATTEMPTS", "3"))
    
    # Selenium Configuration
    WAIT_TIME: int = int(os.getenv("WAIT_TIME", "10"))
    KEEP_BROWSER_OPEN: int = int(os.getenv("KEEP_BROWSER_OPEN", "180"))  # 3 minutes
    
    # File Paths - Check if using relative paths from .env or absolute paths
    # If path starts with ./ or ../, resolve it relative to BASE_DIR
    def _resolve_path(env_var: str, default_path: Path) -> Path:
        """Resolve path from env var, handling relative paths"""
        path_str = os.getenv(env_var)
        if path_str:
            path = Path(path_str)
            # If relative path, make it relative to BASE_DIR
            if not path.is_absolute():
                return (BASE_DIR / path).resolve()
            return path
        return default_path
    
    # User directory for config (always ~/.leetagent for global config)
    USER_DIR: Path = Path(os.getenv("LEETAGENT_HOME", str(Path.home() / ".leetagent")))
    USER_CONFIG_PATH: Path = USER_DIR / "config.json"
    
    # Data directories - can be in project or user home
    COOKIES_PATH: Path = _resolve_path("LEETCODE_COOKIES_PATH", BASE_DIR / "data" / "cookies.json")
    SOLUTIONS_DIR: Path = _resolve_path("SOLUTIONS_DIR", BASE_DIR / "data" / "solutions")
    LOG_PATH: Path = _resolve_path("LOG_PATH", BASE_DIR / "data" / "logs")
    HISTORY_PATH: Path = _resolve_path("LEETAGENT_HISTORY_PATH", BASE_DIR / "data" / "history.json")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Project Metadata
    PROJECT_NAME: str = os.getenv("PROJECT_NAME", "LeetCode Agent Automation")
    VERSION: str = os.getenv("VERSION", "1.0.0")
    AUTHOR: str = os.getenv("AUTHOR", "Sirahmad Rasheed")
    
    def validate(self) -> bool:
        """Validate required configuration"""
        if not self.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is required. "
                "Run 'leetagent config' to set it up."
            )
        # Ensure user directories exist
        self.USER_DIR.mkdir(parents=True, exist_ok=True)
        self.SOLUTIONS_DIR.mkdir(parents=True, exist_ok=True)
        self.LOG_PATH.mkdir(parents=True, exist_ok=True)
        return True
    
    def get_chat_ids(self) -> List[str]:
        """Get list of valid chat IDs"""
        ids = []
        if self.CHAT_ID1:
            ids.append(self.CHAT_ID1)
        if self.CHAT_ID2:
            ids.append(self.CHAT_ID2)
        return ids
    
    def reload_config(self):
        """Reload configuration from config.json (useful after config changes)"""
        self._load_credentials()


# Global settings instance
settings = Settings()

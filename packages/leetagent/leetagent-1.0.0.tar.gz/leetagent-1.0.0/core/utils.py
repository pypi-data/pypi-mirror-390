"""
Utility functions for LeetCode Agent Automation
Common helpers for file operations, string formatting, and validation
"""

import re
import json
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional


def format_timestamp(fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Get current timestamp as formatted string
    
    Args:
        fmt: strftime format string
        
    Returns:
        Formatted timestamp string
    """
    return datetime.now().strftime(fmt)


def sanitize_filename(name: str, max_length: int = 100) -> str:
    """
    Clean string for safe use as filename
    
    Args:
        name: Original filename
        max_length: Maximum filename length
        
    Returns:
        Sanitized filename safe for filesystem
    """
    # Remove invalid characters
    name = re.sub(r'[<>:"/\\|?*]', '', name)
    
    # Replace spaces and special chars with underscores
    name = re.sub(r'[\s\-]+', '_', name)
    
    # Remove leading/trailing underscores
    name = name.strip('_')
    
    # Truncate if too long
    if len(name) > max_length:
        name = name[:max_length]
    
    return name or "unnamed"


def ensure_directory(path: Path) -> Path:
    """
    Create directory if it doesn't exist
    
    Args:
        path: Directory path to create
        
    Returns:
        Path object (for chaining)
    """
    path.mkdir(parents=True, exist_ok=True)
    return path


def clean_code_block(code: str) -> str:
    """
    Remove markdown code fences and extra whitespace
    
    Args:
        code: Raw code string potentially with markdown
        
    Returns:
        Cleaned code string
    """
    # Remove markdown code fences
    code = re.sub(r'^```[\w]*\n?', '', code, flags=re.MULTILINE)
    code = re.sub(r'\n?```$', '', code)
    
    # Remove excessive blank lines
    code = re.sub(r'\n{3,}', '\n\n', code)
    
    return code.strip()


def extract_code_from_response(response: str, language: str = "csharp") -> str:
    """
    Extract code from AI response with markdown formatting
    
    Args:
        response: Full AI response text
        language: Programming language identifier
        
    Returns:
        Extracted and cleaned code
    """
    # Try to find code block with language tag
    pattern = rf'```{language}\n(.*?)```'
    match = re.search(pattern, response, re.DOTALL | re.IGNORECASE)
    
    if match:
        return clean_code_block(match.group(1))
    
    # Try generic code block
    pattern = r'```\n(.*?)```'
    match = re.search(pattern, response, re.DOTALL)
    
    if match:
        return clean_code_block(match.group(1))
    
    # Return full response if no code block found
    return clean_code_block(response)


def load_json_file(file_path: Path) -> Optional[Dict[str, Any]]:
    """
    Load JSON file safely
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Parsed JSON as dict, or None if error
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, Exception):
        return None


def save_json_file(data: Dict[str, Any], file_path: Path) -> bool:
    """
    Save data to JSON file safely
    
    Args:
        data: Dictionary to save
        file_path: Target file path
        
    Returns:
        True if successful, False otherwise
    """
    try:
        ensure_directory(file_path.parent)
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception:
        return False


def truncate_string(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate string to max length with suffix
    
    Args:
        text: String to truncate
        max_length: Maximum length including suffix
        suffix: String to append when truncated
        
    Returns:
        Truncated string
    """
    if len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def parse_leetcode_slug(url: str) -> Optional[str]:
    """
    Extract problem slug from LeetCode URL
    
    Args:
        url: Full LeetCode problem URL
        
    Returns:
        Problem slug or None
        
    Examples:
        "https://leetcode.com/problems/two-sum/" -> "two-sum"
        "https://leetcode.com/problems/add-two-numbers/description/" -> "add-two-numbers"
    """
    pattern = r'leetcode\.com/problems/([^/]+)'
    match = re.search(pattern, url)
    return match.group(1) if match else None


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string like "2m 30s" or "45s"
    """
    if seconds < 60:
        return f"{seconds:.1f}s"
    
    minutes = int(seconds // 60)
    remaining_seconds = seconds % 60
    
    if minutes < 60:
        return f"{minutes}m {remaining_seconds:.0f}s"
    
    hours = int(minutes // 60)
    remaining_minutes = minutes % 60
    return f"{hours}h {remaining_minutes}m"


def validate_email(email: str) -> bool:
    """
    Basic email validation
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid format, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def chunk_list(items: List[Any], chunk_size: int) -> List[List[Any]]:
    """
    Split list into chunks of specified size
    
    Args:
        items: List to split
        chunk_size: Size of each chunk
        
    Returns:
        List of chunks
    """
    return [items[i:i + chunk_size] for i in range(0, len(items), chunk_size)]

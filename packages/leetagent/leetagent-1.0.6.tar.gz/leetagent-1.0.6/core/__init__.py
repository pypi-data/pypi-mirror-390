"""
Core module for LeetCode Agent Automation
Provides logging and utility functions
"""

from .logger import logger
from .utils import (
    format_timestamp,
    sanitize_filename,
    ensure_directory,
    clean_code_block,
    extract_code_from_response,
    load_json_file,
    save_json_file,
    parse_leetcode_slug,
    format_duration,
)

__all__ = [
    "logger",
    "format_timestamp",
    "sanitize_filename",
    "ensure_directory",
    "clean_code_block",
    "extract_code_from_response",
    "load_json_file",
    "save_json_file",
    "parse_leetcode_slug",
    "format_duration",
]

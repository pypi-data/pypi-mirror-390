"""
Utility functions for LeetCode automation
"""

from .text_helpers import (
    strip_explanation_and_fences,
    remove_cpp_section,
    remove_comments,
    format_csharp_code,
    prepare_csharp_solution,
    html_to_text,
    COMMENT_LINE_RE,
    COMMENT_BLOCK_RE,
    HTML_TAG_RE,
    C_SHARP_CODE_RE
)

__all__ = [
    'strip_explanation_and_fences',
    'remove_cpp_section',
    'remove_comments',
    'format_csharp_code',
    'prepare_csharp_solution',
    'html_to_text',
    'COMMENT_LINE_RE',
    'COMMENT_BLOCK_RE',
    'HTML_TAG_RE',
    'C_SHARP_CODE_RE'
]

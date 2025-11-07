"""
Text helper functions for LeetCode automation
Handles code formatting, comment removal, and text processing
"""

import re
from typing import List
import textwrap

# Regex patterns
COMMENT_LINE_RE = re.compile(r"//.*")
COMMENT_BLOCK_RE = re.compile(r"/\*[\s\S]*?\*/")
HTML_TAG_RE = re.compile(r"<[^>]+>")
C_SHARP_CODE_RE = re.compile(r'<code[^>]*class="[^"]*language-csharp[^"]*"[^>]*>(.*?)</code>', re.IGNORECASE | re.DOTALL)


# ================== TEXT HELPERS ==================

def strip_explanation_and_fences(text: str) -> str:
    """
    Remove markdown fences and explanatory text, keeping only code
    
    Args:
        text: Raw text with potential markdown and explanations
        
    Returns:
        Cleaned code text
    """
    if not text:
        return ""

    markers = ["using", "public class Solution", "class Solution"]
    start = -1
    for marker in markers:
        idx = text.find(marker)
        if idx != -1:
            start = idx
            break
    if start != -1:
        text = text[start:]

    if text.startswith("```"):
        text = re.sub(r"^```[^\n]*\n", "", text, count=1)
    if text.endswith("```"):
        text = text[: text.rfind("```")]
    return text.strip()


def remove_cpp_section(text: str) -> str:
    """
    Remove C++ code sections from text
    
    Args:
        text: Text potentially containing C++ code
        
    Returns:
        Text with C++ sections removed
    """
    match = re.search(r"class\s+Solution\s*\{\s*public:", text)
    if match:
        return text[: match.start()].rstrip()
    return text


def remove_comments(text: str) -> str:
    """
    Remove C-style comments (// and /* */) from code
    
    Args:
        text: Code with comments
        
    Returns:
        Code without comments
    """
    text = COMMENT_BLOCK_RE.sub("", text)
    cleaned_lines = []
    for line in text.splitlines():
        cleaned_lines.append(COMMENT_LINE_RE.sub("", line))
    return "\n".join(cleaned_lines)


def format_csharp_code(raw_text: str) -> str:
    """
    Format C# code with proper indentation
    
    Args:
        raw_text: Raw C# code
        
    Returns:
        Formatted C# code with proper indentation
    """
    text = strip_explanation_and_fences((raw_text or "").strip())
    if not text:
        return ""
    text = remove_cpp_section(text)
    text = remove_comments(text)

    formatted_lines: List[str] = []
    indent_level = 0
    for line in [ln.rstrip() for ln in text.splitlines()]:
        stripped = line.strip()
        if not stripped:
            if formatted_lines and formatted_lines[-1] != "":
                formatted_lines.append("")
            continue
        current_indent = indent_level
        if stripped.startswith("}"):
            current_indent = max(current_indent - 1, 0)
        formatted_lines.append("    " * current_indent + stripped)
        indent_level = max(current_indent + stripped.count("{") - stripped.count("}"), 0)

    cleaned = "\n".join(formatted_lines).strip()
    return cleaned + ("\n" if cleaned else "")


def prepare_csharp_solution(raw_text: str) -> str:
    """
    Prepare and validate C# solution code
    
    Args:
        raw_text: Raw C# code
        
    Returns:
        Formatted and validated C# solution, or empty string if invalid
    """
    formatted = format_csharp_code(raw_text)
    if not formatted:
        return ""
    if "class Solution" not in formatted:
        return ""
    return formatted


def html_to_text(html_fragment: str) -> str:
    """
    Convert HTML fragment to plain text
    
    Args:
        html_fragment: HTML string
        
    Returns:
        Plain text without HTML tags and with decoded entities
    """
    import html
    
    if not html_fragment:
        return ""
    
    # First decode HTML entities (like &nbsp;, &#39;, &lt;, etc.)
    text = html.unescape(html_fragment)
    
    # Remove HTML tags
    text = HTML_TAG_RE.sub(" ", text)
    
    # Clean up multiple spaces and newlines
    text = re.sub(r"[ \t]+", " ", text)  # Multiple spaces to single space
    text = re.sub(r"\n\s*\n+", "\n\n", text)  # Multiple newlines to double newline
    
    # Remove leading/trailing whitespace from each line
    lines = [line.strip() for line in text.split("\n")]
    text = "\n".join(line for line in lines if line)
    
    return text.strip()
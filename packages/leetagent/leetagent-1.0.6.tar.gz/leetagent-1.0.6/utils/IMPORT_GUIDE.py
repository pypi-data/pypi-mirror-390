"""
Quick Import Reference for text_helpers functions

Copy and paste these import statements into your files
"""

# ========================================
# Option 1: Import specific functions
# ========================================

from utils.text_helpers import format_csharp_code
from utils.text_helpers import prepare_csharp_solution
from utils.text_helpers import strip_explanation_and_fences
from utils.text_helpers import remove_comments
from utils.text_helpers import html_to_text

# Usage:
# formatted = format_csharp_code(raw_code)


# ========================================
# Option 2: Import multiple at once
# ========================================

from utils.text_helpers import (
    format_csharp_code,
    prepare_csharp_solution,
    strip_explanation_and_fences,
    remove_comments,
    html_to_text
)

# Usage:
# formatted = format_csharp_code(raw_code)
# text = html_to_text(html_string)


# ========================================
# Option 3: Import via utils package
# ========================================

from utils import (
    format_csharp_code,
    prepare_csharp_solution,
    strip_explanation_and_fences
)

# Usage: Same as above


# ========================================
# Option 4: Import entire module
# ========================================

from utils import text_helpers

# Usage:
# formatted = text_helpers.format_csharp_code(raw_code)
# text = text_helpers.html_to_text(html_string)


# ========================================
# Option 5: Import with alias
# ========================================

from utils.text_helpers import format_csharp_code as format_code

# Usage:
# formatted = format_code(raw_code)


# ========================================
# Recommended for most cases:
# ========================================

from utils.text_helpers import (
    format_csharp_code,
    prepare_csharp_solution
)

# These are the two most commonly used functions
# - format_csharp_code: For formatting AI-generated code
# - prepare_csharp_solution: For final validation before submission

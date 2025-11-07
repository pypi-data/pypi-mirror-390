"""
Example usage of text_helpers functions
Run from the LeetcodeAgentAutomation directory: python -m utils.example_usage
Or import these functions in your own scripts
"""

import sys
from pathlib import Path

# Add parent directory to path if running directly
if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent.parent))

# Method 1: Import individual functions directly from text_helpers module
from utils.text_helpers import (
    format_csharp_code, 
    prepare_csharp_solution,
    strip_explanation_and_fences,
    html_to_text,
    remove_comments
)


# Example 1: Format C# code with markdown
raw_code = """
Here's the solution:

```csharp
using System;
public class Solution {
public int Add(int a, int b) {
return a + b;
}
}
```
"""

formatted = format_csharp_code(raw_code)
print("Example 1 - Formatted C# code:")
print(formatted)
print("\n" + "="*50 + "\n")


# Example 2: Prepare solution (validates class exists)
solution = prepare_csharp_solution(raw_code)
print("Example 2 - Prepared solution:")
print(solution)
print("\n" + "="*50 + "\n")


# Example 3: Strip markdown fences
code_with_fences = """```csharp
public class Solution {
    public int Solve() { return 42; }
}
```"""

stripped = strip_explanation_and_fences(code_with_fences)
print("Example 3 - Stripped fences:")
print(stripped)
print("\n" + "="*50 + "\n")


# Example 4: HTML to text
html = "<p>This is <strong>bold</strong> text</p><div>With multiple tags</div>"
plain_text = html_to_text(html)
print("Example 4 - HTML to text:")
print(plain_text)
print("\n" + "="*50 + "\n")


# Example 5: Remove comments
code_with_comments = """
public class Solution {
    // This is a comment
    public int Calculate() {
        /* Block comment */
        return 100;
    }
}
"""

cleaned = remove_comments(code_with_comments)
print("Example 5 - Removed comments:")
print(cleaned)


if __name__ == "__main__":
    print("\n" + "="*50)
    print("All examples completed successfully!")
    print("="*50)

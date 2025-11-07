# Utils Module

Text helper functions for LeetCode automation. These standalone functions can be imported and used throughout your project.

## 📁 Files

- `text_helpers.py` - Core text processing functions
- `__init__.py` - Package initialization (makes imports easier)
- `example_usage.py` - Usage examples

## 🚀 Quick Start

### Method 1: Import from text_helpers module

```python
from utils.text_helpers import format_csharp_code, prepare_csharp_solution

code = """
```csharp
public class Solution { public int Add(int a, int b) { return a+b; } }
```
"""

formatted = format_csharp_code(code)
print(formatted)
```

### Method 2: Import from utils package

```python
from utils import format_csharp_code, html_to_text

result = format_csharp_code(raw_code)
text = html_to_text("<p>Hello</p>")
```

### Method 3: Import entire module

```python
from utils import text_helpers

formatted = text_helpers.format_csharp_code(code)
cleaned = text_helpers.remove_comments(code)
```

## 📚 Available Functions

### `strip_explanation_and_fences(text: str) -> str`

Remove markdown code fences and explanatory text, keeping only code.

**Example:**
```python
from utils.text_helpers import strip_explanation_and_fences

text = """
Here's the solution:
```csharp
public class Solution { }
```
"""

result = strip_explanation_and_fences(text)
# Output: "public class Solution { }"
```

---

### `remove_cpp_section(text: str) -> str`

Remove C++ code sections from mixed-language text.

**Example:**
```python
from utils.text_helpers import remove_cpp_section

text = """
Some text here
class Solution { public:
    int solve() { return 0; }
};
"""

result = remove_cpp_section(text)
# Output: "Some text here"
```

---

### `remove_comments(text: str) -> str`

Remove C-style comments (`//` and `/* */`) from code.

**Example:**
```python
from utils.text_helpers import remove_comments

code = """
public class Solution {
    // This is a line comment
    public int Calculate() {
        /* Block comment */
        return 100;
    }
}
"""

result = remove_comments(code)
# Comments removed, code preserved
```

---

### `format_csharp_code(raw_text: str) -> str`

Format C# code with proper indentation (4 spaces per level).

**Features:**
- Removes markdown fences
- Removes comments
- Adds proper indentation
- Handles braces correctly

**Example:**
```python
from utils.text_helpers import format_csharp_code

raw = """```csharp
public class Solution {
public int Add(int a,int b){
return a+b;
}
}
```"""

formatted = format_csharp_code(raw)
print(formatted)
```

**Output:**
```csharp
public class Solution {
    public int Add(int a,int b){
        return a+b;
    }
}
```

---

### `prepare_csharp_solution(raw_text: str) -> str`

Prepare and validate C# solution code. Returns empty string if invalid.

**Validation:**
- Must contain "class Solution"
- Must be valid C# code structure

**Example:**
```python
from utils.text_helpers import prepare_csharp_solution

# Valid solution
code = "public class Solution { public int Solve() { return 0; } }"
result = prepare_csharp_solution(code)
# Returns formatted code

# Invalid solution (no Solution class)
bad_code = "public class MyClass { }"
result = prepare_csharp_solution(bad_code)
# Returns ""
```

---

### `html_to_text(html_fragment: str) -> str`

Convert HTML fragment to plain text by removing tags.

**Example:**
```python
from utils.text_helpers import html_to_text

html = "<p>This is <strong>bold</strong> text</p><div>More text</div>"
text = html_to_text(html)
# Output: "This is bold text\nMore text"
```

---

## 🎯 Available Regex Patterns

You can also import pre-compiled regex patterns:

```python
from utils.text_helpers import (
    COMMENT_LINE_RE,      # Matches // comments
    COMMENT_BLOCK_RE,     # Matches /* */ comments
    HTML_TAG_RE,          # Matches HTML tags
    C_SHARP_CODE_RE       # Matches C# code blocks in HTML
)

# Example usage
text = "Some code // with comment"
cleaned = COMMENT_LINE_RE.sub("", text)
```

## 🔧 Usage in Your Project

### In main.py or other modules:

```python
from utils.text_helpers import format_csharp_code, prepare_csharp_solution

class LeetCodeAutomation:
    def process_solution(self, raw_code: str) -> str:
        # Format the code
        formatted = format_csharp_code(raw_code)
        
        # Validate and prepare
        solution = prepare_csharp_solution(formatted)
        
        if not solution:
            raise ValueError("Invalid solution code")
        
        return solution
```

### In modules/ai_generator.py:

```python
from utils import strip_explanation_and_fences, remove_comments

class GeminiSolutionGenerator:
    def clean_response(self, response: str) -> str:
        # Remove fences
        code = strip_explanation_and_fences(response)
        
        # Remove comments
        code = remove_comments(code)
        
        return code
```

## 🧪 Testing

Run the example script to test all functions:

```bash
# From LeetcodeAgentAutomation directory
python utils/example_usage.py
```

## 📋 Function Summary Table

| Function | Input | Output | Purpose |
|----------|-------|--------|---------|
| `strip_explanation_and_fences` | Raw text with markdown | Clean code | Remove fences and explanations |
| `remove_cpp_section` | Text with C++ | Text without C++ | Remove C++ code sections |
| `remove_comments` | Code with comments | Code without comments | Remove // and /* */ comments |
| `format_csharp_code` | Raw C# code | Formatted C# code | Add proper indentation |
| `prepare_csharp_solution` | Raw code | Validated solution | Format + validate Solution class |
| `html_to_text` | HTML string | Plain text | Remove HTML tags |

## ✅ Benefits

- ✨ **Standalone Functions** - No class dependencies, easy to import
- 📦 **Modular Design** - Use only what you need
- 🎯 **Type Hints** - Full type annotations for better IDE support
- 📖 **Documented** - Docstrings for every function
- 🧪 **Tested** - Example usage provided
- 🔄 **Reusable** - Import anywhere in your project

## 💡 Tips

1. **Import what you need**: Only import the functions you'll use
2. **Use prepare_csharp_solution**: For final validation before submission
3. **Chain functions**: Combine multiple helpers for complex processing
4. **Check return values**: Some functions may return empty strings for invalid input

## 🤝 Integration Examples

### Example 1: Process AI-generated code

```python
from utils import format_csharp_code, prepare_csharp_solution

def process_ai_response(raw_response: str) -> str:
    """Process raw AI response into clean solution"""
    formatted = format_csharp_code(raw_response)
    validated = prepare_csharp_solution(formatted)
    
    if not validated:
        raise ValueError("AI generated invalid code")
    
    return validated
```

### Example 2: Clean problem description

```python
from utils import html_to_text

def get_clean_description(html_desc: str) -> str:
    """Convert HTML problem description to plain text"""
    return html_to_text(html_desc)
```

### Example 3: Multi-step processing

```python
from utils.text_helpers import (
    strip_explanation_and_fences,
    remove_comments,
    format_csharp_code
)

def full_clean(raw_code: str) -> str:
    """Complete cleaning pipeline"""
    # Step 1: Remove fences
    code = strip_explanation_and_fences(raw_code)
    
    # Step 2: Remove comments
    code = remove_comments(code)
    
    # Step 3: Format
    code = format_csharp_code(code)
    
    return code
```

---

**Now your text_helpers functions are ready to be imported and used throughout your project!** 🎉

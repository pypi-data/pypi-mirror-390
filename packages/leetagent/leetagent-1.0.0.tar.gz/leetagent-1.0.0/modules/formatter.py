"""
Code formatting and cleaning utilities
Handles code post-processing and validation
"""

import re
from typing import Optional

from core.logger import logger
from core.utils import clean_code_block


class CodeFormatter:
    """Formats and validates generated code"""
    
    def __init__(self, language: str = "C#"):
        self.language = language
    
    def format_solution(self, code: str) -> str:
        """
        Format and clean solution code
        
        Args:
            code: Raw code string
            
        Returns:
            Formatted code string
        """
        logger.info(f"Formatting {self.language} code")
        
        # Remove markdown fences
        code = clean_code_block(code)
        
        # Language-specific formatting
        if self.language.lower() in ['c#', 'csharp']:
            code = self._format_csharp(code)
        elif self.language.lower() in ['python', 'python3']:
            code = self._format_python(code)
        
        # General cleanup
        code = self._general_cleanup(code)
        
        logger.info("Code formatting complete")
        return code
    
    def _format_csharp(self, code: str) -> str:
        """C#-specific formatting"""
        
        # Ensure using statements at top
        using_pattern = r'(using\s+[\w.]+;)'
        usings = re.findall(using_pattern, code)
        
        if usings:
            # Remove usings from middle of code
            code_without_usings = re.sub(using_pattern, '', code)
            
            # Add usings at top
            unique_usings = sorted(set(usings))
            code = '\n'.join(unique_usings) + '\n\n' + code_without_usings.strip()
        
        # Fix spacing around braces
        code = re.sub(r'\{\s*\n\s*\n+', '{\n', code)
        code = re.sub(r'\n\s*\n+\s*\}', '\n}', code)
        
        return code
    
    def _format_python(self, code: str) -> str:
        """Python-specific formatting"""
        
        # Ensure imports at top
        import_pattern = r'^((?:from|import)\s+.+)$'
        imports = re.findall(import_pattern, code, re.MULTILINE)
        
        if imports:
            # Remove imports from middle
            code_without_imports = re.sub(import_pattern, '', code, flags=re.MULTILINE)
            
            # Add imports at top
            unique_imports = sorted(set(imports))
            code = '\n'.join(unique_imports) + '\n\n' + code_without_imports.strip()
        
        # Remove excessive blank lines (max 2)
        code = re.sub(r'\n{3,}', '\n\n', code)
        
        return code
    
    def _general_cleanup(self, code: str) -> str:
        """General code cleanup"""
        
        # Remove trailing whitespace
        lines = [line.rstrip() for line in code.split('\n')]
        code = '\n'.join(lines)
        
        # Ensure single newline at end
        code = code.rstrip() + '\n'
        
        # Remove multiple consecutive blank lines
        code = re.sub(r'\n{3,}', '\n\n', code)
        
        return code
    
    def validate_solution(self, code: str) -> bool:
        """
        Validate solution code structure
        
        Args:
            code: Code to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not code or not code.strip():
            logger.error("Code is empty")
            return False
        
        # Check minimum length
        if len(code.strip()) < 20:
            logger.error("Code too short, likely incomplete")
            return False
        
        # Language-specific validation
        if self.language.lower() in ['c#', 'csharp']:
            return self._validate_csharp(code)
        elif self.language.lower() in ['python', 'python3']:
            return self._validate_python(code)
        
        return True
    
    def _validate_csharp(self, code: str) -> bool:
        """Validate C# code structure"""
        
        # Check for class definition
        if not re.search(r'\bclass\s+\w+', code):
            logger.warning("No class definition found")
            return False
        
        # Check for balanced braces
        open_braces = code.count('{')
        close_braces = code.count('}')
        
        if open_braces != close_braces:
            logger.error(f"Unbalanced braces: {open_braces} open, {close_braces} close")
            return False
        
        # Check for method definition (public/private/etc.)
        if not re.search(r'\b(public|private|protected|internal)\s+\w+\s+\w+\s*\(', code):
            logger.warning("No method definition found")
            return False
        
        logger.info("C# code structure validated")
        return True
    
    def _validate_python(self, code: str) -> bool:
        """Validate Python code structure"""
        
        # Check for class or function definition
        if not re.search(r'\b(class|def)\s+\w+', code):
            logger.warning("No class or function definition found")
            return False
        
        # Basic indentation check
        lines = code.split('\n')
        has_indented_lines = any(line.startswith((' ', '\t')) for line in lines if line.strip())
        
        if not has_indented_lines:
            logger.warning("No indentation found, code may be malformed")
            return False
        
        logger.info("Python code structure validated")
        return True
    
    def extract_class_name(self, code: str) -> Optional[str]:
        """
        Extract main class name from code
        
        Args:
            code: Source code
            
        Returns:
            Class name or None
        """
        if self.language.lower() in ['c#', 'csharp']:
            match = re.search(r'\bclass\s+(\w+)', code)
            if match:
                return match.group(1)
        elif self.language.lower() in ['python', 'python3']:
            match = re.search(r'\bclass\s+(\w+)', code)
            if match:
                return match.group(1)
        
        return None

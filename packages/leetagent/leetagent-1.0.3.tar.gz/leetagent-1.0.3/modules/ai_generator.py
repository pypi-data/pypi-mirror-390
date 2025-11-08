"""
AI-powered solution generator using Google Gemini
Generates code solutions with retry logic and feedback incorporation
"""

import time
from typing import Optional, Dict, Any

import google.generativeai as genai

from core.logger import logger
from core.utils import extract_code_from_response
from config import settings


class GeminiSolutionGenerator:
    """Generates LeetCode solutions using Gemini AI"""
    
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model_name = settings.GEMINI_MODEL_NAME
        self.max_attempts = settings.MAX_AI_ATTEMPTS
        self.model = None
    
    def _initialize_model(self):
        """Initialize Gemini model with configuration"""
        try:
            self.model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    'temperature': 0.7,
                    'top_p': 0.95,
                    'top_k': 40,
                    'max_output_tokens': 2048,
                }
            )
            logger.info(f"Initialized Gemini model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
    
    def generate_solution(
        self,
        problem: Dict[str, Any],
        language: str = "C#",
        feedback: Optional[str] = None,
        attempt_num: int = 1
    ) -> Optional[str]:
        """
        Generate solution code for problem
        
        Args:
            problem: Problem data from scraper
            language: Target programming language
            feedback: Optional feedback from previous attempts
            attempt_num: Current attempt number
            
        Returns:
            Generated code string or None if failed
        """
        if not self.model:
            self._initialize_model()
        
        # Build prompt
        prompt = self._build_prompt(problem, language, feedback, attempt_num)
        
        try:
            logger.info(f"Generating {language} solution (attempt {attempt_num}/{self.max_attempts})")
            
            response = self.model.generate_content(prompt)
            
            if not response or not response.text:
                logger.error("Empty response from Gemini")
                return None
            
            # Extract code from response
            code = extract_code_from_response(response.text, language.lower())
            
            if not code:
                logger.error("No code found in response")
                return None
            
            logger.info(f"Successfully generated solution ({len(code)} chars)")
            return code
            
        except Exception as e:
            logger.error(f"Error generating solution: {e}")
            return None
    
    def generate_with_retry(
        self,
        problem: Dict[str, Any],
        language: str = "C#",
        initial_feedback: Optional[str] = None
    ) -> Optional[str]:
        """
        Generate solution with automatic retry on failure
        
        Args:
            problem: Problem data from scraper
            language: Target programming language
            initial_feedback: Optional initial feedback
            
        Returns:
            Generated code or None after all attempts exhausted
        """
        feedback = initial_feedback
        
        for attempt in range(1, self.max_attempts + 1):
            code = self.generate_solution(
                problem=problem,
                language=language,
                feedback=feedback,
                attempt_num=attempt
            )
            
            if code:
                return code
            
            # Add generic feedback for next attempt
            feedback = "Previous attempt failed. Please provide a complete, working solution."
            
            if attempt < self.max_attempts:
                logger.warning(f"Retrying in 3 seconds... ({attempt}/{self.max_attempts})")
                time.sleep(3)
        
        logger.error(f"Failed to generate solution after {self.max_attempts} attempts")
        return None
    
    def _build_prompt(
        self,
        problem: Dict[str, Any],
        language: str,
        feedback: Optional[str],
        attempt_num: int
    ) -> str:
        """
        Build comprehensive prompt for Gemini
        
        Args:
            problem: Problem data
            language: Target language
            feedback: Optional feedback
            attempt_num: Current attempt number
            
        Returns:
            Formatted prompt string
        """
        title = problem.get('title', 'Unknown')
        difficulty = problem.get('difficulty', 'Unknown')
        content = problem.get('content', '')
        
        # Clean HTML tags from content
        import re
        content = re.sub(r'<[^>]+>', '', content)
        
        prompt_parts = [
            f"You are an expert {language} programmer solving LeetCode problems.",
            f"\n**Problem: {title}**",
            f"**Difficulty: {difficulty}**",
            f"\n{content}",
            f"\n**Requirements:**",
            f"1. Provide a complete, working {language} solution",
            f"2. Include all necessary using statements/imports",
            f"3. Use optimal time and space complexity",
            f"4. Add brief comments explaining the approach",
            f"5. Follow {language} best practices and conventions",
            f"\n**Output Format:**",
            f"Provide ONLY the complete code wrapped in ```{language.lower()} code block.",
            f"Do NOT include explanations outside the code block."
        ]
        
        # Add feedback if provided
        if feedback:
            prompt_parts.insert(3, f"\n**Feedback from previous attempt:**\n{feedback}\n")
        
        # Add urgency for later attempts
        if attempt_num > 1:
            prompt_parts.append(f"\nThis is attempt {attempt_num}. Ensure the solution is correct and complete.")
        
        return "\n".join(prompt_parts)

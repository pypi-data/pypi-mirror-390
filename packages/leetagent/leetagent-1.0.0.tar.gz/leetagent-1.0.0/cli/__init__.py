"""
CLI package
Command-line interface components
"""

from .main_cli import (
    console,
    display_welcome,
    display_auto_welcome,
    display_menu,
    prompt_problem_url,
    prompt_language,
    confirm_action,
    display_config,
    display_problem_info,
    display_progress,
    display_success,
    display_error,
    display_warning,
    create_spinner_context,
    display_code_preview,
    display_submission_result,
    clear_screen,
    pause
)

__all__ = [
    'console',
    'display_welcome',
    'display_auto_welcome',
    'display_menu',
    'prompt_problem_url',
    'prompt_language',
    'confirm_action',
    'display_config',
    'display_problem_info',
    'display_progress',
    'display_success',
    'display_error',
    'display_warning',
    'create_spinner_context',
    'display_code_preview',
    'display_submission_result',
    'clear_screen',
    'pause'
]

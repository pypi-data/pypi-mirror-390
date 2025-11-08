#!/usr/bin/env python3
"""
LeetAgent CLI Entry Point
Ensures the command works immediately after pip install
"""

def main():
    """Main entry point for leetagent CLI"""
    import sys
    from pathlib import Path
    
    # Add parent directory to path to import modules
    current_dir = Path(__file__).parent
    if str(current_dir) not in sys.path:
        sys.path.insert(0, str(current_dir))
    
    # Import and run the CLI
    try:
        from cli.main_cli import app
        app()
    except ImportError:
        # Fallback for development mode
        try:
            from leetagent_launcher import main as launcher_main
            launcher_main()
        except ImportError:
            print("Error: Unable to import LeetAgent CLI")
            print("Please reinstall: pip install --upgrade leetagent")
            sys.exit(1)


if __name__ == "__main__":
    main()

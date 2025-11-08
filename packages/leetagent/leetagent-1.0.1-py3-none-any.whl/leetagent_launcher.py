"""
Entry point launcher for LeetAgent CLI
"""

def main():
    """Main entry point that properly imports and runs the CLI app"""
    import sys
    from pathlib import Path
    
    # Add the project directory to path
    project_dir = Path(__file__).parent
    if str(project_dir) not in sys.path:
        sys.path.insert(0, str(project_dir))
    
    # Import and run the CLI app
    from cli.main_cli import app
    app()


if __name__ == "__main__":
    main()

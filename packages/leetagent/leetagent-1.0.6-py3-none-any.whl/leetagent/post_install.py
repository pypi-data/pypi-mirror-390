#!/usr/bin/env python3
"""
Post-installation script for LeetAgent
Provides helpful instructions for PATH setup
"""

import os
import sys
from pathlib import Path


def get_scripts_dir():
    """Get the Python Scripts directory path"""
    if sys.platform == "win32":
        # Windows: Multiple possible locations
        scripts_paths = [
            Path(sys.prefix) / "Scripts",
            Path(sys.base_prefix) / "Scripts",
            Path.home() / "AppData" / "Local" / "Programs" / "Python" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts",
            Path.home() / "AppData" / "Local" / "Packages" / "PythonSoftwareFoundation.Python.3.13_qbz5n2kfra8p0" / "LocalCache" / "local-packages" / "Python313" / "Scripts",
        ]
    else:
        # Unix-like systems
        scripts_paths = [
            Path(sys.prefix) / "bin",
            Path.home() / ".local" / "bin",
        ]
    
    # Return first existing path
    for path in scripts_paths:
        if path.exists():
            return path
    return scripts_paths[0]  # Return first as fallback


def is_in_path(directory):
    """Check if directory is in PATH"""
    path_var = os.environ.get("PATH", "")
    path_dirs = path_var.split(os.pathsep)
    return str(directory) in path_dirs


def print_instructions():
    """Print post-installation instructions"""
    scripts_dir = get_scripts_dir()
    
    print("\n" + "="*60)
    print("LeetAgent installed successfully!")
    print("="*60 + "\n")
    
    # Check if Scripts dir is in PATH
    if is_in_path(scripts_dir):
        print("[OK] Scripts directory is in PATH")
        print(f"Location: {scripts_dir}\n")
        print("Quick Start:")
        print("   leetagent --help")
        print("   leetagent config")
        print("   leetagent auto\n")
    else:
        print("[WARN] Scripts directory NOT in PATH")
        print(f"Location: {scripts_dir}\n")
        
        print("Option 1: Run via Python (Works Now!)")
        print("   python -m leetagent --help")
        print("   python -m leetagent config")
        print("   python -m leetagent auto\n")
        
        print("Option 2: Add to PATH (Permanent Fix)\n")
        
        if sys.platform == "win32":
            print("   Windows:")
            print("   1. Press Win+R, type: sysdm.cpl")
            print("   2. Advanced → Environment Variables")
            print("   3. Edit 'Path' variable and add:")
            print(f"      {scripts_dir}")
            print("   4. Restart terminal\n")
        else:
            shell = os.environ.get("SHELL", "bash")
            if "zsh" in shell:
                rc_file = "~/.zshrc"
            elif "fish" in shell:
                rc_file = "~/.config/fish/config.fish"
            else:
                rc_file = "~/.bashrc"
            
            print(f"   Linux/macOS (add to {rc_file}):")
            print(f'   export PATH="$PATH:{scripts_dir}"')
            print(f"   Then: source {rc_file}\n")
    
    print("="*60)
    print("Documentation: https://github.com/satyamyadav/leetagent")
    print("Issues: https://github.com/satyamyadav/leetagent/issues")
    print("="*60 + "\n")


if __name__ == "__main__":
    print_instructions()

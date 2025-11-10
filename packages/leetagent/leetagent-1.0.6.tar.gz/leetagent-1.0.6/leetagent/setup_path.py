"""
Post-installation script that adds Scripts directory to PATH
Cross-platform automatic PATH configuration
"""

import os
import sys
import platform
from pathlib import Path


def get_scripts_dir():
    """Get the Python Scripts directory"""
    if platform.system() == "Windows":
        # Check various Windows Python installation locations
        possible_paths = [
            Path(sys.prefix) / "Scripts",
            Path(sys.base_prefix) / "Scripts",
            Path.home() / "AppData" / "Local" / "Programs" / "Python" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts",
            Path.home() / "AppData" / "Roaming" / "Python" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts",
        ]
        
        # Also check for Microsoft Store Python
        appdata_local = Path.home() / "AppData" / "Local"
        if appdata_local.exists():
            for pkg_dir in appdata_local.glob("Packages/PythonSoftwareFoundation.Python.*"):
                scripts = pkg_dir / "LocalCache" / "local-packages" / f"Python{sys.version_info.major}{sys.version_info.minor}" / "Scripts"
                if scripts.exists():
                    possible_paths.insert(0, scripts)
    else:
        possible_paths = [
            Path(sys.prefix) / "bin",
            Path.home() / ".local" / "bin",
        ]
    
    for path in possible_paths:
        if path.exists():
            return path
    return possible_paths[0]


def is_in_path(directory):
    """Check if directory is in PATH"""
    path_var = os.environ.get("PATH", "")
    return str(directory) in path_var.split(os.pathsep)


def add_to_windows_path(directory):
    """Add directory to Windows PATH using registry (requires admin or user registry)"""
    import winreg
    
    try:
        # Try user environment first (doesn't require admin)
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Environment",
            0,
            winreg.KEY_READ | winreg.KEY_WRITE
        )
        
        try:
            current_path, _ = winreg.QueryValueEx(key, "Path")
        except FileNotFoundError:
            current_path = ""
        
        # Check if already in PATH
        if str(directory) in current_path.split(os.pathsep):
            winreg.CloseKey(key)
            return True, "Already in PATH"
        
        # Add to PATH
        if current_path and not current_path.endswith(os.pathsep):
            current_path += os.pathsep
        new_path = current_path + str(directory)
        
        winreg.SetValueEx(key, "Path", 0, winreg.REG_EXPAND_SZ, new_path)
        winreg.CloseKey(key)
        
        # Broadcast environment change
        import ctypes
        HWND_BROADCAST = 0xFFFF
        WM_SETTINGCHANGE = 0x1A
        ctypes.windll.user32.SendMessageW(
            HWND_BROADCAST, WM_SETTINGCHANGE, 0, "Environment"
        )
        
        return True, "Added to PATH successfully"
    except Exception as e:
        return False, str(e)


def add_to_unix_path(directory):
    """Add directory to Unix shell configuration"""
    shell = os.environ.get("SHELL", "bash")
    
    if "zsh" in shell:
        rc_file = Path.home() / ".zshrc"
    elif "fish" in shell:
        rc_file = Path.home() / ".config" / "fish" / "config.fish"
        export_line = f'set -x PATH $PATH {directory}\n'
    else:
        rc_file = Path.home() / ".bashrc"
    
    if "fish" not in shell:
        export_line = f'export PATH="$PATH:{directory}"\n'
    
    try:
        # Check if already in file
        if rc_file.exists():
            content = rc_file.read_text()
            if str(directory) in content:
                return True, f"Already in {rc_file}"
        
        # Append to file
        with open(rc_file, "a") as f:
            f.write(f"\n# Added by LeetAgent\n")
            f.write(export_line)
        
        return True, f"Added to {rc_file}"
    except Exception as e:
        return False, str(e)


def configure_path():
    """Main function to configure PATH"""
    scripts_dir = get_scripts_dir()
    
    print("\n" + "="*60)
    print("LeetAgent Post-Installation Setup")
    print("="*60 + "\n")
    
    if is_in_path(scripts_dir):
        print(f"[OK] Scripts directory already in PATH")
        print(f"     {scripts_dir}\n")
        print("You can use: leetagent --help")
        return
    
    print(f"[INFO] Scripts directory: {scripts_dir}")
    print(f"[WARN] Not currently in PATH\n")
    
    # Ask user for permission
    response = input("Add to PATH automatically? (y/n): ").lower().strip()
    
    if response != 'y':
        print("\n[SKIP] PATH not modified")
        print("\nRun 'python -m leetagent-doctor' for manual setup instructions")
        return
    
    # Attempt to add to PATH
    if platform.system() == "Windows":
        success, message = add_to_windows_path(scripts_dir)
    else:
        success, message = add_to_unix_path(scripts_dir)
    
    if success:
        print(f"\n[SUCCESS] {message}")
        print(f"[INFO] Added: {scripts_dir}")
        
        if platform.system() == "Windows":
            print("\n[NOTE] Restart your terminal for changes to take effect")
            print("       Or run: refreshenv (if using Chocolatey)")
        else:
            print(f"\n[NOTE] Run: source {Path.home()}/{'zshrc' if 'zsh' in os.environ.get('SHELL', '') else 'bashrc'}")
        
        print("\nThen you can use: leetagent --help")
    else:
        print(f"\n[ERROR] Failed to modify PATH: {message}")
        print("\nRun 'python -m leetagent-doctor' for manual setup instructions")


if __name__ == "__main__":
    try:
        configure_path()
    except KeyboardInterrupt:
        print("\n\n[CANCELLED] Setup interrupted")
    except Exception as e:
        print(f"\n[ERROR] {e}")
        print("\nRun 'python -m leetagent-doctor' for manual setup instructions")

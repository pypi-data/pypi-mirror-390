"""
pycom0com - Python bindings for com0com virtual serial ports
"""

import os
from pathlib import Path
from ctypes import windll
from typing import NoReturn
from sys import executable, exit
from subprocess import run, CompletedProcess, TimeoutExpired



def is_admin() -> bool:
    """
    Check if the script is running with administrator privileges
    
    Returns:
        is_admin (bool):
            `True` if running as administrator, `False` otherwise
    """

    try:
        return windll.shell32.IsUserAnAdmin()
    except (AttributeError, OSError, WindowsError):
        return False


def elevate_privileges() -> NoReturn:
    """
    Restart the script with administrator privileges
    
    Raises:
        SystemExit:
            Always exits the current process after requesting elevation
    """

    script_path: str = str(Path(__file__).resolve())
    windll.shell32.ShellExecuteW(
        None, "runas", executable, f'"{script_path}"', None, 1
    )
    exit(0)


def install_driver() -> bool:
    """
    Install the com0com driver from the bin directory
    
    Returns:
        is_access (bool):
            `True` if driver installation was successful,  
            `False` otherwise
        
    Raises:
        subprocess.TimeoutExpired: If driver installation times out
        Exception: For any unexpected errors during installation
    """

    try:
        # Get path to bin directory
        bin_dir: Path = Path(__file__).parent / "bin"
        
        # Main driver INF file
        inf_file: Path = bin_dir / "com0com.inf"
        
        # Verify INF file exists
        if not inf_file.exists():
            print("❌ Driver INF file not found:", inf_file)
            return False
        
        print("Installing com0com driver...")
        
        # Use pnputil to install driver
        result: CompletedProcess = run([
            "pnputil", "/add-driver", 
            str(inf_file), 
            "/install"
        ], capture_output=True, text=True, timeout=120)
        
        if result.returncode == 0:
            print("✅ Driver successfully installed!")
            print("Created virtual ports will be available in Device Manager")

            return True
        elif result.returncode == 259:
            print("✅ Driver was already installed! pnputil output:")
            print(result.stdout)
            print("Created virtual ports will be available in Device Manager")
            return True
        else:
            print("❌ Error installing driver:")
            print(result.stderr)
            return False
            
    except TimeoutExpired:
        print("❌ Timeout during driver installation")
        return False
    except FileNotFoundError:
        print("❌ pnputil not found. This utility is required for driver installation")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {str(e)}")
        return False


def main():
    """
    Main installation function.
    
    Handles Windows compatibility check, admin privileges verification,
    and driver installation process
    
    Exits:
        SystemExit:
            With code 1 if not Windows, driver installation fails, 
            or insufficient privileges
    """

    print("=" * 50)
    print("com0com Virtual COM Port Installer")
    print("=" * 50)
    
    # Check Windows compatibility
    if os.name != 'nt':
        print("❌ This script only works on Windows")
        sys.exit(1)
    
    # Verify administrator privileges
    if not is_admin():
        print("⚠️  Administrator privileges required for driver installation")
        elevate_privileges()
        return
    
    # Install driver
    success: bool = install_driver()
    
    if success:
        print("\n🎉 Installation completed successfully!")
        print("\nYou can now use pycom0com to create")
        print("virtual serial ports in Python")
    else:
        print("\n💥 Installation failed")
        exit(1)



if __name__ == "__main__":
    main()
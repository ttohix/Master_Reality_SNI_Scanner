#!/usr/bin/env python3
"""
Master SNI Scanner - Auto Installer v2.0.0
Detects OS and installs all dependencies for both Server and Client
"""

import os
import sys
import subprocess
import platform
import shutil
import time

# Colors
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
CYAN = '\033[96m'
MAGENTA = '\033[95m'
RESET = '\033[0m'


def print_info(msg): print(f"{BLUE}[INFO]{RESET} {msg}")


def print_success(msg): print(f"{GREEN}[✓]{RESET} {msg}")


def print_error(msg): print(f"{RED}[✗]{RESET} {msg}")


def print_warning(msg): print(f"{YELLOW}[!]{RESET} {msg}")


def print_banner_logo():
    print(f"""
{MAGENTA}
╔══════════════════════════════════════════════════════════════════╗
║     Master SNI Scanner v2.0.0 - Auto Installer                  ║
║     Detect OS | Install Dependencies | Setup Complete           ║
╚══════════════════════════════════════════════════════════════════╝
{RESET}""")


def detect_os():
    system = platform.system().lower()
    if system == 'windows':
        return 'windows'
    elif system == 'linux':
        return 'linux'
    elif system == 'darwin':
        return 'macos'
    else:
        return 'unknown'


def get_package_manager():
    if shutil.which('apt-get'):
        return 'apt'
    elif shutil.which('yum'):
        return 'yum'
    elif shutil.which('dnf'):
        return 'dnf'
    elif shutil.which('pacman'):
        return 'pacman'
    elif shutil.which('zypper'):
        return 'zypper'
    else:
        return None


def check_xray_installed():
    xray_paths = ['/usr/local/bin/xray', '/usr/bin/xray']
    for path in xray_paths:
        if os.path.exists(path):
            return True
    if shutil.which('xray'):
        return True
    return False


def check_python_package(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


def check_script_files():
    """Check if server.py and client.py exist"""
    scripts = ['server.py', 'client.py']
    missing = []
    for script in scripts:
        if os.path.exists(script):
            print_success(f"{script} found")
        else:
            print_warning(f"{script} not found")
            missing.append(script)
    return missing


def check_requirements():
    requirements = {
        'python3': {'status': False, 'version': None},
        'pip': {'status': False},
        'requests': {'status': False},
        'cryptography': {'status': False},
        'xray': {'status': False}
    }

    try:
        python_version = sys.version_info
        if python_version.major >= 3 and python_version.minor >= 6:
            requirements['python3']['status'] = True
            requirements['python3']['version'] = f"{python_version.major}.{python_version.minor}.{python_version.micro}"
    except:
        pass

    if shutil.which('pip3') or shutil.which('pip'):
        requirements['pip']['status'] = True

    requirements['requests']['status'] = check_python_package('requests')
    requirements['cryptography']['status'] = check_python_package('cryptography')
    requirements['xray']['status'] = check_xray_installed()

    return requirements


def print_status_table(requirements):
    headers = ["Requirement", "Status", "Details"]
    rows = []

    for name, info in requirements.items():
        status = f"{GREEN}✓ Installed{RESET}" if info['status'] else f"{RED}✗ Not installed{RESET}"
        detail = ""
        if name == 'python3' and info['version']:
            detail = f"v{info['version']}"
        elif name == 'xray' and info['status']:
            detail = "Found"
        rows.append([name.upper(), status, detail])

    col_widths = [len("Requirement"), len("Status"), len("Details")]
    for row in rows:
        for i, cell in enumerate(row):
            clean_cell = cell.replace(GREEN, '').replace(RED, '').replace(YELLOW, '').replace(RESET, '')
            col_widths[i] = max(col_widths[i], len(clean_cell) + 2)

    total_width = sum(col_widths) + len(rows[0]) + 1

    print(f"{CYAN}{'─' * total_width}{RESET}")
    header_line = "│"
    for i, header in enumerate(headers):
        header_line += f" {header.ljust(col_widths[i] - 1)}│"
    print(f"{CYAN}{header_line}{RESET}")
    print(f"{CYAN}{'─' * total_width}{RESET}")

    for row in rows:
        row_line = "│"
        for i, cell in enumerate(row):
            clean_cell = cell.replace(GREEN, '').replace(RED, '').replace(YELLOW, '').replace(RESET, '')
            padding = col_widths[i] - len(clean_cell) - 1
            row_line += f" {cell}{' ' * padding}│"
        print(f"{row_line}{RESET}")

    print(f"{CYAN}{'─' * total_width}{RESET}")


def install_on_windows():
    print_info("Installing on Windows...")

    if not shutil.which('python'):
        print_error("Python is not installed!")
        print_warning("Download: https://www.python.org/downloads/")
        return False

    print_info("Installing Python packages...")
    packages = ['requests', 'cryptography']
    for package in packages:
        if not check_python_package(package):
            print_info(f"Installing {package}...")
            subprocess.run(f'python -m pip install {package} -q', shell=True, capture_output=True)
        else:
            print_success(f"{package} already installed")

    if not check_xray_installed():
        print_warning("Xray not found.")
        print_warning("Download from: https://github.com/XTLS/Xray-core/releases")
        print_warning("Extract to: C:\\Program Files\\xray\\ and add to PATH")
        input(f"\n{YELLOW}Press Enter after installing Xray...{RESET}")

    return True


def install_on_linux():
    print_info("Installing on Linux...")

    pm = get_package_manager()
    if not pm:
        print_error("No package manager detected!")
        return False

    system_packages = {
        'apt': 'python3 python3-pip curl openssl',
        'yum': 'python3 python3-pip curl openssl',
        'dnf': 'python3 python3-pip curl openssl',
        'pacman': 'python python-pip curl openssl',
        'zypper': 'python3 python3-pip curl openssl'
    }

    if pm in system_packages:
        print_info(f"Installing system packages using {pm}...")
        cmd = f"sudo {pm} install -y {system_packages[pm]}"
        subprocess.run(cmd, shell=True, capture_output=True)

    print_info("Installing Python packages...")
    packages = ['requests', 'cryptography']
    for package in packages:
        if not check_python_package(package):
            print_info(f"Installing {package}...")
            subprocess.run(f'pip3 install {package} -q', shell=True, capture_output=True)
        else:
            print_success(f"{package} already installed")

    if not check_xray_installed():
        print_info("Installing Xray-core...")
        cmd = 'bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install'
        subprocess.run(cmd, shell=True, capture_output=True)
        time.sleep(3)
    else:
        print_success("Xray already installed")

    return True


def install_on_macos():
    print_info("Installing on macOS...")

    if not shutil.which('brew'):
        print_info("Installing Homebrew...")
        subprocess.run(
            '/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"',
            shell=True)

    print_info("Installing system packages...")
    subprocess.run('brew install python3 curl openssl', shell=True, capture_output=True)

    print_info("Installing Python packages...")
    packages = ['requests', 'cryptography']
    for package in packages:
        if not check_python_package(package):
            print_info(f"Installing {package}...")
            subprocess.run(f'pip3 install {package} -q', shell=True, capture_output=True)
        else:
            print_success(f"{package} already installed")

    if not check_xray_installed():
        print_info("Installing Xray-core...")
        cmd = 'bash -c "$(curl -L https://github.com/XTLS/Xray-install/raw/main/install-release.sh)" @ install'
        subprocess.run(cmd, shell=True, capture_output=True)
        time.sleep(3)
    else:
        print_success("Xray already installed")

    return True


def create_launcher_scripts():
    print_info("Creating launcher scripts...")

    if platform.system().lower() == 'windows':
        with open('run_server.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting Master SNI Scanner Server...\n')
            f.write('python server.py\n')
            f.write('pause\n')

        with open('run_client.bat', 'w') as f:
            f.write('@echo off\n')
            f.write('echo Starting Master SNI Scanner Client...\n')
            f.write('python client.py\n')
            f.write('pause\n')

        print_success("Created: run_server.bat, run_client.bat")
    else:
        with open('run_server.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Master SNI Scanner Server..."\n')
            f.write('sudo python3 server.py\n')
        os.chmod('run_server.sh', 0o755)

        with open('run_client.sh', 'w') as f:
            f.write('#!/bin/bash\n')
            f.write('echo "Starting Master SNI Scanner Client..."\n')
            f.write('python3 client.py "$@"\n')
        os.chmod('run_client.sh', 0o755)

        print_success("Created: run_server.sh, run_client.sh")


def create_requirements_file():
    if not os.path.exists('requirements.txt'):
        with open('requirements.txt', 'w') as f:
            f.write('# Master SNI Scanner v2.0.0\n')
            f.write('requests>=2.31.0\n')
            f.write('cryptography>=41.0.0\n')
        print_success("Created: requirements.txt")
    else:
        print_success("requirements.txt already exists")


def main():
    print_banner_logo()

    os_name = detect_os()
    print_info(f"Detected OS: {os_name.upper()}")

    if os_name == 'unknown':
        print_error("Unsupported operating system!")
        sys.exit(1)

    # Check script files
    print_info("\nChecking script files...")
    missing_scripts = check_script_files()

    if missing_scripts:
        print_warning(f"Missing scripts: {', '.join(missing_scripts)}")
        print_warning("Please ensure server.py and client.py are in the same directory")

    # Check requirements
    requirements = check_requirements()
    print_status_table(requirements)

    all_installed = all(info['status'] for info in requirements.values())

    if all_installed:
        print_success("\nAll requirements are already installed!")
        answer = input(f"\n{YELLOW}Reinstall anyway? (y/n): {RESET}").strip().lower()
        if answer != 'y':
            create_launcher_scripts()
            create_requirements_file()
            print(f"\n{GREEN}{'=' * 60}{RESET}")
            print_success("Setup complete!")
            print(f"  Server: {CYAN}sudo python3 server.py{RESET}")
            print(f"  Client: {CYAN}python3 client.py{RESET}")
            print(f"{GREEN}{'=' * 60}{RESET}")
            sys.exit(0)

    print_info("\nInstalling missing dependencies...")

    success = False
    if os_name == 'windows':
        success = install_on_windows()
    elif os_name == 'linux':
        success = install_on_linux()
    elif os_name == 'macos':
        success = install_on_macos()

    if not success:
        print_error("Installation failed!")
        sys.exit(1)

    create_launcher_scripts()
    create_requirements_file()

    final_check = check_requirements()
    missing = [name for name, info in final_check.items() if not info['status']]

    print(f"\n{GREEN}{'=' * 60}{RESET}")
    if missing:
        print_warning(f"Missing: {', '.join(missing)}")
        print_warning("Please install them manually.")
    else:
        print_success("All requirements installed successfully!")

    if missing_scripts:
        print_warning(f"Scripts not found: {', '.join(missing_scripts)}")

    print(f"\n{YELLOW}How to use:{RESET}")
    print(f"  Server: {CYAN}sudo python3 server.py{RESET}")
    print(f"  Client: {CYAN}python3 client.py{RESET}")
    print(f"{GREEN}{'=' * 60}{RESET}")


if __name__ == "__main__":
    main()

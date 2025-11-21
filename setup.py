#!/usr/bin/env python
"""
Setup script for Crypto MCP Server
Automates the installation and configuration process
"""

import os
import sys
import subprocess
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")


def print_step(step, text):
    """Print step information"""
    print(f"[{step}] {text}")


def run_command(cmd, description):
    """Run a shell command and handle errors"""
    print(f"  Running: {description}")
    try:
        result = subprocess.run(
            cmd, shell=True, check=True, capture_output=True, text=True
        )
        if result.stdout:
            print(f"  ✓ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ✗ Error: {e}")
        if e.stderr:
            print(f"  {e.stderr}")
        return False


def check_python_version():
    """Check if Python version is 3.9+"""
    print_step("1/6", "Checking Python version")
    version = sys.version_info
    if version.major == 3 and version.minor >= 9:
        print(f"  ✓ Python {version.major}.{version.minor}.{version.micro} detected")
        return True
    else:
        print(f"  ✗ Python 3.9+ required, found {version.major}.{version.minor}")
        return False


def create_virtual_environment():
    """Create virtual environment"""
    print_step("2/6", "Creating virtual environment")
    if Path("venv").exists():
        print("  ℹ Virtual environment already exists")
        return True
    return run_command(f"{sys.executable} -m venv venv", "Virtual environment creation")


def install_dependencies():
    """Install project dependencies"""
    print_step("3/6", "Installing dependencies")
    
    # Determine pip path based on OS
    if sys.platform == "win32":
        pip_path = "venv\\Scripts\\pip.exe"
    else:
        pip_path = "venv/bin/pip"
    
    if not Path(pip_path).exists():
        print("  ✗ Virtual environment not found. Please run step 2 first.")
        return False
    
    # Upgrade pip
    run_command(f"{pip_path} install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    return run_command(
        f"{pip_path} install -r requirements.txt",
        "Installing project dependencies"
    )


def setup_environment():
    """Set up environment configuration"""
    print_step("4/6", "Setting up environment configuration")
    
    if Path(".env").exists():
        print("  ℹ .env file already exists")
        response = input("  Do you want to overwrite it? (y/N): ")
        if response.lower() != 'y':
            print("  Keeping existing .env file")
            return True
    
    if Path(".env.example").exists():
        try:
            with open(".env.example", "r") as src:
                content = src.read()
            with open(".env", "w") as dst:
                dst.write(content)
            print("  ✓ Created .env file from .env.example")
            return True
        except Exception as e:
            print(f"  ✗ Error creating .env file: {e}")
            return False
    else:
        print("  ✗ .env.example not found")
        return False


def run_tests():
    """Run test suite"""
    print_step("5/6", "Running test suite")
    
    response = input("  Do you want to run tests? (Y/n): ")
    if response.lower() == 'n':
        print("  Skipping tests")
        return True
    
    # Determine pytest path
    if sys.platform == "win32":
        pytest_path = "venv\\Scripts\\pytest.exe"
    else:
        pytest_path = "venv/bin/pytest"
    
    if not Path(pytest_path).exists():
        print("  ✗ pytest not found in virtual environment")
        return False
    
    return run_command(f"{pytest_path} tests/ -v", "Running tests")


def print_next_steps():
    """Print next steps for the user"""
    print_step("6/6", "Setup complete!")
    
    print("\n" + "=" * 60)
    print("  Next Steps:")
    print("=" * 60)
    print("\n1. Activate the virtual environment:")
    
    if sys.platform == "win32":
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    
    print("\n2. (Optional) Edit .env file to add API keys:")
    print("   # Open .env in your favorite editor")
    
    print("\n3. Run the server:")
    print("   python main.py")
    
    print("\n4. Run the examples:")
    print("   python examples/simple_example.py")
    
    print("\n5. Run tests:")
    print("   pytest")
    
    print("\n" + "=" * 60)
    print("  Documentation:")
    print("=" * 60)
    print("  • README.md - Full documentation")
    print("  • QUICKSTART.md - Quick reference guide")
    print("  • CONTRIBUTING.md - How to contribute")
    print("  • PROJECT_SUMMARY.md - Project overview")
    print("\n")


def main():
    """Main setup function"""
    print_header("Crypto MCP Server - Setup Script")
    print("This script will set up the Crypto MCP Server environment.\n")
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    # Run setup steps
    steps = [
        check_python_version,
        create_virtual_environment,
        install_dependencies,
        setup_environment,
        run_tests,
    ]
    
    for step_func in steps:
        if not step_func():
            print("\n❌ Setup failed. Please fix the errors and try again.\n")
            return False
    
    # Print next steps
    print_next_steps()
    
    print("✅ Setup completed successfully!\n")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

#!/usr/bin/env python
"""
Quality check script for Crypto MCP Server
Runs all code quality checks and generates a report
"""

import subprocess
import sys
from pathlib import Path


def print_header(text):
    """Print formatted header"""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70 + "\n")


def run_check(name, command, description):
    """Run a quality check command"""
    print(f"Running: {name}")
    print(f"Description: {description}")
    print("-" * 70)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=120
        )
        
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        
        if result.returncode == 0:
            print(f"✅ {name} PASSED\n")
            return True
        else:
            print(f"❌ {name} FAILED (exit code: {result.returncode})\n")
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏱️  {name} TIMEOUT\n")
        return False
    except Exception as e:
        print(f"❌ {name} ERROR: {e}\n")
        return False


def main():
    """Run all quality checks"""
    print_header("Crypto MCP Server - Quality Checks")
    
    # Change to project directory
    os.chdir(Path(__file__).parent)
    
    results = {}
    
    # 1. Code Formatting Check (Black)
    results['black'] = run_check(
        "Black (Code Formatting)",
        "black --check crypto_mcp_server tests examples --line-length=100",
        "Checks if code is formatted according to Black style"
    )
    
    # 2. Import Sorting Check (isort)
    results['isort'] = run_check(
        "isort (Import Sorting)",
        "isort --check-only crypto_mcp_server tests examples",
        "Checks if imports are sorted correctly"
    )
    
    # 3. Linting (Flake8)
    results['flake8'] = run_check(
        "Flake8 (Linting)",
        "flake8 crypto_mcp_server tests examples --max-line-length=100 --extend-ignore=E203,W503",
        "Checks code for style violations and potential errors"
    )
    
    # 4. Type Checking (MyPy)
    results['mypy'] = run_check(
        "MyPy (Type Checking)",
        "mypy crypto_mcp_server --ignore-missing-imports",
        "Checks type hints and catches type errors"
    )
    
    # 5. Test Suite
    results['pytest'] = run_check(
        "Pytest (Test Suite)",
        "pytest tests/ -v --tb=short",
        "Runs all unit tests"
    )
    
    # 6. Test Coverage
    results['coverage'] = run_check(
        "Coverage (Test Coverage)",
        "pytest tests/ --cov=crypto_mcp_server --cov-report=term --cov-fail-under=80",
        "Checks test coverage (target: 80%+)"
    )
    
    # Print summary
    print_header("Quality Check Summary")
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed
    
    print(f"Total Checks: {total}")
    print(f"Passed: {passed} ✅")
    print(f"Failed: {failed} ❌")
    print(f"Success Rate: {(passed/total)*100:.1f}%\n")
    
    print("Detailed Results:")
    print("-" * 70)
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"  {check.upper():15} : {status}")
    
    print("\n" + "=" * 70)
    
    if failed == 0:
        print("🎉 All quality checks passed! Code is ready for review.")
        return 0
    else:
        print(f"⚠️  {failed} check(s) failed. Please fix the issues and re-run.")
        return 1


if __name__ == "__main__":
    import os
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n❌ Quality checks cancelled by user.\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)

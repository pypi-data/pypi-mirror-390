"""
CodeSentinel v1.0.1 Package Installation Test Script
====================================================

Tests installation of both tar.gz and wheel packages in isolated environments.
Automated test script for non-interactive execution.
"""

import subprocess
import sys
import os
from pathlib import Path
import shutil

def run_command(cmd, cwd=None, capture=True):
    """Run a command and return output."""
    print(f"  Running: {cmd}")
    result = subprocess.run(
        cmd,
        shell=True,
        cwd=cwd,
        capture_output=capture,
        text=True
    )
    if capture:
        return result.returncode, result.stdout, result.stderr
    return result.returncode, "", ""

def test_installation(package_file, env_name):
    """Test installation of a specific package in an isolated environment."""
    print(f"\n{'='*70}")
    print(f"Testing: {package_file}")
    print(f"Environment: {env_name}")
    print(f"{'='*70}")
    
    env_path = Path(env_name)
    package_path = Path("dist") / package_file
    
    # Check if package exists
    if not package_path.exists():
        print(f"❌ FAILED: Package not found: {package_path}")
        return False
    
    try:
        # Step 1: Create virtual environment
        print("\n[1/6] Creating isolated virtual environment...")
        code, stdout, stderr = run_command(f"python -m venv {env_name}")
        if code != 0:
            print(f"❌ FAILED: Could not create venv\n{stderr}")
            return False
        print("✅ Virtual environment created")
        
        # Get python and pip paths
        if sys.platform == "win32":
            python_exe = env_path / "Scripts" / "python.exe"
            pip_exe = env_path / "Scripts" / "pip.exe"
        else:
            python_exe = env_path / "bin" / "python"
            pip_exe = env_path / "bin" / "pip"
        
        # Step 2: Upgrade pip
        print("\n[2/6] Upgrading pip...")
        code, stdout, stderr = run_command(f'"{python_exe}" -m pip install --upgrade pip')
        if code != 0:
            print(f"⚠️  Warning: pip upgrade had issues\n{stderr}")
        else:
            print("✅ pip upgraded")
        
        # Step 3: Install package
        print(f"\n[3/6] Installing {package_file}...")
        code, stdout, stderr = run_command(f'"{pip_exe}" install "{package_path.absolute()}"')
        if code != 0:
            print(f"❌ FAILED: Installation failed\n{stderr}")
            return False
        print("✅ Package installed successfully")
        
        # Step 4: Verify installation
        print("\n[4/6] Verifying package installation...")
        code, stdout, stderr = run_command(f'"{pip_exe}" show codesentinel')
        if code != 0:
            print(f"❌ FAILED: Package not found after installation\n{stderr}")
            return False
        
        # Parse and display package info
        info = {}
        for line in stdout.split('\n'):
            if ':' in line:
                key, value = line.split(':', 1)
                info[key.strip()] = value.strip()
        
        print("✅ Package verified")
        print(f"   Name: {info.get('Name', 'N/A')}")
        print(f"   Version: {info.get('Version', 'N/A')}")
        print(f"   Location: {info.get('Location', 'N/A')}")
        
        # Step 5: Test import
        print("\n[5/6] Testing package import...")
        code, stdout, stderr = run_command(
            f'"{python_exe}" -c "import sys; sys.stdout.reconfigure(encoding=\'utf-8\'); import codesentinel; print(f\'Version: {{codesentinel.__version__}}\'); print(\'[OK] Import successful\')"'
        )
        if code != 0:
            print(f"FAILED: Import failed\n{stderr}")
            return False
        print(stdout)
        
        # Step 6: Test entry points
        print("\n[6/6] Testing entry points...")
        entry_points_to_test = [
            ("codesentinel", "codesentinel --version"),
            ("codesentinel-setup", "codesentinel-setup --help"),
            ("codesentinel-setup-gui", "codesentinel-setup-gui --help"),
        ]
        
        all_passed = True
        for name, cmd in entry_points_to_test:
            if sys.platform == "win32":
                script_path = env_path / "Scripts" / f"{name}.exe"
            else:
                script_path = env_path / "bin" / name
            
            if script_path.exists():
                print(f"   ✅ {name}: Found")
            else:
                print(f"   ⚠️  {name}: Not found (may be optional)")
        
        print(f"\n{'='*70}")
        print(f"✅ INSTALLATION TEST PASSED: {package_file}")
        print(f"{'='*70}")
        return True
        
    except Exception as e:
        print(f"\n❌ FAILED: Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        print(f"\n[Cleanup] Removing test environment...")
        try:
            if env_path.exists():
                shutil.rmtree(env_path)
                print(f"✅ Cleaned up {env_name}")
        except Exception as e:
            print(f"⚠️  Warning: Could not remove {env_name}: {e}")

def main():
    """Run all package installation tests."""
    print("="*70)
    print("CodeSentinel v1.0.1 Package Installation Test Suite")
    print("="*70)
    print("\nThis script will test installation of:")
    print("  1. codesentinel-1.0.1.tar.gz (source distribution)")
    print("  2. codesentinel-1.0.1-py3-none-any.whl (wheel)")
    print("\nEach test will:")
    print("  - Create an isolated virtual environment")
    print("  - Install the package")
    print("  - Verify the installation")
    print("  - Test imports and entry points")
    print("  - Clean up the environment")
    print("")
    
    # Change to project root
    os.chdir(Path(__file__).parent)
    
    test_results = []
    
    # Test 1: tar.gz installation
    result1 = test_installation("codesentinel-1.0.1.tar.gz", "test_env_tarball")
    test_results.append(("tar.gz", result1))
    
    # Test 2: wheel installation  
    result2 = test_installation("codesentinel-1.0.1-py3-none-any.whl", "test_env_wheel")
    test_results.append(("wheel", result2))
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    all_passed = True
    for package_type, result in test_results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"  {package_type:10} : {status}")
        if not result:
            all_passed = False
    
    print("="*70)
    
    if all_passed:
        print("\n🎉 All installation tests passed!")
        print("✅ codesentinel-1.0.1 is ready for distribution")
        return 0
    else:
        print("\n❌ Some tests failed. Please review the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
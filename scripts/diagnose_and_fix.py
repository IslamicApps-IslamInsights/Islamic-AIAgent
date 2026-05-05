#!/usr/bin/env python3
"""
Comprehensive Diagnostics and Quick Fix Script
"""

import os
import sys
import subprocess
import json
from pathlib import Path

def print_section(title):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def check_disk_space():
    """Check disk space"""
    print_section("Disk Space Check")
    import shutil
    try:
        stat = shutil.disk_usage("/")
        free_gb = stat.free / (1024**3)
        total_gb = stat.total / (1024**3)
        used_pct = (stat.used / stat.total) * 100
        
        print(f"Total: {total_gb:.1f} GB")
        print(f"Used: {used_pct:.1f}%")
        print(f"Free: {free_gb:.1f} GB")
        
        if free_gb < 0.5:
            print("❌ CRITICAL: Less than 500MB free!")
            return False
        elif free_gb < 2:
            print("⚠️  WARNING: Less than 2GB free - KB models may fail")
            return False
        else:
            print("✅ Sufficient disk space")
            return True
    except Exception as e:
        print(f"⚠️  Could not check: {e}")
        return True


def check_env_file():
    """Check .env file"""
    print_section("Environment File Check")
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return False
    
    with open(env_file) as f:
        env_content = f.read()
    
    if "GOOGLE_API_KEY=" not in env_content:
        print("❌ GOOGLE_API_KEY not in .env")
        return False
    
    # Extract key (safely)
    for line in env_content.split("\n"):
        if line.startswith("GOOGLE_API_KEY="):
            key = line.split("=", 1)[1].strip()
            if key and len(key) > 20:
                print(f"✅ API Key configured ({key[:15]}...)")
                return True
            else:
                print(f"❌ API Key invalid or missing")
                return False
    
    return False


def check_python_packages():
    """Check critical packages"""
    print_section("Python Packages Check")
    critical_packages = [
        "flask",
        "flask_cors", 
        "google",
        "agentscope",
        "langchain",
        "chromadb",
        "dotenv"
    ]
    
    missing = []
    for pkg in critical_packages:
        try:
            __import__(pkg)
            print(f"✅ {pkg}")
        except ImportError:
            print(f"❌ {pkg} - MISSING")
            missing.append(pkg)
    
    return len(missing) == 0


def check_directories():
    """Check required directories"""
    print_section("Directory Structure Check")
    required_dirs = [
        "backend/api",
        "backend/core",
        "backend/knowledge",
        "backend/utils",
        "backend/data",
        "logs",
        "frontend",
    ]
    
    all_ok = True
    for d in required_dirs:
        if Path(d).exists():
            print(f"✅ {d}/")
        else:
            print(f"❌ {d}/ - MISSING")
            all_ok = False
    
    # Create missing directories
    if not all_ok:
        print("\nCreating missing directories...")
        for d in required_dirs:
            Path(d).mkdir(parents=True, exist_ok=True)
        print("✅ Directories created")
    
    return True


def check_backend_logs():
    """Check recent backend logs"""
    print_section("Backend Logs (Last 20 lines)")
    log_file = Path("logs/backend.log")
    
    if log_file.exists():
        lines = log_file.read_text().split("\n")
        for line in lines[-20:]:
            if line.strip():
                # Highlight errors
                if "error" in line.lower() or "❌" in line:
                    print(f"❌ {line}")
                elif "warning" in line.lower() or "⚠️" in line:
                    print(f"⚠️  {line}")
                else:
                    print(f"   {line}")
    else:
        print("No backend logs found yet")


def main():
    print("\n🔧 Islamic AI Agent - Diagnostics & Quick Fix")
    print("=" * 60)
    
    # Change to project root
    if Path("backend").exists():
        os.chdir(os.path.dirname(os.path.abspath(__file__)) + "/..")
    
    checks = [
        ("Disk Space", check_disk_space),
        ("Environment", check_env_file),
        ("Python Packages", check_python_packages),
        ("Directory Structure", check_directories),
    ]
    
    results = {}
    for name, check_fn in checks:
        try:
            results[name] = check_fn()
        except Exception as e:
            print(f"Error during {name} check: {e}")
            results[name] = False
    
    check_backend_logs()
    
    # Summary
    print_section("Summary")
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    print(f"Checks passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All checks passed! Backend should work.")
        print("\nTo fix remaining issues:")
        print("1. If API key is reported as leaked:")
        print("   - Visit https://aistudio.google.com")
        print("   - Generate a new API key")
        print("   - Update .env with: GOOGLE_API_KEY=your_new_key")
        print("\n2. If disk space is low:")
        print("   - Free up space (at least 2GB recommended)")
        print("   - Or run backend/api/server_lite.py instead for reduced features")
    else:
        print("\n⚠️  Some checks failed. Fix the issues above and try again.")


if __name__ == "__main__":
    main()

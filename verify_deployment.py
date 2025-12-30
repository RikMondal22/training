#!/usr/bin/env python3
"""
Pre-deployment verification script for Render deployment.
Modified for single requirements.txt at root level.
"""

import os
import sys
from pathlib import Path

def check_file_exists(filepath, required=True):
    """Check if a file exists."""
    exists = Path(filepath).exists()
    status = "✅" if exists else ("❌" if required else "⚠️")
    req_text = "(required)" if required else "(optional)"
    print(f"{status} {filepath} {req_text}")
    return exists

def check_file_content(filepath, search_terms, description):
    """Check if file contains specific content."""
    try:
        with open(filepath, 'r') as f:
            content = f.read()
            all_found = all(term in content for term in search_terms)
            status = "✅" if all_found else "❌"
            print(f"{status} {filepath} - {description}")
            return all_found
    except FileNotFoundError:
        print(f"❌ {filepath} not found")
        return False

def main():
    print("=" * 60)
    print("BSK Deployment Verification (Single requirements.txt)")
    print("=" * 60)
    print()
    
    all_checks_passed = True
    
    # Check new files
    print("📁 Checking for deployment files:")
    print("-" * 60)
    checks = [
        check_file_exists("render.yaml"),
        check_file_exists("requirements.txt"),  # Single file at root
        check_file_exists(".gitignore"),
    ]
    all_checks_passed &= all(checks)
    
    # Verify NO separate requirements files
    if Path("backend/requirements.txt").exists():
        print("⚠️  backend/requirements.txt exists - consider removing it")
        print("   (Using root requirements.txt instead)")
    if Path("frontend/requirements.txt").exists():
        print("⚠️  frontend/requirements.txt exists - consider removing it")
        print("   (Using root requirements.txt instead)")
    print()
    
    # Check modified files
    print("🔧 Checking modified files:")
    print("-" * 60)
    checks = [
        check_file_content(
            "backend/run.py",
            ["os.getenv", "PORT"],
            "Port configuration"
        ),
        check_file_content(
            "backend/app/main.py",
            ["/health", "ALLOWED_ORIGINS"],
            "Health endpoint and CORS"
        ),
        check_file_content(
            "frontend/app.py",
            ["os.getenv", "BACKEND_URL"],
            "Backend URL configuration"
        ),
    ]
    all_checks_passed &= all(checks)
    print()
    
    # Check dependencies in single requirements.txt
    print("📦 Checking dependencies in requirements.txt:")
    print("-" * 60)
    
    required_deps = [
        "fastapi", "uvicorn", "streamlit", "sqlalchemy", "psycopg2-binary",
        "pandas", "sentence-transformers", "chromadb", "nltk", "requests"
    ]
    
    try:
        with open("requirements.txt", 'r') as f:
            content = f.read().lower()
            for dep in required_deps:
                if dep in content:
                    print(f"✅ Dependency found: {dep}")
                else:
                    print(f"❌ Missing dependency: {dep}")
                    all_checks_passed = False
    except FileNotFoundError:
        print("❌ requirements.txt not found at root level")
        all_checks_passed = False
    
    print()
    
    # Check render.yaml for correct build commands
    print("🔍 Checking render.yaml configuration:")
    print("-" * 60)
    if Path("render.yaml").exists():
        checks = [
            check_file_content(
                "render.yaml",
                ["pip install -r requirements.txt"],
                "Uses root requirements.txt"
            ),
            check_file_content(
                "render.yaml",
                ["cd backend", "cd frontend"],
                "Correct start commands"
            ),
        ]
        all_checks_passed &= all(checks)
    print()
    
    # Environment variables
    print("🔐 Environment variables checklist:")
    print("-" * 60)
    print("You will need to set these on Render:")
    print()
    print("Backend:")
    print("  - DATABASE_URL (your Neon PostgreSQL URL)")
    print("  - SECRET_KEY (generate a secure random string)")
    print("  - PYTHON_VERSION (3.12.0)")
    print()
    print("Frontend:")
    print("  - BACKEND_URL (your backend URL after deployment)")
    print("  - PYTHON_VERSION (3.12.0)")
    print()
    
    # Final summary
    print("=" * 60)
    if all_checks_passed:
        print("✅ All checks passed! Ready for deployment.")
        print()
        print("Next steps:")
        print("1. Remove backend/requirements.txt if exists")
        print("2. Remove frontend/requirements.txt if exists")
        print("3. Commit and push to GitHub:")
        print("   git add .")
        print('   git commit -m "Prepare for Render deployment"')
        print("   git push origin main")
        print()
        print("4. Deploy on Render (follow DEPLOYMENT_CHECKLIST.md)")
        return 0
    else:
        print("❌ Some checks failed. Please fix the issues above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
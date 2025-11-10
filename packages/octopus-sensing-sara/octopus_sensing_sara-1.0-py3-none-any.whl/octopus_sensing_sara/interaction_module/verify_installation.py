#!/usr/bin/env python3
"""
Verification script to check if all components are properly installed.
Run this before starting the server to verify everything is ready.

Usage:
    python verify_installation.py
"""

import sys
from pathlib import Path


def print_header(text: str):
    """Print a formatted header."""
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def check_python_version():
    """Check Python version."""
    print("✓ Checking Python version...")
    version = sys.version_info
    if version.major >= 3 and version.minor >= 10:
        print(f"  ✅ Python {version.major}.{version.minor}.{version.micro} (OK)")
        return True
    else:
        print(f"  ❌ Python {version.major}.{version.minor}.{version.micro} (Need 3.10+)")
        return False


def check_dependencies():
    """Check if all required packages are installed."""
    print("\n✓ Checking dependencies...")

    required_packages = [
        ("fastapi", "FastAPI"),
        ("uvicorn", "Uvicorn"),
        ("pydantic", "Pydantic"),
        ("pydantic_settings", "Pydantic Settings"),
        ("langchain", "LangChain"),
        ("langchain_openai", "LangChain OpenAI"),
        ("langchain_anthropic", "LangChain Anthropic"),
        ("langchain_community", "LangChain Community"),
        ("sqlalchemy", "SQLAlchemy"),
        ("aiosqlite", "Aiosqlite"),
        ("dotenv", "Python Dotenv"),
    ]

    all_ok = True
    for package, name in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {name}")
        except ImportError:
            print(f"  ❌ {name} (Missing)")
            all_ok = False

    return all_ok


def check_project_structure():
    """Check if all required files and directories exist."""
    print("\n✓ Checking project structure...")

    required_paths = [
        "app/__init__.py",
        "app/main.py",
        "app/api/routes.py",
        "app/api/dependencies.py",
        "app/core/config.py",
        "app/core/llm_factory.py",
        "app/core/prompt_builder.py",
        "app/models/database.py",
        "app/models/schemas.py",
        "app/services/conversation_service.py",
        "app/services/memory_service.py",
        "app/services/user_service.py",
        "app/storage/database.py",
        "app/storage/repositories.py",
        "run.py",
        ".env",
    ]

    all_ok = True
    for path in required_paths:
        if Path(path).exists():
            print(f"  ✅ {path}")
        else:
            print(f"  ❌ {path} (Missing)")
            all_ok = False

    return all_ok


def check_configuration():
    """Check if .env file is properly configured."""
    print("\n✓ Checking configuration...")

    env_path = Path(".env")
    if not env_path.exists():
        print("  ❌ .env file not found")
        return False

    env_content = env_path.read_text()

    checks = {
        "LLM_PROVIDER": "LLM provider set",
        "DATABASE_URL": "Database URL configured",
    }

    all_ok = True
    for key, description in checks.items():
        if key in env_content and not env_content.split(key)[1].split('\n')[0].strip().endswith('-here'):
            print(f"  ✅ {description}")
        else:
            print(f"  ⚠️  {description} (May need configuration)")

    # Check API keys
    if "OPENAI_API_KEY=sk-" in env_content and not "sk-your-key-here" in env_content:
        print("  ✅ OpenAI API key configured")
    elif "ANTHROPIC_API_KEY=sk-ant-" in env_content and not "sk-ant-your-key-here" in env_content:
        print("  ✅ Anthropic API key configured")
    elif "LLM_PROVIDER=ollama" in env_content:
        print("  ✅ Ollama configured (no API key needed)")
    else:
        print("  ⚠️  API key may need to be configured")
        all_ok = False

    return all_ok


def check_imports():
    """Check if main modules can be imported."""
    print("\n✓ Checking module imports...")

    modules = [
        ("octopus_sensing_sara.core.config", "Configuration"),
        ("octopus_sensing_sara.models.database", "Database Models"),
        ("octopus_sensing_sara.models.schemas", "API Schemas"),
        ("octopus_sensing_sara.core.llm_factory", "LLM Factory"),
        ("octopus_sensing_sara.core.prompt_builder", "Prompt Builder"),
        ("octopus_sensing_sara.services.memory_service", "Memory Service"),
        ("octopus_sensing_sara.services.user_service", "User Service"),
        ("octopus_sensing_sara.services.conversation_service", "Conversation Service"),
        ("octopus_sensing_sara.api.routes", "API Routes"),
        ("octopus_sensing_sara.main", "Main Application"),
    ]

    all_ok = True
    for module_name, description in modules:
        try:
            __import__(module_name)
            print(f"  ✅ {description}")
        except Exception as e:
            print(f"  ❌ {description} (Import error: {str(e)[:50]}...)")
            all_ok = False

    return all_ok


def main():
    """Run all verification checks."""
    print_header("SARA Chatbot Installation Verification")

    print("This script will verify that your installation is complete and ready to run.\n")

    checks = [
        ("Python Version", check_python_version),
        ("Dependencies", check_dependencies),
        ("Project Structure", check_project_structure),
        ("Configuration", check_configuration),
        ("Module Imports", check_imports),
    ]

    results = {}
    for name, check_func in checks:
        try:
            results[name] = check_func()
        except Exception as e:
            print(f"\n  ❌ {name} check failed with error: {e}")
            results[name] = False

    # Summary
    print_header("Verification Summary")

    all_passed = all(results.values())

    for name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status}  {name}")

    print()

    if all_passed:
        print("🎉 All checks passed! Your installation is ready.")
        print("\nTo start the server, run:")
        print("    python -m octopus_sensing_sara.run")
        print("\nThen open: http://localhost:8000/docs")
        return 0
    else:
        print("⚠️  Some checks failed. Please review the errors above.")
        print("\nCommon fixes:")
        print("  1. Install dependencies: poetry install")
        print("  2. Configure .env: cp .env.example .env && nano .env")
        print("  3. Check Python version: python --version (need 3.10+)")
        return 1


if __name__ == "__main__":
    sys.exit(main())

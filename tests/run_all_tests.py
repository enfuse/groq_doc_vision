#!/usr/bin/env python3
"""
Comprehensive test runner for Groq Document Comprehension
Run this script to verify all README examples and functionality work correctly.
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

def run_test_script(script_name, description):
    """Run a test script and return success status"""
    print(f"\n{'='*60}")
    print(f"🧪 {description}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, script_name], 
                              capture_output=False, 
                              text=True, 
                              cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            return True
        else:
            print(f"❌ {description} - FAILED (exit code: {result.returncode})")
            return False
    except Exception as e:
        print(f"❌ {description} - ERROR: {e}")
        return False

def test_cli_commands():
    """Test CLI commands"""
    print(f"\n{'='*60}")
    print(f"🧪 Testing CLI Commands")
    print(f"{'='*60}")
    
    cli_tests = [
        {
            "cmd": ["groq-pdf", "../example_docs/example.pdf", "--start-page", "1", "--end-page", "1", "--quiet"],
            "desc": "Basic CLI processing"
        },
        {
            "cmd": ["groq-pdf", "../example_docs/example.pdf", "--info-only"],
            "desc": "CLI info-only mode"
        },
        {
            "cmd": ["groq-pdf", "--validate-schema", "test_schema.json"],
            "desc": "CLI schema validation"
        }
    ]
    
    all_passed = True
    for test in cli_tests:
        print(f"\n🔧 Testing: {test['desc']}")
        try:
            result = subprocess.run(test["cmd"], 
                                  capture_output=True, 
                                  text=True, 
                                  cwd=Path(__file__).parent)
            
            if result.returncode == 0:
                print(f"✅ {test['desc']} - PASSED")
            else:
                print(f"❌ {test['desc']} - FAILED")
                print(f"   Error: {result.stderr}")
                all_passed = False
        except Exception as e:
            print(f"❌ {test['desc']} - ERROR: {e}")
            all_passed = False
    
    return all_passed

def check_prerequisites():
    """Check if all prerequisites are met"""
    print("🔍 Checking Prerequisites...")
    
    # Check API key
    if not os.environ.get("GROQ_API_KEY"):
        print("❌ GROQ_API_KEY environment variable not set")
        print("   Please set your Groq API key: export GROQ_API_KEY='your-key-here'")
        return False
    
    # Check if example PDF exists
    example_pdf = Path(__file__).parent.parent / "example_docs" / "example.pdf"
    if not example_pdf.exists():
        print(f"❌ Example PDF not found: {example_pdf}")
        return False
    
    # Check if package can be imported
    try:
        import groq_pdf_vision
        print("✅ groq_pdf_vision package can be imported")
    except ImportError as e:
        print(f"❌ Cannot import groq_pdf_vision: {e}")
        print("   Make sure you've installed the package: pip install -e .")
        return False
    
    print("✅ All prerequisites met")
    return True

def main():
    """Run all tests"""
    print("🚀 Groq Document Comprehension - Comprehensive Test Suite")
    print("=" * 60)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Test scripts to run
    tests = [
        ("test_readme_examples.py", "README Python SDK Examples"),
        ("test_flask_integration.py", "Integration Examples (Flask, FastAPI, Batch)"),
        ("test_example_schema.py", "Example Schema Usage"),
    ]
    
    results = []
    
    # Run Python test scripts
    for script, description in tests:
        success = run_test_script(script, description)
        results.append((description, success))
    
    # Run CLI tests
    cli_success = test_cli_commands()
    results.append(("CLI Commands", cli_success))
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{test_name:<40} {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} test suites passed")
    
    if passed == total:
        print("🎉 All tests passed! The library is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
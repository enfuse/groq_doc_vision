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

def confirm_full_tests():
    """Ask user confirmation for running full document tests"""
    print(f"\n{'='*60}")
    print("⚠️  FULL DOCUMENT TESTS AVAILABLE")
    print(f"{'='*60}")
    print("🔍 The following FULL document tests are available:")
    print("   • Vision 2030 (85 pages) - ~4-5 minutes")
    print("   • Example Document (76 pages) - ~4-5 minutes") 
    print("   • Americas Children 2023 (118 pages) - ~4-5 minutes")
    print("   • Federal Economic Wellbeing 2020 (88 pages) - ~2-3 minutes")
    print()
    print("⏱️  IMPORTANT: These tests take significantly longer than basic tests!")
    print("💰 Cost: Each test uses ~$0.25-0.70 in API credits")
    print("🔄 Total estimated time: ~15-20 minutes for all full tests")
    print()
    
    while True:
        response = input("❓ Do you want to run the FULL document tests? (y/N): ").strip().lower()
        if response in ['y', 'yes']:
            return True
        elif response in ['n', 'no', '']:
            print("⏭️  Skipping full document tests (recommended for quick validation)")
            return False
        else:
            print("Please enter 'y' for yes or 'n' for no")

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

def check_full_test_files():
    """Check if full test document files exist"""
    base_path = Path(__file__).parent.parent / "example_docs"
    required_files = [
        "vision2030.pdf",
        "example.pdf", 
        "americas_children_2023.pdf",
        "fed_economic_wellbeing_2020.pdf"
    ]
    
    missing_files = []
    for file in required_files:
        if not (base_path / file).exists():
            missing_files.append(file)
    
    if missing_files:
        print(f"⚠️  Some full test documents are missing: {', '.join(missing_files)}")
        print("   Full tests will be limited to available documents only")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Groq Document Comprehension - Comprehensive Test Suite")
    print("=" * 60)
    
    if not check_prerequisites():
        print("\n❌ Prerequisites not met. Please fix the issues above and try again.")
        sys.exit(1)
    
    # Basic test scripts to run
    basic_tests = [
        ("test_readme_examples.py", "README Python SDK Examples"),
        ("test_flask_integration.py", "Integration Examples (Flask, FastAPI, Batch)"),
        ("test_example_schema.py", "Example Schema Usage"),
    ]
    
    # Full document test scripts
    full_tests = [
        ("test_vision2030_full_async.py", "Vision 2030 Full Document (85 pages)"),
        ("test_example_full_async.py", "Example Document Full Processing (76 pages)"),
        ("test_americas_children_full_async.py", "Americas Children 2023 Full Document (118 pages)"),
        ("test_fed_economic_wellbeing_full_async.py", "Federal Economic Wellbeing 2020 Full Document (88 pages)"),
    ]
    
    results = []
    
    # Run basic Python test scripts
    print("\n🏃‍♂️ Running BASIC tests (quick validation)...")
    for script, description in basic_tests:
        success = run_test_script(script, description)
        results.append((description, success))
    
    # Run CLI tests
    cli_success = test_cli_commands()
    results.append(("CLI Commands", cli_success))
    
    # Ask about full tests
    run_full_tests = confirm_full_tests()
    
    if run_full_tests:
        print("\n🚀 Running FULL document tests (this will take a while)...")
        check_full_test_files()  # Warn about missing files
        
        for script, description in full_tests:
            # Check if the test file exists before trying to run it
            test_file = Path(__file__).parent / script
            if test_file.exists():
                success = run_test_script(script, description)
                results.append((description, success))
            else:
                print(f"⚠️  Skipping {description} - test file not found: {script}")
                results.append((description, None))  # Mark as skipped
    
    # Print summary
    print(f"\n{'='*60}")
    print("📊 TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = 0
    failed = 0
    skipped = 0
    total = len(results)
    
    for test_name, success in results:
        if success is True:
            status = "✅ PASSED"
            passed += 1
        elif success is False:
            status = "❌ FAILED"
            failed += 1
        else:
            status = "⏭️  SKIPPED"
            skipped += 1
        
        print(f"{test_name:<50} {status}")
    
    print(f"\n🎯 Results: {passed} passed, {failed} failed, {skipped} skipped (out of {total} total)")
    
    if failed == 0:
        if skipped > 0:
            print("🎉 All executed tests passed! Some tests were skipped.")
        else:
            print("🎉 All tests passed! The library is working correctly.")
        sys.exit(0)
    else:
        print("⚠️  Some tests failed. Please check the output above for details.")
        sys.exit(1)

if __name__ == "__main__":
    main() 
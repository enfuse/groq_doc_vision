# Test Suite for Groq Document Comprehension

This directory contains comprehensive tests to verify that all functionality and examples from the main README work correctly.

## Quick Start

Run all tests with a single command:

```bash
cd tests
python run_all_tests.py
```

## Prerequisites

Before running tests, ensure you have:

1. **API Key**: Set your Groq API key as an environment variable:
   ```bash
   export GROQ_API_KEY="your-api-key-here"
   ```

2. **Package Installation**: Install the package in development mode:
   ```bash
   pip install -e .
   ```

3. **Virtual Environment** (recommended):
   ```bash
   python -m venv groq_pdf_vision_env
   source groq_pdf_vision_env/bin/activate  # On Windows: groq_pdf_vision_env\Scripts\activate
   pip install -e .
   ```

## Test Files

### Core Test Scripts

- **`run_all_tests.py`** - Main test runner that executes all tests and provides a summary
- **`test_readme_examples.py`** - Tests all Python SDK examples from the main README
- **`test_flask_integration.py`** - Tests integration examples (Flask, FastAPI, batch processing)
- **`test_example_schema.py`** - Tests example schema usage patterns

### Supporting Files

- **`test_schema.json`** - Sample schema file for CLI testing
- **`README.md`** - This file

## Individual Test Scripts

You can also run individual test scripts:

### Python SDK Examples
```bash
python test_readme_examples.py
```
Tests:
- Basic Quick Start example
- Synchronous processing with progress callbacks
- Asynchronous processing with progress callbacks
- Basic extraction patterns
- Custom schema creation and usage
- Schema building helpers

### Integration Examples
```bash
python test_flask_integration.py
```
Tests:
- Flask integration logic
- FastAPI integration logic
- Batch processing patterns

### Schema Usage
```bash
python test_example_schema.py
```
Tests:
- Loading JSON schemas from files
- Building schemas with helpers
- Custom field addition

## CLI Testing

The test runner also verifies CLI functionality:

- Basic PDF processing
- Info-only mode
- Schema validation
- Custom schema usage

## Expected Output

When all tests pass, you should see:

```
🎯 Results: 4/4 test suites passed
🎉 All tests passed! The library is working correctly.
```

## Troubleshooting

### Common Issues

1. **API Key Not Set**
   ```
   ❌ GROQ_API_KEY environment variable not set
   ```
   **Solution**: Set your API key: `export GROQ_API_KEY="your-key-here"`

2. **Package Not Installed**
   ```
   ❌ Cannot import groq_pdf_vision
   ```
   **Solution**: Install the package: `pip install -e .`

3. **Example PDF Missing**
   ```
   ❌ Example PDF not found
   ```
   **Solution**: Ensure you're running from the correct directory and `example_docs/example.pdf` exists

### Test Failures

If specific tests fail:

1. **Check API connectivity**: Ensure your API key is valid and you have internet access
2. **Check file paths**: Ensure all example files exist in the expected locations
3. **Check dependencies**: Ensure all required packages are installed

## Performance Notes

- Tests process limited pages (1-3) to run quickly
- Full test suite typically takes 2-3 minutes
- Individual tests can be run for faster iteration

## Adding New Tests

To add new tests:

1. Create a new test script following the naming pattern `test_*.py`
2. Add it to the `tests` list in `run_all_tests.py`
3. Follow the existing pattern of clear test descriptions and pass/fail reporting

## Test Coverage

These tests verify:

- ✅ All README Python examples work
- ✅ All CLI commands function correctly
- ✅ Schema creation and validation
- ✅ Synchronous and asynchronous processing
- ✅ Progress callbacks
- ✅ Integration patterns
- ✅ Error handling
- ✅ File I/O operations

The test suite provides confidence that the library works as documented and can be safely used in production environments. 
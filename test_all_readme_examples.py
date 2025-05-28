#!/usr/bin/env python3
"""
Comprehensive test of all README examples (Fixed version)
Tests all SDK examples mentioned in the README to ensure they work correctly.
Handles sync/async context properly.
"""

import asyncio
import os
import sys
import subprocess
from pathlib import Path
import time
import json

# Import the functions from groq_pdf_vision
from groq_pdf_vision import (
    extract_pdf, 
    extract_pdf_async, 
    estimate_processing_time,
    create_financial_schema
)

# Create schemas dictionary for compatibility
schemas = {
    'financial': create_financial_schema()
}

def test_basic_extraction():
    """Test basic PDF extraction functionality."""
    print("Testing basic PDF extraction...")
    start_time = time.time()
    result = extract_pdf("example_docs/example.pdf", start_page=1, end_page=1, save_results=False)
    end_time = time.time()
    
    assert result is not None, "Result should not be None"
    assert "accumulated_data" in result, "Result should contain accumulated_data"
    
    print(f"✅ Basic extraction test passed in {end_time - start_time:.2f}s")
    print(f"   Extracted {len(str(result))} characters of data")
    return True

async def test_async_extraction():
    """Test async PDF extraction functionality."""
    print("Testing async PDF extraction...")
    start_time = time.time()
    
    # Test async extraction
    result, metadata = await extract_pdf_async("example_docs/example.pdf", start_page=1, end_page=1)
    
    end_time = time.time()
    
    assert result is not None, "Result should not be None"
    assert metadata is not None, "Metadata should not be None"
    assert "accumulated_data" in result, "Result should contain accumulated_data"
    
    print(f"✅ Async extraction test passed in {end_time - start_time:.2f}s")
    print(f"   Extracted {len(str(result))} characters of data")
    print(f"   Metadata: {metadata}")
    return True

def test_schema_extraction():
    """Test extraction with predefined schemas."""
    print("Testing schema-based extraction...")
    
    # Test with financial schema
    start_time = time.time()
    result = extract_pdf("example_docs/example.pdf", schema=schemas['financial'], start_page=1, end_page=1, save_results=False)
    end_time = time.time()
    
    assert result is not None, "Result should not be None"
    assert "accumulated_data" in result, "Result should contain accumulated_data"
    
    print(f"✅ Schema extraction test passed in {end_time - start_time:.2f}s")
    print(f"   Used financial schema")
    return True

def test_custom_schema():
    """Test extraction with custom schema."""
    print("Testing custom schema extraction...")
    
    # Create a custom schema
    custom_schema = {
        "type": "object",
        "properties": {
            "title": {"type": "string", "description": "Document title"},
            "summary": {"type": "string", "description": "Brief summary"},
            "key_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key points from the document"
            }
        }
    }
    
    start_time = time.time()
    result = extract_pdf("example_docs/example.pdf", schema=custom_schema, start_page=1, end_page=1, save_results=False)
    end_time = time.time()
    
    assert result is not None, "Result should not be None"
    
    print(f"✅ Custom schema test passed in {end_time - start_time:.2f}s")
    print(f"   Used custom schema with title, summary, and key_points")
    return True

def test_processing_estimates():
    """Test processing time estimation."""
    print("Testing processing time estimation...")
    
    estimates = estimate_processing_time("example_docs/example.pdf")
    
    assert estimates is not None, "Estimates should not be None"
    assert "total_pages_in_pdf" in estimates, "Should contain total_pages_in_pdf"
    assert "estimated_time_seconds" in estimates, "Should contain estimated_time_seconds"
    
    print(f"✅ Estimation test passed")
    print(f"   Document: {estimates['total_pages_in_pdf']} pages")
    print(f"   Estimated time: {estimates['estimated_time_formatted']}")
    return True

def test_batch_processing():
    """Test batch processing functionality."""
    print("Testing batch processing simulation...")
    
    # Create temporary directories
    import tempfile
    import shutil
    
    with tempfile.TemporaryDirectory() as temp_dir:
        input_dir = os.path.join(temp_dir, "batch_input")
        output_dir = os.path.join(temp_dir, "batch_output")
        
        os.makedirs(input_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        # Copy example PDF to input directory
        test_pdf = os.path.join(input_dir, "test_document.pdf")
        shutil.copy("example_docs/example.pdf", test_pdf)
        
        start_time = time.time()
        
        # Simulate batch processing by processing individual file
        result = extract_pdf(
            test_pdf,
            start_page=1,
            end_page=2,
            save_results=True
        )
        
        end_time = time.time()
        
        # Check that the result is valid
        assert result is not None, "Batch result should not be None"
        assert "accumulated_data" in result, "Result should contain accumulated_data"
        
        print(f"✅ Batch processing simulation test passed in {end_time - start_time:.2f}s")
        print(f"   Processed 1 PDF with pages 1-2")
        return True

def test_cli_interface():
    """Test CLI interface functionality."""
    print("Testing CLI interface...")
    
    # Test info-only mode
    result = subprocess.run(['groq-pdf', 'example_docs/example.pdf', '--info-only'],
                          capture_output=True, text=True, timeout=30)
    
    assert result.returncode == 0, f"CLI info command failed: {result.stderr}"
    
    # Test actual processing with limited pages
    result = subprocess.run(['groq-pdf', 'example_docs/example.pdf', '--start-page', '1', '--end-page', '1', '--quiet'],
                          capture_output=True, text=True, timeout=60)
    
    assert result.returncode == 0, f"CLI processing failed: {result.stderr}"
    
    print(f"✅ CLI interface test passed")
    print(f"   Info and processing commands work correctly")
    return True

def run_all_tests():
    """Run all README example tests"""
    print('🚀 Testing all README examples...')
    print('=' * 50)
    
    tests = [
        ('Basic Extraction', test_basic_extraction),
        ('Async Extraction', test_async_extraction),
        ('Schema Extraction', test_schema_extraction),
        ('Custom Schema', test_custom_schema),
        ('Processing Estimates', test_processing_estimates),
        ('Batch Processing', test_batch_processing),
        ('CLI Interface', test_cli_interface),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                # Run async function in its own event loop
                success = asyncio.run(test_func())
            else:
                success = test_func()
            results[test_name] = success
        except Exception as e:
            print(f'\n❌ {test_name} failed with exception: {e}')
            results[test_name] = False
    
    # Summary
    print('\n' + '=' * 50)
    print('📊 TEST SUMMARY')
    print('=' * 50)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    for test_name, success in results.items():
        status = '✅ PASS' if success else '❌ FAIL'
        print(f'{status} {test_name}')
    
    print(f'\nOverall: {passed}/{total} tests passed')
    
    if passed == total:
        print('🎉 All README examples are working correctly!')
        return True
    else:
        print('⚠️  Some examples need attention.')
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 
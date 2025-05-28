#!/usr/bin/env python3
"""
Test script to verify all README examples work correctly
"""

import os
import asyncio
import json
import sys
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from groq_pdf_vision import extract_pdf, extract_pdf_async
from groq_pdf_vision.schema_helpers import create_base_schema, add_custom_fields

# Set API key
os.environ["GROQ_API_KEY"] = "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"

# Get the example PDF path relative to the tests directory
EXAMPLE_PDF = str(Path(__file__).parent.parent / "example_docs" / "example.pdf")

def test_basic_quick_start():
    """Test the basic Quick Start example"""
    print("🧪 Testing Basic Quick Start Example...")
    
    # Extract data from a PDF (limit pages for testing)
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=2)

    # Access page-level results
    for page in result["page_results"]:
        print(f"Page {page['page_number']}: {page['content'][:100]}...")

    # Access accumulated data
    print(f"Total pages: {len(result['page_results'])}")
    print(f"Images found: {len(result['accumulated_data']['image_descriptions'])}")
    print("✅ Basic Quick Start - PASSED\n")

def test_sync_progress():
    """Test synchronous processing with progress callback"""
    print("🧪 Testing Sync Progress Example...")
    
    def progress_callback(message, current, total):
        percentage = (current / total) * 100
        print(f"🔄 [{current}/{total}] ({percentage:.1f}%) {message}")

    result = extract_pdf(
        EXAMPLE_PDF,
        start_page=1,
        end_page=3,
        progress_callback=progress_callback
    )
    print(f"✅ Completed in {result['processing_stats']['processing_time_seconds']:.1f} seconds")
    print("✅ Sync Progress - PASSED\n")

async def test_async_progress():
    """Test async processing with progress callback"""
    print("🧪 Testing Async Progress Example...")
    
    def progress_callback(message, current, total):
        percentage = (current / total) * 100
        print(f"🔄 [{current}/{total}] ({percentage:.1f}%) {message}")

    result, metadata = await extract_pdf_async(
        EXAMPLE_PDF,
        start_page=1,
        end_page=3,
        progress_callback=progress_callback
    )
    print(f"✅ Completed in {metadata['processing_time_seconds']:.1f} seconds")
    print("✅ Async Progress - PASSED\n")

def test_basic_extraction():
    """Test basic extraction example from Usage section"""
    print("🧪 Testing Basic Extraction Example...")
    
    # Extract from PDF
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=2, save_results=False)

    # Process results
    for page in result["page_results"]:
        print(f"Page {page['page_number']}:")
        print(f"  Content: {len(page['content'])} characters")
        print(f"  Images: {len(page['image_descriptions'])} found")
        print(f"  Tables: {len(page['tables_data'])} found")
    
    print("✅ Basic Extraction - PASSED\n")

async def test_async_processing():
    """Test async processing example"""
    print("🧪 Testing Async Processing Example...")
    
    async def process_document():
        result, metadata = await extract_pdf_async(EXAMPLE_PDF, start_page=1, end_page=2)
        print(f"Processed in {metadata['processing_time_seconds']:.1f} seconds")
        return result

    result = await process_document()
    print("✅ Async Processing - PASSED\n")

def test_custom_schemas():
    """Test custom schema examples"""
    print("🧪 Testing Custom Schema Examples...")
    
    # Use the default comprehensive schema (recommended for most cases)
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=1)
    print("✅ Default schema works")

    # Create a custom schema by extending the base
    base_schema = create_base_schema()
    custom_fields = {
        "product_names": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Product names mentioned"
        },
        "prices": {
            "type": "array", 
            "items": {"type": "string"},
            "description": "Prices and costs mentioned"
        }
    }
    custom_schema = add_custom_fields(base_schema, custom_fields)
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=1, schema=custom_schema)
    print("✅ Custom schema with base extension works")

    # Or define a completely custom schema
    minimal_schema = {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer"},
            "summary": {"type": "string"},
            "key_points": {
                "type": "array",
                "items": {"type": "string"}
            }
        }
    }
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=1, schema=minimal_schema)
    print("✅ Minimal custom schema works")
    print("✅ Custom Schemas - PASSED\n")

def test_schema_building():
    """Test schema building examples"""
    print("🧪 Testing Schema Building Examples...")
    
    # Default schema works for most documents
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=1)
    print("✅ Default schema works")

    # Financial document extraction
    base = create_base_schema()
    financial_fields = {
        "financial_figures": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Revenue, profit, costs, and other financial amounts"
        },
        "companies_mentioned": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Company names and organizations"
        }
    }
    financial_schema = add_custom_fields(base, financial_fields)
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=1, schema=financial_schema)
    print("✅ Financial schema works")

    # Research document extraction  
    research_fields = {
        "methodology": {"type": "string", "description": "Research methodology"},
        "findings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key findings and results"
        }
    }
    research_schema = add_custom_fields(base, research_fields)
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=1, schema=research_schema)
    print("✅ Research schema works")

    print("✅ Schema Building - PASSED\n")

def test_sync_examples():
    """Test all synchronous examples"""
    print("🚀 Testing Synchronous README Examples...\n")
    
    test_basic_quick_start()
    test_sync_progress()
    test_basic_extraction()
    test_custom_schemas()
    test_schema_building()
    
    print("✅ All synchronous examples passed!")

async def test_async_examples():
    """Test all asynchronous examples"""
    print("\n🚀 Testing Asynchronous README Examples...\n")
    
    await test_async_progress()
    await test_async_processing()
    
    print("✅ All asynchronous examples passed!")

if __name__ == "__main__":
    # Test sync examples first
    test_sync_examples()
    
    # Then test async examples
    asyncio.run(test_async_examples())
    
    print("\n🎉 All README examples tested successfully!") 
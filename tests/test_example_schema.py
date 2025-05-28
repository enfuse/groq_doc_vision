#!/usr/bin/env python3
"""
Test example schema usage from README
"""

import os
import json
import sys
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from groq_pdf_vision import extract_pdf
from groq_pdf_vision.schema_helpers import create_base_schema, add_custom_fields

# Set API key
os.environ["GROQ_API_KEY"] = "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"

# Get file paths relative to the tests directory
EXAMPLE_PDF = str(Path(__file__).parent.parent / "example_docs" / "example.pdf")
EXAMPLE_SCHEMA = str(Path(__file__).parent.parent / "example_docs" / "example_custom_schema.json")

def test_example_schema_method1():
    """Test Method 1: Load JSON Schema Directly"""
    print("🧪 Testing Method 1: Load JSON Schema Directly...")
    
    # Load the example schema
    with open(EXAMPLE_SCHEMA, 'r') as f:
        schema = json.load(f)

    # Use it for extraction
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=1, schema=schema)
    
    print(f"✅ Method 1 works - processed {len(result['page_results'])} page(s)")
    print("✅ Method 1 - PASSED\n")

def test_example_schema_method2():
    """Test Method 2: Build with Schema Helpers (Recommended)"""
    print("🧪 Testing Method 2: Build with Schema Helpers...")
    
    # Start with the base schema
    base = create_base_schema()

    # Add your custom fields
    custom_fields = {
        "document_type": {
            "type": "string", 
            "description": "Type of document (financial, technical, academic, etc.)"
        },
        "key_findings": {
            "type": "array", 
            "items": {"type": "string"}, 
            "description": "Most important findings or insights from this page"
        },
        "sentiment": {
            "type": "string", 
            "description": "Overall sentiment of the page content"
        }
    }

    # Combine them
    schema = add_custom_fields(base, custom_fields)
    result = extract_pdf(EXAMPLE_PDF, start_page=1, end_page=1, schema=schema)
    
    print(f"✅ Method 2 works - processed {len(result['page_results'])} page(s)")
    print("✅ Method 2 - PASSED\n")

def main():
    """Run all example schema tests"""
    print("🚀 Testing Example Schema Usage...\n")
    
    test_example_schema_method1()
    test_example_schema_method2()
    
    print("🎉 All example schema tests passed!")

if __name__ == "__main__":
    main() 
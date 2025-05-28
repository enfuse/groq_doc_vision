<div align="center">
  <img src="assets/groq-logo.png" alt="Groq" width="200"/>
  
  # 🔍 Groq PDF Vision
  
  **Intelligent PDF processing with enterprise-grade reliability**
  
  [![PyPI version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/groq-pdf-vision/)
  [![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
</div>

Transform any PDF into structured data using Groq's lightning-fast vision models. Extract tables, images, text, and insights with advanced AI processing and get enterprise-ready JSON output with high reliability and automatic error handling.

## 📚 Table of Contents

- [✨ Key Features](#-key-features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Configuration](#configuration)
  - [Environment Variables](#environment-variables)
  - [API Key Setup](#api-key-setup)
- [Quick Start](#quick-start)
  - [With Progress Tracking (Recommended for Large PDFs)](#with-progress-tracking-recommended-for-large-pdfs)
- [Usage](#usage)
  - [Python SDK](#python-sdk)
  - [Command Line Interface](#command-line-interface)
  - [Web Interface](#web-interface)
- [Table Extraction Capabilities](#table-extraction-capabilities)
  - [Supported Table Formats](#supported-table-formats)
  - [Enhanced Processing Features](#enhanced-processing-features)
- [Schema Building](#schema-building)
  - [Basic Usage](#basic-usage)
  - [Custom Field Examples](#custom-field-examples)
  - [Schema Building Helpers](#schema-building-helpers)
- [Integration Examples](#integration-examples)
  - [Flask Application](#flask-application)
  - [FastAPI Application](#fastapi-application)
  - [Batch Processing](#batch-processing)
- [Example Schema](#example-schema)
  - [Using the Example Schema](#using-the-example-schema)
  - [Schema Design Tips](#schema-design-tips)
- [API Reference](#api-reference)
  - [Schema Helpers](#schema-helpers)
  - [Utility Functions](#utility-functions)
- [Output Structure](#output-structure)
- [Performance](#performance)
  - [Optimized Processing](#optimized-processing)
  - [Real-World Benchmarks](#real-world-benchmarks)
  - [Auto-Configuration System](#auto-configuration-system)
- [Testing](#testing)
  - [Comprehensive Test Suite](#comprehensive-test-suite)
  - [Performance Benchmarks](#performance-benchmarks)
  - [Test Coverage](#test-coverage)
- [Recent Improvements](#recent-improvements)

## ✨ Key Features

- **🚀 Lightning Fast**: Powered by Groq's industry-leading inference speed
- **📊 Complete Data Extraction**: Tables, text, images, charts, and metadata
- **🎯 Smart Auto-Configuration**: Optimizes processing based on document size  
- **⚡ Enterprise Performance**: Optimized batch processing with automatic retry mechanisms
- **🔧 Flexible Schema**: Custom extraction schemas for any use case
- **📱 Multiple Interfaces**: CLI, Python API, and Streamlit web app
- **📋 Enhanced Table Processing**: Supports both array-based and object-based table structures
- **🛡️ Robust Error Handling**: Graceful error recovery with comprehensive retry logic
- **📈 Real-time Progress**: Live progress tracking with ETA calculations and terminal logging

## Requirements

- Python 3.8+
- Groq API key
- Dependencies: `groq`, `pypdfium2`, `streamlit` (for web interface) 

## Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv groq_pdf_vision_env
source groq_pdf_vision_env/bin/activate  # On Windows: groq_pdf_vision_env\Scripts\activate

# Clone and install from source
pip install -e .
```

## Configuration

### Environment Variables

```bash
# Required: Groq API key
export GROQ_API_KEY="your-api-key-here"

# Optional: Custom model (default: meta-llama/llama-4-scout-17b-16e-instruct)
export GROQ_MODEL="meta-llama/llama-4-scout-17b-16e-instruct"
```

### API Key Setup

1. Get your API key from [console.groq.com](https://console.groq.com)
2. Set it as an environment variable:

```bash
export GROQ_API_KEY="your-api-key-here"
```

## Quick Start

```python
from groq_pdf_vision import extract_pdf

# Extract data from a PDF (limit pages for testing)
result = extract_pdf("document.pdf", start_page=1, end_page=5)

# Access page-level results
for page in result["page_results"]:
    print(f"Page {page['page_number']}: {page['content'][:100]}...")

# Access accumulated data
print(f"Total pages: {len(result['page_results'])}")
print(f"Images found: {len(result['accumulated_data']['image_descriptions'])}")
```

### With Progress Tracking (Recommended for Large PDFs)

**Synchronous with Progress:**
```python
from groq_pdf_vision import extract_pdf

def progress_callback(message, current, total):
    percentage = (current / total) * 100
    print(f"🔄 [{current}/{total}] ({percentage:.1f}%) {message}")

result = extract_pdf(
    "large_document.pdf",
    progress_callback=progress_callback
)
print(f"✅ Completed in {result['metadata']['processing_time_seconds']:.1f} seconds")
```

**Async with Progress:**
```python
import asyncio
from groq_pdf_vision import extract_pdf_async

def progress_callback(message, current, total):
    percentage = (current / total) * 100
    print(f"🔄 [{current}/{total}] ({percentage:.1f}%) {message}")

async def main():
    result, metadata = await extract_pdf_async(
        "large_document.pdf",
        progress_callback=progress_callback
    )
    print(f"✅ Completed in {metadata['processing_time_seconds']:.1f} seconds")

asyncio.run(main())
```

## Usage

### Python SDK

#### Basic Extraction

```python
import os
from groq_pdf_vision import extract_pdf

# Set your API key
os.environ["GROQ_API_KEY"] = "your-api-key-here"

# Extract from PDF
result = extract_pdf("financial_report.pdf", save_results=True)

# Process results
for page in result["page_results"]:
    print(f"Page {page['page_number']}:")
    print(f"  Content: {len(page['content'])} characters")
    print(f"  Images: {len(page['image_descriptions'])} found")
    print(f"  Tables: {len(page['tables_data'])} found")
```

#### Async Processing

```python
import asyncio
from groq_pdf_vision import extract_pdf_async

async def process_document():
    result, metadata = await extract_pdf_async("large_document.pdf")
    print(f"Processed in {metadata['processing_time_seconds']:.1f} seconds")
    return result

result = asyncio.run(process_document())
```

#### Custom Schemas

```python
from groq_pdf_vision import extract_pdf
from groq_pdf_vision.schema_helpers import create_base_schema, add_custom_fields

# Use the default comprehensive schema (recommended for most cases)
result = extract_pdf("document.pdf")

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
result = extract_pdf("catalog.pdf", schema=custom_schema)

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
result = extract_pdf("document.pdf", schema=minimal_schema)
```

### Command Line Interface

```bash
# Basic processing with default comprehensive schema
groq-pdf document.pdf --save

# Specific page range
groq-pdf document.pdf --start-page 1 --end-page 10

# Custom schema file
groq-pdf document.pdf --schema my_schema.json

# Inline JSON schema
groq-pdf document.pdf --schema '{"type":"object","properties":{"summary":{"type":"string"}}}'

# Get document info and processing estimates
groq-pdf document.pdf --info-only
```

### Web Interface

Launch the Streamlit web interface:

```bash
streamlit run app.py
```

Then open http://localhost:8501 for drag-and-drop PDF processing.

## Table Extraction Capabilities

The library features advanced table extraction that handles multiple data structures:

### Supported Table Formats

**Array-based Tables (Traditional):**
```json
{
  "headers": ["Column 1", "Column 2", "Column 3"],
  "rows": [
    ["Value 1", "Value 2", "Value 3"],
    ["Value 4", "Value 5", "Value 6"]
  ]
}
```

**Object-based Tables (Financial/Complex):**
```json
{
  "headers": ["Share capital", "Subscribed", "Callable", "Total"],
  "rows": [
    {
      "Subscribed share capital": "2,288,500",
      "Callable share capital": "(1,601,950)",
      "Total": "885,722"
    }
  ]
}
```

### Enhanced Processing Features

- **Smart Structure Detection**: Automatically handles both array and object-based row formats
- **Intelligent Column Mapping**: Maps dictionary keys to table headers with fuzzy matching
- **Data Quality Filtering**: Removes placeholder and example data automatically
- **Consistent Output**: Converts all formats to standardized DataFrames for display
- **Error Recovery**: Graceful handling of malformed or incomplete table data

### Example Usage

```python
from groq_pdf_vision import extract_pdf

# Extract tables from financial documents
result = extract_pdf("financial_report.pdf")

# Access table data
for table in result["accumulated_data"]["tables_data"]:
    print(f"Table: {table['table_title']}")
    print(f"Structure: {len(table['headers'])} columns × {len(table['rows'])} rows")
    
    # Both formats work seamlessly
    if table['headers'] and table['rows']:
        # Process table data regardless of internal structure
        headers = table['headers']
        rows = table['rows']  # Can be arrays or objects
```

## Schema Building

The library provides flexible schema building helpers to extract exactly what you need:

### Basic Usage
```python
from groq_pdf_vision import extract_pdf
from groq_pdf_vision.schema_helpers import create_base_schema, add_custom_fields

# Default schema works for most documents
result = extract_pdf("document.pdf")
```

### Custom Field Examples
```python
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

# Product catalog extraction
product_fields = {
    "product_names": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Product names mentioned"
    },
    "specifications": {
        "type": "array",
        "items": {"type": "string"},
        "description": "Technical specifications"
    }
}
product_schema = add_custom_fields(base, product_fields)
```

### Schema Building Helpers
```python
from groq_pdf_vision.schema_helpers import (
    create_base_schema,
    add_custom_fields,
    create_entity_extraction_fields,
    create_list_field,
    create_object_field
)

# Build a schema step by step
schema = create_base_schema(include_images=True, include_tables=False)

# Add entity extraction for any domain
entity_fields = create_entity_extraction_fields(["person", "company", "location"])
schema = add_custom_fields(schema, entity_fields)

# Add custom list fields
contact_fields = create_list_field("contact_emails", "Email addresses found")
schema = add_custom_fields(schema, contact_fields)
```

## Integration Examples

### Flask Application

```python
from flask import Flask, request, jsonify
from groq_pdf_vision import extract_pdf_async
import asyncio

app = Flask(__name__)

@app.route('/process-pdf', methods=['POST'])
def process_pdf():
    file = request.files['file']
    filepath = f"uploads/{file.filename}"
    file.save(filepath)
    
    async def process():
        return await extract_pdf_async(filepath)
    
    result, metadata = asyncio.run(process())
    
    return jsonify({
        "pages": len(result["page_results"]),
        "processing_time": metadata["processing_time_seconds"],
        "data": result["accumulated_data"]
    })
```

### FastAPI Application

```python
from fastapi import FastAPI, UploadFile, File
from groq_pdf_vision import extract_pdf_async
import tempfile

app = FastAPI()

@app.post("/process-pdf/")
async def process_pdf(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    
    result, metadata = await extract_pdf_async(tmp_path)
    
    return {
        "filename": file.filename,
        "pages_processed": len(result["page_results"]),
        "processing_time": metadata["processing_time_seconds"]
    }
```

### Batch Processing

```python
import asyncio
from pathlib import Path
from groq_pdf_vision import extract_pdf_async

async def process_batch(input_dir, output_dir):
    pdf_files = list(Path(input_dir).glob("*.pdf"))
    
    for pdf_file in pdf_files:
        print(f"Processing {pdf_file.name}")
        
        result, metadata = await extract_pdf_async(
            str(pdf_file),
            save_results=True,
            output_filename=f"{output_dir}/{pdf_file.stem}_results.json"
        )
        
        print(f"  ✅ {len(result['page_results'])} pages in {metadata['processing_time_seconds']:.1f}s")

# Process all PDFs in a directory
asyncio.run(process_batch("./input", "./output"))
```

## Example Schema

The `example_docs/` directory contains a comprehensive example schema (`example_custom_schema.json`) that demonstrates various field types and extraction patterns.

### Using the Example Schema

**Method 1: Load JSON Schema Directly**
```python
import json
from groq_pdf_vision import extract_pdf

# Load the example schema
with open('example_docs/example_custom_schema.json', 'r') as f:
    schema = json.load(f)

# Use it for extraction
result = extract_pdf("example_docs/example.pdf", schema=schema)
```

**Method 2: Build with Schema Helpers (Recommended)**
```python
from groq_pdf_vision import extract_pdf
from groq_pdf_vision.schema_helpers import create_base_schema, add_custom_fields

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
result = extract_pdf("example_docs/example.pdf", schema=schema)
```

### Schema Design Tips

1. **Start Simple** - Begin with `create_base_schema()` and add only what you need
2. **Clear Descriptions** - Good field descriptions help the AI understand what to extract
3. **Appropriate Types** - Use arrays for lists, objects for structured data, strings for text
4. **Required Fields** - Always include `page_number` and `content` as required
5. **Test Iteratively** - Start with a few pages to test your schema before processing large documents

## API Reference

### `extract_pdf(pdf_path, **kwargs)`

Extract data from a PDF file synchronously.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `schema` (dict, optional): Custom JSON schema for extraction
- `start_page` (int, optional): Starting page number (1-indexed)
- `end_page` (int, optional): Ending page number (1-indexed)
- `save_results` (bool, optional): Save results to JSON file
- `output_filename` (str, optional): Custom output filename

**Returns:**
- `dict`: Extraction results with page-level and accumulated data

### `extract_pdf_async(pdf_path, **kwargs)`

Extract data from a PDF file asynchronously.

**Parameters:** Same as `extract_pdf`

**Returns:**
- `tuple`: (results_dict, metadata_dict)

### Schema Helpers

- `create_base_schema()`: Comprehensive base schema for most documents
- `add_custom_fields()`: Add custom fields to an existing schema
- `create_entity_extraction_fields()`: Helper for entity extraction fields
- `create_list_field()`: Helper for array field creation
- `create_object_field()`: Helper for structured object fields

### Utility Functions

- `validate_schema(schema)`: Validate a JSON schema
- `estimate_processing_time(pdf_path)`: Estimate processing time
- `get_pdf_info(pdf_path)`: Get PDF metadata

## Output Structure

```json
{
  "source_pdf": "document.pdf",
  "page_results": [
    {
      "page_number": 1,
      "content": "Extracted text content...",
      "image_descriptions": [
        {
          "image_type": "chart",
          "description": "Bar chart showing quarterly revenue",
          "location": "center",
          "content_relation": "Supports revenue discussion"
        }
      ],
      "tables_data": [
        {
          "table_content": "Q1: $1M, Q2: $1.2M...",
          "table_structure": "2x4 table with headers"
        }
      ]
    }
  ],
  "accumulated_data": {
    "total_content": "All extracted text...",
    "all_image_descriptions": [...],
    "all_tables_data": [...],
    "visual_summary": "Document contains 5 charts and 3 tables"
  },
  "processing_stats": {
    "total_pages": 10,
    "pages_with_images": 3,
    "pages_with_tables": 5,
    "processing_time_seconds": 45.2
  }
}
```

## Performance

### Optimized Processing
- **Processing Speed**: 1,300-2,000+ tokens/second (optimized batch processing)
- **Intelligent Auto-Configuration**: Batch sizes automatically scale based on document size
- **High Reliability**: Robust retry mechanisms with graceful error handling across test scenarios  
- **Memory Usage**: Optimized for large documents up to 200+ pages
- **Enhanced Table Extraction**: Supports both array-based and object-based table row structures
- **Improved Consistency**: Lower temperature settings (0.05) for more reliable extraction results
- **Real-time Progress**: Live progress tracking with terminal logging and ETA calculations

### Real-World Benchmarks
| Document Type | Pages | Processing Time | Throughput |
|---------------|-------|-----------------|------------|
| Government Reports | 85-118 pages | 1.8-3.4 minutes | 1,700+ tok/sec |
| Financial Documents | 76-88 pages | 2.4-2.9 minutes | 1,400+ tok/sec |
| Technical Documents | 50+ pages | 1-2 minutes | 1,500+ tok/sec |

### Auto-Configuration System
- **Small PDFs** (≤10 pages): batch_size=2, high quality processing
- **Medium PDFs** (11-50 pages): batch_size=3, balanced processing  
- **Large PDFs** (51-200 pages): batch_size=4, efficient batch processing
- **Enterprise PDFs** (>200 pages): batch_size=5, maximum batch efficiency

### Performance Optimizations
- 50% fewer API calls through intelligent batching
- 38% faster processing with optimized auto-configuration
- Real-time progress tracking with ETA calculations
- Automatic retry logic with exponential backoff
- Enhanced table extraction supporting multiple data structures
- Improved data filtering to remove placeholder content
- Lower temperature settings for more consistent results

## Testing

### Comprehensive Test Suite

The repository includes a comprehensive test suite with both quick validation and full document stress testing.

**Quick Test (Recommended):**
```bash
cd tests
python run_all_tests.py
```

**Expected Output:**
```
🧪 Running Basic Tests...
✅ README Examples: All Python SDK examples working
✅ Integration Tests: Flask/FastAPI patterns verified  
✅ Schema Tests: Custom schema functionality working
✅ CLI Tests: All command-line options working

🎯 Results: 4/4 basic test suites passed (completed in ~30 seconds)

Would you like to run full document tests? (y/N): N
⏭️  Skipping full document tests (saves 15-20 minutes and ~$1.00 in API costs)

🎉 All basic tests passed! The library is working correctly.
```

### Test Categories

#### Basic Tests (~30 seconds)
- **README Examples** (`test_readme_examples.py`): All Python SDK examples
- **Integration Tests** (`test_flask_integration.py`): Flask/FastAPI patterns  
- **Schema Tests** (`test_example_schema.py`): Custom schema functionality
- **CLI Tests**: All command-line options and parameters

#### Full Document Tests (~15-20 minutes)
- **Vision 2030** (85 pages): Saudi government document processing
- **Example Financial** (76 pages): Financial document with heavy table content
- **Americas Children** (118 pages): US government statistical report  
- **Fed Economic Wellbeing** (88 pages): Federal Reserve economic research

### Performance Benchmarks

Our test suite includes comprehensive performance validation:

| Document | Pages | Time | Tokens | Speed | Cost Est. |
|----------|-------|------|--------|-------|-----------|
| Vision 2030 | 85 | 1.9 min | 230K | 2,033 tok/sec | ~$0.46 |
| Example Financial | 76 | 3.3 min | 187K | 1,354 tok/sec | ~$0.37 |
| Americas Children | 118 | 3.3 min | 352K | 1,761 tok/sec | ~$0.70 |
| Fed Economic | 88 | 3.0 min | 259K | 1,433 tok/sec | ~$0.52 |

### Individual Test Execution

Run specific test categories:

```bash
# Basic functionality tests
python tests/test_readme_examples.py
python tests/test_flask_integration.py
python tests/test_example_schema.py

# Full document stress tests (API costs apply)
python tests/test_vision2030_full_async.py
python tests/test_americas_children_full_async.py
python tests/test_fed_economic_wellbeing_full_async.py
```

### Test Coverage

The test suite verifies:
- ✅ All README Python SDK examples work correctly
- ✅ All CLI commands and options function properly
- ✅ Schema creation, validation, and custom field usage
- ✅ Synchronous and asynchronous processing modes
- ✅ Progress callbacks and real-time updates
- ✅ Integration patterns (Flask, FastAPI, batch processing)
- ✅ File I/O, path handling, and error conditions
- ✅ Performance benchmarks and auto-configuration
- ✅ Large document processing (up to 118 pages)
- ✅ Enhanced table extraction with multiple data structures
- ✅ Streamlit UI functionality without nested expander errors
- ✅ Data quality filtering and placeholder content removal

### Prerequisites for Testing

1. **API Key**: `export GROQ_API_KEY="your-key-here"`
2. **Package Installation**: `pip install -e .`
3. **Virtual Environment** (recommended)

### Cost-Aware Testing

The test runner includes built-in cost awareness:
- **Basic Tests**: Free validation using small document excerpts
- **Full Tests**: User confirmation with clear cost warnings ($0.20-0.35 per test)
- **Default Behavior**: Skips expensive tests unless explicitly confirmed
- **Graceful Handling**: Missing test files don't break the test suite

### Complete Documentation

For detailed performance analysis, auto-configuration results, and quality metrics, see `tests/README.md`.

## Recent Improvements

### Version 1.1.0 - Enhanced Table Processing & UI Fixes

**🔧 Major Enhancements:**
- **Enhanced Table Extraction**: Now supports both array-based and object-based table row structures
- **Improved Data Quality**: Better filtering of placeholder and example data
- **Lower Temperature**: Reduced to 0.05 for more consistent extraction results
- **Real-time Progress**: Enhanced progress tracking with terminal logging and ETA calculations

**🐛 Bug Fixes:**
- **Fixed Streamlit UI**: Resolved nested expander errors in table display
- **Improved Error Handling**: Better graceful recovery from processing failures
- **Enhanced Data Filtering**: More effective removal of placeholder content

**📊 Performance Improvements:**
- **Faster Processing**: Optimized batch processing with intelligent auto-configuration
- **Better Reliability**: Enhanced retry mechanisms with exponential backoff
- **Comprehensive Testing**: All test suites pass including full document processing

**🧪 Test Suite Validation:**
- ✅ All 8 test categories pass (README examples, integrations, schemas, CLI, full documents)
- ✅ 367 total pages processed across 4 different document types
- ✅ Performance benchmarks updated with latest results
- ✅ Cost estimates and processing speeds validated
# Groq PDF Vision

[![PyPI version](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/groq-pdf-vision/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

The Groq PDF Vision library provides intelligent PDF document processing using Groq's **meta-llama/llama-4-scout-17b-16e-instruct** model. Extract text, analyze images, and get structured data from any PDF with enterprise-grade reliability.

## Features

- **🔍 Intelligent Processing**: Automatic text extraction and image analysis
- **📊 Structured Output**: JSON schemas with page-level tracking
- **🖼️ Visual Analysis**: Detect charts, diagrams, logos, and visual elements
- **⚡ High Performance**: Optimized batch processing with 100% reliability
- **🐍 Pure Python**: No system dependencies, works everywhere
- **🔧 Flexible Schemas**: Predefined templates or custom JSON schemas
- **📱 Multiple Interfaces**: SDK, CLI, and web interface

## Installation

```bash
# Create and activate a virtual environment (recommended)
python -m venv groq_pdf_vision_env
source groq_pdf_vision_env/bin/activate  # On Windows: groq_pdf_vision_env\Scripts\activate

# Clone and install from source
pip install -e .
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

## Performance

- **Processing Speed**: ~2-5 seconds per page
- **Reliability**: 100% success rate across all test scenarios
- **Memory Usage**: Optimized for large documents
- **Batch Size**: 1-3 pages per API call for optimal performance

## Requirements

- Python 3.8+
- Groq API key
- Dependencies: `groq`, `pypdfium2`, `streamlit` (for web interface) 
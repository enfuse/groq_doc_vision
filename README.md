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
# Clone and install from source
pip install -e .
```

## Quick Start

```python
from groq_pdf_vision import extract_pdf

# Extract data from a PDF
result = extract_pdf("document.pdf")

# Access page-level results
for page in result["page_results"]:
    print(f"Page {page['page_number']}: {page['content'][:100]}...")

# Access accumulated data
print(f"Total pages: {len(result['page_results'])}")
print(f"Images found: {len(result['accumulated_data']['image_descriptions'])}")
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
from groq_pdf_vision import extract_pdf, create_financial_schema

# Use predefined schema
schema = create_financial_schema()
result = extract_pdf("report.pdf", schema=schema)

# Use custom schema
custom_schema = {
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

result = extract_pdf("document.pdf", schema=custom_schema)
```

### Command Line Interface

```bash
# Basic processing
groq-pdf document.pdf --save

# Specific page range
groq-pdf document.pdf --start-page 1 --end-page 10

# Use predefined schema
groq-pdf document.pdf --schema-preset financial

# Custom schema file
groq-pdf document.pdf --schema my_schema.json

# Inline JSON schema
groq-pdf document.pdf --schema '{"type":"object","properties":{"summary":{"type":"string"}}}'

# Get document info
groq-pdf document.pdf --info-only
```

### Web Interface

Launch the Streamlit web interface:

```bash
streamlit run app.py
```

Then open http://localhost:8501 for drag-and-drop PDF processing.

## Predefined Schemas

The library includes several predefined schemas for common use cases:

```python
from groq_pdf_vision import (
    create_simple_schema,        # Basic text extraction
    create_entity_extraction_schema,  # Named entities
    create_financial_schema,     # Financial documents
    create_technical_schema,     # Technical documentation
    create_academic_schema       # Academic papers
)

# Use any predefined schema
schema = create_financial_schema()
result = extract_pdf("annual_report.pdf", schema=schema)
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

### Schema Creators

- `create_simple_schema()`: Basic text and image extraction
- `create_entity_extraction_schema()`: Named entity recognition
- `create_financial_schema()`: Financial document analysis
- `create_technical_schema()`: Technical documentation
- `create_academic_schema()`: Academic paper analysis

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
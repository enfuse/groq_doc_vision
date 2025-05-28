#!/usr/bin/env python3
"""
Test Flask integration example from README
"""

import os
import asyncio
import tempfile
import shutil
import sys
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from groq_pdf_vision import extract_pdf_async

# Set API key
os.environ["GROQ_API_KEY"] = "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"

# Get the example PDF path relative to the tests directory
EXAMPLE_PDF = str(Path(__file__).parent.parent / "example_docs" / "example.pdf")

async def test_flask_integration_logic():
    """Test the core logic from the Flask integration example"""
    print("🧪 Testing Flask Integration Logic...")
    
    # Simulate the Flask logic without the web framework
    filepath = EXAMPLE_PDF
    
    async def process():
        return await extract_pdf_async(filepath, start_page=1, end_page=2)
    
    result, metadata = await process()
    
    # Simulate the response data
    response_data = {
        "pages": len(result["page_results"]),
        "processing_time": metadata["processing_time_seconds"],
        "data": result["accumulated_data"]
    }
    
    print(f"✅ Flask integration logic works:")
    print(f"   Pages: {response_data['pages']}")
    print(f"   Processing time: {response_data['processing_time']:.2f}s")
    print(f"   Data keys: {list(response_data['data'].keys())}")
    print("✅ Flask Integration - PASSED\n")

async def test_fastapi_integration_logic():
    """Test the core logic from the FastAPI integration example"""
    print("🧪 Testing FastAPI Integration Logic...")
    
    # Simulate file upload and processing
    with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp:
        # Copy example PDF to temp file (simulating upload)
        shutil.copy(EXAMPLE_PDF, tmp.name)
        tmp_path = tmp.name
    
    result, metadata = await extract_pdf_async(tmp_path, start_page=1, end_page=2)
    
    # Simulate the response
    response_data = {
        "filename": "example.pdf",
        "pages_processed": len(result["page_results"]),
        "processing_time": metadata["processing_time_seconds"]
    }
    
    print(f"✅ FastAPI integration logic works:")
    print(f"   Filename: {response_data['filename']}")
    print(f"   Pages processed: {response_data['pages_processed']}")
    print(f"   Processing time: {response_data['processing_time']:.2f}s")
    
    # Clean up temp file
    os.unlink(tmp_path)
    print("✅ FastAPI Integration - PASSED\n")

async def test_batch_processing():
    """Test the batch processing example logic"""
    print("🧪 Testing Batch Processing Logic...")
    
    # Simulate batch processing with one file
    pdf_files = [EXAMPLE_PDF]
    
    for pdf_file in pdf_files:
        print(f"Processing {os.path.basename(pdf_file)}")
        
        result, metadata = await extract_pdf_async(
            pdf_file,
            start_page=1,
            end_page=2,
            save_results=False  # Don't save for test
        )
        
        print(f"  ✅ {len(result['page_results'])} pages in {metadata['processing_time_seconds']:.1f}s")
    
    print("✅ Batch Processing - PASSED\n")

async def main():
    """Run all integration tests"""
    print("🚀 Testing Integration Examples...\n")
    
    await test_flask_integration_logic()
    await test_fastapi_integration_logic()
    await test_batch_processing()
    
    print("🎉 All integration examples tested successfully!")

if __name__ == "__main__":
    asyncio.run(main()) 
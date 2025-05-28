#!/usr/bin/env python3
"""
Async test script to process the ENTIRE vision2030.pdf document (85 pages)
This is a stress test for large document processing.
"""

import asyncio
import json
import os
import sys
import time
from pathlib import Path

# Add parent directory to path so we can import the package
sys.path.insert(0, str(Path(__file__).parent.parent))

from groq_pdf_vision import extract_pdf_async

# Check for API key - fail fast if not available
if not os.environ.get("GROQ_API_KEY"):
    print("❌ ERROR: GROQ_API_KEY environment variable not set")
    print("   Please set your Groq API key: export GROQ_API_KEY='your-key-here'")
    sys.exit(1)

# Get file paths relative to the tests directory
VISION2030_PDF = str(Path(__file__).parent.parent / "example_docs" / "vision2030.pdf")
CUSTOM_SCHEMA = str(Path(__file__).parent.parent / "example_docs" / "example_custom_schema.json")

async def test_vision2030_full_async():
    """Test processing the ENTIRE vision2030.pdf with custom schema (async)"""
    print('🚀 Processing ENTIRE vision2030.pdf with custom schema (85 pages)...')
    print('📋 This is a stress test for large document processing')
    print('⏱️  Expected processing time: ~4-6 minutes')
    print('💰 Expected cost: ~$0.30-0.50 (based on token usage)')
    print('🔄 Progress will be shown in real-time below:')
    print('=' * 60)
    
    # Load the custom schema
    with open(CUSTOM_SCHEMA, 'r') as f:
        schema = json.load(f)

    start_time = time.time()

    def progress_callback(message, current, total):
        percentage = (current / total) * 100
        elapsed_time = time.time() - start_time
        if current > 0:
            estimated_total = (elapsed_time / current) * total
            remaining_time = estimated_total - elapsed_time
            print(f'🔄 [{current}/{total}] ({percentage:.1f}%) {message} | Elapsed: {elapsed_time:.1f}s | ETA: {remaining_time:.1f}s')
        else:
            print(f'🔄 [{current}/{total}] ({percentage:.1f}%) {message}')
    
    # Process entire document with custom schema (async)
    result, metadata = await extract_pdf_async(
        VISION2030_PDF,
        schema=schema,
        progress_callback=progress_callback,
        save_results=True,
        output_filename='vision2030_full_results.json'
    )

    end_time = time.time()
    total_time = end_time - start_time

    print('=' * 60)
    print(f'🎉 FULL DOCUMENT PROCESSING COMPLETED!')
    print(f'📊 Final Results Summary:')
    print(f'   Total pages processed: {len(result["page_results"])}')
    print(f'   Total processing time: {total_time:.1f} seconds ({total_time/60:.1f} minutes)')
    print(f'   Average time per page: {total_time/len(result["page_results"]):.1f} seconds')
    print(f'   Token usage: {metadata["token_usage"]["total_tokens"]} tokens')
    
    # Calculate estimated cost (rough estimate: $0.00002 per token)
    estimated_cost = metadata["token_usage"]["total_tokens"] * 0.00002
    print(f'   Estimated cost: ~${estimated_cost:.4f}')
    print(f'   Results saved to: vision2030_full_results.json')
    print()

    # Analyze the results
    pages_with_content = sum(1 for page in result["page_results"] if page.get("content", "").strip())
    pages_with_images = sum(1 for page in result["page_results"] if page.get("contains_images", False))
    pages_with_tables = sum(1 for page in result["page_results"] if page.get("contains_tables", False))
    total_entities = sum(len(page.get("entities", [])) for page in result["page_results"])
    total_findings = sum(len(page.get("key_findings", [])) for page in result["page_results"])

    print(f'📈 Content Analysis:')
    print(f'   Pages with text content: {pages_with_content}/{len(result["page_results"])}')
    print(f'   Pages with images: {pages_with_images}/{len(result["page_results"])}')
    print(f'   Pages with tables: {pages_with_tables}/{len(result["page_results"])}')
    print(f'   Total entities extracted: {total_entities}')
    print(f'   Total key findings: {total_findings}')
    print()

    # Show sample results from different parts of the document
    sample_pages = [0, len(result["page_results"])//2, -1]  # First, middle, last
    for i in sample_pages:
        page = result["page_results"][i]
        print(f'📄 Sample Page {page["page_number"]}:')
        print(f'   Content length: {len(page.get("content", ""))} characters')
        print(f'   Content preview: {page.get("content", "")[:100]}...')
        print(f'   Document type: {page.get("document_type", "N/A")}')
        print(f'   Sentiment: {page.get("sentiment", "N/A")}')
        print(f'   Images: {len(page.get("image_descriptions", []))}')
        print(f'   Entities: {len(page.get("entities", []))}')
        print(f'   Key findings: {len(page.get("key_findings", []))}')
        print()

    print('✅ Vision2030 Full Document Test - PASSED')
    return True

async def main():
    """Main async function"""
    print("🚀 Starting FULL vision2030.pdf processing test...")
    print("⚠️  This will process all 85 pages and may take 4-6 minutes")
    print("💡 You can interrupt with Ctrl+C if needed")
    print()
    
    try:
        success = await test_vision2030_full_async()
        if success:
            print('🎉 Full document test completed successfully!')
        else:
            print('❌ Test failed')
            sys.exit(1)
    except KeyboardInterrupt:
        print('\n⚠️  Test interrupted by user')
        sys.exit(1)
    except Exception as e:
        print(f'\n❌ Test failed with error: {e}')
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main()) 
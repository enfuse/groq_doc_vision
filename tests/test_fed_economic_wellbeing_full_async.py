#!/usr/bin/env python3
"""
Async test script to process the ENTIRE fed_economic_wellbeing_2020.pdf document
This is a stress test for large document processing with economic data, tables and charts.
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
FED_ECONOMIC_PDF = str(Path(__file__).parent.parent / "example_docs" / "fed_economic_wellbeing_2020.pdf")
CUSTOM_SCHEMA = str(Path(__file__).parent.parent / "example_docs" / "example_custom_schema.json")

async def test_fed_economic_wellbeing_full_async():
    """Test processing the ENTIRE fed_economic_wellbeing_2020.pdf with custom schema (async)"""
    print('🚀 Processing ENTIRE fed_economic_wellbeing_2020.pdf with custom schema...')
    print('📋 This is a stress test for large document processing with economic data and charts')
    print('⏱️  Expected processing time: ~5-8 minutes')
    print('💰 Expected cost: ~$0.40-0.70 (based on token usage)')
    print('🔄 Progress will be shown in real-time below:')
    print('=' * 60)
    
    # Load the custom schema
    with open(CUSTOM_SCHEMA, 'r') as f:
        schema = json.load(f)

    start_time = time.time()

    def progress_callback(message, current, total):
        percentage = (current / total) * 100
        elapsed = time.time() - start_time
        if current > 0:
            estimated_total = elapsed * (total / current)
            remaining = estimated_total - elapsed
            print(f"🔄 [{current}/{total}] ({percentage:.1f}%) {message} | "
                  f"⏱️ Elapsed: {elapsed:.1f}s | ETA: {remaining:.1f}s")
        else:
            print(f"🔄 [{current}/{total}] ({percentage:.1f}%) {message}")
        sys.stdout.flush()  # Force immediate output

    try:
        # Process the entire document with custom schema
        result, metadata = await extract_pdf_async(
            pdf_file_path=FED_ECONOMIC_PDF,
            schema=schema,
            progress_callback=progress_callback
        )
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        print('=' * 60)
        print('✅ SUCCESS: Federal Economic Wellbeing 2020 processing completed!')
        print(f'⏱️  Total processing time: {processing_time:.1f} seconds ({processing_time/60:.1f} minutes)')
        print(f'📄 Pages processed: {len(result.get("page_results", []))}')
        
        # Calculate token usage if available
        total_tokens = 0
        if metadata and "token_usage" in metadata:
            total_tokens = metadata["token_usage"].get("total_tokens", 0)
            print(f'🔤 Total tokens used: {total_tokens:,}')
            if total_tokens > 0:
                tokens_per_second = total_tokens / processing_time
                print(f'⚡ Processing speed: {tokens_per_second:.1f} tokens/second')
        
        # Save results to file
        output_file = "fed_economic_wellbeing_full_results.json"
        output_data = {
            "processing_metadata": metadata,
            "extraction_results": result
        }
        with open(output_file, 'w') as f:
            json.dump(output_data, f, indent=2)
        
        print(f'💾 Results saved to: {output_file}')
        
        # Show some sample extracted content
        if result.get("page_results"):
            print('\n📊 Sample extracted content from first few pages:')
            for i, page in enumerate(result["page_results"][:3]):
                print(f'\n--- Page {i+1} ---')
                content = page.get("content", "")[:200]
                print(f'Content preview: {content}...')
                
                if page.get("contains_images"):
                    images = page.get("image_descriptions", [])
                    if images:
                        print(f'Images detected: {len(images)} image(s)')
                        # Handle both string and object formats for image descriptions
                        first_image = images[0]
                        if isinstance(first_image, str):
                            print(f'First image: {first_image[:100]}...')
                        elif isinstance(first_image, dict):
                            # Extract description from object format
                            description = first_image.get("description", str(first_image))
                            print(f'First image: {description[:100]}...')
                        else:
                            print(f'First image: {str(first_image)[:100]}...')
                
                # Show any extracted entities or key findings
                if page.get("entities"):
                    entities = page.get("entities", [])
                    if isinstance(entities, list) and len(entities) > 0:
                        entities_sample = entities[:3] if len(entities) > 3 else entities
                        print(f'Entities found: {", ".join(str(e) for e in entities_sample)}')
        
        print('\n🎉 Federal Economic Wellbeing 2020 full document processing test completed successfully!')
        return True
        
    except Exception as e:
        print(f'❌ ERROR during processing: {str(e)}')
        return False

async def main():
    """Main function to run the test"""
    print("🧪 Federal Economic Wellbeing 2020 Full Document Async Processing Test")
    print("=" * 60)
    
    # Check if files exist
    if not os.path.exists(FED_ECONOMIC_PDF):
        print(f"❌ ERROR: PDF file not found: {FED_ECONOMIC_PDF}")
        return False
    
    if not os.path.exists(CUSTOM_SCHEMA):
        print(f"❌ ERROR: Schema file not found: {CUSTOM_SCHEMA}")
        return False
    
    # Run the test
    success = await test_fed_economic_wellbeing_full_async()
    
    if success:
        print("\n✅ All tests passed!")
        return True
    else:
        print("\n❌ Test failed!")
        return False

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1) 
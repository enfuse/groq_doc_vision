#!/usr/bin/env python3
"""
Groq PDF Vision Extraction Wrapper
Intelligent PDF processing that automatically handles any size document.
Always returns accumulated results for comprehensive extraction.
"""

import asyncio
import json
import os
import base64
import time
from io import BytesIO
from typing import List, Dict, Any, Tuple, Optional, Callable

from groq import AsyncGroq
import pypdfium2 as pdfium
from PIL import Image

# --- Configuration ---
GROQ_MODEL_ID = "meta-llama/llama-4-scout-17b-16e-instruct"
# GROQ_MODEL_ID = "meta-llama/llama-4-maverick-17b-128e-instruct"

# Image processing parameters
IMAGE_FORMAT = "jpeg"
BASE64_IMAGE_SIZE_LIMIT_MB = 3.5
MAX_IMAGE_DIMENSION = 4096

# Batch processing parameters for automatic scaling
MAX_IMAGES_PER_BATCH = 5
RATE_LIMIT_DELAY = 1.0
MAX_RETRIES = 3
RETRY_DELAY = 2.0

# Auto-scaling thresholds
SMALL_PDF_THRESHOLD = 10
MEDIUM_PDF_THRESHOLD = 50
LARGE_PDF_THRESHOLD = 200

def load_api_key():
    """Load Groq API key from emaillist.txt file or environment."""
    # Try environment variable first
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return api_key
    
    # Try emaillist.txt file
    try:
        with open("emaillist.txt", "r") as f:
            content = f.read()
            for line in content.split('\n'):
                if 'GROQ API KEY' in line:
                    api_key = line.split(' - ')[-1].strip()
                    os.environ["GROQ_API_KEY"] = api_key
                    return api_key
    except FileNotFoundError:
        pass
    
    raise ValueError("❌ Groq API key not found. Please set GROQ_API_KEY environment variable or add it to emaillist.txt")

def get_default_schema():
    """Get the comprehensive default schema for PDF extraction."""
    return {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer", "description": "Page number (1-indexed) where this data was extracted from"},
            "content": {"type": "string", "description": "Main text content extracted from the page"},
            "custom_content": {"type": "string", "description": "Source document identifier"},
            "error": {"type": "integer", "description": "Error code (0 for success)"},
            "name": {"type": "string", "description": "Page identifier name"},
            "result": {"type": "string", "description": "Processing summary"},
            "wordings_and_terms": {"type": "array", "items": {"type": "string"}, "description": "Key terms found"},
            "key_main_takeaways": {"type": "array", "items": {"type": "string"}, "description": "Main takeaways"},
            "primary_insights": {"type": "array", "items": {"type": "string"}, "description": "Primary insights"},
            "explicit_sections": {"type": "array", "items": {"type": "string"}, "description": "Section headings"},
            "explicit_pages": {"type": "array", "items": {"type": "integer"}, "description": "Referenced page numbers"},
            "contains_tables": {"type": "boolean", "description": "Whether page contains tables"},
            "contains_images": {"type": "boolean", "description": "Whether page contains images, charts, or diagrams"},
            "image_descriptions": {
                "type": "array",
                "description": "Descriptions of visual elements",
                "items": {
                    "type": "object",
                    "properties": {
                        "image_type": {"type": "string", "description": "Type of image (chart, diagram, photo, logo, etc.)"},
                        "description": {"type": "string", "description": "Detailed description of the image"},
                        "location": {"type": "string", "description": "Location on page (top, middle, bottom, etc.)"},
                        "content_relation": {"type": "string", "description": "How the image relates to the text content"}
                    }
                }
            },
            "visual_summary": {"type": "string", "description": "Overall summary of visual elements on the page"},
            "tables_data": {
                "type": "array",
                "description": "Extracted table data",
                "items": {
                    "type": "object",
                    "properties": {
                        "table_title": {"type": "string"},
                        "headers": {"type": "array", "items": {"type": "string"}},
                        "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                        "table_notes": {"type": "string"}
                    }
                }
            }
        }
    }

def auto_configure_processing(total_pages: int) -> Dict[str, Any]:
    """Automatically configure processing parameters based on PDF size."""
    if total_pages <= SMALL_PDF_THRESHOLD:
        return {"batch_size": 2, "dpi": 200, "description": "Small PDF - High quality processing"}
    elif total_pages <= MEDIUM_PDF_THRESHOLD:
        return {"batch_size": 3, "dpi": 150, "description": "Medium PDF - Balanced processing"}
    elif total_pages <= LARGE_PDF_THRESHOLD:
        return {"batch_size": 2, "dpi": 150, "description": "Large PDF - Efficient processing"}
    else:
        return {"batch_size": 1, "dpi": 120, "description": "Enterprise PDF - Memory optimized processing"}

def convert_pdf_to_images(pdf_path: str, dpi: int = 150, start_page: int = 1, end_page: Optional[int] = None) -> List[Image.Image]:
    """Convert PDF pages to PIL Images using pypdfium2."""
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        total_pages = len(pdf)
        
        if end_page is None:
            end_page = total_pages
        
        start_page = max(1, start_page)
        end_page = min(total_pages, end_page)
        
        images = []
        for page_num in range(start_page - 1, end_page):
            page = pdf.get_page(page_num)
            scale = dpi / 72.0
            
            # Use simplified render call
            pil_image = page.render(scale=scale).to_pil()
            
            images.append(pil_image)
        
        pdf.close()
        return images
        
    except Exception as e:
        raise Exception(f"Error converting PDF to images: {str(e)}")

def resize_image_if_needed(image: Image.Image, max_dimension: int = MAX_IMAGE_DIMENSION) -> Image.Image:
    """Resize image if it exceeds maximum dimensions while maintaining aspect ratio."""
    width, height = image.size
    
    if width <= max_dimension and height <= max_dimension:
        return image
    
    if width > height:
        new_width = max_dimension
        new_height = int((height * max_dimension) / width)
    else:
        new_height = max_dimension
        new_width = int((width * max_dimension) / height)
    
    return image.resize((new_width, new_height), Image.Resampling.LANCZOS)

def encode_image_to_base64(image: Image.Image, format: str = IMAGE_FORMAT, quality: int = 85) -> str:
    """Convert PIL Image to base64 string with size optimization."""
    image = resize_image_if_needed(image)
    
    if image.mode in ('RGBA', 'LA', 'P'):
        background = Image.new('RGB', image.size, (255, 255, 255))
        if image.mode == 'P':
            image = image.convert('RGBA')
        background.paste(image, mask=image.split()[-1] if image.mode in ('RGBA', 'LA') else None)
        image = background
    
    buffer = BytesIO()
    save_kwargs = {"format": format.upper(), "optimize": True}
    if format.lower() == "jpeg":
        save_kwargs["quality"] = quality
    
    image.save(buffer, **save_kwargs)
    
    while buffer.tell() > BASE64_IMAGE_SIZE_LIMIT_MB * 1024 * 1024 and quality > 20:
        quality -= 10
        buffer = BytesIO()
        save_kwargs["quality"] = quality
        image.save(buffer, **save_kwargs)
    
    buffer.seek(0)
    return base64.b64encode(buffer.getvalue()).decode('utf-8')

async def process_batch_with_retry(
    client: AsyncGroq, images: List[str], schema: Dict[str, Any],
    batch_num: int, total_batches: int, page_numbers: List[int]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Process a batch of images with retry logic."""
    
    for attempt in range(MAX_RETRIES):
        try:
            # Generate example JSON structure from the schema
            def generate_example_from_schema(schema_dict):
                """Generate an example JSON object from a schema."""
                if schema_dict.get("type") != "object":
                    return {}
                
                example = {}
                properties = schema_dict.get("properties", {})
                
                for field_name, field_def in properties.items():
                    field_type = field_def.get("type", "string")
                    description = field_def.get("description", "")
                    
                    if field_type == "string":
                        if "page" in field_name.lower():
                            example[field_name] = "Page X"
                        elif "content" in field_name.lower():
                            example[field_name] = "main text content from page"
                        elif description:
                            example[field_name] = f"example {field_name}"
                        else:
                            example[field_name] = f"example_{field_name}"
                    elif field_type == "integer":
                        if "page" in field_name.lower():
                            example[field_name] = 1
                        else:
                            example[field_name] = 0
                    elif field_type == "number":
                        example[field_name] = 0.0
                    elif field_type == "boolean":
                        example[field_name] = True
                    elif field_type == "array":
                        items_def = field_def.get("items", {})
                        if items_def.get("type") == "string":
                            example[field_name] = ["example1", "example2"]
                        elif items_def.get("type") == "object":
                            # Handle nested objects
                            nested_example = generate_example_from_schema(items_def)
                            example[field_name] = [nested_example] if nested_example else []
                        else:
                            example[field_name] = []
                    elif field_type == "object":
                        example[field_name] = generate_example_from_schema(field_def)
                
                return example
            
            # Generate example structure from the provided schema
            example_structure = generate_example_from_schema(schema)
            example_json = json.dumps({"pages": [example_structure]}, indent=2)
            
            # Create a more explicit prompt that uses the custom schema
            prompt_text = f"""Extract data from these PDF pages and return as a valid JSON object with a "pages" array.

IMPORTANT: Return EXACTLY this structure based on the provided schema:
{example_json}

Process these pages: {page_numbers}

COMPREHENSIVE EXTRACTION INSTRUCTIONS:
1. TEXT CONTENT: Extract all text content according to the schema fields.

2. VISUAL ELEMENTS: If the schema includes image-related fields, carefully analyze all visual elements including:
   - Charts and graphs (bar, line, pie, scatter, etc.)
   - Diagrams and flowcharts
   - Images and photographs
   - Logos and branding elements
   - Illustrations and drawings
   - Maps and technical drawings
   - Screenshots or interface elements

3. SCHEMA COMPLIANCE: Follow the exact field names and types specified in the schema.

4. DATA EXTRACTION: Extract data according to the field descriptions in the schema.

Return ONLY the JSON object with the "pages" array containing one object per page that matches the schema structure."""

            messages = [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt_text
                        }
                    ] + [
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/{IMAGE_FORMAT};base64,{img_b64}"}
                        } for img_b64 in images
                    ]
                }
            ]
            
            # Use json_object format but with a more structured prompt
            response = await client.chat.completions.create(
                model=GROQ_MODEL_ID, 
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.1, 
                max_tokens=8000
            )
            
            content = response.choices[0].message.content
            
            try:
                parsed_content = json.loads(content)
                
                # Handle different response structures more robustly
                if isinstance(parsed_content, dict):
                    if 'pages' in parsed_content and isinstance(parsed_content['pages'], list):
                        batch_results = parsed_content['pages']
                    elif 'data' in parsed_content and isinstance(parsed_content['data'], list):
                        batch_results = parsed_content['data']
                    elif 'results' in parsed_content and isinstance(parsed_content['results'], list):
                        batch_results = parsed_content['results']
                    else:
                        # If it's a single page object, wrap it in a list
                        batch_results = [parsed_content]
                elif isinstance(parsed_content, list):
                    batch_results = parsed_content
                else:
                    raise Exception(f"Unexpected response format: {type(parsed_content)}")
                
                # Validate that we have the expected number of results
                if len(batch_results) != len(page_numbers):
                    print(f"  ⚠️  Warning: Expected {len(page_numbers)} results, got {len(batch_results)}")
                    # Pad with empty results if needed using schema structure
                    while len(batch_results) < len(page_numbers):
                        page_num = page_numbers[len(batch_results)]
                        empty_result = generate_example_from_schema(schema)
                        empty_result["page_number"] = page_num
                        if "content" in empty_result:
                            empty_result["content"] = f"Partial processing for page {page_num}"
                        batch_results.append(empty_result)
                
            except json.JSONDecodeError as e:
                raise Exception(f"Invalid JSON response: {e}\nContent: {content[:500]}...")
            
            usage_info = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
            
            return batch_results, usage_info
            
        except Exception as e:
            if attempt < MAX_RETRIES - 1:
                delay = RETRY_DELAY * (2 ** attempt)
                print(f"  Batch processing failed (attempt {attempt + 1}/{MAX_RETRIES}), retrying in {delay}s: {str(e)[:200]}...")
                await asyncio.sleep(delay)
            else:
                print(f"  ❌ Batch {batch_num}/{total_batches} failed after {MAX_RETRIES} attempts: {str(e)[:200]}...")
                empty_results = []
                for page_num in page_numbers:
                    # Create error result using schema structure
                    error_result = generate_example_from_schema(schema)
                    error_result["page_number"] = page_num
                    if "content" in error_result:
                        error_result["content"] = f"Failed to process page {page_num}"
                    if "error" in error_result:
                        error_result["error"] = 1
                    empty_results.append(error_result)
                return empty_results, {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}

def accumulate_results(all_results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Accumulate all page results into a single comprehensive result."""
    if not all_results:
        return {}
    
    # Get the first result to understand the schema structure
    first_result = all_results[0]
    accumulated = {}
    
    # Initialize accumulated data based on the actual schema fields
    for field_name, field_value in first_result.items():
        if field_name == "page_number":
            continue  # Skip page_number as it's page-specific
        
        if isinstance(field_value, str):
            accumulated[field_name] = ""
        elif isinstance(field_value, list):
            accumulated[field_name] = []
        elif isinstance(field_value, bool):
            accumulated[field_name] = False
        elif isinstance(field_value, (int, float)):
            accumulated[field_name] = field_value  # Keep first value for numbers
        else:
            accumulated[field_name] = field_value
    
    # Special handling for visual summaries if present
    if any("visual_summary" in result for result in all_results):
        accumulated["visual_summaries"] = []
    
    # Accumulate data from all pages
    for page_result in all_results:
        for field_name, field_value in page_result.items():
            if field_name == "page_number":
                continue
            
            if field_name not in accumulated:
                accumulated[field_name] = field_value
                continue
            
            # Handle different field types
            if isinstance(field_value, str) and field_value:
                if field_name == "content":
                    accumulated[field_name] += field_value + " "
                elif accumulated[field_name] == "":
                    accumulated[field_name] = field_value
                elif field_name in ["name", "result", "custom_content"]:
                    # For these fields, create a combined description
                    if field_name == "name":
                        accumulated[field_name] = f"Accumulated Pages 1-{len(all_results)}"
                    elif field_name == "result":
                        accumulated[field_name] = f"Accumulated analysis of {len(all_results)} pages"
                    elif field_name == "custom_content" and accumulated[field_name] == "":
                        accumulated[field_name] = field_value
            
            elif isinstance(field_value, list) and field_value:
                # For arrays, extend with unique items
                for item in field_value:
                    if item and item not in accumulated[field_name]:
                        accumulated[field_name].append(item)
            
            elif isinstance(field_value, bool):
                # For booleans, use OR logic (true if any page is true)
                accumulated[field_name] = accumulated[field_name] or field_value
            
            elif isinstance(field_value, (int, float)):
                # For numbers, handle based on field name
                if field_name == "error":
                    accumulated[field_name] = max(accumulated[field_name], field_value)
                elif "count" in field_name.lower() or "total" in field_name.lower():
                    accumulated[field_name] += field_value
                # For other numbers, keep the first non-zero value or average
        
        # Special handling for visual summaries
        if "visual_summary" in page_result and page_result["visual_summary"]:
            if "visual_summaries" in accumulated:
                accumulated["visual_summaries"].append(page_result["visual_summary"])
    
    # Clean up content field
    if "content" in accumulated:
        accumulated["content"] = accumulated["content"].strip()
    
    # Clean up any page-specific arrays that might have duplicates
    for field_name, field_value in accumulated.items():
        if isinstance(field_value, list) and field_name in ["explicit_pages", "page_numbers"]:
            accumulated[field_name] = sorted(list(set(field_value)))
    
    return accumulated

async def extract_data_from_pdf(
    pdf_file_path: str,
    response_schema: Optional[Dict[str, Any]] = None,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
    save_results: bool = False,
    output_filename: Optional[str] = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extract data from PDF with automatic configuration and accumulated results.
    
    Args:
        pdf_file_path: Path to the PDF file
        response_schema: JSON schema for extraction (uses default if None)
        start_page: Start page number (1-indexed, optional)
        end_page: End page number (1-indexed, optional)
        progress_callback: Function for progress updates (message, current, total)
        save_results: Whether to save results to JSON file
        output_filename: Custom output filename (auto-generated if None)
    
    Returns:
        Tuple of (accumulated_results, processing_metadata)
    """
    
    api_key = load_api_key()
    client = AsyncGroq(api_key=api_key)
    
    if response_schema is None:
        response_schema = get_default_schema()
    
    pdf = pdfium.PdfDocument(pdf_file_path)
    total_pages = len(pdf)
    pdf.close()
    
    if start_page is None:
        start_page = 1
    if end_page is None:
        end_page = total_pages
    
    pages_to_process = end_page - start_page + 1
    config = auto_configure_processing(pages_to_process)
    
    print(f"📄 Processing PDF: {pdf_file_path}")
    print(f"   Total pages in PDF: {total_pages}")
    print(f"   Processing pages {start_page}-{end_page} ({pages_to_process} pages)")
    print(f"   Auto-configuration: {config['description']}")
    print(f"   Batch size: {config['batch_size']}, DPI: {config['dpi']}")
    
    start_time = time.time()
    
    images = convert_pdf_to_images(pdf_file_path, config['dpi'], start_page, end_page)
    
    batch_size = config['batch_size']
    total_batches = (len(images) + batch_size - 1) // batch_size
    
    print(f"   Processing {len(images)} pages in {total_batches} batches of up to {batch_size} pages each")
    
    all_results = []
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
    
    for batch_num in range(total_batches):
        batch_start = batch_num * batch_size
        batch_end = min(batch_start + batch_size, len(images))
        batch_images = images[batch_start:batch_end]
        batch_page_numbers = list(range(start_page + batch_start, start_page + batch_end))
        
        if progress_callback:
            progress_callback(f"Processing batch {batch_num + 1}/{total_batches}: pages {batch_page_numbers[0]}-{batch_page_numbers[-1]}", 
                            batch_num + 1, total_batches)
        else:
            print(f"Progress: {((batch_num + 1) / total_batches) * 100:.1f}% ({batch_num + 1}/{total_batches})")
            print(f"  Processing batch {batch_num + 1}/{total_batches}: pages {batch_page_numbers[0]}-{batch_page_numbers[-1]}")
        
        batch_b64_images = []
        for img in batch_images:
            b64_img = encode_image_to_base64(img, IMAGE_FORMAT)
            batch_b64_images.append(b64_img)
        
        batch_results, batch_usage = await process_batch_with_retry(
            client, batch_b64_images, response_schema, batch_num + 1, total_batches, batch_page_numbers
        )
        
        # Add explicit page numbers to each result
        for i, result in enumerate(batch_results):
            if i < len(batch_page_numbers):
                result['page_number'] = batch_page_numbers[i]
        
        all_results.extend(batch_results)
        
        for key in total_usage:
            total_usage[key] += batch_usage.get(key, 0)
        
        if batch_num < total_batches - 1:
            await asyncio.sleep(RATE_LIMIT_DELAY)
    
    end_time = time.time()
    processing_time = end_time - start_time
    
    print(f"  ✅ Completed processing {len(images)} pages in {total_batches} batches")
    print(f"  📊 Token usage: {total_usage['total_tokens']} total tokens")
    print(f"  ⏱️  Processing time: {processing_time:.2f} seconds")
    
    accumulated_data = accumulate_results(all_results)
    
    result = {
        "source_pdf": pdf_file_path,
        "page_results": all_results,  # Individual page results with page numbers
        "accumulated_data": accumulated_data,
        "processing_stats": {
            "total_pages": len(images),
            "total_batches": total_batches,
            "batch_size": batch_size,
            "dpi_used": config['dpi'],
            "processing_time_seconds": processing_time,
            "auto_config": config['description']
        }
    }
    
    metadata = {
        "processing_time_seconds": processing_time,
        "token_usage": total_usage,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pages_processed": len(images),
        "batches_used": total_batches
    }
    
    if save_results:
        if output_filename is None:
            base_name = os.path.splitext(os.path.basename(pdf_file_path))[0]
            output_filename = f"{base_name}_extraction_results.json"
        
        output_data = {
            "processing_metadata": metadata,
            "extraction_results": result
        }
        
        with open(output_filename, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)
        
        print(f"📁 Results saved to: {output_filename}")
    
    acc_data = accumulated_data
    print(f"\n📊 Extraction Summary:")
    print(f"   Total content length: {len(acc_data.get('content', ''))} characters")
    print(f"   Tables found: {len(acc_data.get('tables_data', []))}")
    print(f"   Images found: {len(acc_data.get('image_descriptions', []))}")
    print(f"   Key takeaways: {len(acc_data.get('key_main_takeaways', []))}")
    print(f"   Terms extracted: {len(acc_data.get('wordings_and_terms', []))}")
    
    if total_usage['total_tokens'] > 0:
        cost_estimate = total_usage['total_tokens'] * 0.00002
        print(f"   Token usage: {total_usage['total_tokens']} tokens (~${cost_estimate:.4f})")
    
    return result, metadata

# Legacy function for backward compatibility
async def extract_data_from_pdf_with_groq_vision(
    pdf_file_paths: List[str],
    response_schema: Optional[Dict[str, Any]] = None,
    **kwargs
) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """Legacy function for backward compatibility. Now processes each PDF and returns accumulated results."""
    results = []
    usage_info = []
    
    for pdf_path in pdf_file_paths:
        result, metadata = await extract_data_from_pdf(pdf_path, response_schema, **kwargs)
        results.append(result)
        usage_info.append(metadata.get('token_usage', {}))
    
    return results, usage_info

# CLI interface
async def main():
    """Command line interface for PDF processing."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Groq PDF Vision Extraction")
    parser.add_argument("pdf_file", help="Path to PDF file")
    parser.add_argument("--start-page", type=int, help="Start page number (1-indexed)")
    parser.add_argument("--end-page", type=int, help="End page number (1-indexed)")
    parser.add_argument("--save", action="store_true", help="Save results to JSON file")
    parser.add_argument("--output", help="Output filename for results")
    parser.add_argument("--schema", help="Path to custom JSON schema file OR inline JSON schema string")
    parser.add_argument("--schema-json", help="Inline JSON schema string (alternative to --schema)")
    
    args = parser.parse_args()
    
    schema = None
    if args.schema:
        # Try to parse as JSON first, then as file path
        try:
            # Check if it looks like JSON (starts with { or [)
            schema_input = args.schema.strip()
            if schema_input.startswith('{') or schema_input.startswith('['):
                schema = json.loads(schema_input)
                print(f"📋 Using inline JSON schema")
            else:
                # Treat as file path
                with open(args.schema, 'r') as f:
                    schema = json.load(f)
                print(f"📋 Using schema from file: {args.schema}")
        except json.JSONDecodeError:
            # If JSON parsing fails, try as file path
            try:
                with open(args.schema, 'r') as f:
                    schema = json.load(f)
                print(f"📋 Using schema from file: {args.schema}")
            except FileNotFoundError:
                print(f"❌ Error: Could not parse as JSON or find file: {args.schema}")
                return
        except FileNotFoundError:
            print(f"❌ Error: Schema file not found: {args.schema}")
            return
    elif args.schema_json:
        try:
            schema = json.loads(args.schema_json)
            print(f"📋 Using inline JSON schema from --schema-json")
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in --schema-json: {e}")
            return
    
    try:
        result, metadata = await extract_data_from_pdf(
            args.pdf_file,
            response_schema=schema,
            start_page=args.start_page,
            end_page=args.end_page,
            save_results=args.save,
            output_filename=args.output
        )
        
        print("\n🎉 Processing completed successfully!")
        
    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main()) 
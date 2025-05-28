"""
Core PDF processing functions for the Groq PDF Vision SDK
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
    """Load Groq API key from environment or emaillist.txt file."""
    # Try environment variable first
    api_key = os.environ.get("GROQ_API_KEY")
    if api_key:
        return api_key
    
    raise ValueError(
        "❌ Groq API key not found. Please set GROQ_API_KEY environment variable "
        "or add it to emaillist.txt file in format: 'GROQ API KEY - your_key_here'"
    )


def get_default_schema():
    """Get the comprehensive default schema for PDF extraction."""
    from .schema_helpers import create_base_schema
    return create_base_schema()


def auto_configure_processing(total_pages: int) -> Dict[str, Any]:
    """Automatically configure processing parameters based on PDF size."""
    if total_pages <= SMALL_PDF_THRESHOLD:  # <= 10 pages
        return {"batch_size": 2, "dpi": 200, "description": "Small PDF - High quality processing"}
    elif total_pages <= MEDIUM_PDF_THRESHOLD:  # 11-50 pages
        return {"batch_size": 3, "dpi": 150, "description": "Medium PDF - Balanced processing"}
    elif total_pages <= LARGE_PDF_THRESHOLD:  # 51-200 pages
        return {"batch_size": 4, "dpi": 150, "description": "Large PDF - Efficient batch processing"}
    else:  # > 200 pages
        return {"batch_size": 5, "dpi": 120, "description": "Enterprise PDF - Maximum batch efficiency"}


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
            elif "title" in field_name.lower():
                example[field_name] = "actual title from document"
            elif description:
                example[field_name] = f"actual {field_name} data"
            else:
                example[field_name] = f"actual_{field_name}"
        elif field_type == "integer":
            if "page" in field_name.lower():
                example[field_name] = 1
            else:
                example[field_name] = 0
        elif field_type == "number":
            example[field_name] = 0.0
        elif field_type == "boolean":
            example[field_name] = False  # Default to false for safer extraction
        elif field_type == "array":
            items_def = field_def.get("items", {})
            if items_def.get("type") == "string":
                # For table data, show the structure but emphasize real data
                if "header" in field_name.lower() or "row" in field_name.lower():
                    example[field_name] = ["actual_data_1", "actual_data_2"]
                else:
                    example[field_name] = ["actual_item_1", "actual_item_2"]
            elif items_def.get("type") == "object":
                # Handle nested objects
                nested_example = generate_example_from_schema(items_def)
                example[field_name] = [nested_example] if nested_example else []
            else:
                example[field_name] = []
        elif field_type == "object":
            example[field_name] = generate_example_from_schema(field_def)
    
    return example


async def process_batch_with_retry(
    client: AsyncGroq, images: List[str], schema: Dict[str, Any],
    batch_num: int, total_batches: int, page_numbers: List[int]
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """Process a batch of images with retry logic."""
    
    for attempt in range(MAX_RETRIES):
        try:
            # Generate example structure from the provided schema
            example_structure = generate_example_from_schema(schema)
            example_json = json.dumps({"pages": [example_structure]}, indent=2)
            
            # Create a more explicit prompt that uses the custom schema
            prompt_text = f"""Extract data from these PDF pages and return as a valid JSON object with a "pages" array.

IMPORTANT: Return EXACTLY this structure based on the provided schema:
{example_json}

Process these pages: {page_numbers}

CRITICAL INSTRUCTIONS:
1. DO NOT use placeholder or example data like "example_table_title", "example1", "example2"
2. Extract REAL data from the PDF pages
3. If a table exists but data cannot be extracted, use empty arrays [] for headers and rows
4. If no table exists, set contains_tables to false and tables_data to empty array

COMPREHENSIVE EXTRACTION INSTRUCTIONS:
1. TEXT CONTENT: Extract all actual text content according to the schema fields.

2. TABLE EXTRACTION: For each table found:
   - Extract the ACTUAL table title/caption (not "example_table_title")
   - Extract the REAL column headers from the table
   - Extract the ACTUAL row data from each row
   - If extraction fails, use empty arrays instead of placeholder text
   - Set contains_tables to true only if tables are actually found

3. VISUAL ELEMENTS: If the schema includes image-related fields, carefully analyze all visual elements including:
   - Charts and graphs (bar, line, pie, scatter, etc.)
   - Diagrams and flowcharts
   - Images and photographs
   - Logos and branding elements
   - Illustrations and drawings
   - Maps and technical drawings
   - Screenshots or interface elements

4. SCHEMA COMPLIANCE: Follow the exact field names and types specified in the schema.

5. DATA QUALITY: 
   - Use REAL data from the PDF, never placeholder text
   - If data cannot be extracted, use appropriate empty values (empty strings, empty arrays, false)
   - Ensure table headers and rows contain actual data or remain empty

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
            
            # Use json_object format with lower temperature for more consistent results
            response = await client.chat.completions.create(
                model=GROQ_MODEL_ID, 
                messages=messages,
                response_format={"type": "json_object"},
                temperature=0.05,  # Lower temperature for more consistent extraction
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
                    # Pad with empty results if needed using proper empty structure
                    while len(batch_results) < len(page_numbers):
                        page_num = page_numbers[len(batch_results)]
                        # Create proper empty result instead of example data
                        empty_result = {
                            "page_number": page_num,
                            "content": f"Partial processing for page {page_num}",
                            "custom_content": "",
                            "error": 0,
                            "name": f"Page {page_num}",
                            "result": f"Processed page {page_num}",
                            "wordings_and_terms": [],
                            "key_main_takeaways": [],
                            "primary_insights": [],
                            "explicit_sections": [],
                            "explicit_pages": [page_num],
                            "contains_tables": False,
                            "contains_images": False,
                            "image_descriptions": [],
                            "visual_summary": "",
                            "tables_data": []
                        }
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
                await asyncio.sleep(delay)
            else:
                empty_results = []
                for page_num in page_numbers:
                    # Create proper empty error result instead of example data
                    error_result = {
                        "page_number": page_num,
                        "content": f"Failed to process page {page_num}",
                        "custom_content": "",
                        "error": 1,
                        "name": f"Page {page_num}",
                        "result": f"Failed to process page {page_num}",
                        "wordings_and_terms": [],
                        "key_main_takeaways": [],
                        "primary_insights": [],
                        "explicit_sections": [],
                        "explicit_pages": [page_num],
                        "contains_tables": False,
                        "contains_images": False,
                        "image_descriptions": [],
                        "visual_summary": "",
                        "tables_data": []
                    }
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
                # For arrays, extend with unique items but exclude example data
                for item in field_value:
                    # Enhanced filtering for example/dummy data
                    if (item and item not in accumulated[field_name]):
                        # Skip obvious example/dummy data patterns
                        item_str = str(item).lower()
                        is_example_data = (
                            item_str.startswith('example') or
                            item_str.startswith('actual_') or
                            item_str in ['example1', 'example2', 'example_table_title', 'example summary'] or
                            'placeholder' in item_str or
                            item_str == 'actual title from document' or
                            item_str.startswith('actual_data_') or
                            item_str.startswith('actual_item_')
                        )
                        
                        # Special handling for tables_data to filter out empty/example tables
                        if field_name == 'tables_data' and isinstance(item, dict):
                            table_title = item.get('table_title', '').lower()
                            headers = item.get('headers', [])
                            rows = item.get('rows', [])
                            
                            # Skip if table has example data or is empty
                            has_real_data = (
                                table_title and 
                                not table_title.startswith('example') and
                                not table_title.startswith('actual_') and
                                table_title != 'actual title from document' and
                                (headers or rows)  # Has actual content
                            )
                            
                            if has_real_data:
                                accumulated[field_name].append(item)
                        elif not is_example_data:
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


async def extract_pdf_async(
    pdf_file_path: str,
    schema: Optional[Dict[str, Any]] = None,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
    save_results: bool = False,
    output_filename: Optional[str] = None,
    api_key: Optional[str] = None
) -> Tuple[Dict[str, Any], Dict[str, Any]]:
    """
    Extract data from PDF with automatic configuration and accumulated results (async).
    
    Args:
        pdf_file_path: Path to the PDF file
        schema: JSON schema for extraction (uses default if None)
        start_page: Start page number (1-indexed, optional)
        end_page: End page number (1-indexed, optional)
        progress_callback: Function for progress updates (message, current, total)
        save_results: Whether to save results to JSON file
        output_filename: Custom output filename (auto-generated if None)
        api_key: Groq API key (uses environment/file if None)
    
    Returns:
        Tuple of (extraction_results, processing_metadata)
    """
    
    if api_key:
        os.environ["GROQ_API_KEY"] = api_key
    
    api_key = load_api_key()
    
    # Use async context manager for proper cleanup
    async with AsyncGroq(api_key=api_key) as client:
        if schema is None:
            schema = get_default_schema()
        
        pdf = pdfium.PdfDocument(pdf_file_path)
        total_pages = len(pdf)
        pdf.close()
        
        if start_page is None:
            start_page = 1
        if end_page is None:
            end_page = total_pages
        
        pages_to_process = end_page - start_page + 1
        config = auto_configure_processing(total_pages)
        
        start_time = time.time()
        
        images = convert_pdf_to_images(pdf_file_path, config['dpi'], start_page, end_page)
        
        batch_size = config['batch_size']
        total_batches = (len(images) + batch_size - 1) // batch_size
        
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
            
            batch_b64_images = []
            for img in batch_images:
                b64_img = encode_image_to_base64(img, IMAGE_FORMAT)
                batch_b64_images.append(b64_img)
            
            batch_results, batch_usage = await process_batch_with_retry(
                client, batch_b64_images, schema, batch_num + 1, total_batches, batch_page_numbers
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
        
        return result, metadata


def extract_pdf(
    pdf_file_path: str,
    schema: Optional[Dict[str, Any]] = None,
    start_page: Optional[int] = None,
    end_page: Optional[int] = None,
    progress_callback: Optional[Callable[[str, int, int], None]] = None,
    save_results: bool = False,
    output_filename: Optional[str] = None,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    Extract data from PDF with automatic configuration (synchronous wrapper).
    
    Args:
        pdf_file_path: Path to the PDF file
        schema: JSON schema for extraction (uses default if None)
        start_page: Start page number (1-indexed, optional)
        end_page: End page number (1-indexed, optional)
        progress_callback: Function for progress updates (message, current, total)
        save_results: Whether to save results to JSON file
        output_filename: Custom output filename (auto-generated if None)
        api_key: Groq API key (uses environment/file if None)
    
    Returns:
        Dictionary containing extraction results and metadata
    """
    
    async def _extract():
        return await extract_pdf_async(
            pdf_file_path=pdf_file_path,
            schema=schema,
            start_page=start_page,
            end_page=end_page,
            progress_callback=progress_callback,
            save_results=save_results,
            output_filename=output_filename,
            api_key=api_key
        )
    
    # Always use asyncio.run for better event loop management
    result, metadata = asyncio.run(_extract())
    
    # Combine result and metadata for simpler synchronous API
    return {
        **result,
        "metadata": metadata
    } 
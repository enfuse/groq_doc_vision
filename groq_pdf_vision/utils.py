"""
Utility functions for the Groq PDF Vision SDK
"""

import json
import os
from typing import Dict, Any, Optional, Tuple
import pypdfium2 as pdfium


def validate_schema(schema: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate a JSON schema for PDF extraction.
    
    Args:
        schema: JSON schema dictionary to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        # Basic structure validation
        if not isinstance(schema, dict):
            return False, "Schema must be a dictionary"
        
        if schema.get("type") != "object":
            return False, "Schema type must be 'object'"
        
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            return False, "Schema properties must be a dictionary"
        
        # Check for required page_number field
        if "page_number" not in properties:
            return False, "Schema must include 'page_number' field for page tracking"
        
        page_number_field = properties["page_number"]
        if page_number_field.get("type") != "integer":
            return False, "page_number field must be of type 'integer'"
        
        # Validate each property
        for field_name, field_def in properties.items():
            if not isinstance(field_def, dict):
                return False, f"Field '{field_name}' definition must be a dictionary"
            
            field_type = field_def.get("type")
            if not field_type:
                return False, f"Field '{field_name}' must have a 'type' property"
            
            valid_types = ["string", "integer", "number", "boolean", "array", "object"]
            if field_type not in valid_types:
                return False, f"Field '{field_name}' has invalid type '{field_type}'. Must be one of: {valid_types}"
            
            # Validate array items
            if field_type == "array":
                items = field_def.get("items")
                if items and isinstance(items, dict):
                    items_type = items.get("type")
                    if items_type and items_type not in valid_types:
                        return False, f"Field '{field_name}' array items have invalid type '{items_type}'"
        
        return True, None
        
    except Exception as e:
        return False, f"Schema validation error: {str(e)}"


def estimate_processing_time(pdf_path: str, start_page: Optional[int] = None, end_page: Optional[int] = None) -> Dict[str, Any]:
    """
    Estimate processing time and cost for a PDF.
    
    Args:
        pdf_path: Path to the PDF file
        start_page: Start page number (1-indexed, optional)
        end_page: End page number (1-indexed, optional)
    
    Returns:
        Dictionary with time and cost estimates
    """
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        total_pages = len(pdf)
        pdf.close()
        
        if start_page is None:
            start_page = 1
        if end_page is None:
            end_page = total_pages
        
        pages_to_process = end_page - start_page + 1
        
        # Time estimates based on empirical data
        if pages_to_process <= 10:
            time_per_page = 3  # seconds
            description = "Small PDF - High quality processing"
        elif pages_to_process <= 50:
            time_per_page = 2.5  # seconds
            description = "Medium PDF - Balanced processing"
        elif pages_to_process <= 200:
            time_per_page = 2  # seconds
            description = "Large PDF - Efficient processing"
        else:
            time_per_page = 1.5  # seconds
            description = "Enterprise PDF - Memory optimized processing"
        
        estimated_time = pages_to_process * time_per_page
        
        # Cost estimates (based on average token usage)
        tokens_per_page = 3200  # Average from testing
        total_tokens = pages_to_process * tokens_per_page
        cost_per_token = 0.00002  # Groq pricing
        estimated_cost = total_tokens * cost_per_token
        
        return {
            "total_pages_in_pdf": total_pages,
            "pages_to_process": pages_to_process,
            "estimated_time_seconds": estimated_time,
            "estimated_time_formatted": format_duration(estimated_time),
            "estimated_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost,
            "processing_description": description,
            "cost_per_page": estimated_cost / pages_to_process
        }
        
    except Exception as e:
        return {
            "error": f"Could not estimate processing time: {str(e)}"
        }


def estimate_cost(pages: int, tokens_per_page: int = 3200) -> Dict[str, float]:
    """
    Estimate processing cost for a given number of pages.
    
    Args:
        pages: Number of pages to process
        tokens_per_page: Average tokens per page (default from testing)
    
    Returns:
        Dictionary with cost breakdown
    """
    total_tokens = pages * tokens_per_page
    cost_per_token = 0.00002  # Groq pricing
    total_cost = total_tokens * cost_per_token
    
    return {
        "pages": pages,
        "tokens_per_page": tokens_per_page,
        "total_tokens": total_tokens,
        "cost_per_token": cost_per_token,
        "total_cost_usd": total_cost,
        "cost_per_page": total_cost / pages
    }


def format_duration(seconds: float) -> str:
    """
    Format duration in seconds to human-readable string.
    
    Args:
        seconds: Duration in seconds
    
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f} minutes"
    else:
        hours = seconds / 3600
        return f"{hours:.1f} hours"


def load_schema_from_file(schema_path: str) -> Dict[str, Any]:
    """
    Load a JSON schema from a file.
    
    Args:
        schema_path: Path to the JSON schema file
    
    Returns:
        Schema dictionary
    
    Raises:
        FileNotFoundError: If schema file doesn't exist
        json.JSONDecodeError: If schema file contains invalid JSON
    """
    if not os.path.exists(schema_path):
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema = json.load(f)
    
    # Validate the loaded schema
    is_valid, error_msg = validate_schema(schema)
    if not is_valid:
        raise ValueError(f"Invalid schema in {schema_path}: {error_msg}")
    
    return schema


def save_schema_to_file(schema: Dict[str, Any], output_path: str) -> None:
    """
    Save a schema dictionary to a JSON file.
    
    Args:
        schema: Schema dictionary to save
        output_path: Path where to save the schema file
    
    Raises:
        ValueError: If schema is invalid
    """
    # Validate schema before saving
    is_valid, error_msg = validate_schema(schema)
    if not is_valid:
        raise ValueError(f"Cannot save invalid schema: {error_msg}")
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(schema, f, indent=2, ensure_ascii=False)


def get_pdf_info(pdf_path: str) -> Dict[str, Any]:
    """
    Get basic information about a PDF file.
    
    Args:
        pdf_path: Path to the PDF file
    
    Returns:
        Dictionary with PDF information
    """
    try:
        pdf = pdfium.PdfDocument(pdf_path)
        total_pages = len(pdf)
        
        # Get file size
        file_size = os.path.getsize(pdf_path)
        file_size_mb = file_size / (1024 * 1024)
        
        pdf.close()
        
        return {
            "file_path": pdf_path,
            "file_size_bytes": file_size,
            "file_size_mb": round(file_size_mb, 2),
            "total_pages": total_pages,
            "can_process": True
        }
        
    except Exception as e:
        return {
            "file_path": pdf_path,
            "error": str(e),
            "can_process": False
        }


def create_progress_callback(verbose: bool = True):
    """
    Create a progress callback function for PDF processing.
    
    Args:
        verbose: Whether to print detailed progress information
    
    Returns:
        Progress callback function
    """
    def progress_callback(message: str, current: int, total: int):
        if verbose:
            percentage = (current / total) * 100
            print(f"Progress: {percentage:.1f}% ({current}/{total}) - {message}")
    
    return progress_callback


def merge_schemas(base_schema: Dict[str, Any], additional_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge additional fields into a base schema.
    
    Args:
        base_schema: Base schema to extend
        additional_fields: Additional field definitions to add
    
    Returns:
        Merged schema dictionary
    """
    merged_schema = base_schema.copy()
    
    if "properties" not in merged_schema:
        merged_schema["properties"] = {}
    
    merged_schema["properties"].update(additional_fields)
    
    # Validate the merged schema
    is_valid, error_msg = validate_schema(merged_schema)
    if not is_valid:
        raise ValueError(f"Merged schema is invalid: {error_msg}")
    
    return merged_schema


def extract_schema_from_example(example_output: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a schema from an example output structure.
    
    Args:
        example_output: Example output dictionary
    
    Returns:
        Generated schema dictionary
    """
    def infer_type(value):
        if isinstance(value, str):
            return "string"
        elif isinstance(value, int):
            return "integer"
        elif isinstance(value, float):
            return "number"
        elif isinstance(value, bool):
            return "boolean"
        elif isinstance(value, list):
            return "array"
        elif isinstance(value, dict):
            return "object"
        else:
            return "string"
    
    properties = {}
    
    for field_name, field_value in example_output.items():
        field_type = infer_type(field_value)
        field_def = {"type": field_type}
        
        if field_type == "array" and field_value:
            # Infer array item type from first element
            first_item = field_value[0]
            item_type = infer_type(first_item)
            field_def["items"] = {"type": item_type}
            
            if item_type == "object" and isinstance(first_item, dict):
                # Recursively generate schema for object items
                field_def["items"] = extract_schema_from_example(first_item)
        
        elif field_type == "object":
            # Recursively generate schema for nested objects
            field_def = extract_schema_from_example(field_value)
        
        properties[field_name] = field_def
    
    schema = {
        "type": "object",
        "properties": properties
    }
    
    # Ensure page_number is included
    if "page_number" not in properties:
        schema["properties"]["page_number"] = {"type": "integer", "description": "Page number (1-indexed)"}
    
    return schema 
"""
Schema building helpers for PDF extraction
"""

from typing import Dict, Any, List, Optional


def create_base_schema(
    include_images: bool = True,
    include_tables: bool = True,
    include_visual_analysis: bool = True
) -> Dict[str, Any]:
    """
    Create a comprehensive base schema that works for most documents.
    
    This is the recommended starting point for most use cases.
    You can extend it with custom fields as needed.
    
    Args:
        include_images: Whether to include image analysis
        include_tables: Whether to include table extraction
        include_visual_analysis: Whether to include visual element analysis
    
    Returns:
        JSON schema dictionary
    """
    schema = {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer", "description": "Page number (1-indexed)"},
            "content": {"type": "string", "description": "Main text content from the page"},
            "summary": {"type": "string", "description": "Brief summary of the page content"},
            "key_points": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Main points and takeaways from the page"
            }
        },
        "required": ["page_number", "content"]
    }
    
    if include_images:
        schema["properties"]["contains_images"] = {
            "type": "boolean", 
            "description": "Whether page contains images, charts, or diagrams"
        }
        schema["properties"]["image_descriptions"] = {
            "type": "array",
            "description": "Descriptions of visual elements",
            "items": {
                "type": "object",
                "properties": {
                    "image_type": {"type": "string", "description": "Type of visual element"},
                    "description": {"type": "string", "description": "Detailed description"},
                    "location": {"type": "string", "description": "Location on page"}
                }
            }
        }
    
    if include_tables:
        schema["properties"]["contains_tables"] = {
            "type": "boolean", 
            "description": "Whether page contains tables"
        }
        schema["properties"]["tables_data"] = {
            "type": "array",
            "description": "Extracted table data",
            "items": {
                "type": "object",
                "properties": {
                    "table_title": {"type": "string"},
                    "headers": {"type": "array", "items": {"type": "string"}},
                    "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}
                }
            }
        }
    
    if include_visual_analysis:
        schema["properties"]["visual_summary"] = {
            "type": "string", 
            "description": "Overall summary of visual elements on the page"
        }
    
    return schema


def add_custom_fields(base_schema: Dict[str, Any], custom_fields: Dict[str, Any]) -> Dict[str, Any]:
    """
    Add custom fields to an existing schema.
    
    Args:
        base_schema: Base schema to extend
        custom_fields: Dictionary of custom field definitions
    
    Returns:
        Extended schema
    """
    extended_schema = base_schema.copy()
    extended_schema["properties"].update(custom_fields)
    return extended_schema


def create_entity_extraction_fields(entity_types: List[str]) -> Dict[str, Any]:
    """
    Helper to create entity extraction fields for any domain.
    
    Args:
        entity_types: List of entity types to extract
    
    Returns:
        Dictionary of entity extraction fields
    """
    return {
        "entities": {
            "type": "array",
            "description": f"Named entities found: {', '.join(entity_types)}",
            "items": {
                "type": "object",
                "properties": {
                    "name": {"type": "string", "description": "Entity name"},
                    "type": {"type": "string", "description": f"Entity type: {', '.join(entity_types)}"},
                    "context": {"type": "string", "description": "Context where entity appears"}
                }
            }
        }
    }


def create_list_field(field_name: str, description: str) -> Dict[str, Any]:
    """
    Helper to create a list field for extracting arrays of items.
    
    Args:
        field_name: Name of the field
        description: Description of what to extract
    
    Returns:
        Field definition
    """
    return {
        field_name: {
            "type": "array",
            "items": {"type": "string"},
            "description": description
        }
    }


def create_object_field(field_name: str, properties: Dict[str, Any], description: str) -> Dict[str, Any]:
    """
    Helper to create a structured object field.
    
    Args:
        field_name: Name of the field
        properties: Object properties
        description: Description of the object
    
    Returns:
        Field definition
    """
    return {
        field_name: {
            "type": "object",
            "properties": properties,
            "description": description
        }
    }


# Example usage functions for documentation
def example_financial_extraction():
    """Example: How to create a schema for financial documents"""
    base = create_base_schema()
    
    financial_fields = {
        "financial_figures": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Revenue, profit, costs, and other financial amounts"
        },
        "time_periods": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Fiscal periods, quarters, years mentioned"
        },
        "companies_mentioned": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Company names and organizations"
        }
    }
    
    return add_custom_fields(base, financial_fields)


def example_research_extraction():
    """Example: How to create a schema for research documents"""
    base = create_base_schema()
    
    research_fields = {
        "methodology": {
            "type": "string",
            "description": "Research methodology described"
        },
        "findings": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Key findings and results"
        },
        "citations": {
            "type": "array",
            "items": {"type": "string"},
            "description": "Citations and references"
        }
    }
    
    return add_custom_fields(base, research_fields)


def example_custom_extraction():
    """Example: How to create a completely custom schema"""
    base = create_base_schema(include_images=False, include_tables=False)
    
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
        },
        "contact_info": {
            "type": "object",
            "properties": {
                "emails": {"type": "array", "items": {"type": "string"}},
                "phones": {"type": "array", "items": {"type": "string"}},
                "addresses": {"type": "array", "items": {"type": "string"}}
            },
            "description": "Contact information found"
        }
    }
    
    return add_custom_fields(base, custom_fields) 
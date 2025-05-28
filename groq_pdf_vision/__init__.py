"""
Groq PDF Vision Extraction SDK

A comprehensive Python SDK for extracting data from PDF documents using Groq's vision models
with intelligent automatic processing, image analysis, and custom schema support.

Key Features:
- Pure Python implementation with no system dependencies
- Intelligent auto-scaling for any PDF size
- Image description and visual analysis
- Page-level tracking for all extracted data
- High reliability with automatic retry mechanisms and graceful error handling
- Custom schema support for domain-specific extraction
- Both synchronous and asynchronous APIs

Example Usage:
    import asyncio
    from groq_pdf_vision import extract_pdf, extract_pdf_async
    
    # Synchronous API
    result = extract_pdf("document.pdf", save_results=True)
    
    # Asynchronous API
    async def process():
        result, metadata = await extract_pdf_async("document.pdf")
        return result
    
    # Custom schema
    schema = {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer"},
            "content": {"type": "string"},
            "summary": {"type": "string"}
        }
    }
    result = extract_pdf("document.pdf", schema=schema)
"""

__version__ = "1.0.0"
__author__ = "SDAIA Team"
__email__ = "contact@sdaia.gov.sa"

# Import main functions
from .core import (
    extract_pdf_async,
    extract_pdf,
    get_default_schema,
    auto_configure_processing,
)

from .schema_helpers import (
    create_base_schema,
    add_custom_fields,
    create_entity_extraction_fields,
    create_list_field,
    create_object_field,
)

from .utils import (
    validate_schema,
    estimate_processing_time,
    estimate_cost,
)

# Main exports
__all__ = [
    # Core functions
    "extract_pdf_async",
    "extract_pdf", 
    "get_default_schema",
    "auto_configure_processing",
    
    # Schema helpers
    "create_base_schema",
    "add_custom_fields",
    "create_entity_extraction_fields",
    "create_list_field",
    "create_object_field",
    
    # Utilities
    "validate_schema",
    "estimate_processing_time",
    "estimate_cost",
    
    # Package info
    "__version__",
    "__author__",
    "__email__",
] 
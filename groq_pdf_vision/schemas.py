"""
Schema helper functions for common PDF extraction patterns
"""

from typing import Dict, Any, List, Optional


def create_simple_schema(
    include_images: bool = True,
    include_tables: bool = True,
    custom_fields: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Create a simple schema for basic PDF extraction.
    
    Args:
        include_images: Whether to include image analysis fields
        include_tables: Whether to include table extraction fields
        custom_fields: Additional custom fields to include
    
    Returns:
        JSON schema dictionary
    """
    schema = {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer", "description": "Page number (1-indexed)"},
            "content": {"type": "string", "description": "Main text content from the page"},
            "summary": {"type": "string", "description": "Brief summary of the page content"}
        },
        "required": ["page_number", "content"]
    }
    
    if include_images:
        schema["properties"]["contains_images"] = {"type": "boolean", "description": "Whether page contains images"}
        schema["properties"]["image_descriptions"] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "image_type": {"type": "string"},
                    "description": {"type": "string"},
                    "location": {"type": "string"}
                }
            }
        }
    
    if include_tables:
        schema["properties"]["contains_tables"] = {"type": "boolean", "description": "Whether page contains tables"}
        schema["properties"]["tables_data"] = {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "table_title": {"type": "string"},
                    "headers": {"type": "array", "items": {"type": "string"}},
                    "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}}
                }
            }
        }
    
    if custom_fields:
        schema["properties"].update(custom_fields)
    
    return schema


def create_entity_extraction_schema(
    entity_types: Optional[List[str]] = None,
    include_context: bool = True
) -> Dict[str, Any]:
    """
    Create a schema focused on entity extraction.
    
    Args:
        entity_types: List of entity types to extract (person, organization, location, etc.)
        include_context: Whether to include context for each entity
    
    Returns:
        JSON schema dictionary
    """
    if entity_types is None:
        entity_types = ["person", "organization", "location", "date", "money", "product"]
    
    entity_properties = {
        "name": {"type": "string", "description": "Entity name"},
        "type": {"type": "string", "description": f"Entity type: {', '.join(entity_types)}"}
    }
    
    if include_context:
        entity_properties["context"] = {"type": "string", "description": "Context where entity appears"}
    
    schema = {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer", "description": "Page number (1-indexed)"},
            "content": {"type": "string", "description": "Main text content from the page"},
            "entities": {
                "type": "array",
                "description": "Named entities found on the page",
                "items": {
                    "type": "object",
                    "properties": entity_properties
                }
            },
            "entity_summary": {"type": "string", "description": "Summary of key entities mentioned"}
        },
        "required": ["page_number", "content", "entities"]
    }
    
    return schema


def create_financial_schema() -> Dict[str, Any]:
    """
    Create a schema optimized for financial document extraction.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer", "description": "Page number (1-indexed)"},
            "content": {"type": "string", "description": "Main text content from the page"},
            "document_type": {"type": "string", "description": "Type of financial document"},
            "financial_figures": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Revenue, profit, costs, and other financial amounts mentioned"
            },
            "key_metrics": {
                "type": "array", 
                "items": {"type": "string"},
                "description": "KPIs, ratios, and performance metrics"
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
            },
            "contains_tables": {"type": "boolean", "description": "Whether page contains financial tables"},
            "tables_data": {
                "type": "array",
                "description": "Financial tables and data",
                "items": {
                    "type": "object",
                    "properties": {
                        "table_title": {"type": "string"},
                        "headers": {"type": "array", "items": {"type": "string"}},
                        "rows": {"type": "array", "items": {"type": "array", "items": {"type": "string"}}},
                        "financial_category": {"type": "string", "description": "Type of financial data"}
                    }
                }
            },
            "risk_factors": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Risk factors and warnings mentioned"
            }
        },
        "required": ["page_number", "content", "contains_tables"]
    }


def create_technical_schema() -> Dict[str, Any]:
    """
    Create a schema optimized for technical documentation.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer", "description": "Page number (1-indexed)"},
            "content": {"type": "string", "description": "Main text content from the page"},
            "document_type": {"type": "string", "description": "Type of technical document"},
            "system_components": {
                "type": "array",
                "items": {"type": "string"},
                "description": "System components, modules, and technologies mentioned"
            },
            "configuration_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Configuration and setup instructions"
            },
            "api_endpoints": {
                "type": "array",
                "items": {"type": "string"},
                "description": "API endpoints and URLs mentioned"
            },
            "code_examples": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Code snippets and examples"
            },
            "error_codes": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Error codes and troubleshooting information"
            },
            "version_numbers": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Software versions and release numbers"
            },
            "contains_diagrams": {"type": "boolean", "description": "Whether page contains technical diagrams"},
            "diagram_descriptions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "diagram_type": {"type": "string", "description": "Type of diagram (flowchart, architecture, etc.)"},
                        "description": {"type": "string", "description": "Description of the diagram"},
                        "components": {"type": "array", "items": {"type": "string"}, "description": "Components shown in diagram"}
                    }
                }
            }
        },
        "required": ["page_number", "content", "contains_diagrams"]
    }


def create_academic_schema() -> Dict[str, Any]:
    """
    Create a schema optimized for academic papers and research documents.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer", "description": "Page number (1-indexed)"},
            "content": {"type": "string", "description": "Main text content from the page"},
            "document_section": {"type": "string", "description": "Section of the paper (abstract, introduction, methodology, etc.)"},
            "research_methods": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Research methodologies and approaches mentioned"
            },
            "findings": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Key findings and results"
            },
            "citations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Citations and references mentioned"
            },
            "statistical_data": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Statistical data, p-values, confidence intervals"
            },
            "hypothesis": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Hypotheses and research questions"
            },
            "conclusions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Conclusions and implications"
            },
            "keywords": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Academic keywords and terminology"
            },
            "contains_figures": {"type": "boolean", "description": "Whether page contains figures or charts"},
            "figure_descriptions": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "figure_type": {"type": "string", "description": "Type of figure (chart, graph, diagram, etc.)"},
                        "description": {"type": "string", "description": "Description of the figure"},
                        "data_type": {"type": "string", "description": "Type of data shown"}
                    }
                }
            }
        },
        "required": ["page_number", "content", "contains_figures"]
    }


def create_legal_schema() -> Dict[str, Any]:
    """
    Create a schema optimized for legal documents.
    
    Returns:
        JSON schema dictionary
    """
    return {
        "type": "object",
        "properties": {
            "page_number": {"type": "integer", "description": "Page number (1-indexed)"},
            "content": {"type": "string", "description": "Main text content from the page"},
            "document_type": {"type": "string", "description": "Type of legal document"},
            "parties_involved": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Parties, entities, and individuals mentioned"
            },
            "legal_terms": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Legal terminology and concepts"
            },
            "important_dates": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Dates, deadlines, and time periods"
            },
            "obligations": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Obligations and responsibilities"
            },
            "rights": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Rights and entitlements"
            },
            "penalties": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Penalties, fines, and consequences"
            },
            "monetary_amounts": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Monetary amounts, fees, and financial terms"
            },
            "jurisdiction": {"type": "string", "description": "Legal jurisdiction or governing law"}
        },
        "required": ["page_number", "content"]
    } 
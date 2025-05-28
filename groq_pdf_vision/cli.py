"""
Command Line Interface for the Groq PDF Vision SDK
"""

import argparse
import asyncio
import json
import sys
from typing import Optional

from .core import extract_pdf_async
from .utils import (
    validate_schema, 
    estimate_processing_time, 
    get_pdf_info,
    create_progress_callback
)
from .schemas import (
    create_simple_schema,
    create_entity_extraction_schema,
    create_financial_schema,
    create_technical_schema,
    create_academic_schema,
    create_legal_schema
)


def parse_schema_argument(schema_arg: str) -> dict:
    """Parse schema argument which can be a file path or inline JSON."""
    try:
        # Check if it looks like JSON (starts with { or [)
        schema_input = schema_arg.strip()
        if schema_input.startswith('{') or schema_input.startswith('['):
            schema = json.loads(schema_input)
            print(f"📋 Using inline JSON schema")
            return schema
        else:
            # Treat as file path
            with open(schema_arg, 'r') as f:
                schema = json.load(f)
            print(f"📋 Using schema from file: {schema_arg}")
            return schema
    except json.JSONDecodeError:
        # If JSON parsing fails, try as file path
        try:
            with open(schema_arg, 'r') as f:
                schema = json.load(f)
            print(f"📋 Using schema from file: {schema_arg}")
            return schema
        except FileNotFoundError:
            print(f"❌ Error: Could not parse as JSON or find file: {schema_arg}")
            sys.exit(1)
    except FileNotFoundError:
        print(f"❌ Error: Schema file not found: {schema_arg}")
        sys.exit(1)


def get_predefined_schema(schema_name: str) -> Optional[dict]:
    """Get a predefined schema by name."""
    schemas = {
        "simple": create_simple_schema,
        "entity": create_entity_extraction_schema,
        "financial": create_financial_schema,
        "technical": create_technical_schema,
        "academic": create_academic_schema,
        "legal": create_legal_schema
    }
    
    if schema_name in schemas:
        return schemas[schema_name]()
    return None


async def main():
    """Main CLI function."""
    parser = argparse.ArgumentParser(
        description="Groq PDF Vision Extraction SDK - Extract data from PDF documents with AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process entire PDF with default schema
  groq-pdf document.pdf --save

  # Process specific pages
  groq-pdf document.pdf --start-page 1 --end-page 10 --save

  # Use custom schema file
  groq-pdf document.pdf --schema my_schema.json --save

  # Use inline JSON schema
  groq-pdf document.pdf --schema '{"type":"object","properties":{"page_number":{"type":"integer"},"content":{"type":"string"}}}' --save

  # Use predefined schema
  groq-pdf document.pdf --schema-preset financial --save

  # Get PDF info and estimates
  groq-pdf document.pdf --info-only

  # Validate a schema file
  groq-pdf --validate-schema my_schema.json

Schema Presets:
  simple     - Basic text and image extraction
  entity     - Named entity extraction
  financial  - Financial document analysis
  technical  - Technical documentation
  academic   - Academic paper analysis
  legal      - Legal document analysis
        """
    )
    
    # Main arguments
    parser.add_argument("pdf_file", nargs='?', help="Path to PDF file")
    parser.add_argument("--start-page", type=int, help="Start page number (1-indexed)")
    parser.add_argument("--end-page", type=int, help="End page number (1-indexed)")
    parser.add_argument("--save", action="store_true", help="Save results to JSON file")
    parser.add_argument("--output", help="Output filename for results")
    parser.add_argument("--api-key", help="Groq API key (overrides environment/file)")
    
    # Schema options
    schema_group = parser.add_mutually_exclusive_group()
    schema_group.add_argument("--schema", help="Path to custom JSON schema file OR inline JSON schema string")
    schema_group.add_argument("--schema-json", help="Inline JSON schema string (alternative to --schema)")
    schema_group.add_argument("--schema-preset", choices=["simple", "entity", "financial", "technical", "academic", "legal"], 
                             help="Use a predefined schema preset")
    
    # Utility options
    parser.add_argument("--info-only", action="store_true", help="Show PDF info and processing estimates only")
    parser.add_argument("--validate-schema", help="Validate a schema file and exit")
    parser.add_argument("--quiet", action="store_true", help="Suppress progress output")
    parser.add_argument("--version", action="version", version="groq-pdf-vision 1.0.0")
    
    args = parser.parse_args()
    
    # Handle schema validation
    if args.validate_schema:
        try:
            with open(args.validate_schema, 'r') as f:
                schema = json.load(f)
            
            is_valid, error_msg = validate_schema(schema)
            if is_valid:
                print(f"✅ Schema is valid: {args.validate_schema}")
                sys.exit(0)
            else:
                print(f"❌ Schema is invalid: {error_msg}")
                sys.exit(1)
        except Exception as e:
            print(f"❌ Error validating schema: {e}")
            sys.exit(1)
    
    # Require PDF file for other operations
    if not args.pdf_file:
        parser.error("PDF file is required (unless using --validate-schema)")
    
    # Handle info-only mode
    if args.info_only:
        print(f"📄 Analyzing PDF: {args.pdf_file}")
        
        # Get PDF info
        pdf_info = get_pdf_info(args.pdf_file)
        if not pdf_info.get("can_process"):
            print(f"❌ Cannot process PDF: {pdf_info.get('error')}")
            sys.exit(1)
        
        print(f"   File size: {pdf_info['file_size_mb']} MB")
        print(f"   Total pages: {pdf_info['total_pages']}")
        
        # Get processing estimates
        estimates = estimate_processing_time(args.pdf_file, args.start_page, args.end_page)
        if "error" in estimates:
            print(f"❌ Error getting estimates: {estimates['error']}")
            sys.exit(1)
        
        print(f"\n📊 Processing Estimates:")
        print(f"   Pages to process: {estimates['pages_to_process']}")
        print(f"   Estimated time: {estimates['estimated_time_formatted']}")
        print(f"   Estimated cost: ${estimates['estimated_cost_usd']:.4f}")
        print(f"   Cost per page: ${estimates['cost_per_page']:.4f}")
        print(f"   Processing mode: {estimates['processing_description']}")
        
        sys.exit(0)
    
    # Determine schema to use
    schema = None
    if args.schema:
        schema = parse_schema_argument(args.schema)
    elif args.schema_json:
        try:
            schema = json.loads(args.schema_json)
            print(f"📋 Using inline JSON schema from --schema-json")
        except json.JSONDecodeError as e:
            print(f"❌ Error: Invalid JSON in --schema-json: {e}")
            sys.exit(1)
    elif args.schema_preset:
        schema = get_predefined_schema(args.schema_preset)
        print(f"📋 Using predefined schema: {args.schema_preset}")
    
    # Validate schema if provided
    if schema:
        is_valid, error_msg = validate_schema(schema)
        if not is_valid:
            print(f"❌ Error: Invalid schema: {error_msg}")
            sys.exit(1)
    
    # Create progress callback
    progress_callback = None if args.quiet else create_progress_callback(verbose=True)
    
    try:
        print(f"🚀 Starting PDF processing...")
        
        result, metadata = await extract_pdf_async(
            pdf_file_path=args.pdf_file,
            schema=schema,
            start_page=args.start_page,
            end_page=args.end_page,
            progress_callback=progress_callback,
            save_results=args.save,
            output_filename=args.output,
            api_key=args.api_key
        )
        
        print(f"\n🎉 Processing completed successfully!")
        
        # Print summary
        acc_data = result["accumulated_data"]
        stats = result["processing_stats"]
        
        print(f"\n📊 Extraction Summary:")
        print(f"   Pages processed: {stats['total_pages']}")
        print(f"   Processing time: {stats['processing_time_seconds']:.2f} seconds")
        print(f"   Content length: {len(acc_data.get('content', ''))} characters")
        
        if 'tables_data' in acc_data:
            print(f"   Tables found: {len(acc_data['tables_data'])}")
        if 'image_descriptions' in acc_data:
            print(f"   Images found: {len(acc_data['image_descriptions'])}")
        if 'key_main_takeaways' in acc_data:
            print(f"   Key takeaways: {len(acc_data['key_main_takeaways'])}")
        
        if metadata['token_usage']['total_tokens'] > 0:
            cost_estimate = metadata['token_usage']['total_tokens'] * 0.00002
            print(f"   Token usage: {metadata['token_usage']['total_tokens']} tokens (~${cost_estimate:.4f})")
        
        if args.save:
            output_file = args.output or f"{args.pdf_file.replace('.pdf', '')}_extraction_results.json"
            print(f"   Results saved to: {output_file}")
        
    except KeyboardInterrupt:
        print(f"\n⚠️  Processing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Processing failed: {e}")
        import traceback
        if not args.quiet:
            traceback.print_exc()
        sys.exit(1)


def cli_main():
    """Entry point for the CLI."""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(f"\n⚠️  Interrupted by user")
        sys.exit(1)


if __name__ == "__main__":
    cli_main() 
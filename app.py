#!/usr/bin/env python3
"""
Streamlit Web UI for Groq PDF Vision Extraction
Simple drag-and-drop interface for processing PDFs using the core groq_pdf_vision module.
"""

import streamlit as st
import asyncio
import tempfile
import os
import json
import time
from datetime import datetime
import sys

# Import from the core module
from groq_pdf_vision import extract_pdf_async, get_default_schema
from groq_pdf_vision.schema_helpers import (
    create_base_schema, 
    add_custom_fields,
    create_entity_extraction_fields,
    create_list_field,
    create_object_field
)

# Page configuration
st.set_page_config(
    page_title="PDF Vision Extraction POC",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    /* Ensure the entire app container respects dark mode */
    html[data-theme="dark"] div[data-testid="stAppViewContainer"] {
        background: var(--secondary-background-color, #0E1117) !important;
    }
    html[data-theme="dark"] div[data-testid="stHeader"] {
        background-color: var(--secondary-background-color, #0E1117) !important;
    }

    /* General Streamlit fixes to remove top space above our header */
    header.stAppHeader {
        background-color: transparent !important;
    }
    section.stMain .block-container {
        padding-top: 0rem !important;
    }
    
    /* Default (Light Mode) styles for our custom header */
    .main-header {
        padding: 2rem 0; /* This top padding is where the logo sits */
        border-bottom: 2px solid #f0f2f6; /* Light border for light theme */
        margin-bottom: 2rem;
        margin-top: 0rem !important; /* Ensure it's at the top */
        background: linear-gradient(135deg, #f8f9fa 0%, #ffffff 100%); /* Light gradient for light theme */
    }
    .powered-by {
        font-size: 0.8rem;
        color: #666; /* Dark text for light theme */
        margin-bottom: 1rem;
        font-style: italic;
    }

    /* Dark Mode Overrides for our custom header */
    html[data-theme="dark"] .main-header {
        background: var(--secondary-background-color, #0E1117); /* Use Streamlit's dark theme secondary bg */
        border-bottom-color: var(--border-color, #31333F);       /* Use Streamlit's dark theme border color */
    }
    html[data-theme="dark"] .powered-by {
        color: var(--text-color, #FAFAFA); /* Use Streamlit's dark theme text color */
    }

    /* Other styles remain the same */
    .upload-section {
        border: 2px dashed #cccccc;
        border-radius: 10px;
        padding: 2rem;
        text-align: center;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        border: 1px solid #c3e6cb;
        border-radius: 5px;
        padding: 1rem;
        margin: 1rem 0;
    }
    .metric-card {
        background-color: #f8f9fa;
        border-radius: 5px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

def check_api_key():
    """Check if API key is available"""
    if os.environ.get("GROQ_API_KEY"):
        return True
    else:
        st.error("❌ Groq API key not found. Please set GROQ_API_KEY environment variable")
        st.info("💡 Please ensure your Groq API key is set as environment variable `GROQ_API_KEY`")
        return False

def format_processing_time(seconds):
    """Format processing time in a readable format"""
    if seconds < 60:
        return f"{seconds:.1f} seconds"
    else:
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds:.1f}s"

def display_results(result, metadata):
    """Display the extraction results in a comprehensive format showing ALL data"""
    accumulated_data = result["accumulated_data"]
    processing_stats = result["processing_stats"]
    page_results = result["page_results"]
    
    # Processing Summary
    st.subheader("📊 Processing Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Pages Processed", 
            processing_stats["total_pages"],
            help="Total number of pages processed"
        )
    
    with col2:
        st.metric(
            "Processing Time", 
            format_processing_time(processing_stats["processing_time_seconds"]),
            help="Total time taken to process the PDF"
        )
    
    with col3:
        st.metric(
            "Tables Found", 
            len(accumulated_data.get("tables_data", [])),
            help="Number of tables extracted from the PDF"
        )
    
    with col4:
        cost_estimate = metadata["token_usage"]["total_tokens"] * 0.00002
        st.metric(
            "Estimated Cost", 
            f"${cost_estimate:.4f}",
            help=f"Based on {metadata['token_usage']['total_tokens']} tokens"
        )
    
    # Token Usage Details
    st.subheader("🔢 Token Usage")
    token_col1, token_col2, token_col3 = st.columns(3)
    
    with token_col1:
        st.metric("Prompt Tokens", metadata["token_usage"]["prompt_tokens"])
    with token_col2:
        st.metric("Completion Tokens", metadata["token_usage"]["completion_tokens"])
    with token_col3:
        st.metric("Total Tokens", metadata["token_usage"]["total_tokens"])
    
    # Content Overview
    st.subheader("📝 Full Document Content")
    content = accumulated_data.get("content", "")
    if content:
        with st.expander("📄 Complete Extracted Text", expanded=False):
            st.text_area(
                "Full Document Text", 
                content,
                height=300,
                disabled=True,
                label_visibility="collapsed"
            )
        st.caption(f"Total content length: {len(content):,} characters")
    
    # Key Insights - Show ALL
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 All Key Takeaways")
        takeaways = accumulated_data.get("key_main_takeaways", [])
        if takeaways:
            for i, takeaway in enumerate(takeaways, 1):
                st.write(f"{i}. {takeaway}")
        else:
            st.write("No key takeaways extracted")
    
    with col2:
        st.subheader("🔍 All Key Terms")
        terms = accumulated_data.get("wordings_and_terms", [])
        if terms:
            # Show all terms in a more organized way
            with st.expander(f"View All {len(terms)} Terms", expanded=True):
                # Display in chunks for better readability
                for i in range(0, len(terms), 5):
                    chunk = terms[i:i+5]
                    st.write(" • ".join(chunk))
        else:
            st.write("No key terms extracted")
    
    # ALL Tables - No Limits
    st.subheader("📊 All Extracted Tables")
    tables = accumulated_data.get("tables_data", [])
    if tables:
        st.write(f"**Total tables found: {len(tables)}**")
        for i, table in enumerate(tables, 1):
            # Get table title, handling both direct strings and object structure
            if isinstance(table, dict):
                table_title = table.get('table_title', f'Table {i}')
                # Skip obvious example/placeholder data
                if (table_title.lower().startswith('example') or 
                    table_title.lower().startswith('actual_') or
                    table_title.lower() == 'actual title from document'):
                    continue
                    
                with st.expander(f"Table {i}: {table_title}", expanded=False):
                    # Show table metadata
                    if 'page_number' in table:
                        st.caption(f"Found on page {table['page_number']}")
                    
                    # Show table summary if available
                    if table.get("summary") and not table["summary"].lower().startswith('example'):
                        st.write("**Summary:**", table["summary"])
                    
                    # Display table data
                    headers = table.get("headers", [])
                    rows = table.get("rows", [])
                    
                    if headers and rows:
                        # Filter out example data from headers and rows
                        clean_headers = [h for h in headers if not str(h).lower().startswith(('example', 'actual_data_'))]
                        clean_rows = []
                        
                        # Handle both array-based rows (list of lists) and object-based rows (list of dicts)
                        for row in rows:
                            if isinstance(row, list):
                                # Array-based row structure
                                clean_row = [cell for cell in row if not str(cell).lower().startswith(('example', 'actual_data_'))]
                                if clean_row:  # Only add if row has real data
                                    clean_rows.append(clean_row)
                            elif isinstance(row, dict):
                                # Object-based row structure - convert to array based on headers
                                clean_row = []
                                for header in clean_headers:
                                    # Try to find matching value for each header
                                    cell_value = ""
                                    for key, value in row.items():
                                        if key.lower() == header.lower() or header.lower() in key.lower():
                                            cell_value = str(value) if value else ""
                                            break
                                    clean_row.append(cell_value)
                                
                                # Check if row has any real data (not just empty strings)
                                if any(cell.strip() for cell in clean_row):
                                    clean_rows.append(clean_row)
                        
                        if clean_headers and clean_rows:
                            # Convert to DataFrame for better display
                            import pandas as pd
                            try:
                                # Ensure consistent column count
                                max_cols = max(len(clean_headers), max(len(row) for row in clean_rows) if clean_rows else 0)
                                
                                # Pad headers if needed
                                while len(clean_headers) < max_cols:
                                    clean_headers.append(f"Column {len(clean_headers) + 1}")
                                
                                # Pad rows if needed
                                for row in clean_rows:
                                    while len(row) < max_cols:
                                        row.append("")
                                
                                df = pd.DataFrame(clean_rows, columns=clean_headers[:max_cols])
                                st.dataframe(df, use_container_width=True)
                                
                                # Show row count info
                                st.caption(f"Displaying {len(clean_rows)} rows × {len(clean_headers)} columns")
                                
                            except Exception as e:
                                st.warning(f"Could not display as formatted table: {e}")
                                st.write("**Headers:**", clean_headers)
                                st.write("**Rows:**", clean_rows)
                        else:
                            st.write("Table structure detected but no data extracted")
                    elif table.get("table_content"):
                        # Fallback to raw table content
                        st.text_area("Table Content", table["table_content"], height=100, disabled=True)
                    else:
                        st.write("Table detected but no content extracted")
                        
                    # Show raw table data without nested expander - use details/collapsible section instead
                    st.write("**Raw Table Data (for debugging):**")
                    st.json(table)
            else:
                # Handle simple string table data
                table_str = str(table)
                if not table_str.lower().startswith(('example', 'actual_')):
                    with st.expander(f"Table {i}", expanded=False):
                        st.write(table_str)
    else:
        st.write("No tables found in the document")
    
    # ALL Images - Show Everything
    st.subheader("🖼️ All Image Descriptions")
    images = accumulated_data.get("image_descriptions", [])
    if images:
        st.write(f"**Total images found: {len(images)}**")
        for i, image in enumerate(images, 1):
            with st.expander(f"Image {i}: {image.get('image_type', 'Unknown type')}", expanded=False):
                if isinstance(image, dict):
                    # Show image metadata
                    if 'page_number' in image:
                        st.caption(f"Found on page {image['page_number']}")
                    
                    # Display description and details
                    if 'description' in image:
                        st.write("**Description:**", image['description'])
                    if 'location' in image:
                        st.write("**Location:**", image['location'])
                    if 'relevance' in image:
                        st.write("**Relevance:**", image['relevance'])
                    
                    # Show full image object directly (no nested expander)
                    st.write("**Raw Image Data:**")
                    st.json(image)
                else:
                    # Handle string descriptions
                    st.write(str(image))
    else:
        st.write("No images found in the document")
    
    # Entities (if available)
    entities = accumulated_data.get("entities", [])
    if entities:
        st.subheader("🏷️ All Extracted Entities")
        st.write(f"**Total entities found: {len(entities)}**")
        with st.expander("View All Entities", expanded=False):
            for i, entity in enumerate(entities, 1):
                st.write(f"{i}. {entity}")
    
    # Page-by-Page Analysis
    st.subheader("📄 Page-by-Page Analysis")
    if page_results:
        st.write(f"**Detailed results for all {len(page_results)} pages:**")
        
        # Summary statistics
        pages_with_images = sum(1 for page in page_results if page.get('image_descriptions'))
        pages_with_tables = sum(1 for page in page_results if page.get('tables_data'))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pages with Text", len([p for p in page_results if p.get('content', '').strip()]))
        with col2:
            st.metric("Pages with Images", pages_with_images)
        with col3:
            st.metric("Pages with Tables", pages_with_tables)
        
        # Individual page details
        for page in page_results:
            page_num = page.get('page_number', 'Unknown')
            content_preview = page.get('content', '')[:100]
            
            # Create summary for page
            page_summary = f"Page {page_num}"
            if page.get('image_descriptions'):
                page_summary += f" • {len(page['image_descriptions'])} images"
            if page.get('tables_data'):
                page_summary += f" • {len(page['tables_data'])} tables"
            if content_preview:
                page_summary += f" • {len(page.get('content', ''))} chars"
            
            with st.expander(page_summary, expanded=False):
                # Page content
                if page.get('content'):
                    st.text_area(
                        f"Content from Page {page_num}",
                        page['content'],
                        height=150,
                        disabled=True
                    )
                
                # Page images
                if page.get('image_descriptions'):
                    st.write("**Images on this page:**")
                    for img in page['image_descriptions']:
                        if isinstance(img, dict):
                            st.write(f"• {img.get('image_type', 'Image')}: {img.get('description', 'No description')}")
                        else:
                            st.write(f"• {str(img)}")
                
                # Page tables
                if page.get('tables_data'):
                    st.write("**Tables on this page:**")
                    for table in page['tables_data']:
                        if isinstance(table, dict) and table.get('table_title'):
                            st.write(f"• {table['table_title']}")
                        else:
                            st.write("• Table data found")
    
    # Visual Summary
    visual_summary = accumulated_data.get("visual_summary", "")
    if visual_summary:
        st.subheader("👁️ Visual Summary")
        st.write(visual_summary)
    
    # Download Results
    st.subheader("💾 Download Complete Results")
    
    # Prepare download data
    download_data = {
        "processing_metadata": metadata,
        "extraction_results": result
    }
    
    json_str = json.dumps(download_data, indent=2, ensure_ascii=False)
    
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 Download Full Results (JSON)",
            data=json_str,
            file_name=f"pdf_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            help="Download the complete extraction results as a JSON file"
        )
    
    with col2:
        st.metric("Download Size", f"{len(json_str):,} characters")

def build_custom_schema():
    """Interactive schema builder using SDK helpers"""
    st.subheader("🔧 Schema Configuration")
    
    schema_mode = st.radio(
        "Choose schema mode:",
        ["Example Schema (Recommended)", "Custom JSON", "Interactive Builder"],
        help="Example Schema provides comprehensive extraction. Custom JSON for advanced users. Interactive Builder for easy customization."
    )
    
    if schema_mode == "Example Schema (Recommended)":
        st.info("📋 Using the comprehensive example schema (recommended for most documents)")
        
        # Load the example schema from file
        try:
            with open('example_docs/example_custom_schema.json', 'r') as f:
                schema = json.load(f)
            
            # Show preview of example schema
            with st.expander("Preview Example Schema Fields", expanded=False):
                st.write("**Main fields included:**")
                st.write("• page_number, content, document_type")
                st.write("• key_findings, entities (with details)")
                st.write("• contains_tables, tables_data (with headers/rows)")
                st.write("• contains_images, image_descriptions (detailed)")
                st.write("• sentiment, confidence_score")
                st.write("• **Total fields:** {}".format(len(schema.get("properties", {}))))
                
                st.write("**Enhanced features:**")
                st.write("• Structured entity extraction with context")
                st.write("• Detailed table structure with summaries")
                st.write("• Rich image analysis with relevance scoring")
                st.write("• Document sentiment analysis")
                st.write("• Confidence scoring for quality assessment")
            
        except FileNotFoundError:
            st.warning("⚠️ Example schema file not found, falling back to SDK default")
            schema = get_default_schema()
        except json.JSONDecodeError:
            st.error("❌ Error reading example schema file, falling back to SDK default")
            schema = get_default_schema()
        
        return schema
    
    elif schema_mode == "Custom JSON":
        st.info("📝 Paste your custom JSON schema below")
        
        # Load example schema as the default in the text area
        try:
            with open('example_docs/example_custom_schema.json', 'r') as f:
                default_json = f.read()
        except:
            # Fallback if file not found
            default_json = '''{
  "type": "object",
  "properties": {
    "page_number": {"type": "integer"},
    "content": {"type": "string"},
    "summary": {"type": "string", "description": "Brief summary of the page"},
    "key_points": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Important points from this page"
    }
  },
  "required": ["page_number", "content"]
}'''
        
        schema_json = st.text_area(
            "JSON Schema",
            value=default_json,
            height=400,
            help="Paste your complete JSON schema here. Must include 'page_number' and 'content' fields."
        )
        
        try:
            schema = json.loads(schema_json)
            st.success("✅ Valid JSON schema")
            return schema
        except json.JSONDecodeError as e:
            st.error(f"❌ Invalid JSON: {e}")
            return None
    
    else:  # Interactive Builder
        st.info("🛠️ Build your schema step by step using SDK helpers")
        
        # Base schema options
        st.write("**1. Base Schema Configuration**")
        col1, col2 = st.columns(2)
        with col1:
            include_images = st.checkbox("Include image analysis", value=True)
        with col2:
            include_tables = st.checkbox("Include table extraction", value=True)
        
        # Start with base schema
        schema = create_base_schema(include_images=include_images, include_tables=include_tables)
        
        # Entity extraction
        st.write("**2. Entity Extraction (Optional)**")
        use_entities = st.checkbox("Add entity extraction fields")
        if use_entities:
            entity_types = st.multiselect(
                "Select entity types to extract:",
                ["person", "company", "organization", "location", "date", "money", "product", "technology"],
                default=["person", "company", "location"]
            )
            if entity_types:
                entity_fields = create_entity_extraction_fields(entity_types)
                schema = add_custom_fields(schema, entity_fields)
        
        # Custom fields
        st.write("**3. Custom Fields**")
        add_custom = st.checkbox("Add custom fields")
        if add_custom:
            num_fields = st.number_input("Number of custom fields", min_value=1, max_value=10, value=2)
            
            custom_fields = {}
            for i in range(num_fields):
                st.write(f"**Custom Field {i+1}:**")
                col1, col2, col3 = st.columns([2, 1, 2])
                
                with col1:
                    field_name = st.text_input(f"Field name", key=f"field_name_{i}", value=f"custom_field_{i+1}")
                
                with col2:
                    field_type = st.selectbox(
                        "Type", 
                        ["string", "array", "object"],
                        key=f"field_type_{i}"
                    )
                
                with col3:
                    description = st.text_input(f"Description", key=f"field_desc_{i}", value="Custom field description")
                
                # Build field definition
                if field_type == "string":
                    custom_fields[field_name] = {
                        "type": "string",
                        "description": description
                    }
                elif field_type == "array":
                    custom_fields[field_name] = {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": description
                    }
                elif field_type == "object":
                    custom_fields[field_name] = {
                        "type": "object",
                        "properties": {
                            "value": {"type": "string"},
                            "metadata": {"type": "string"}
                        },
                        "description": description
                    }
            
            if custom_fields:
                schema = add_custom_fields(schema, custom_fields)
        
        # Schema preview
        st.write("**4. Schema Preview**")
        with st.expander("View Generated Schema", expanded=False):
            st.json(schema)
        
        # Field count summary
        field_count = len(schema.get("properties", {}))
        st.success(f"✅ Schema built with {field_count} fields")
        
        return schema

async def process_pdf_async(temp_path, start_page=None, end_page=None, progress_callback=None, schema=None):
    """Process PDF asynchronously with optional progress callback and custom schema"""
    return await extract_pdf_async(
        temp_path,
        schema=schema,
        start_page=start_page,
        end_page=end_page,
        save_results=False,
        progress_callback=progress_callback
    )

def create_progress_callback(progress_bar, status_text, show_terminal_logs=True):
    """Create a progress callback that updates both Streamlit UI and terminal logs"""
    def progress_callback(message, current, total):
        # Update Streamlit progress bar
        progress_percent = current / total
        progress_bar.progress(progress_percent, text=f"Progress: {current}/{total} batches ({progress_percent*100:.1f}%)")
        
        # Update status text
        status_text.text(f"🔄 {message}")
        
        # Print to terminal for debugging (this will show in the terminal where Streamlit is running)
        if show_terminal_logs:
            print(f"Progress: {progress_percent*100:.1f}% ({current}/{total})")
            print(f"  {message}")
            # Force flush to ensure immediate output
            sys.stdout.flush()
    
    return progress_callback

def main():
    """Main Streamlit app"""
    
    # Header with Groq branding
    st.markdown('<div class="main-header">', unsafe_allow_html=True)
    
    # Add Groq logo at the top
    if os.path.exists("assets/groq-logo.png"):
        st.image("assets/groq-logo.png", width=150)
        st.markdown('<div class="powered-by">Powered by Groq AI</div>', unsafe_allow_html=True)
    
    st.title("📄 PDF Vision Extraction POC")
    st.markdown("**Drag and drop your PDF to extract text, tables, and insights using Groq's vision models**")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Check API key first
    if not check_api_key():
        st.stop()
    
    # Sidebar for options
    with st.sidebar:
        st.header("⚙️ Processing Options")
        
        # Schema Configuration Section
        custom_schema = build_custom_schema()
        
        st.divider()
        
        # Page range selection
        st.subheader("📄 Page Range")
        use_page_range = st.checkbox("Process specific page range", help="Leave unchecked to process entire PDF")
        
        start_page = None
        end_page = None
        
        if use_page_range:
            col1, col2 = st.columns(2)
            with col1:
                start_page = st.number_input("Start Page", min_value=1, value=1)
            with col2:
                end_page = st.number_input("End Page", min_value=1, value=5)
        
        st.divider()
        
        # Information
        st.subheader("ℹ️ About")
        st.write("This application uses the Groq PDF Vision SDK to process PDFs with Groq's vision models.")
        st.write("**Features:**")
        st.write("• Automatic PDF size detection")
        st.write("• Intelligent batch processing")
        st.write("• Table extraction")
        st.write("• Key insights generation")
        st.write("• **High reliability** with automatic retry mechanisms and graceful error handling")
        st.write("• **Comprehensive extraction** including tables, images, text, and metadata")
    
    # File upload section
    st.markdown('<div class="upload-section">', unsafe_allow_html=True)
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Drag and drop your PDF file here or click to browse"
    )
    st.markdown('</div>', unsafe_allow_html=True)
    
    if uploaded_file is not None:
        # Display file info
        st.success(f"✅ File uploaded: **{uploaded_file.name}** ({uploaded_file.size:,} bytes)")
        
        # Process button
        if st.button("🚀 Process PDF", type="primary", use_container_width=True):
            
            # Check if schema is valid (for custom JSON mode)
            if custom_schema is None:
                st.error("❌ Please fix your custom schema before processing")
                return
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name
            
            try:
                # Show processing info
                if use_page_range:
                    st.info(f"📄 Processing pages {start_page} to {end_page}")
                else:
                    st.info("📄 Processing entire PDF with automatic configuration")
                
                # Show schema info
                try:
                    with open('example_docs/example_custom_schema.json', 'r') as f:
                        example_schema = json.load(f)
                    is_example_schema = custom_schema == example_schema
                except:
                    is_example_schema = custom_schema == get_default_schema()
                
                schema_type = "Example" if is_example_schema else "Custom"
                field_count = len(custom_schema.get("properties", {}))
                st.info(f"🔧 Using {schema_type} schema with {field_count} fields")
                
                # Create progress components
                progress_bar = st.progress(0.0, text="Initializing...")
                status_text = st.empty()
                
                # Create progress callback
                progress_callback = create_progress_callback(progress_bar, status_text)
                
                # Process the PDF
                status_text.text("🚀 Starting PDF processing...")
                start_time = time.time()
                
                result, metadata = asyncio.run(
                    process_pdf_async(temp_path, start_page, end_page, progress_callback, custom_schema)
                )
                
                end_time = time.time()
                
                # Clear progress components and show success
                progress_bar.progress(1.0, text="✅ Processing completed!")
                status_text.text("🎉 PDF processed successfully!")
                
                # Success message
                processing_time = end_time - start_time
                st.balloons()
                st.success(f"🎉 PDF processed successfully in {format_processing_time(processing_time)}!")
                
                # Display results
                display_results(result, metadata)
                
            except Exception as e:
                st.error(f"❌ Error processing PDF: {str(e)}")
                st.exception(e)
            
            finally:
                # Clean up temporary file
                try:
                    os.unlink(temp_path)
                except:
                    pass
    
    else:
        # Instructions when no file is uploaded
        st.info("👆 Upload a PDF file to get started")
        
        # Example file processing
        st.subheader("📄 Example Processing")
        if os.path.exists("example_docs/example.pdf"):
            st.write("Use the example 76-page financial document to test the system:")
            
            if st.button("📊 Process example.pdf", help="Process the included 76-page financial document"):
                try:
                    # Check if schema is valid (for custom JSON mode)
                    if custom_schema is None:
                        st.error("❌ Please fix your custom schema before processing")
                        return
                    
                    st.info("📄 Processing example.pdf (76 pages) with real-time progress...")
                    
                    # Show schema info
                    try:
                        with open('example_docs/example_custom_schema.json', 'r') as f:
                            example_schema = json.load(f)
                        is_example_schema = custom_schema == example_schema
                    except:
                        is_example_schema = custom_schema == get_default_schema()
                    
                    schema_type = "Example" if is_example_schema else "Custom"
                    field_count = len(custom_schema.get("properties", {}))
                    st.info(f"🔧 Using {schema_type} schema with {field_count} fields")
                    
                    # Create progress components
                    progress_bar = st.progress(0.0, text="Initializing...")
                    status_text = st.empty()
                    
                    # Create progress callback
                    progress_callback = create_progress_callback(progress_bar, status_text)
                    
                    # Process the PDF
                    status_text.text("🚀 Starting example PDF processing...")
                    start_time = time.time()
                    
                    result, metadata = asyncio.run(
                        process_pdf_async("example_docs/example.pdf", progress_callback=progress_callback, schema=custom_schema)
                    )
                    
                    end_time = time.time()
                    
                    # Clear progress components and show success
                    progress_bar.progress(1.0, text="✅ Processing completed!")
                    status_text.text("🎉 Example PDF processed successfully!")
                    
                    processing_time = end_time - start_time
                    st.balloons()
                    st.success(f"🎉 Example PDF processed successfully in {format_processing_time(processing_time)}!")
                    
                    display_results(result, metadata)
                    
                except Exception as e:
                    st.error(f"❌ Error processing example PDF: {str(e)}")
                    st.exception(e)

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
Streamlit Web UI for Groq PDF Vision Extraction
Simple drag-and-drop interface for processing PDFs using the wrapper.py functions.
"""

import streamlit as st
import asyncio
import tempfile
import os
import json
import time
from datetime import datetime

# Import the wrapper functions (no modifications needed)
from wrapper import extract_data_from_pdf, load_api_key

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
    try:
        load_api_key()
        return True
    except ValueError as e:
        st.error(f"❌ {str(e)}")
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
    """Display the extraction results in a nice format"""
    accumulated_data = result["accumulated_data"]
    processing_stats = result["processing_stats"]
    
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
    
    # Content Preview
    st.subheader("📝 Content Preview")
    content = accumulated_data.get("content", "")
    if content:
        st.text_area(
            "Extracted Text (first 1000 characters)", 
            content[:1000] + ("..." if len(content) > 1000 else ""),
            height=150,
            disabled=True
        )
    
    # Key Insights
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🎯 Key Takeaways")
        takeaways = accumulated_data.get("key_main_takeaways", [])
        if takeaways:
            for i, takeaway in enumerate(takeaways[:5], 1):
                st.write(f"{i}. {takeaway}")
        else:
            st.write("No key takeaways extracted")
    
    with col2:
        st.subheader("🔍 Key Terms")
        terms = accumulated_data.get("wordings_and_terms", [])
        if terms:
            # Display terms as tags
            terms_text = " • ".join(terms[:10])
            st.write(terms_text)
            if len(terms) > 10:
                st.caption(f"... and {len(terms) - 10} more terms")
        else:
            st.write("No key terms extracted")
    
    # Tables
    st.subheader("📊 Extracted Tables")
    tables = accumulated_data.get("tables_data", [])
    if tables:
        for i, table in enumerate(tables[:3], 1):  # Show first 3 tables
            with st.expander(f"Table {i}: {table.get('table_title', 'Untitled')}"):
                if table.get("headers") and table.get("rows"):
                    # Convert to DataFrame for better display
                    import pandas as pd
                    try:
                        df = pd.DataFrame(table["rows"], columns=table["headers"])
                        st.dataframe(df, use_container_width=True)
                    except:
                        st.json(table)
                else:
                    st.json(table)
        
        if len(tables) > 3:
            st.caption(f"... and {len(tables) - 3} more tables in the full results")
    else:
        st.write("No tables found in the document")
    
    # Download Results
    st.subheader("💾 Download Results")
    
    # Prepare download data
    download_data = {
        "processing_metadata": metadata,
        "extraction_results": result
    }
    
    json_str = json.dumps(download_data, indent=2, ensure_ascii=False)
    
    st.download_button(
        label="📥 Download Full Results (JSON)",
        data=json_str,
        file_name=f"pdf_extraction_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
        mime="application/json",
        help="Download the complete extraction results as a JSON file"
    )

async def process_pdf_async(temp_path, start_page=None, end_page=None):
    """Process PDF asynchronously"""
    return await extract_data_from_pdf(
        temp_path,
        start_page=start_page,
        end_page=end_page,
        save_results=False
    )

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
        
        # Page range selection
        st.subheader("Page Range")
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
        st.write("This POC uses your existing `wrapper.py` to process PDFs with Groq's vision models.")
        st.write("**Features:**")
        st.write("• Automatic PDF size detection")
        st.write("• Intelligent batch processing")
        st.write("• Table extraction")
        st.write("• Key insights generation")
        st.write("• 100% reliability (zero failed pages)")
    
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
            
            # Save uploaded file to temporary location
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(uploaded_file.getvalue())
                temp_path = tmp_file.name
            
            try:
                # Processing with progress
                with st.spinner("🔄 Processing PDF... This may take a few minutes for large documents."):
                    
                    # Show processing info
                    if use_page_range:
                        st.info(f"📄 Processing pages {start_page} to {end_page}")
                    else:
                        st.info("📄 Processing entire PDF with automatic configuration")
                    
                    # Process the PDF
                    start_time = time.time()
                    result, metadata = asyncio.run(
                        process_pdf_async(temp_path, start_page, end_page)
                    )
                    end_time = time.time()
                    
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
                    with st.spinner("🔄 Processing example.pdf (76 pages)... This will take about 4 minutes."):
                        start_time = time.time()
                        result, metadata = asyncio.run(
                            process_pdf_async("example_docs/example.pdf")
                        )
                        end_time = time.time()
                        
                        processing_time = end_time - start_time
                        st.balloons()
                        st.success(f"🎉 Example PDF processed successfully in {format_processing_time(processing_time)}!")
                        
                        display_results(result, metadata)
                        
                except Exception as e:
                    st.error(f"❌ Error processing example PDF: {str(e)}")
                    st.exception(e)

if __name__ == "__main__":
    main() 
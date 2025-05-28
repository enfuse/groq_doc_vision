# Groq PDF Vision - Test Suite & Performance Results

This directory contains comprehensive test suites for the Groq PDF Vision library, including performance benchmarks and real-world document processing results.

## 🚀 Quick Start

Run all tests with the automated test runner:

```bash
python3 run_all_tests.py
```

The test runner includes:
- **Basic Tests** (~30 seconds): Quick validation of core functionality
- **Full Document Tests** (~15-20 minutes): Comprehensive stress testing with user confirmation

## 📊 Performance Benchmarks

### Auto-Configuration System Results

Our intelligent auto-configuration system optimizes batch sizes based on document size:

| Document Size | Category | Batch Size | DPI | Configuration |
|---------------|----------|------------|-----|---------------|
| ≤ 10 pages | Small PDF | 2 pages | 200 | High quality processing |
| 11-50 pages | Medium PDF | 3 pages | 150 | Balanced processing |
| 51-200 pages | Large PDF | 4 pages | 150 | Efficient batch processing |
| > 200 pages | Enterprise PDF | 5 pages | 120 | Maximum batch efficiency |

### Full Document Processing Results

#### Vision 2030 Saudi Arabia (85 pages)
- **Processing Time**: 1.8 minutes (110.7 seconds)
- **Token Usage**: 225,024 tokens
- **Processing Speed**: 2,033 tokens/second
- **Batch Configuration**: 22 batches × 4 pages
- **Auto-Config**: Large PDF - Efficient batch processing
- **Content Analysis**:
  - Pages with text: 65/86
  - Pages with images: 50/86
  - Pages with tables: 7/86
- **Cost Estimate**: ~$0.23

#### Example Financial Document (76 pages)
- **Processing Time**: 2.4 minutes (146.2 seconds)
- **Token Usage**: 197,991 tokens
- **Processing Speed**: 1,354 tokens/second
- **Batch Configuration**: 19 batches × 4 pages
- **Auto-Config**: Large PDF - Efficient batch processing
- **Content Analysis**:
  - Pages with text: 75/79
  - Pages with images: 11/79
  - Pages with tables: 45/79
- **Cost Estimate**: ~$0.20

#### Americas Children 2023 Report (118 pages)
- **Processing Time**: 3.4 minutes (202.8 seconds)
- **Token Usage**: 346,562 tokens
- **Processing Speed**: 1,709 tokens/second
- **Batch Configuration**: 30 batches × 4 pages
- **Auto-Config**: Large PDF - Efficient batch processing
- **Content Analysis**:
  - Rich government report with charts and tables
  - Comprehensive statistical data extraction
- **Cost Estimate**: ~$0.35

#### Federal Economic Wellbeing 2020 (88 pages)
- **Processing Time**: 2.9 minutes (174.6 seconds)
- **Token Usage**: 265,143 tokens
- **Processing Speed**: 1,519 tokens/second
- **Batch Configuration**: 22 batches × 4 pages
- **Auto-Config**: Large PDF - Efficient batch processing
- **Content Analysis**:
  - Economic data with rich visualizations
  - 29 pages with substantial table data
- **Cost Estimate**: ~$0.27

### Performance Comparison: Americas Children vs Federal Economic Wellbeing

| Metric | Americas Children (118p) | Fed Economic (88p) | Difference |
|--------|-------------------------|-------------------|------------|
| **Processing Time** | 202.8s (3.4 min) | 174.6s (2.9 min) | -28.2s (-14%) |
| **Token Usage** | 346,562 tokens | 265,143 tokens | -81,419 tokens (-23%) |
| **Processing Speed** | 1,709 tokens/sec | 1,519 tokens/sec | Fed 11% slower |
| **Time per Page** | 1.7s/page | 2.0s/page | Fed 18% slower per page |
| **Tokens per Page** | 2,938 tokens/page | 3,013 tokens/page | Fed +75 tokens/page |
| **Cost Efficiency** | ~$0.35 | ~$0.27 | 23% less expensive |
| **Batch Configuration** | 30 batches × 4 pages | 22 batches × 4 pages | Same optimization |

**Key Insights**:
- Both documents correctly used batch_size=4 (Large PDF category)
- Fed Economic document had higher per-page complexity but processed faster overall
- Auto-configuration system performed consistently across different document types
- Cost scales linearly with token usage (~$0.001 per 1K tokens)

## 🧪 Test Suite Structure

### Basic Tests (Quick Validation)

#### 1. README Examples (`test_readme_examples.py`)
Tests all code examples from the main README:
- Synchronous processing examples
- Asynchronous processing examples
- Custom schema usage
- Progress callback functionality

#### 2. Integration Examples (`test_flask_integration.py`)
Tests integration patterns:
- Flask web application integration
- FastAPI integration logic
- Batch processing workflows

#### 3. Schema Usage (`test_example_schema.py`)
Tests schema functionality:
- Loading JSON schemas directly
- Building schemas with helper functions
- Custom schema validation

#### 4. CLI Commands
Tests command-line interface:
- Basic PDF processing
- Info-only mode
- Schema validation
- Parameter handling

### Full Document Tests (Stress Testing)

#### 1. Vision 2030 (`test_vision2030_full_async.py`)
- Tests large government document processing
- Arabic and English mixed content
- Complex layouts with images and diagrams

#### 2. Example Document (`test_example_full_async.py`)
- Tests financial document processing
- Heavy table content extraction
- Multi-page financial statements

#### 3. Americas Children (`test_americas_children_full_async.py`)
- Tests government statistical report
- Rich charts and data visualization
- Comprehensive data extraction

#### 4. Federal Economic Wellbeing (`test_fed_economic_wellbeing_full_async.py`)
- Tests economic research document
- Mixed content types (text, tables, charts)
- Real-world economic data

## 🔧 Auto-Configuration Optimization History

### Initial Performance Issues (Resolved)
- **Problem**: 118-page document using batch_size=2 instead of expected batch_size=4
- **Root Cause**: Auto-configuration using `pages_to_process` instead of `total_pages`
- **Fix**: Updated logic to use total document size for configuration decisions
- **Result**: 50% fewer API calls, 38% faster processing, 45% improved token throughput

### Before vs After Optimization
| Metric | Before (118p) | After (118p) | Improvement |
|--------|---------------|--------------|-------------|
| **Batches** | 59 batches × 2 pages | 30 batches × 4 pages | 50% fewer API calls |
| **Processing Time** | 5.5 minutes | 3.4 minutes | 38% faster |
| **Token Usage** | 388,753 tokens | 346,562 tokens | 11% more efficient |
| **Processing Speed** | 1,182 tokens/sec | 1,709 tokens/sec | 45% faster |

## 📋 Data Extraction Capabilities

### Content Structure
Each page result includes:
```json
{
  "page_number": 15,
  "content": "extracted text content...",
  "contains_tables": true,
  "tables_data": [
    {
      "table_title": "Table A. Financial Data",
      "headers": ["Year", "Value", "Change"],
      "rows": [
        {"Year": "2019", "Value": "85", "Change": "5"}
      ],
      "summary": "Financial performance table"
    }
  ],
  "contains_images": true,
  "image_descriptions": [
    {
      "image_type": "chart",
      "description": "Bar chart showing economic trends",
      "location": "center",
      "relevance": "supporting data"
    }
  ],
  "entities": ["Federal Reserve", "Economic Policy"],
  "key_findings": ["Economic growth increased by 5%"]
}
```

### Page-Level Tracking
- **✅ Clear Page Association**: Every extracted element is tagged with its source page
- **✅ Precise Location**: Images and tables clearly linked to specific pages
- **✅ Easy Navigation**: Filter and cross-reference content by page number
- **✅ Complete Context**: Correlate visual elements with surrounding text

## 💰 Cost Analysis

### Token Usage Patterns
- **Text-Heavy Pages**: ~2,000-3,000 tokens per page
- **Image-Rich Pages**: ~3,000-4,000 tokens per page
- **Table-Heavy Pages**: ~2,500-3,500 tokens per page
- **Mixed Content**: ~2,500-3,500 tokens per page

### Cost Estimates (at $0.001/1K tokens)
- **Small Documents** (≤10 pages): $0.02-0.04
- **Medium Documents** (11-50 pages): $0.05-0.15
- **Large Documents** (51-200 pages): $0.15-0.70
- **Enterprise Documents** (>200 pages): $0.50-2.00+

## 🎯 Performance Optimization Features

### 1. Intelligent Batch Sizing
- Automatically scales batch size based on document complexity
- Minimizes API calls while maintaining quality
- Balances speed vs. accuracy

### 2. Real-Time Progress Tracking
- Live progress updates with ETA calculations
- Immediate output with `sys.stdout.flush()`
- Detailed batch-by-batch reporting

### 3. Robust Error Handling
- Automatic retry logic with exponential backoff
- Graceful degradation for failed pages
- Comprehensive error reporting

### 4. Memory Optimization
- Efficient image processing and compression
- Streaming JSON output for large results
- Cleanup of temporary resources

## 🔍 Quality Assurance

### Test Coverage
- **Unit Tests**: Core functionality validation
- **Integration Tests**: End-to-end workflow testing
- **Performance Tests**: Large document stress testing
- **Regression Tests**: Ensure optimizations don't break functionality

### Validation Metrics
- **Accuracy**: Content extraction fidelity
- **Completeness**: No missing pages or elements
- **Consistency**: Reliable results across document types
- **Performance**: Processing speed and efficiency

## 🚀 Running Tests

### Prerequisites
```bash
# Set API key
export GROQ_API_KEY='your-key-here'

# Install dependencies
pip install -e .
```

### Individual Test Execution
```bash
# Basic functionality tests
python3 test_readme_examples.py
python3 test_flask_integration.py
python3 test_example_schema.py

# Full document stress tests (longer processing)
python3 test_vision2030_full_async.py
python3 test_americas_children_full_async.py
python3 test_fed_economic_wellbeing_full_async.py
```

### Automated Test Suite
```bash
# Run all tests with user confirmation for full tests
python3 run_all_tests.py
```

## 📈 Future Enhancements

### Planned Optimizations
1. **Dynamic Batch Sizing**: Adjust batch size based on content complexity
2. **Parallel Processing**: Concurrent batch processing for faster throughput
3. **Smart Caching**: Cache repeated content for efficiency
4. **Quality Metrics**: Automated extraction quality assessment

### Scalability Targets
- **1000+ Page Documents**: Enterprise-scale processing
- **Multi-Document Batches**: Parallel document processing
- **Real-Time Processing**: Sub-second per-page processing
- **Cost Optimization**: Further reduce token usage through smart prompting

---

*This test suite demonstrates the library's capability to handle real-world document processing scenarios with excellent performance, accuracy, and cost efficiency.* 
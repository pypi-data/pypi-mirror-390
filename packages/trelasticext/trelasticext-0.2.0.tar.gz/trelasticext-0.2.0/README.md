# TRelasticExt

A Python package for enhanced Elasticsearch (8.x.x) operations with specialized support for Hebrew text processing.

## Installation

```bash
pip install trelasticext
```

## Features

- Elasticsearch document management (create, update, delete)
- Hebrew text tokenization and analysis
- Text similarity search with customizable parameters
- Bulk operations for efficient data handling
- Support for cross-index and cross-cluster operations

## Quick Start

```python
import trelasticext as ee

# Connect to Elasticsearch
es_params = {"ehost": "http://localhost:9200", "index": "my_index"}

# Search for documents
results = ee.get_es_records_by_field("location", "document_location", es_params)

# Tokenize Hebrew text
tokens = ee.ftokens("שלום עולם")

# Build a custom query
query = ee.query_builder(
    text="מילים לחיפוש",
    fields=["content", "title"],
    fuzziness=1,
    query_type="multimatch"
)
```

## Advanced Usage

### Document Operations

```python
# Add a document
doc = {"title": "Sample Document", "content": "This is a test"}
ee.post_es_record(doc, es_params)

# Update a document by ID
update_doc = {"doc": {"title": "Updated Title"}}
ee.update_by_id("doc_id", update_doc, es_params["index"], es_params)

# Delete a document
ee.delete_es_record("doc_id", es_params)
```

### Bulk Operations

```python
# Copy data between Elasticsearch clusters
source_params = {"ehost": "http://source-es:9200", "index": "source_index"}
target_params = {"ehost": "http://target-es:9200", "index": "target_index"}

ee.copy_records_between_hosts(source_params, target_params, clear_data=True)
```

### Text Analysis

```python
# Analyze text using Elasticsearch analyzers
analysis = ee.get_es_analyze_text(
    index="my_index",
    analyzer="hebrew",
    text="טקסט לניתוח",
    es_params=es_params
)

# Get tokens with language filtering
hebrew_tokens = ee.ftokens("מילים באנגלית and Hebrew", lang=["HEB"])
```

## API Reference

### Main Functions

- `get_es_records_by_field(field, value, es_params, les=None, default_result=False, all_records=False)`
- `get_es_source_by_field(field, value, es_params, les=None)`
- `post_es_record(doc, es_params, les=None)`
- `update_by_id(doc_id, doc, index, es_params, les=None)`
- `delete_es_record(doc_id, es_params, les=None)`
- `ftokens(text, spliter=None, lang=None)`
- `query_builder(text, fields=["sentence"], fuzziness=0, ...)`

## Requirements

- Python 3.6+
- elasticsearch
- pandas
- numpy
- fasttext
- Levenshtein

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
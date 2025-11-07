"""
TRelasticExt - Elasticsearch Extensions for Hebrew and Multi-language Text Processing

This package provides utilities for working with Elasticsearch in Hebrew and multi-language
text processing contexts, including tokenization, synonym management, and query building.
"""

# Import Elasticsearch extension functions
from .elastic_extension import (
    load_synonyms,
    write_synonyms,
    get_index_records,
    get_es_analyze_text,
    get_es_records_by_field,
    get_record_by_id,
    get_es_source_by_field,
    get_es_sentence_from_source,
    get_es_scored_source_by_field,
    get_sentence_count,
    delete_es_record,
    delete_by_query,
    post_es_record,
    bulk_store,
    copy_records_between_hosts,
    get_parasha,
    update_by_id,
    update_by_location,
    es_tokenizer,
    tokens2expresions,
    ftokens,
    clean_query_text,
    query_builder,
    hebSentence2record,
    searchBQsequences,
)

# Import Hebrew tokenizer functions
from .heb_tokenizer import (
    is_hebrew_token,
    tokenize,
)

__version__ = "0.2.0"
__author__ = "Hadar Miller"

__all__ = [
    # Elasticsearch functions
    "load_synonyms",
    "write_synonyms",
    "get_index_records",
    "get_es_analyze_text",
    "get_es_records_by_field",
    "get_record_by_id",
    "get_es_source_by_field",
    "get_es_sentence_from_source",
    "get_es_scored_source_by_field",
    "get_sentence_count",
    "delete_es_record",
    "delete_by_query",
    "post_es_record",
    "bulk_store",
    "copy_records_between_hosts",
    "get_parasha",
    "update_by_id",
    "update_by_location",
    "es_tokenizer",
    "tokens2expresions",
    "ftokens",
    "clean_query_text",
    "query_builder",
    "hebSentence2record",
    "searchBQsequences",
    # Hebrew tokenizer functions
    "is_hebrew_token",
    "tokenize",
]
# Changelog

All notable changes to the TRelasticExt project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-06

### Changed
- Restructured package to use professional src/ layout following Python packaging best practices
- Updated Elasticsearch dependency to support broader version range: `elasticsearch>=7.0.0,<9.0.0`
- Updated pandas dependency to `>=1.3.0` for better compatibility
- Updated numpy dependency to `>=1.20.0` for better compatibility
- Migrated from flat package structure to `src/trelasticext/` layout
- Enhanced `__init__.py` with explicit function exports and `__all__` list
- Added comprehensive docstring to package `__init__.py`

### Added
- Created professional `setup.py` with complete metadata and classifiers
- Created modern `pyproject.toml` following PEP standards
- Added http_auth parameter support to all Elasticsearch client functions (14 functions)
- Added comprehensive CHANGELOG.md for version tracking
- Added dev dependencies for testing and code quality (pytest, black, flake8)
- Python 3.8-3.11 support explicitly documented

### Fixed
- Authentication support now available across all Elasticsearch operations
- Better error handling in Elasticsearch connection functions

## [0.1.0] - Initial Release

### Added
- Initial release of TRelasticExt package
- Elasticsearch extension functions for Hebrew text processing
- Hebrew tokenizer with multi-language support (Hebrew, Arabic, Greek, Latin)
- Synonym management utilities
- Query building functions for Elasticsearch
- Bulk operations support
- Record management (CRUD operations)
- Text analysis and tokenization utilities

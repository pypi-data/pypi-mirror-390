# Changelog

All notable changes to TRAligner will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2025-11-06

### Added
- Proper src/ package layout for better distribution
- Comprehensive test suite with test_alignment.py
- Full API documentation in API_REFERENCE.md
- Enhanced README with detailed usage examples
- pyproject.toml for modern Python packaging
- Support for LLM-based token comparison
- Enhanced morphology embedding matching capabilities
- Improved Greek stemming integration

### Changed
- Restructured package following Python packaging best practices
- Migrated to src/traligner/ layout for better import isolation
- Updated documentation with comprehensive examples and results interpretation
- Improved alignment scoring mechanism for better sequence matching

### Fixed
- Fixed IndexError in `calc_token_value` with proper parameter mapping
- Corrected `increment2one` dictionary key mapping in alignment scoring
- Fixed `sus_t` and `src_t` parameter confusion in test suite

### Documentation
- Added comprehensive README with installation and usage instructions
- Created API_REFERENCE.md with detailed function documentation
- Included examples with Hebrew text alignment
- Documented Smith-Waterman and Needleman-Wunsch algorithms

## [0.1.0] - 2024-06-12

### Added
- Initial release of TRAligner
- Smith-Waterman alignment algorithm implementation
- Needleman-Wunsch alignment algorithm implementation
- Multi-language tokenization support
- Hebrew text processing capabilities
- Fuzzy matching with Levenshtein distance
- Scoring mechanisms for alignment quality assessment
- Basic test suite

### Features
- Text alignment for Hebrew and multi-language texts
- Support for exact and fuzzy matching
- Configurable match/mismatch/gap scores
- Multiple alignment method options
- Token-level comparison functions

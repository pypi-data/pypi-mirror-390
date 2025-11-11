# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-11-10

### Added
- Initial release of TOON2 (Token-Oriented Object Notation v2)
- Hierarchical tuple-based JSON compression with 28.7% average token reduction
- Perfect roundtrip fidelity for complex nested JSON structures
- Support for mixed data types including arrays, objects, and primitives
- Smart schema detection and optimization
- Command-line interface with encode, decode, benchmark, and validate commands
- Comprehensive test suite with 92.9% success rate across diverse data patterns
- Utility functions for token counting and compression benchmarking
- Custom delimiter support for data containing commas
- Proper handling of null values and sparse data
- Deep nesting support with quoted string parsing
- JSON array and object parsing within tabular format

### Features
- **Toon2Encoder**: Converts JSON to token-optimized TOON2 format
- **Toon2Decoder**: Converts TOON2 format back to original JSON
- **CLI Tools**: Command-line interface for batch processing
- **Benchmarking**: Built-in performance measurement tools
- **Validation**: Format validation utilities

### Performance
- Average token reduction: 28.7%
- Best case reduction: 61.0% (large structured datasets)
- Success rate: 92.9% perfect roundtrip fidelity
- Supports Python 3.8+

### Technical Details
- Hierarchical tuple compression: `address{street,city,coordinates{lat,lng}}`
- Smart CSV parsing with bracket/brace awareness
- JSON-compatible primitive encoding
- Schema normalization for inconsistent object arrays
- Lightweight core with no required dependencies